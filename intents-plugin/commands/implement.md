---
description: Implement a planned feature with quality checks. Use when ready to build.
argument-hint: <feature-id> [--skip-tests] [--skip-review]
---

# /intents:implement

Orchestrate implementation of a planned feature.

## Usage

```
/intents:implement <feature-id>
/intents:implement <feature-id> --skip-tests
/intents:implement <feature-id> --skip-review
```

## Workflow

### Stage 1: Validate Prerequisites

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

```yaml
# .intents/graph.yaml
feature-id:
  status: in-progress
```

**Error → STOP.** Inform user.

### Stage 4: Test Spec (unless --skip-tests)

Spawn `test-spec` agent for this feature.

**✓ CHECKPOINT:** Show results, ask user to continue.
**Error →** Resume agent to fix, then checkpoint again.

### Stage 5: Feature Implementer

Spawn `feature-implementer` agent:

```
Feature: <feature-id>
Plan: docs/plans/<feature>/PLAN.md
Memory: docs/plans/<feature>/MEMORY.md
```

Agent handles internally:
- Chunk-by-chunk implementation
- Validation against plan
- MEMORY.md updates
- Phase gates

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

Update graph status:
- Success → `implemented`
- User abort → `broken` (log reason)

## Options

| Option | Effect |
|--------|--------|
| `--skip-tests` | Skip Stage 4 |
| `--skip-review` | Skip Stage 6 |

## Resume

Re-run command to resume. The `feature-implementer` reads MEMORY.md and continues from last completed chunk.

## Completion

```
✅ Feature implemented: <feature-id>

Graph: status → implemented
Files: [list of created/modified]

Next:
  - Test manually
  - Merge to main
```
