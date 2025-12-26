---
description: Implement a planned feature with quality checks. Use when ready to build.
argument-hint: <feature-id> [--skip-tests] [--skip-review]
---

# /intents:implement

Implement a planned feature with full workflow orchestration.

## Usage

```
/intents:implement <feature-id>
/intents:implement <path-to-plan>
```

## Prerequisites

- Feature must exist in `.intents/graph.yaml`
- `docs/plans/<feature>/PLAN.md` must exist
- Status should be `planned` or `broken`

If not ready, tell user to run `/intents:plan <feature>` first.

## Workflow

### Step 1: Validate

```
Read .intents/graph.yaml
Find feature by ID
Verify PLAN.md exists
```

If feature not found or no plan, stop and inform user.

### Step 2: Update Status → in-progress

```yaml
feature-id:
  status: in-progress
```

### Step 3: Test Spec (if needed)

Spawn `test-spec` agent if no tests exist for this feature.

### Step 4: Feature Implementer

Spawn `feature-implementer` agent:

```
Implement: <feature-id>
Plan: docs/plans/<feature>/PLAN.md
Memory: docs/plans/<feature>/MEMORY.md
```

Agent will:
- Implement chunks sequentially
- Validate each chunk
- Update MEMORY.md with progress
- Pause at phase gates for testing

### Step 5: Quality Checks

Spawn review agents as appropriate:

| Agent | When |
|-------|------|
| `code-reviewer` | Always |
| `security-auditor` | Auth, API, or data handling |
| `accessibility-reviewer` | UI components |

### Step 6: Update Status

**Success:** `status: implemented`
**Failure:** `status: broken`

## Options

| Option | Effect |
|--------|--------|
| `--skip-tests` | Skip test-spec step |
| `--skip-review` | Skip quality check agents |

## Resume

If interrupted, re-run the command. The `feature-implementer` reads MEMORY.md and resumes from last completed chunk.

## Completion

```
Feature implemented: <feature-id>

Graph: status → implemented
Files: [list of created/modified]

Next:
  - Test manually
  - Merge to main
```
