# Research 012: AI Agent Harnesses

**Date:** 2026-01-12

**Status:** Complete

**Related:** intents-plugin design philosophy, harness engineering

## Problem Statement

What is an AI agent harness? How does it differ from frameworks and runtimes? What are the canonical components and design patterns? This research consolidates industry definitions and positions the intents-plugin within the emerging harness ecosystem.

## Constraints

- Definitions are still evolving in the industry
- Multiple valid approaches exist on the autonomy spectrum
- Must distinguish between runtime control and structural scaffolding

---

## Part 1: Definition

### What is a Harness?

An agent harness is the infrastructure that wraps around an AI model to manage long-running tasks. The model generates responses. The harness handles everything else.

> Think of the model as an engine. The harness is the car. Best engine without steering and brakes goes nowhere useful.
> — [Parallel AI](https://parallel.ai/articles/what-is-an-agent-harness)

A harness is **not** the agent itself. It is the software system that governs how the agent operates, ensuring it remains reliable, efficient, and steerable.

### The Stack: Framework vs Runtime vs Harness

| Layer | What it does | Examples |
|-------|--------------|----------|
| **Framework** | Build agents (primitives, abstractions) | LangChain, CrewAI |
| **Runtime** | Execute agents (orchestration, state) | LangGraph |
| **Harness** | Workflows, guardrails, deployment, context management | DeepAgents, Claude Agent SDK, intents-plugin |

> An agent created in a framework can run inside any compatible runtime. A harness wraps both and adds workflows, guardrails, and deployment integrations.
> — [Analytics Vidhya](https://www.analyticsvidhya.com/blog/2025/12/agent-frameworks-vs-runtimes-vs-harnesses/)

### Why Harnesses Matter

> The model is commodity. The harness is moat.
> — [Phil Schmid](https://www.philschmid.de/agent-harness-2026)

Manus (an AI coding company) rewrote their harness five times in six months. Same models. Five architectures. Each rewrite improved reliability and task completion. The model didn't change. The harness did.

---

## Part 2: Canonical Components

The six canonical harness components (per industry consensus):

| Component | Purpose | intents-plugin Implementation |
|-----------|---------|-------------------------------|
| **Reasoning engine** | Core model inference | Claude (Opus/Sonnet) |
| **Planning & orchestration** | Task breakdown, sequencing | PLAN.md chunks, dependency graphs |
| **Tool registry** | Available capabilities | Claude Code tools + custom agents |
| **Memory & context** | State across sessions | MEMORY.md kanban, session logs |
| **State & persistence** | Progress tracking | Git commits, kanban board |
| **Structured I/O** | Consistent interfaces | Markdown files, agent outputs |

---

## Part 3: Anthropic's Harness Research

Source: [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

### Two-Part Pattern

1. **Initializer Agent**: Runs once to establish foundation
   - Creates startup scripts
   - Creates progress tracking file
   - Sets up initial state

2. **Coding Agent**: Operates in subsequent sessions
   - Works incrementally on single features
   - Commits progress to git
   - Updates progress files before ending

### Failure Modes Harnesses Prevent

| Failure Mode | Description | How Harness Prevents |
|--------------|-------------|---------------------|
| **Over-ambition** | Attempting entire project in one session | Chunking, incremental work |
| **Premature victory** | Declaring done too early | Progress tracking, feature lists |
| **Context loss** | Forgetting state between sessions | Structured documentation |
| **Merge conflicts** | Code not ready for integration | Git checkpoints after each session |

### intents-plugin Alignment

| Anthropic Pattern | intents-plugin Equivalent |
|-------------------|---------------------------|
| Initializer agent | `/intents:plan` → feature-plan agent |
| Coding agent | chunk-worker agents |
| Progress file | MEMORY.md kanban |
| Feature lists | PLAN.md chunks with dependencies |
| Git checkpoints | Workers commit after each chunk |

---

## Part 4: The Autonomy Spectrum

AI coding harnesses exist on a spectrum from fully autonomous to fully manual.

```
Fully Autonomous ←————————————————————→ Fully Manual
     │                                        │
     │  Ralph                                 │
     │  (runtime loop)                        │
     │                                        │
     │           intents-plugin               │
     │           (human drives,               │
     │            agents execute)             │
     │                                        │
     │                              Raw Claude│
     │                              (no harness)
```

### Autonomous Approaches (e.g., Ralph)

[Ralph](https://github.com/frankbria/ralph-claude-code) is an autonomous development framework that runs Claude Code in a loop until objectives are completed.

**How it works:**
- Reads project instructions from PROMPT.md
- Executes Claude Code with current priorities
- Tracks file modifications
- Evaluates completion signals
- Repeats until success or limits reached

**Safety mechanisms:**
- Rate limiting (100 API calls/hour, configurable)
- Circuit breaker (stops after 3+ loops with no file changes)
- Max retry limits
- 5-hour API limit detection

**Requires:** Pre-authorized actions via `--allowed-tools` or similar

### Orchestrated Approaches (e.g., intents-plugin)

Human drives the workflow, agents execute within bounded contexts.

**How it works:**
- Human runs `/intents:plan` to create plan
- Human runs `/intents:implement` to start work
- Chunk-workers pick from kanban, implement, commit
- Human reviews at phase gates
- Human spawns next chunks

**Safety through structure:**
- Phase gates catch drift early
- Chunks keep context small
- Kanban tracks actual completion
- Human judgment at decision points

### Tradeoff Analysis

| What autonomous loops guard against | What they don't guard against |
|-------------------------------------|-------------------------------|
| Runaway iterations (max retries) | Model confusion compounding |
| API cost spikes (rate limits) | Wrong abstractions accumulating |
| Session timeouts (5hr detection) | Drift from original intent |
| Stagnation (no-change detection) | Subtle bugs building up |

**Key insight:** The metric isn't "my agent ran for 3 days"—it's "my agent built what I intended."

### When Each Approach Fits

**Autonomous makes sense for:**
- Well-defined, mechanical tasks (migrations, formatting, repetitive refactors)
- Tasks where "good enough" is acceptable
- When you'll review everything at the end anyway

**Orchestrated makes sense for:**
- Features requiring judgment calls
- Unfamiliar codebases where drift is costly
- When you want to catch problems early, not at the end

---

## Part 5: Human-in-the-Loop Philosophy

Human-in-the-loop isn't about hitting enter. It's about where human time goes.

### The Real Value Proposition

| Phase | Time | Who | Value |
|-------|------|-----|-------|
| Planning/design | Hours | Human | High-value thinking |
| Implementation | Minutes | Agents | Mechanical coding |
| Refinement | Hours | Human | Quality/judgment |

The workflow pipelines naturally: while agents implement Feature A, you're designing Feature B. Your bottleneck shifts from "writing code" to "thinking clearly about what to build."

### The Failure Mode

The failure mode isn't Claude stopping—it's Claude continuing while quality degrades. Phase gates catch drift early, before it compounds.

---

## Sources

### Primary Sources (Verified)

| Source | URL | Key Contribution |
|--------|-----|------------------|
| **Anthropic Harness Research** | [anthropic.com](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | Two-part pattern, failure modes |
| **Phil Schmid** | [philschmid.de](https://www.philschmid.de/agent-harness-2026) | "Model is commodity, harness is moat" |
| **LangChain** | [blog.langchain.com](https://blog.langchain.com/agent-frameworks-runtimes-and-harnesses-oh-my/) | Framework vs runtime vs harness taxonomy |
| **Analytics Vidhya** | [analyticsvidhya.com](https://www.analyticsvidhya.com/blog/2025/12/agent-frameworks-vs-runtimes-vs-harnesses/) | Six canonical components |
| **Parallel AI** | [parallel.ai](https://parallel.ai/articles/what-is-an-agent-harness) | "Engine vs car" analogy |
| **Ralph** | [github.com](https://github.com/frankbria/ralph-claude-code) | Autonomous loop implementation |

### Related Reading

| Source | URL | Topic |
|--------|-----|-------|
| **Taming the Beast** | [mattquinn.ca](https://mattquinn.ca/journal/taming-the-beast) | Practical harness engineering experience |
| **Aakash Gupta** | [medium.com](https://aakashgupta.medium.com/2025-was-agents-2026-is-agent-harnesses-heres-why-that-changes-everything-073e9877655e) | Industry trend analysis |

---

## Validation Status

### Verified Against Sources

| Claim | Source |
|-------|--------|
| Harness = infrastructure wrapping model | Multiple sources (Parallel AI, LangChain) |
| Six canonical components | Analytics Vidhya |
| Framework/runtime/harness stack | LangChain |
| Two-part pattern (initializer + coding agent) | Anthropic |
| Over-ambition and premature victory failure modes | Anthropic |

### Reasonable Assumptions

| Assumption | Rationale |
|------------|-----------|
| Autonomy spectrum framing | Synthesis of observed approaches; not explicitly stated in sources |
| "Model is commodity, harness is moat" becoming consensus | Cited by multiple sources; industry direction |

---

## Methodology

1. Web search for current harness definitions and frameworks
2. Fetched and analyzed primary sources
3. Compared intents-plugin design to industry patterns
4. Synthesized autonomy spectrum framework from observed approaches

**Research date:** 2026-01-12
