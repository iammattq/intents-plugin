# Hook Setup Guide

Optional hooks for automatic quality gates during `/intents:implement`.

## Quick Setup

Add to `.claude/settings.json`:

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

## Hook Behavior

| Hook | When | What It Does |
|------|------|--------------|
| SessionStart | Session begins | Loads MEMORY.md + PLAN.md for in-progress features |
| SubagentStop | Chunk completes | Runs tests, auto-commits on pass, blocks on fail |
| Stop | Feature completes | Full validation pipeline (tests, plan verification, code review) |

## SubagentStop: Chunk Validation

When `feature-implementer` writes `.claude/.chunk-complete` marker:

1. Marker file detected by hook
2. Tests run automatically (auto-detected: npm test/pytest/cargo test)
3. On pass: MEMORY.md updated, changes auto-committed
4. On fail: Block with test output, retry up to 3 times
5. Marker deleted after processing

## Stop: Final Validation Pipeline

When the Stop hook is enabled, feature completion triggers:

### Validation Steps

1. **Quality Checks (Tests)**
   - Auto-detects project type (package.json, pyproject.toml, Cargo.toml)
   - Runs appropriate test command
   - Blocks with test output on failure

2. **Plan Verification**
   - Compares implementation to PLAN.md ship criteria
   - Checks MEMORY.md for completed items
   - Blocks with missing criteria on failure

3. **Code Review** (on feature completion)
   - Spawns code-reviewer agent for final review
   - Reviews all files changed in the feature branch
   - Runs once per feature (not per chunk)

4. **Graph Update**
   - Sets status to `implemented` on full pass
   - Automatic - no manual graph editing needed

### Failure Handling

- **Retry limit**: After 3 consecutive failures, approves with warning
- **Actionable feedback**: Block reasons include actual test output and missing criteria
- **Fail open**: Hook errors don't block - workflow continues with warning

### Flow Diagram

```
Stop Event
    |
    v
[stop_hook_active?] --yes--> APPROVE (prevent loop)
    |
    no
    v
[retry limit exceeded?] --yes--> APPROVE (with warning)
    |
    no
    v
[run tests] --fail--> INCREMENT retry, BLOCK (with output)
    |
    pass
    v
[verify plan] --fail--> INCREMENT retry, BLOCK (with criteria)
    |
    pass
    v
[feature complete?] --no--> APPROVE
    |
    yes
    v
[spawn code review]
    |
    v
[update graph: implemented]
    |
    v
APPROVE
```

## Reference

See [docs/research/005-claude-code-stop-hooks.md](../docs/research/005-claude-code-stop-hooks.md) for detailed hook mechanics.
