# Harness Cleanup — Implementation Progress

## Current State

**Phase:** 1 (in progress)
**Branch:** `feature/harness-cleanup`
**Status:** 1A complete; remaining Phase 1 chunks ready

## Kanban

### Ready

All Phase 1 chunks are independent — can be picked in any order or run in parallel. Phase 2 is a separate PR; pick only after Phase 1 merges to keep evaluation clean.

**Phase 1 — Plugin cleanup:**

- **1C** (S): Delete non-functional metrics hooks + README/implement.md sections
- **1D** (XS): Delete orphaned `doc-reviewer` agent + README row
- **1E** (M): Merge `performance-reviewer` into `code-reviewer` as Performance sub-rubric; delete performance-reviewer agent

**Phase 2 — Design system skill pilot:**

- **2A** (M): Create `design-system` skill with DESIGN.md loader + starter template

### Blocked

(none — no inter-chunk dependencies)

### Done

- **1A** (S): Fix chunk-worker correctness ✓
- **1B** (XS): Fix stale README plan-critic description ✓
- **1F** (XS): Fix stale ccpp.md model version ✓

---

## Session Log

### Session: 1F — ccpp.md model version
**Date:** 2026-04-18
**Status:** Complete

#### Completed
- Updated `commands/ccpp.md:52` commit template: Claude Opus 4.5 → 4.7

#### Files
- `commands/ccpp.md`

### Session: 1B — README plan-critic line
**Date:** 2026-04-18
**Status:** Complete

#### Completed
- Updated `README.md:129` to describe multi-lens critique instead of advocate/critic debate

#### Files
- `README.md`

### Session: 1A — chunk-worker correctness
**Date:** 2026-04-18
**Status:** Complete

#### Completed
- Removed `Task` from `agents/chunk-worker.md` tools frontmatter
- Rewrote Step 3 to describe direct Read/Write/Edit implementation (no delegation)
- Updated constraints block to note subagents cannot spawn subagents
- Updated Step 4 validation checkpoint ("Implementation complete" instead of "agent returned")
- Updated failure-fix loop to apply targeted fix via Read/Write/Edit (not spawn fix agent)

#### Files
- `agents/chunk-worker.md` — aligned doc with actual behavior

#### Decisions
- Also fixed Step 4's orphan references to "Implementation agent returned" and "Spawn fix agent" while in this file — same class of issue (aligning doc with reality). Extended the chunk slightly beyond literal plan scope because the references were obviously related.

### Session: Plan created
**Date:** 2026-04-18
**Status:** Complete

#### Completed
- Researched community patterns (spec-kit, Superpowers, compound-engineering, flow-next, HumanLayer ACE-FCA)
- Researched Claude Code subagent mechanics: confirmed subagents cannot spawn subagents (SDK docs, GitHub #19077)
- Researched commands vs skills (April 2026): confirmed unified but both surfaces supported
- YAGNI-audited an earlier expanded plan; cut from 2-3 days of work to 4-6 hours
- Drafted PLAN.md with 6 Phase 1 chunks + 1 Phase 2 chunk
- Explicit Non-Goals section capturing what was deferred and why

#### Files
- `docs/plans/harness-cleanup/PLAN.md` — full plan with test specs
- `docs/plans/harness-cleanup/MEMORY.md` — this file

#### Decisions
- **Keep chunk-worker on Opus:** user's pushback was correct — worker actually writes code (Task delegation was broken), Opus warranted
- **Merge perf-reviewer instead of model-tier adjusting:** merge resolves the perf-on-Haiku quality concern implicitly (now runs at code-reviewer's Opus level)
- **One skill pilot, not four:** design-system first (stated pain); defer nextjs-vercel/supabase/tailwind-v4 until pilot signal
- **No commands/ reorg:** current split (commands/ for tasks, skills/ for reference) matches Anthropic's task-vs-reference framing
- **Lean design-system skill:** thin loader for DESIGN.md + minimal fallback, not a 300-line conventions doc; reduces 40/47-skills-hurt-output risk
- **Phase 1 and Phase 2 as separate PRs:** isolates skill pilot evaluation signal

#### Next Steps
- User approves plan
- Pick up Phase 1 chunks (any order, parallel-safe)
- After Phase 1 merges, run `/intents:implement` on a real feature to validate chunk-worker fix end-to-end
- Then Phase 2 (design-system skill pilot)

---

## Kanban Rules

- Workers pick chunks from Ready, implement per PLAN.md chunk detail, move to Done
- No inter-chunk dependencies in this plan — any Ready chunk is safe to start
- Phase 2 chunks can be started after Phase 1 merges (to isolate evaluation signal) — not a hard block, just a sequencing preference
- Orchestrator spawns workers until Ready is empty per phase
