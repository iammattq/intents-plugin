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

**Gitignore check (one-time per project).** Chunk-worker status files (`docs/plans/*/.chunks/`) are transient scratch and MUST be gitignored — they're the per-worker race-safety mechanism, not audit data (audit lives in the reduced MEMORY.md Session Log, which IS committed).

```bash
# Read the project's root .gitignore, then:
grep -qE '(^|/)docs/plans/\*/\.chunks/' .gitignore 2>/dev/null
```

- **Rule already present** (matches literally, or a more permissive parent like `**/.chunks/` or `docs/plans/*/`) → proceed.
- **Rule absent, `.gitignore` exists** → append:
  ```
  
  # Per-chunk status files — transient scratch reduced into MEMORY.md by the orchestrator (intents-plugin)
  docs/plans/*/.chunks/
  ```
  Stage and commit as a one-off setup commit:
  ```bash
  git add .gitignore
  git commit -m "chore: ignore chunk-worker status files (intents-plugin)"
  ```
- **`.gitignore` doesn't exist** → create it with the rule + comment, same commit.

This is a one-time check; once committed, future plans in this project inherit the rule.

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
     - Parallel: consider multiple independent Ready chunks, then
       run the pre-flight check in step 4 before spawning

  4. Pre-flight conflict check (required before parallel spawn)
     For each candidate chunk, read **Files:** from PLAN.md Chunk
     Details (authoritative — NOT the summary table's count column).
     Compute pairwise intersection across the selected set.

     If any pair shares a file → STOP. Show the overlap to the user
     and offer:
       (a) Run sequentially in declared order
       (b) Drop one chunk from this wave (name which)
       (c) Abort — user revises PLAN.md to narrow Files scope

     If disjoint → proceed to spawn.

     (Single-chunk waves skip this check.)

  5. Spawn chunk-worker(s):

     Task: chunk-worker

     chunk: <chunk_id>
     plan_path: docs/plans/<feature>/

     Worker handles: implement → validate → write
     {plan_path}/.chunks/{chunk_id}.json → commit declared Files scope

  6. Wave reducer (after all workers in the wave return)
     Read every docs/plans/<feature>/.chunks/*.json produced by the
     wave. Rebuild MEMORY.md sections from status files + PLAN.md
     chunk table:

       - Ready:   chunks in PLAN.md with no status file, minus Blocked
       - Blocked: chunks whose Depends cite at least one chunk not
                  yet status="done"
       - Done:    chunks with status="done"
       - status="failed" or "partial" → appear under Ready with an
                  inline annotation (e.g., "- 1A ⚠ partial — see log")

     Append each status file's session_entry to the Session Log
     section in wave-completion order.

     Commit MEMORY.md ONLY (.chunks/*.json is gitignored):

       git add docs/plans/<feature>/MEMORY.md
       git commit -m "chore(<feature>): reconcile kanban after wave"

     No-op if docs/plans/<feature>/.chunks/ doesn't exist (e.g., an
     in-flight plan predating this protocol).

  7. Show results to user (including any failed/partial annotations)
  8. Check for phase boundary (all chunks in phase N done?)
     - If phase complete: STOP for manual testing
     - User says "continue" → proceed to next phase
  9. Loop
```

**Parallel execution:** Multiple chunk-workers may be spawned in a single message ONLY after step 4 (pre-flight conflict check) passes. Even chunks with no declared `Depends` can conflict on Files scope — pre-flight catches that before workers race on the same file.

**✓ CHECKPOINT:** After each wave (single chunk or batch), show results and ask user to continue.

#### Status file directory (`.chunks/`)

Workers write their outcome to `docs/plans/<feature>/.chunks/<chunk_id>.json`. See `agents/chunk-worker.md` for the authoritative schema (`chunk`, `status`, `files`, `unblocks`, `date`, `session_entry`). The wave reducer (step 6 above) reads these files to rebuild MEMORY.md and commits the result as a single orchestrator commit.

- **Gitignored.** `.chunks/` is scratch — it's excluded via the root `.gitignore` (`docs/plans/*/.chunks/`). Stage 2 auto-adds the rule on first run in a project if absent. The audit trail lives in the reduced MEMORY.md Session Log (committed) and the per-chunk git commits. Status files can be deleted after reduction without losing information.
- **Why gitignored, not committed:** keeps commit history clean; transient per-worker scratch exists only to avoid the MEMORY.md last-write-wins race between parallel workers. Narrow cost: switching machines mid-wave (after worker commit, before reducer runs) leaves unreduced status files behind locally. Not a real scenario for single-machine workflows.
- **Fallback behavior.** If `docs/plans/<feature>/.chunks/` doesn't exist (e.g., an in-flight plan from before this protocol landed), the reducer is a no-op and those plans finish on the old protocol (workers edit MEMORY.md directly). No silent protocol mixing.

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
