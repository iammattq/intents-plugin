# 1M Context Window & the "Dumb Zone"

> Sources: Chroma (context-rot), Anthropic Opus 4.7 release notes, Claude Code GitHub issues, developer field reports. Researched 2026-04-18.

## Decision Outcome (2026-04-18)

Re-calibrated chunk sizing in `agents/feature-plan.md` and `agents/chunk-worker.md` based on field data about how 1M-window models actually degrade. **Headline:** 200K is still the practical effective-context ceiling — *not* 40% of 1M.

**Changes:**

- T-shirt sizes bumped (S 1–3, M 4–8, L 9–15, XL 15+ files) — Opus 4.7 can handle more cohesive scope per worker session.
- `~40% context max` guidance replaced with concrete `<200K effective tokens` target + warning that 40% of 1M lands in the dumb zone.
- `chunk-worker.md` got an explicit `CONTEXT BUDGET` constraint: bail at ~40% usage with partial-status MEMORY.md entry rather than pushing through degradation.
- Planning now prefers larger cohesive L chunks over splitting into multiple Ms — fixed overhead per worker session (PLAN.md + MEMORY.md + file reads ≈ 10–20K tokens) amortizes better.
- Noted that Opus 4.7's new tokenizer counts **1x–1.35x** more tokens than 4.6 for the same text — existing pre-4.7 estimates may undercount by ~35%.

The rest of this doc is the underlying research.

---

## The "Dumb Zone" — Empirical Thresholds

Claude Opus 4.6 self-reported degradation timeline (confirmed by field reports):

| Context Usage | Symptoms |
|---|---|
| 0–20% | Clean performance |
| 20–40% | Initial degradation: circular reasoning, forgotten earlier decisions |
| 40–50% | Compaction pressure; model itself recommends restarting the session |
| 50–80% | Thrashing between approaches, false claims of completion |
| 80%+ | "Gets rough" (model's own words) |

In one documented Claude Code session on Opus 4.6 with 1M context enabled, the model proactively recommended a session restart at **48% usage** — i.e. ~480K tokens into a 1M window. This is the practical "effective context" ceiling, not the advertised one.

Chroma's context-rot research (tested 18 frontier models) found **every model degrades as input grows**, non-uniformly. A 200K-window model can show significant degradation at 50K (25%). The problem is architectural, not model-specific.

## Why Bigger Windows Don't Just Work

1. **Attention budget is finite.** Anthropic's own context-engineering framing: each new token depletes the model's attention budget. Quality correlates with signal density, not raw capacity.
2. **Lost-in-the-middle is real.** Content at the beginning and end of the window is recalled reliably; details buried in the middle drop by 30%+ in retrieval accuracy.
3. **Coherent structured text is actually harder than shuffled text** in some tasks — the model over-indexes on surrounding narrative.
4. **Claude models tend to abstain rather than hallucinate** when uncertain — visible as "I don't have enough context" rather than confident wrong answers. Good for reliability, bad if you assumed success.

## What Opus 4.7 Changed

From the Anthropic release notes:

- **"Stronger performance over its full 1M token context window"** — SOTA on MRCR and GraphWalks long-context retrieval benchmarks.
- **Better at file-system memory** — agents maintaining scratchpads / MEMORY.md-style files specifically called out as improved.
- **New tokenizer uses 1x–1.35x more tokens** vs Opus 4.6 (up to ~35% more, varies by content). Token budgets calibrated on 4.6 will undercount.
- **Fewer tool calls by default**, more reasoning. More direct and literal instruction-following.
- **Fewer subagents spawned by default** — steerable via prompting.
- `task_budget` advisory parameter (beta) gives the model a running countdown of its loop budget. Minimum 20K tokens.
- Sampling parameters (`temperature`, `top_p`, `top_k`) removed from the API.
- Extended thinking budgets removed; adaptive thinking is the only thinking-on mode.

4.7 pushes the degradation curve *later*, but doesn't flatten it. Context rot is not solved.

## Token Efficiency: Fewer Big Chunks Beat Many Small Ones

Each chunk-worker invocation has fixed overhead:

- Read PLAN.md (~5–10K)
- Read MEMORY.md (~2–5K)
- Read in-scope files (varies)
- Initial prompt / scaffolding (~2–5K)

**Total fixed cost ≈ 10–20K tokens per worker session.** Running 10 files as five M-chunks pays that cost 5×. Running the same 10 files as one L-chunk pays it once. Developer reports (including the one in Karan Goyal's 4.6 guide) confirm: raising per-session context from 200K to 500K+ *reduced* total token spend because the model re-requested info less often.

**But** — this only holds below the dumb zone. Past ~200K effective tokens, quality drops outweigh the savings.

## Why Subagent Isolation Still Matters

The single most important architectural takeaway: **isolated context windows beat one big shared window**. The `chunk-worker` pattern (fresh session per chunk, MEMORY.md as durable state) is exactly what context-rot research recommends:

> "Rather than identifying a safe percentage, the research recommends preventive architecture — using subagents with isolated context windows to prevent noise accumulation entirely, rather than trying to optimize within a single large window." — Morph, Context Rot Guide

Don't abandon chunk isolation in favor of loading the full feature into one 1M session. The 1M window is a capacity increase per chunk, not a replacement for chunking.

## Practical Guidance (distilled)

- **Target <200K effective tokens per chunk-worker session.** Even on 1M models.
- **Prefer larger cohesive L chunks over multiple Ms** when the work forms one reasoning thread. Fewer startup loads = lower total spend.
- **Bail at ~40% context usage.** Write a partial-status entry to MEMORY.md and return. Don't push through the dumb zone.
- **Lean on MEMORY.md.** 4.7 is specifically better at file-system memory — richer session logs reduce re-derivation cost in later chunks.
- **Re-estimate pre-4.7 token budgets at +35%** to account for the new tokenizer.
- **Keep chunk-worker as an isolated subagent.** Fresh context per chunk is the recommended pattern, not an artifact of old limits.

## Open Questions

- Does Opus 4.7's MRCR gain meaningfully shift the dumb-zone threshold upward (e.g. toward 60%), or just raise the ceiling slightly? No independent 4.7-specific field reports yet as of 2026-04-18 — the 40–50% number comes from 4.6 self-reports and 4.6 field data.
- Is the `task_budget` advisory parameter useful for chunk-worker invocations? Unclear whether it helps the model self-moderate within a chunk or just adds scaffolding.
- At what cohesive scope does parallelism loss outweigh the token savings of bigger chunks? (Multiple workers in parallel across independent chunks is still cheaper wall-clock than one big worker, even if more expensive in total tokens.)

## Sources

- [Context Rot: How Increasing Input Tokens Impacts LLM Performance — Chroma](https://www.trychroma.com/research/context-rot)
- [What's new in Claude Opus 4.7 — Anthropic docs](https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-7)
- [Opus 4.6 1M context: self-reported degradation at 40% — GitHub Issue #34685](https://github.com/anthropics/claude-code/issues/34685)
- [Claude's 1 Million Context Window: What Changed (2026) — Karo Zieminski](https://karozieminski.substack.com/p/claude-1-million-context-window-guide-2026)
- [Claude Opus 4.6 1M Context Developer Guide — Karan Goyal](https://karangoyal.cc/blog/claude-opus-4-6-1m-context-window-guide)
- [Context Rot: Why LLMs Degrade as Context Grows — Morph](https://www.morphllm.com/context-rot)
