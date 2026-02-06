# Agent Teams Feature: Brainstorm

## Problem Statement

The intents-plugin's debate, review, and research workflows are constrained by a fundamental limitation: **subagents cannot spawn subagents**. This forces all multi-agent coordination into either:

1. **Internal monologue** — a single agent plays both sides of a debate (feature-refine doing Builder + Stress-Tester), which undermines debate quality because LLMs are inherently agreeable with themselves
2. **Command-level orchestration** — the command file (plan.md, implement.md) manually sequences agent calls, which is clunky and can't model peer-to-peer collaboration

The research in `docs/research/009-productive-debate-frameworks.md` and `docs/research/006-code-review-agents.md` identified clear patterns (Red-Blue/Purple teaming, Dialectical Synthesis, steel-manning) that structurally require **independent agent contexts communicating laterally** — exactly what agent teams would enable.

## What Doesn't Work Today (And Why)

### feature-refine Debate

`feature-refine.md` lists `Task` in its tools, but when spawned by `plan.md` it runs as a subagent — making that `Task` tool inert. The Builder/Stress-Tester debate runs as internal monologue within one sonnet context.

**Why this is a quality problem:**
- Research 009 Framework 4 (Red-Blue Team) requires "each team develops arguments **independently**"
- `brainstorm-best-practices.md` flags: "LLMs are often too agreeable, making explicit prompting for debate necessary"
- A single agent arguing with itself converges prematurely — it's structurally incapable of genuine adversarial pressure
- The steel-man phase, min/max rounds, and synthesis structure were implemented but the underlying single-context problem remained

### Review Phase (implement.md Stage 4)

Review agents (`code-reviewer`, `security-auditor`, `accessibility-reviewer`, `performance-reviewer`) run independently and report to the parent. No cross-referencing occurs.

**Why this is a quality problem:**
- Research 006 describes the Purple Team pattern: "purple teams emerged where red and blue collaborate in real-time rather than sequentially"
- `code-reviewer` might flag a pattern issue with security implications that `security-auditor` never sees
- Cross-cutting concerns (security ↔ performance, accessibility ↔ code quality) fall through the cracks
- The parent (implement.md) has to manually reconcile separate outputs with no structured cross-referencing

### Research Phase (plan.md Phase 2-3)

`codebase-researcher` and `technical-researcher` run sequentially. External research only triggers "if needed" based on the codebase researcher's output.

**Why this is suboptimal:**
- The researchers are independent — no dependency between them
- Waiting for codebase research to complete before deciding on external research adds latency
- If codebase-researcher discovers something that should inform external search queries, it can't communicate that directly

## Agent Teams: What Changes

Agent teams introduce peer-to-peer messaging via `TeammateTool`, `SendMessage`, and `spawnTeam`. The topology shifts from hub-and-spoke to lateral:

```
Hub-and-spoke (current):        Team (agent teams):

   plan.md                         plan.md
      │                               │
      ├── codebase-researcher         spawnTeam([
      ├── feature-refine              │  advocate,
      │      ✗ can't spawn            │  critic,
      │      └── debate-advocate      │  coordinator
      └── feature-plan                ])
                                      │
                                      ├─ advocate ←──SendMessage──→ critic
                                      ├─ critic ←──SendMessage──→ coordinator
                                      └─ coordinator ←──SendMessage──→ advocate
```

**Key difference:** Team members are peers, not parent-child. No recursion risk — they message each other laterally. The coordinator doesn't "spawn" the advocate; it sends it a message.

## Opportunities Identified

### 1. Debate Team (Highest Impact)

**Replace** the single-agent feature-refine internal monologue with a team of three:

| Agent | Role | Model |
|-------|------|-------|
| `debate-advocate` | Steel-man and defend the approach | sonnet |
| `debate-critic` | Pressure-test from multiple lenses (code review, security, YAGNI, pragmatist) | sonnet |
| `feature-refine` (refactored) | Coordinate rounds, check convergence, run "hats off" synthesis | sonnet |

