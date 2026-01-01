# Plan: Claude Code Hooks for intents-plugin

**Feature:** stop-hooks
**Status:** planned
**Created:** 2025-12-29
**Refined:** 2025-12-29
**Research:** [005-claude-code-stop-hooks.md](../../research/005-claude-code-stop-hooks.md)

---

## Problem Statement

The intents-plugin harness relies on Claude "remembering" to run quality checks, load context, and validate work against plans. This creates reliability issues:

- Tests may not run consistently
- MEMORY.md context may not be loaded on session resume
- Implementation may not be validated against PLAN.md
- Quality gates depend on instruction following rather than deterministic enforcement

**Current state:** Commands use `<checkpoint>` blocks and `STOP` keywords for manual gates, but these are suggestions that Claude can skip or forget.

**Desired state:** Hooks provide deterministic guarantees—quality checks run automatically, context loads on resume, chunks commit on pass.

**Important context:** The intents-plugin is a portable harness that gets installed INTO target codebases (Next.js apps, Python backends, etc.). Target projects have real test infrastructure (npm test, pytest, cargo test). These hooks run in the target project's context.

---

## Goals

1. **Deterministic quality gates** - Lint/typecheck/test run automatically, not by request
2. **Automatic context loading** - MEMORY.md and PLAN.md loaded when resuming in-progress features
3. **Chunk validation** - Each implementation chunk validated and committed before proceeding
4. **Final verification** - Full validation pipeline at feature completion with graph status update

## Non-Goals

- Per-chunk code review (expensive, save for final review)
- Prompt-based hooks (start with deterministic command-based, consider for Phase 4)
- Complex installation/configuration flows (YAGNI)

---

## Proposed Approach

### Hook Location

Hooks live in `intents-plugin/hooks/` and run directly from there. No copying needed—if the plugin is installed, the hooks are available.

```
intents-plugin/hooks/             # Hooks run from here
  session_start.py
  chunk_complete.py
  feature_complete.py
  utils/
    ...
```

### Hook Overview

| Hook | Event | Purpose |
|------|-------|---------|
| `session_start.py` | SessionStart | Load MEMORY.md + PLAN.md for in-progress features |
| `chunk_complete.py` | SubagentStop | Validate chunk, update MEMORY.md, auto-commit on pass |
| `feature_complete.py` | Stop | Full validation, code review, graph update |

All hooks:
- Check `stop_hook_active` to prevent infinite loops
- Use Python for JSON handling and file operations
- Exit 0 with JSON decision (approve/block)
- Include test output in block reasons for actionable feedback
- Implement retry limit (3 attempts) to prevent infinite loops
- Auto-detect test commands based on project type

### Test Command Auto-Detection

```python
def get_test_command():
    if os.path.exists('package.json'):
        return 'npm test'
    elif os.path.exists('pyproject.toml') or os.path.exists('setup.py'):
        return 'pytest'
    elif os.path.exists('Cargo.toml'):
        return 'cargo test'
    return None  # Skip validation if unknown project type
```

No configuration needed. If someone has a non-standard setup, they edit the hook file directly.

---

## Trade-offs

| Trade-off | Decision | Rationale |
|-----------|----------|-----------|
| Python vs Bash | Python | Better JSON handling, cleaner logic |
| Per-chunk commit vs batch | Per-chunk | Granular git history, easier rollback |
| Prompt vs command hooks | Command | Deterministic, cheaper, debuggable |
| Code review timing | End only | Per-chunk too expensive, final review catches issues |
| Test command discovery | Auto-detect | Simple, no config needed, fail gracefully if unknown |
| Chunk detection | Marker file | Deterministic vs fragile pattern matching |
| Retry limit | 3 attempts | Prevent infinite loops, then approve with warning |

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Unknown project type | Medium | Low | Skip validation, approve with warning |
| Marker file deletion fails | Low | Medium | Wrap in try/except, log but don't fail |
| Hooks slow down workflow | Medium | Medium | Fail fast, show systemMessage progress |
| Infinite retry loops | Low | Medium | 3-attempt limit, then approve with warning |

---

## Phases

### Phase 1: Foundation

