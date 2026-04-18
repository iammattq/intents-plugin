# Chunk-Worker Parallel Safety

## Problem Statement

Opus orchestrator already runs `chunk-worker` agents in parallel when Ready chunks have no declared dependencies (`commands/implement.md:74`), but `chunk-worker` was designed for sequential execution. Two concrete race conditions corrupt state silently — no errors, no retries, no wasted tokens on repair cycles, but git history and kanban drift from reality:

1. **`git add -A` bleed** — `chunk-worker.md:156` stages every modified file in the working tree, not just the chunk's declared `Files` scope. When worker A finishes while worker B is mid-edit, A's commit ("implement chunk 1A") contains partial work from 1B. Future `git revert 1A` also rips out 1B's code.

2. **MEMORY.md last-write-wins** — `chunk-worker.md:109-148` has each worker `Edit` MEMORY.md to move its chunk Ready→Done and append a session entry. Claude Code's Edit read-before-write enforcement is per-session, so subagent A's write doesn't invalidate subagent B's stale read. B's write overwrites A's — A's kanban entry and session log are lost silently.

3. **No orchestrator guard** — `commands/implement.md` Stage 3 spawns multiple workers when chunks are Ready with "no dependencies between them," but never checks the Files scope for overlap. Relies entirely on chunk authoring discipline.

## Goals

- Eliminate the `git add -A` bleed by scoping commits to declared Files
- Eliminate the MEMORY.md last-write race by moving workers off direct MEMORY.md edits
- Add a pre-flight file-conflict check to the orchestrator before parallel spawn
- Preserve the PLAN.md / MEMORY.md surface so humans reading a feature directory see the same shape
- Validate on one new feature end-to-end before declaring the approach right

## Non-Goals

- Worktree isolation per chunk (bigger change; these three fixes earn their keep first)
- Commit-hash verification against declared scope (follow-up if scoped `git add` proves insufficient)
- Migration of existing in-flight plans — they finish on the old protocol
- Automatic conflict resolution in the orchestrator — user decides serialize/drop/abort
- Replacing Markdown PLAN/MEMORY with a structured format

## Approach

Three surgical fixes across two files, split into two chunks with disjoint file scopes:

- **Chunk 1A** rewrites chunk-worker Step 5 (status write) and Step 6 (commit) so workers write a per-chunk status file (`.chunks/{chunk_id}.json`) instead of editing MEMORY.md, and stage only their declared Files. The status file is gitignored scratch — the orchestrator reduces it into MEMORY.md on wave completion.
- **Chunk 1B** adds a pre-flight conflict check and a post-wave reducer to the orchestrator (`commands/implement.md`). The reducer rebuilds MEMORY.md kanban + session log from the status files.

Chunks touch disjoint files (`agents/chunk-worker.md` vs. `commands/implement.md`) — deliberately structured so this plan is the first real test of the pre-flight check the plan itself introduces.

## Trade-offs

- **`.chunks/*.json` artifacts live in each plan directory as gitignored scratch** — accepting the uncommitted clutter for race-safety. Reducer consolidates content into MEMORY.md Session Log (committed) on wave completion, so audit trail survives without the files themselves entering git history. Narrow cost: if you switch machines mid-wave (after worker commit, before reducer), unreduced status files don't travel.
- **Reducer is orchestrator-instruction, not a script** — accepting potential inconsistency across sessions rather than introducing a Node/Python tooling dependency. Test will surface if inconsistency is a real problem.
- **Scoped `git add` fails loudly when a chunk edits a file outside its declared Files** — accepting the noisier failure as a feature; it surfaces undisciplined chunk scoping rather than silently committing stray work.
- **Protocol change affects only new plans on this branch** — in-flight plans from other branches keep working on the old protocol. After this merges, new plans use the new protocol; remaining old-protocol plans finish and die off.

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Orchestrator reducer executed inconsistently across sessions | Med | Med | Reducer steps are explicit and mechanical in `implement.md`; end-to-end test catches drift before the pattern is trusted |
| Scoped `git add` trips chunks whose declared Files omit something legitimately edited | Med | Low | Error message names the out-of-scope file and suggests "update Files or revise chunk"; chunk re-runs after PLAN.md correction |
| Pre-flight conflict check blocks parallel runs that previously "worked" | Low-Med | Low | Show user the overlap and offer serialize / drop / abort; this IS the intended tightening |
| Orchestrator fallback behavior for plans without `.chunks/` diverges from new-protocol behavior | Low | Med | Reducer no-ops when `.chunks/` is absent; no silent protocol mixing |
| Pre-flight parses PLAN.md markdown table fragile-ly | Med | Low | Parse the Chunk Details `**Files:**` list (authoritative), not the summary table's count column |