**Protocol** (maps to research 009 frameworks):

1. **Steel-Man Phase** (Framework 2): Coordinator sends problem + research artifact to advocate. Advocate builds the strongest possible case. Critic cannot engage yet.

2. **Structured Debate** (Framework 3 — Dialectical Synthesis):
   - Round N: Advocate sends case → Critic receives and responds with concerns + potential resolutions → Coordinator checks convergence
   - Each agent only sees the other's prior round output (forces fresh reasoning, prevents echo chamber)
   - Minimum 2 rounds, maximum 5 (from research 009 design principles)
   - Critical rule: each round must advance toward resolution, not just accumulate objections

3. **"Hats Off" Synthesis** (Framework 4 — Red-Blue Team): Coordinator dissolves roles and synthesizes, producing a recommendation that may differ from both the original idea and the critiques.

**Why this is better than internal monologue:**
- Separate contexts = genuinely independent reasoning
- Advocate can't see critic's arguments forming (and vice versa) — prevents premature convergence
- Coordinator has a bird's-eye view of both perspectives for synthesis
- Addresses the LLM agreeableness problem structurally, not just with prompting

### 2. Purple Team Reviews (High Impact)

**Replace** independent reviewers reporting to parent with a review team:

| Agent | Role |
|-------|------|
| `review-coordinator` (new) | Spawns/messages reviewers, cross-references findings, produces unified report |
| `code-reviewer` | General quality, patterns, anti-patterns |
| `security-auditor` | OWASP Top 10, auth, injection |
| `accessibility-reviewer` | WCAG 2.2 AA compliance |
| `performance-reviewer` | Re-renders, bundle size, SSR |

**Protocol** (maps to research 006 purple team + 009 Framework 4):

1. All reviewers receive the diff and review in parallel
2. Each reviewer sends findings to `review-coordinator`
3. **Cross-reference pass**: Coordinator messages specific reviewers about overlapping concerns:
   - "Security found unvalidated input at auth.ts:42 — code-reviewer, is this sanitized upstream?"
   - "Performance flagged heavy computation at dashboard.tsx:15 — accessibility-reviewer, are there loading states?"
4. Reviewers respond to cross-reference queries
5. Coordinator deduplicates, prioritizes, and produces unified report with severity levels

**Why this is better than independent reviews:**
- Catches cross-cutting concerns no single reviewer would find alone
- Eliminates duplicate findings across reviewers
- Single prioritized output instead of N separate reports the user must reconcile
- Maps directly to the purple team model: "accelerating learning by eliminating the report-and-remediate cycle"

### 3. Parallel Research with Messaging (Medium Impact)

**No new agents needed** — restructure plan.md to run researchers in parallel with optional messaging:

| Agent | Change |
|-------|--------|
| `codebase-researcher` | Can message technical-researcher with "investigate X externally" |
| `technical-researcher` | Can message codebase-researcher with "I found X, check for internal usage" |

**Protocol:**
1. Both researchers start simultaneously with the problem statement
2. If codebase-researcher discovers unfamiliar tech/APIs, it messages technical-researcher directly instead of waiting for the parent to decide
3. If technical-researcher finds patterns, it messages codebase-researcher to check for existing internal implementations
4. Both produce their artifacts, which the parent merges

**Why this is better than sequential:**
- Eliminates the "if needed" bottleneck on external research
- Dynamic discovery: researchers inform each other in real-time
- Faster overall — parallel by default, with coordination when needed

## What We Can Do Now (Without Agent Teams)

While agent teams aren't available yet, the command-level orchestration workaround is viable for the debate:

### Debate at Command Level

`plan.md` Phase 4 changes from:
```
Spawn feature-refine (internal monologue debate)
```

To:
```
Round 1:
  Spawn debate-advocate → steel-man output
  Spawn debate-critic → receives advocate output, returns critique
Round 2:
  Spawn debate-advocate → receives critique, returns response
  Spawn debate-critic → receives response, returns refined critique
...convergence check at command level...
Synthesis:
  Spawn feature-refine → receives full debate transcript, "hats off" synthesis only
```

