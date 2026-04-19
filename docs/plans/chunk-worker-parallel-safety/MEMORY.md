# Chunk-Worker Parallel Safety — Implementation Progress

## Current State

**Phase:** 1 (single phase)
**Branch:** `feature/chunk-worker-parallel-safety`
**Status:** Both chunks complete. Ready for validation against PLAN.md DoD, then PR.

## Kanban

### Ready

(none)

### Blocked

(none)

### Done

- **1A** (M): Chunk-worker — per-chunk status file + scoped commit ✓
- **1B** (M): Orchestrator — pre-flight conflict check + post-wave reducer ✓

---

## Session Log

### Session: 1A
**Date:** 2026-04-18
**Status:** Complete

#### Completed
- Rewrote Step 5 from "Update MEMORY.md Kanban" to "Write Chunk Status File" — worker writes `{plan_path}/.chunks/{chunk_id}.json` with schema {chunk, status, files, unblocks, date, session_entry}; no MEMORY.md edits
- Rewrote Step 6 "Commit" — scoped `git add` from declared Files only; `.chunks/{id}.json` excluded (gitignored); pre-commit sanity check stops on out-of-scope staged files
- Updated constraints block — removed "MEMORY.MD IS MANDATORY"; added "DO NOT EDIT MEMORY.md" and "SCOPED COMMITS" constraints; updated context-budget instruction to write `status: "partial"` to status file instead of MEMORY.md session entry
- Updated Step 4 failure handling — on 2-attempt validation failure, write status file with `status: "failed"` (Step 5) and return without committing
- Updated output format — replaced "Kanban Updated" section with "Status File" section; failure branch now references the status file instead of "Kanban NOT updated"
- Updated Guidelines — DO/DON'T reflects new contract (status file on every outcome, never `git add -A`, never edit MEMORY.md)
- Updated frontmatter `description` and tagline on line 14 to reflect new status-file pattern

#### Files
- `agents/chunk-worker.md` — full rewrite of commit + status-write behavior; constraints, output format, and guidelines updated accordingly

#### Notes
- This chunk was implemented directly in the main session rather than via `chunk-worker` because 1A *is* chunk-worker; running the old worker on its own rewrite would exhibit the exact races being fixed (`git add -A` bleed + MEMORY.md last-write-wins). Reducer step also done manually since 1B hasn't landed yet.

### Session: 1B
**Date:** 2026-04-18
**Status:** Complete

#### Completed
- Stage 3 kanban loop restructured — inserted **pre-flight conflict check** (step 4) before spawn and **wave reducer** (step 6) after workers return. Loop renumbered accordingly (7 steps → 9 steps).
- Pre-flight check parses `**Files:**` from PLAN.md Chunk Details (not the summary-table count column), computes pairwise intersection, and offers serialize / drop / abort on overlap. Single-chunk waves skip.
- Wave reducer: reads every `.chunks/*.json` from the wave, rebuilds MEMORY.md sections (Ready / Blocked / Done / failed+partial annotations) from status files + PLAN.md's `Depends` column, appends session entries to the Session Log in wave-completion order, commits MEMORY.md only. No-op when `.chunks/` absent (old-protocol plans keep working).
- Updated "Parallel execution" note to reference pre-flight; added "Status file directory (`.chunks/`)" subsection documenting schema pointer, gitignored status, mid-wave-machine-switch caveat, and fallback behavior.
- Added `docs/plans/*/.chunks/` entry to root `.gitignore` with a comment naming purpose.

#### Files
- `commands/implement.md` — Stage 3 rewrite + new `.chunks/` subsection
- `.gitignore` — added status-file-directory entry

#### Notes
- Implemented directly in the main session (same reason as 1A): the new orchestrator contract and the new worker contract must land together for downstream plans to use either cleanly. This plan's own execution was the mixed-protocol transition.
- First downstream plan can dogfood the complete contract (new worker + new orchestrator). This plan itself did not — 1A and 1B ran sequentially in the main session, not in parallel via the new pipeline.

---

## Notes

This plan is designed to dogfood the pre-flight conflict check it introduces:

- Chunk 1A modifies `agents/chunk-worker.md`
- Chunk 1B modifies `commands/implement.md` and `.gitignore`

The Files scopes are disjoint, so the pre-flight check (once 1B lands) would allow them to run in parallel. For the first run, the orchestrator is the *old* one (no pre-flight check yet) — so the test here is that two parallel workers, under the *new* chunk-worker contract from 1A, produce clean scoped commits and per-chunk status files.

After the PR merges, any subsequent plan gets the full contract: new chunk-worker + new orchestrator.