## Phases

Single phase, single PR.

| Chunk | Size | Depends | Scope | Files |
|-------|------|---------|-------|-------|
| 1A | M | - | Chunk-worker: per-chunk status file + scoped commit | 1 |
| 1B | M | - | Orchestrator: pre-flight conflict check + post-wave reducer + gitignore | 2 |

Disjoint file scopes — can run in parallel (the dogfood test).

---

## Chunk Details

### Chunk 1A — Chunk-worker: per-chunk status file + scoped commit

**Scope:** Rewrite Step 5 and Step 6 of `agents/chunk-worker.md` to eliminate the `git add -A` bleed and the MEMORY.md last-write race. Worker no longer touches MEMORY.md.

**Files:**
- `agents/chunk-worker.md`

**Tasks:**

- **Header constraints block** (`chunk-worker.md:16-31`):
  - Remove the "MEMORY.MD IS MANDATORY" constraint
  - Add: "Do not edit MEMORY.md — the orchestrator owns kanban reconciliation. Write chunk outcome to `{plan_path}/.chunks/{chunk_id}.json` only."

- **Step 5 rewrite** (lines 109-148) — rename from "Update MEMORY.md Kanban" to "Write Chunk Status File":
  - Worker writes `{plan_path}/.chunks/{chunk_id}.json` with schema:
    ```json
    {
      "chunk": "1A",
      "status": "done" | "failed" | "partial",
      "files": ["path/to/file.ts", ...],
      "unblocks": ["1C", "1D"],
      "date": "YYYY-MM-DD",
      "session_entry": "markdown string matching current Session: <chunk> format"
    }
    ```
  - `files` is the list of files the worker actually modified (may be a subset of declared Files)
  - `unblocks` comes from PLAN.md's `Depends` column — chunks that declared this chunk as a dependency
  - Checkpoint verifies the status file exists and is valid JSON before advancing to Step 6

- **Step 6 rewrite** (lines 152-164) — "Commit":
  - Derive staged file list from the chunk's declared `Files` scope (loaded in Step 1). `.chunks/{chunk_id}.json` is gitignored and NOT staged.
  - `git add` each declared path explicitly, quoted:
    ```bash
    git add "agents/chunk-worker.md"
    ```
  - Pre-commit sanity check: compare `git diff --cached --name-only` to the declared Files list. If extras staged → STOP, error names the out-of-scope file, no commit. Missing declared files are acceptable (chunk may legitimately not have needed every file).
  - Commit message format unchanged

- **Output format** (`chunk-worker.md:168-215`):
  - Replace "Kanban Updated" section with "Status File Written" naming the `.chunks/*.json` path
  - Keep the "Chunk Failed" branch, but route it to write `.chunks/{chunk_id}.json` with `status: "failed"` before returning — so the orchestrator reducer sees the failure

**Definition of Done:**
- `git add -A` absent from the file
- Step 5 writes `.chunks/{chunk_id}.json`; instructs worker to not edit MEMORY.md
- Step 6 verifies staged files match derived scope before commit
- Header constraints document parallel-safe contract
- Output format references `.chunks/*.json`, not MEMORY.md kanban updates

---

### Chunk 1B — Orchestrator: pre-flight conflict check + post-wave reducer

**Scope:** Add two sub-steps to `commands/implement.md` Stage 3 — one before parallel spawn (conflict check), one after wave completes (reducer that rebuilds MEMORY.md from status files). Add `.chunks/` to `.gitignore`.

