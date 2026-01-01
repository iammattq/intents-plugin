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

<constraints>
You are an ORCHESTRATOR, not an implementer.
You MUST use the Task tool to spawn each agent below - do NOT perform implementation, testing, or review work yourself.
Each Stage 4, 5, 6 requires spawning the designated agent(s).
</constraints>

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

**MUST spawn** the `test-spec` agent using the Task tool:

```
Task: test-spec

Feature: <feature-id>
Plan: docs/plans/<feature>/PLAN.md
```

**✓ CHECKPOINT:** Show results, ask user to continue.
**Error →** Resume agent to fix, then checkpoint again.

### Stage 5: Feature Implementer

**MUST spawn** the `feature-implementer` agent (same Task tool pattern as Stage 4):

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

**✓ CHECKPOINT:** Show results, ask user to continue.
**Error →** Resume agent to fix, then checkpoint again.

### Stage 6: Review Loop (unless --skip-review)

**MUST spawn** review agents using the Task tool (same pattern as Stage 4):

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

## Hooks (Optional)

Quality gates can run automatically via hooks. See [docs/hook-setup.md](../docs/hook-setup.md) for configuration.

## Completion

```
✅ Feature implemented: <feature-id>

Graph: status → implemented
Files: [list of created/modified]

Next:
  - Test manually
  - Merge to main
```