Core hooks—SessionStart and Stop.

| Chunk | Scope | Files |
|-------|-------|-------|
| 1A | Hook utilities: project detection, test runners, context loading | `intents-plugin/hooks/utils/__init__.py`, `utils/context.py`, `utils/checks.py` |
| 1B | SessionStart hook: detect in-progress feature, load MEMORY.md + PLAN.md | `intents-plugin/hooks/session_start.py` |
| 1C | Stop hook: auto-detect and run tests, block on failure with output | `intents-plugin/hooks/feature_complete.py` |

**Ship Criteria:**
- [ ] SessionStart loads context for in-progress features only
- [ ] Stop hook auto-detects project type and runs appropriate tests
- [ ] Infinite loop prevention works (`stop_hook_active` check)
- [ ] Hooks fail gracefully (approve on error, don't break workflow)
- [ ] Block reasons include actual test output

**Phase Gate:** Test in a real project. Start session with in-progress feature, verify context loads. Complete a task, verify tests run.

---

### Phase 2: Chunk Automation

Add SubagentStop for chunk-level validation and auto-commit using marker file pattern.

| Chunk | Scope | Files |
|-------|-------|-------|
| 2A | Update feature-implementer: write `.claude/.chunk-complete` marker after each chunk | `intents-plugin/agents/feature-implementer/AGENT.md` (use `agent-builder` skill) |
| 2B | SubagentStop hook: detect marker, validate, update MEMORY.md, auto-commit, delete marker | `intents-plugin/hooks/chunk_complete.py`, `utils/memory.py` |
| 2C | Update implement command: document hook-driven flow | `intents-plugin/commands/implement.md` (use `command-builder` skill) |

**Marker File Format:**
```json
{
  "chunk": "1A",
  "feature": "user-settings",
  "phase": 1,
  "description": "Hook infrastructure and utilities",
  "timestamp": "2025-12-29T10:30:00Z"
}
```

**Ship Criteria:**
- [ ] feature-implementer writes marker file after completing each chunk
- [ ] SubagentStop detects marker, runs validation (auto-detected tests)
- [ ] MEMORY.md updated with chunk completion status (deterministic)
- [ ] Auto-commit on pass: `feat(<feature>): chunk <N> - <description>`
- [ ] Marker file deleted after processing
- [ ] Non-implementation subagents ignored (no marker = no validation)

**Phase Gate:** Implement a test feature, verify each chunk auto-commits on pass.

---

### Phase 3: Final Validation

Full validation pipeline at feature completion.

| Chunk | Scope | Files |
|-------|-------|-------|
| 3A | Enhance Stop hook: detect feature completion, spawn code-reviewer | Update `intents-plugin/hooks/feature_complete.py` |
| 3B | Plan verification: compare implementation to PLAN.md requirements | `intents-plugin/hooks/utils/plan_verify.py` |
| 3C | Graph update: set status to `implemented` on full pass | `intents-plugin/hooks/utils/graph.py` |
| 3D | Update implement command: document final validation flow | `intents-plugin/commands/implement.md` (use `command-builder` skill) |

**Ship Criteria:**
- [ ] Code review runs at feature completion (not per chunk)
- [ ] Implementation verified against PLAN.md requirements
- [ ] Graph status updated to `implemented` automatically on pass
- [ ] Graceful handling when checks fail (block with actionable feedback)
- [ ] 3-retry limit: after 3 failures, approve with warning

**Phase Gate:** Complete a full feature, verify code review runs, graph updates.

---

## Technical Approach

### Directory Structure

```
intents-plugin/
  hooks/
    session_start.py      # SessionStart hook
    chunk_complete.py     # SubagentStop hook
    feature_complete.py   # Stop hook
    utils/
      __init__.py
      context.py          # MEMORY.md/PLAN.md loading
      checks.py           # Test command detection and running
      memory.py           # MEMORY.md update operations
      graph.py            # Graph.yaml operations (Phase 3)
      plan_verify.py      # Plan verification (Phase 3)
```

### Enabling Hooks

User adds to their `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "python3 intents-plugin/hooks/session_start.py"
      }]
    }],
    "SubagentStop": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "python3 intents-plugin/hooks/chunk_complete.py"
      }]
    }],
    "Stop": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "python3 intents-plugin/hooks/feature_complete.py"
      }]
    }]
  }
}
```

Document this in `intents-plugin/README.md`.

### MEMORY.md Update on Chunk Completion

```python
# utils/memory.py
import re
from pathlib import Path
from glob import glob

def find_memory_file(feature: str) -> Path | None:
    """Find MEMORY.md for the given feature."""
    patterns = [
        f'docs/plans/{feature}/MEMORY.md',
        f'docs/plans/*/{feature}/MEMORY.md',  # Enhancement path
    ]
    for pattern in patterns:
        matches = glob(pattern)
        if matches:
            return Path(matches[0])
    return None

def update_chunk_status(feature: str, chunk: str, status: str = 'completed'):
    """Update chunk status in MEMORY.md progress table."""
    memory_path = find_memory_file(feature)
    if not memory_path or not memory_path.exists():
        return False

    content = memory_path.read_text()

    # Update progress table: | 1A | pending | -> | 1A | completed |
    pattern = rf'(\|\s*{re.escape(chunk)}\s*\|)\s*\w+\s*(\|)'
    replacement = rf'\1 {status} \2'
    updated = re.sub(pattern, replacement, content)

    if updated != content:
        memory_path.write_text(updated)
        return True
    return False
```

### Infinite Loop Prevention + Retry Limit

```python
import json
import sys
import os

RETRY_FILE = '.claude/.hook-retries'
MAX_RETRIES = 3

data = json.load(sys.stdin)

# CRITICAL: Prevent infinite loops
if data.get('stop_hook_active'):
    print(json.dumps({"decision": "approve"}))
    sys.exit(0)

# Track retries
retries = 0
if os.path.exists(RETRY_FILE):
    retries = int(open(RETRY_FILE).read().strip())

if retries >= MAX_RETRIES:
    os.remove(RETRY_FILE)
    print(json.dumps({
        "decision": "approve",
        "systemMessage": f"Quality checks failed {MAX_RETRIES} times. Stopping for manual investigation."
    }))
    sys.exit(0)
```

### Error Handling with Test Output

```python
import subprocess

def run_checks():
    cmd = get_test_command()
    if not cmd:
        return True, []  # No tests to run, pass

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=120
        )
        passed = result.returncode == 0
        return passed, [{
            "name": "test",
            "passed": passed,
            "output": result.stdout + result.stderr
        }]
    except Exception as e:
        return False, [{"name": "test", "passed": False, "output": str(e)}]

def format_block_reason(results):
    """Include test output in block reason for actionable feedback."""
    lines = ["Quality checks failed:\n"]
    for r in results:
        status = "✓" if r["passed"] else "✗"
        lines.append(f"{status} {r['name']}")
        if not r["passed"]:
            lines.append(f"   Output:\n{r['output'][:500]}")
    lines.append("\nPlease fix the failing checks.")
    return "\n".join(lines)
```

---

## Implementation Notes

### Required Skills

When modifying intents-plugin components, use the appropriate skills from `.claude/skills/`:

| Component | Skill to Use |
|-----------|--------------|
| Commands (`intents-plugin/commands/`) | `command-builder` |
| Agents (`intents-plugin/agents/`) | `agent-builder` |
| Skills (`intents-plugin/skills/`) | `skill-creator` |
| Unsure which to create | `extension-picker` |

### Dependencies

- Python 3.x (for hook scripts)
- `pyyaml` (for graph.yaml parsing in Phase 3)

---

## Future Enhancements (Post-Phase 3)

- **Prompt-based hooks** for intelligent PLAN.md verification
- **Monorepo support** - run tests scoped to changed workspace
- **Parallel check execution** - run lint/typecheck/test concurrently

---

## Success Metrics

- Quality checks run on 100% of Stop events (not skipped)
- Context loads automatically on resume (no manual file reading)
- Chunks commit atomically with descriptive messages
- Feature completion triggers full review (code-reviewer runs)
- Zero infinite loop incidents (retry limit works)
