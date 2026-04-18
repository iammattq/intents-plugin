# Chunk-Worker Parallel Safety — Implementation Progress

## Current State

**Phase:** 1 (single phase)
**Branch:** `feature/chunk-worker-parallel-safety`
**Status:** Plan drafted. Awaiting user approval before implementation.

## Kanban

### Ready

- **1A** (M): Chunk-worker — per-chunk status file + scoped commit
- **1B** (M): Orchestrator — pre-flight conflict check + post-wave reducer

### Blocked

(none — chunks have disjoint file scopes and no declared dependencies)

### Done

(none)

---

## Session Log

(none yet)

---

## Notes

This plan is designed to dogfood the pre-flight conflict check it introduces:

- Chunk 1A modifies `agents/chunk-worker.md`
- Chunk 1B modifies `commands/implement.md` and `.gitignore`

The Files scopes are disjoint, so the pre-flight check (once 1B lands) would allow them to run in parallel. For the first run, the orchestrator is the *old* one (no pre-flight check yet) — so the test here is that two parallel workers, under the *new* chunk-worker contract from 1A, produce clean scoped commits and per-chunk status files.

After the PR merges, any subsequent plan gets the full contract: new chunk-worker + new orchestrator.