**Files:**
- `commands/implement.md`
- `.gitignore`

**Tasks:**

- **Stage 3 — insert "Pre-flight conflict check" before parallel spawn** (between current steps 3 and 4 in `commands/implement.md:54-60`):
  - For each Ready chunk under consideration for parallel spawn, read the chunk's `**Files:**` list from PLAN.md Chunk Details (authoritative — not the summary table)
  - Compute pairwise intersection across the selected set
  - If any pair shares a file: STOP, show the overlap to the user, offer:
    - (a) run sequentially in declared order
    - (b) drop one chunk from this wave (name which)
    - (c) abort — user revises PLAN.md
  - If disjoint: proceed to spawn

- **Stage 3 — insert "Wave reducer" after parallel spawn returns** (after current step 4):
  - After all workers in the wave return, read `{plan_path}/.chunks/*.json`
  - Rebuild MEMORY.md sections:
    - **Kanban > Ready**: chunks from PLAN.md with no corresponding `.chunks/*.json`, minus blocked
    - **Kanban > Blocked**: chunks whose `Depends` cite at least one chunk not yet `status: "done"`
    - **Kanban > Done**: chunks with `status: "done"` in their status file
    - Chunks with `status: "failed"` or `"partial"` appear under Ready with an inline annotation (e.g., `- 1A ⚠ partial — see session log`)
  - Append each status file's `session_entry` to the Session Log section (in wave-completion order)
  - Write MEMORY.md once, then commit (MEMORY.md only — `.chunks/*.json` is gitignored):
    ```bash
    git add "docs/plans/{feature}/MEMORY.md"
    git commit -m "chore({feature}): reconcile kanban after wave"
    ```
  - This is the orchestrator's commit, distinct from chunk-worker commits

- **Update "Parallel execution" note** (`commands/implement.md:74`):
  - Reference the pre-flight check
  - Clarify: "Multiple chunk-workers may be spawned in one message only after pre-flight passes."

- **Add `.chunks/` to root `.gitignore`:**
  ```
  # Per-chunk status files — transient, reduced into MEMORY.md by the orchestrator
  docs/plans/*/.chunks/
  ```

- **Add new subsection "Status file directory (`.chunks/`)"** after Stage 3:
  - Document the schema (reference chunk-worker.md for authoritative spec)
  - Note: `.chunks/` is gitignored — transient build material; audit trail lives in MEMORY.md Session Log which the reducer writes from the status files
  - Note the reducer is a no-op on plans without `.chunks/` — preserves old-protocol behavior for in-flight plans

**Definition of Done:**
- Stage 3 has pre-flight conflict check documented with the three user options
- Stage 3 has wave reducer documented with explicit rules for each kanban section
- Parallel execution note references pre-flight
- `.chunks/` subsection documents schema pointer, gitignored status, and fallback behavior
- `.gitignore` includes `docs/plans/*/.chunks/`

---

## Open Questions

1. **Commit `.chunks/*.json` files, or gitignore?** Resolved: gitignored. Audit trail lives in MEMORY.md Session Log (which the reducer writes from the ephemeral status files). Accepts loss of cross-machine resume — not a real scenario for a solo workflow.

2. **What if a chunk's actual edits diverge from its declared Files?** Pre-commit check in Chunk 1A fails loudly with the out-of-scope file name. User either revises PLAN.md Files to match reality, or revises the chunk. Either path surfaces undisciplined scoping, which is the intended behavior.

3. **Backward compat with in-flight plans that have no `.chunks/`?** Reducer no-ops when `.chunks/` is absent. Existing plans finish on the old protocol (workers edit MEMORY.md directly — those plans don't run 1A's updated chunk-worker anyway since they predate the branch merge). Clean cutover after all old plans complete.

4. **Should failed chunks block the wave reducer from running?** No — the reducer should still rebuild MEMORY.md, marking failed chunks so the user sees them. Orchestrator then surfaces failures to the user before the next wave.
