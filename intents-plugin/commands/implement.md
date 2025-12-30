---
description: Implement a planned feature with quality checks. Use when ready to build.
argument-hint: <feature-id | parent/enhancement | capabilities/name> [--skip-tests] [--skip-review]
---

# /intents:implement

Orchestrate implementation of a planned feature.

## Usage

```
/intents:implement <feature-id>
/intents:implement <parent>/<enhancement>
/intents:implement capabilities/<capability>
/intents:implement <feature-id> --skip-tests
```

## Workflow

### Stage 1: Validate Prerequisites

Determine lookup method based on argument format:

**If argument contains `/` (path format):**
```
Parse as path (e.g., parent/enhancement or capabilities/name)
Read plan directly from docs/plans/<path>/PLAN.md
Skip graph lookup (enhancements and capabilities don't have graph nodes)
```

**If no `/` (feature-id format):**
```
Read .intents/graph.yaml → find feature by ID
Verify docs/plans/<feature>/PLAN.md exists
Status must be: planned | broken
```

**Error → STOP.** Inform user. If no plan, suggest `/intents:plan <feature>`.

### Stage 2: Git Prep

```bash
git branch --show-current  # Must not be main/master
git status --short         # Warn if uncommitted changes
```

If on main: create feature branch `feature/<feature-id>` and switch to it.

**Error → STOP.** Inform user.

### Stage 3: Update Graph Status

**If feature (not enhancement):**
```yaml
# .intents/graph.yaml
feature-id:
  status: in-progress
```

**If path format (enhancement or capability):**
- Skip graph update (no graph nodes for these)

**Error → STOP.** Inform user.

### Stage 4: Test Spec (unless --skip-tests)

Spawn `test-spec` agent for this feature.

**✓ CHECKPOINT:** Show results, ask user to continue.
**Error →** Resume agent to fix, then checkpoint again.

### Stage 5: Feature Implementer

Spawn `feature-implementer` agent:

**If feature:**
```
Feature: <feature-id>
Plan: docs/plans/<feature>/PLAN.md
Memory: docs/plans/<feature>/MEMORY.md
```

**If path format (enhancement or capability):**
```
Feature: <path>
Plan: docs/plans/<path>/PLAN.md
Memory: docs/plans/<path>/MEMORY.md
```

Agent handles internally:
- Chunk-by-chunk implementation
- Validation against plan
- MEMORY.md updates
- Phase gates
- Writing `.claude/.chunk-complete` marker after each chunk

**Hook Automation (if enabled):**

When SubagentStop hook is configured, chunk completion triggers:
1. Marker file detected by hook
2. Tests run automatically (auto-detected: npm test/pytest/cargo test)
3. On pass: MEMORY.md updated, changes auto-committed
4. On fail: Block with test output, retry up to 3 times
5. Marker deleted after processing

This provides deterministic quality gates without relying on Claude remembering to run tests.

**✓ CHECKPOINT:** Show results, ask user to continue.
**Error →** Resume agent to fix, then checkpoint again.

### Stage 6: Review Loop (unless --skip-review)

Spawn review agents based on feature:

| Agent | When |
|-------|------|
| `code-reviewer` | Always |
| `security-auditor` | Auth, API, payment, admin, data handling |
| `accessibility-reviewer` | UI components |

**Review loop:**
1. Run applicable reviewers
2. If issues found → STOP, show issues to user
3. User decides: **fix** / **skip issue** / **abort**
4. If fix: resume `feature-implementer` with feedback
5. Re-run failed reviewers
6. Repeat until clean or user says proceed

### Stage 7: Finalize

**If feature (not enhancement):**
Update graph status:
- Success → `implemented`
- User abort → `broken` (log reason)

**If path format (enhancement or capability):**
- No graph update needed
- If capability: verify added to `.intents/capabilities.yaml`
- Report completion with plan path

## Options

| Option | Effect |
|--------|--------|
| `--skip-tests` | Skip Stage 4 |
| `--skip-review` | Skip Stage 6 |

## Resume

Re-run command to resume. The `feature-implementer` reads MEMORY.md and continues from last completed chunk.

## Hook Configuration

To enable automatic quality gates, add to `.claude/settings.json`:

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

**Hook behavior:**
- **SessionStart**: Loads MEMORY.md + PLAN.md for in-progress features
- **SubagentStop**: Validates chunks, auto-commits on pass
- **Stop**: Runs final tests before completion

## Completion

```
✅ Feature implemented: <feature-id>

Graph: status → implemented
Files: [list of created/modified]

Next:
  - Test manually
  - Merge to main
```
