---
description: Implement a planned feature with quality checks. Use when ready to build.
argument-hint: <feature> [--skip-review]
---

# /intents:implement

Orchestrate implementation of a planned feature using kanban-based chunk workers.

## Usage

```
/intents:implement <feature>
/intents:implement <feature> --skip-review
```

## Metrics Tracking

When this command starts, the `UserPromptSubmit` hook automatically:
1. Marks the plan phase as ended (if not already)
2. Starts the implement phase timer

The Stop hook displays cumulative metrics after each response:
```
⏱️  feature-name
    Planning:     15m │ 52,103 in / 14,221 out
    Implementing:  8m │ 31,847 in /  9,432 out
    ────────────────────────────────────────────
    Total: 83,950 in / 23,653 out
```

Tracking persists in `docs/plans/<feature>/.tracking.json`.

## Workflow

<constraints>
You are the ORCHESTRATOR. You read the kanban, spawn workers, and manage phase gates.
You MUST use the Task tool to spawn agents - do NOT implement code yourself.
</constraints>

### Stage 1: Validate Prerequisites

```
Read: docs/plans/<feature>/PLAN.md
Read: docs/plans/<feature>/MEMORY.md
```

**Error → STOP.** Inform user. If no plan, suggest `/intents:plan <feature>`.

### Stage 2: Git Prep

```bash
git branch --show-current  # Must not be main/master
git status --short         # Warn if uncommitted changes
```

If on main: create feature branch `feature/<feature>` and switch to it.

**Error → STOP.** Inform user.

### Stage 3: Kanban Loop

**You orchestrate the kanban.** Read MEMORY.md to see Ready/Blocked/Done state.

#### Default Workflow (chunk-worker)

```
LOOP while Ready has chunks:
  1. Read MEMORY.md kanban
  2. Show Ready chunks to user
  3. Pick chunk(s) to implement:
     - Single: spawn one chunk-worker
     - Parallel: spawn multiple chunk-workers for independent Ready chunks

  4. Spawn chunk-worker(s):

     Task: chunk-worker

     chunk: <chunk_id>
     plan_path: docs/plans/<feature>/

     Worker handles: implement → validate → update kanban → commit

  5. Show results to user
  6. Check for phase boundary (all chunks in phase N done?)
     - If phase complete: STOP for manual testing
     - User says "continue" → proceed to next phase
  7. Loop
```

**Parallel execution:** If multiple chunks are Ready with no dependencies between them, you can spawn multiple chunk-workers in a single message.

**✓ CHECKPOINT:** After each chunk (or batch), show results and ask user to continue.

### Stage 4: Review Loop (unless --skip-review)

**MUST spawn** review agents using the Task tool (same pattern as Stage 3):

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

### Stage 5: Finalize

Report completion:

```
✅ Feature implemented: <feature>

Files: [list of created/modified]

Next:
  - Test manually
  - Merge to main
```

## Options

| Option | Effect |
|--------|--------|
| `--skip-review` | Skip Stage 4 |

## Resume

Re-run command to resume. Read MEMORY.md kanban - Ready chunks are what's next, Done shows progress.


## Completion

```
✅ Feature implemented: <feature>

Files: [list of created/modified]

Next:
  - Test manually
  - Merge to main
```
