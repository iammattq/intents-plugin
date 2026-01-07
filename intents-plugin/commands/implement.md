---
description: Implement a planned feature with quality checks. Use when ready to build.
argument-hint: <feature> [--skip-review] [--use-purple]
---

# /intents:implement

Orchestrate implementation of a planned feature using kanban-based chunk workers.

## Usage

```
/intents:implement <feature>
/intents:implement <feature> --use-purple
/intents:implement <feature> --skip-review
```

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

#### Purple Team Workflow (--use-purple)

Same kanban loop, but use purple team iteration instead of chunk-worker:

**For each Ready chunk:**

```
1. Spawn purple-team-a:
   feature: docs/plans/<feature>/
   chunk: <chunk_id>
   tasks: <from PLAN.md>
   files: <from PLAN.md>
   ship_criteria: <from PLAN.md>

2. Spawn purple-team-b:
   feature: docs/plans/<feature>/
   chunk: <chunk_id>
   tasks: <from PLAN.md>
   ship_criteria: <from PLAN.md>

3. If GAPS_REMAIN and iteration < 3:
   Resume purple-team-a with gaps
   Resume purple-team-b to re-assess

4. On PASS: Update MEMORY.md kanban (Ready→Done, unblock dependents)

5. Commit the chunk
```

| Behavior | chunk-worker | purple team (--use-purple) |
|----------|--------------|----------------------------|
| Implementation | Worker does full cycle | Team A implements |
| Validation | Worker validates | Team B validates with steel-man |
| Fixing gaps | Worker retries | Team B fixes, or Team A gets another pass |
| Iteration | 1 pass + retry | Up to 3 A↔B iterations |
| Kanban update | Worker updates | You update after PASS |

**✓ CHECKPOINT:** After each chunk, show results and ask user to continue.

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
| `--use-purple` | Use purple team workflow (Team A implements, Team B validates/fixes, up to 3 iterations) |

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