**Trade-offs of this approach:**
- Works within current subagent constraints
- Debate quality is better than internal monologue (separate contexts)
- But command file becomes complex orchestration logic
- No lateral messaging — parent must relay everything
- More token usage from repeated context passing

### Review Cross-Referencing at Command Level

`implement.md` Stage 4 changes from:
```
Spawn reviewers → collect separate reports → show to user
```

To:
```
Spawn all reviewers in parallel → collect reports
Spawn review-synthesizer → receives all reports, cross-references, deduplicates
Show unified report to user
```

### Parallel Research (Works Today)

`plan.md` Phase 2-3 changes from:
```
Phase 2: Spawn codebase-researcher
Phase 3: If needed, spawn technical-researcher
```

To:
```
Phase 2: Spawn both researchers in parallel (when external research is warranted)
Phase 2.5: Merge findings into unified research artifact
```

## File Changes Summary

### New Agents Needed

| File | Purpose | Needed For |
|------|---------|------------|
| `agents/debate-advocate.md` | Steel-man and defend approaches | Debate team |
| `agents/debate-critic.md` | Pressure-test from multiple lenses | Debate team |
| `agents/review-coordinator.md` | Cross-reference and unify review findings | Purple team reviews |

### Modified Files

| File | Change | Needed For |
|------|--------|------------|
| `agents/feature-refine.md` | Refactor from internal debate to synthesis-only (or debate coordinator when teams available) | Debate team |
| `commands/plan.md` | Phase 4: round-robin debate orchestration; Phase 2-3: parallel research | Debate + research |
| `commands/implement.md` | Stage 4: add cross-reference synthesis step after reviewers | Purple team reviews |

### No Changes Needed

| File | Why |
|------|-----|
| `agents/codebase-researcher.md` | Works as-is; parallel spawning is a command-level change |
| `agents/technical-researcher.md` | Works as-is; parallel spawning is a command-level change |
| `agents/code-reviewer.md` | Works as-is; cross-referencing handled by coordinator |
| `agents/security-auditor.md` | Works as-is |
| `agents/accessibility-reviewer.md` | Works as-is |
| `agents/performance-reviewer.md` | Works as-is |

## Open Questions

1. **Token budget**: Round-robin debate spawns 4-10 agents for 2-5 rounds. What's the cost impact vs. single-agent monologue?
2. **Context passing efficiency**: Each debate round must pass the prior round's output. How much context is lost in translation vs. a single agent with full history?
3. **Convergence detection**: With separate agents, how does the command-level orchestrator reliably detect convergence? Need clear structured output from each round.
4. **Agent teams timeline**: When will TeammateTool/SendMessage/spawnTeam be available? Should we build the command-level workaround now, or wait?
5. **Debate quality validation**: How do we measure whether split-agent debate actually produces better recommendations than internal monologue? Need before/after comparison on a real feature.

## Recommendation

**Start with the command-level workaround for the debate split.** This is the highest-impact change (single-agent debate is the biggest quality gap) and it's implementable today. Design the debate-advocate and debate-critic agents with the assumption they'll eventually be team members — the agent definitions don't change, only the orchestration layer does.

Parallel research is the easiest win — just update plan.md to spawn both researchers simultaneously. Do this first.

Purple team reviews can wait for agent teams — the current independent review model works adequately, and the cross-referencing benefit is smaller than fixing the debate.

## References

- `docs/research/009-productive-debate-frameworks.md` — Steel-manning, Dialectical Synthesis, Red-Blue/Purple Team, Disagree and Commit
- `docs/research/006-code-review-agents.md` — Generator-Critic pattern, purple team reviews, specialized vs. general agents
- `docs/research/brainstorm-best-practices.md` — LLM agreeableness problem, divergent/convergent thinking separation
- `docs/research/007-agent-spawning-patterns.md` — Task tool patterns, parallel execution
