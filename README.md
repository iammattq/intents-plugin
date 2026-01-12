# Intents Plugin for Claude Code

> **Warning**: This plugin is experimental and under active development. Expect breaking changes.

A plugin that keeps Claude Code agents in the context "smart zone" through chunked planning, sub-agent orchestration, and shared memory.

Inspired by [Dex Horthy's R-P-I workflow](https://www.youtube.com/watch?v=rmvDxxNubIg).
Kudos to [Matt Pocock for the Kanban Inspiration](https://x.com/mattpocockuk/status/2008200878633931247?s=20)

## The Problem

Building complex features with AI agents means managing context. When your context window fills up, it's game over—you lose continuity, the agent loses track of what it was doing, and you're stuck manually piecing things back together. Performance also degrades well before hitting limits (the "dumb zone" after ~40% context usage).

This plugin solves context management for long-running implementations:

1. **Chunked implementation** - Plans break work into context-sized pieces
2. **Sub-agent orchestration** - Research, reviews, and implementation run in isolated contexts
3. **Shared memory** - `MEMORY.md` tracks progress across sub-agents and sessions

## Design Philosophy

### Why Human-in-the-Loop?

AI coding harnesses exist on a spectrum from fully autonomous to fully manual. This plugin sits toward the "human drives, agents execute" end.

Fully autonomous approaches (like [Ralph](https://github.com/frankbria/ralph-claude-code)) are appealing—"fire and forget" sounds great. But they require pre-authorizing actions (via `--allowed-tools` or similar), and their safety mechanisms guard against different threats:

| What autonomous loops guard against | What they don't guard against |
|-------------------------------------|-------------------------------|
| Runaway iterations (max retries) | Model confusion compounding |
| API cost spikes (rate limits) | Wrong abstractions accumulating |
| Session timeouts (5hr detection) | Drift from original intent |
| Stagnation (no-change detection) | Subtle bugs building up |

**This plugin takes a different stance:** The metric isn't "my agent ran for 3 days"—it's "my agent built what I intended." The failure mode isn't Claude stopping; it's Claude continuing while quality degrades. Phase gates catch drift early, before it compounds.

More importantly, human-in-the-loop isn't about hitting enter. It's about spending your time on high-value work—designing systems, making architectural decisions, thinking through edge cases—while agents handle implementation. The workflow pipelines naturally: while agents implement Feature A, you're designing Feature B. Your bottleneck shifts from "writing code" to "thinking clearly about what to build."

### When Autonomous Makes Sense

- Well-defined, mechanical tasks (migrations, formatting, repetitive refactors)
- Tasks where "good enough" is acceptable
- When you'll review everything at the end anyway

### When Orchestrated Makes Sense

- Features requiring judgment calls
- Unfamiliar codebases where drift is costly
- When you want to catch problems early, not at the end

For a deeper dive on harness engineering, see [Taming the Beast](https://mattquinn.ca/journal/taming-the-beast).

## Installation

### Option 1: Plugin Mode (Recommended)

Load the plugin using the `--plugin-dir` flag:

```bash
cd /path/to/your/project
claude --plugin-dir /path/to/intents-plugin
```

Commands are namespaced: `/intents:plan`, `/intents:implement`, etc.

### Option 2: Standalone Mode

Symlink contents into your project's `.claude/` directory:

```bash
mkdir -p /path/to/your/project/.claude
ln -s /path/to/intents-plugin/commands /path/to/your/project/.claude/commands
ln -s /path/to/intents-plugin/agents /path/to/your/project/.claude/agents
ln -s /path/to/intents-plugin/skills /path/to/your/project/.claude/skills
```

Commands are unprefixed: `/plan`, `/implement`, etc.

**Note:** Standalone mode may conflict with existing `.claude/` configurations.

### Metrics Tracking (WIP - Not Currently Working)

> **Note**: Metrics tracking hooks are a work in progress and do not currently function. This section documents the intended behavior for future implementation.

To see elapsed time and token usage during `/intents:plan` and `/intents:implement`, add hooks to your project's `.claude/settings.local.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "python3 /path/to/intents-plugin/hooks/user_prompt_submit.py"
      }]
    }],
    "Stop": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "python3 /path/to/intents-plugin/hooks/stop.py"
      }]
    }]
  }
}
```

Replace `/path/to/intents-plugin` with the actual path. After setup, you'll see metrics like:

```
feature-name
    Planning:     15m | 52,103 in / 14,221 out
    Implementing:  8m | 31,847 in /  9,432 out
    ------------------------------------------------
    Total: 83,950 in / 23,653 out
```

## Quick Start

### 1. Plan a feature

```
/intents:plan user-preferences
```

This runs the full R-P workflow:
- **Brainstorm** - Conversational loop to pull detail out and challenge vagueness
- **Research** - Explore codebase for patterns and fit
- **Refine** - Advocate/critic debate with YAGNI lens
- **Plan** - Create PLAN.md with chunks and dependency graph

**Skip options:**
```
/intents:plan sorting --skip-brainstorm   # Idea already clear
/intents:plan sorting --skip-research     # Context known
```

### 2. Implement the feature

```
/intents:implement user-preferences
```

**You become the orchestrator.** The command:
- Reads the kanban in MEMORY.md (Ready/Blocked/Done)
- Spawns `chunk-worker` agents for Ready chunks
- Workers implement -> validate -> update kanban -> commit
- Pauses at phase gates for manual testing

**Parallel execution:** Spawn multiple chunk-workers for independent Ready chunks.

**Options:**
```
/intents:implement sorting --skip-review  # Skip code review stage
```

## Commands

| Command | Description |
|---------|-------------|
| `/intents:plan <feature>` | Run R-P workflow, create plan |
| `/intents:implement <feature>` | Implement with chunk tracking |

### Command Options

**`/intents:plan`**
- `--skip-brainstorm` - Skip ideation (idea already clear)
- `--skip-research` - Skip codebase/tech research

**`/intents:implement`**
- `--skip-review` - Skip code review

## Workflow Overview

```
     +------------------+
     | /intents:plan    |
     | (Research-Plan)  |
     +--------+---------+
              |
              | Creates PLAN.md
              v
     +------------------+
     |/intents:implement|
     | (Implementation) |
     +--------+---------+
              |
              | Chunk by chunk
              | with validation
              v
     +------------------+
     | Feature Complete |
     +------------------+
```

## Agents Included

| Agent | Phase | Purpose |
|-------|-------|---------|
| `codebase-researcher` | Research | Explore internal codebase for context |
| `technical-researcher` | Research | Research external docs and APIs |
| `feature-refine` | Research | Advocate/critic debate with YAGNI lens |
| `feature-plan` | Plan | Create PLAN.md with dependency graph and test specs |
| `chunk-worker` | Implement | Stateless worker: implement -> validate -> update kanban -> commit |
| `code-reviewer` | Review | Validate code quality and patterns |
| `security-auditor` | Review | OWASP security review |
| `accessibility-reviewer` | Review | WCAG compliance check |
| `performance-reviewer` | Review | Performance issue detection |
| `doc-reviewer` | Review | Documentation accuracy review |

## Skills Included

| Skill | Purpose |
|-------|---------|
| `feature-brainstorm` | Conversational ideation loop - pulls detail, challenges vagueness |

## Plan Structure

When you run `/intents:plan`, it creates:

```
docs/plans/<feature>/
  PLAN.md    # Problem, goals, phases, chunks with dependencies
  MEMORY.md  # Kanban board (Ready/Blocked/Done) + session logs
```

### PLAN.md - Chunks with Dependencies

```
## Phase 1: Foundation
| Chunk | Size | Depends | Scope | Files |
|-------|------|---------|-------|-------|
| 1A | M | - | Types + config | 3 |
| 1B | S | - | Page route | 1 |
| 1C | M | 1A | Core component | 2 |
| 1D | S | 1A, 1B | Integration | 2 |
```

- `-` means no dependencies (can start immediately)
- Chunks with same/no dependencies can run **in parallel**

### MEMORY.md - Kanban Board

```markdown
## Kanban

### Ready
- **1A** (M): Types + config
- **1B** (S): Page route

### Blocked
- **1C** (M): Core component -> needs 1A
- **1D** (S): Integration -> needs 1A, 1B

### Done
(none yet)
```

Workers pick from Ready, move to Done, unblock dependents.

Each phase ends with a **phase gate** for manual testing.

## Directory Structure

```
intents-plugin/
  .claude-plugin/
    plugin.json           # Plugin manifest

  agents/                 # 10 specialized agents
    chunk-worker.md
    codebase-researcher.md
    code-reviewer.md
    ...

  skills/
    feature-brainstorm/SKILL.md

  commands/
    plan.md
    implement.md
    ccpp.md

  hooks/
    user_prompt_submit.py
    stop.py

  docs/                   # Research and plans
    plans/
    research/
```

## Best Practices

### When to use this plugin

- **Large features** that span multiple sessions
- **Complex implementations** that benefit from explicit planning
- **Team projects** where plans serve as documentation

### When NOT to use it

- **Quick fixes** - Just edit the code directly
- **Trivial features** - Overhead not worth it for small changes
- **Exploratory work** - R-P-I assumes you know what you're building

### Tips

1. **Review generated plans** - The planner makes educated guesses; correct any errors
2. **Use phase gates** - Don't skip manual testing between phases
3. **Trust the chunking** - Smaller chunks keep Claude in the smart zone

## Troubleshooting

### Feature not found

Either:
1. Run `/intents:plan <feature>` to create it
2. Check `docs/plans/` for existing plans

### Implementation stuck

Check `docs/plans/<feature>/MEMORY.md` for:
- Current chunk and progress
- Blockers logged
- Decisions made

Resume with `/intents:implement <feature>`.

## Background & Credits

This plugin is an experiment building a "harness" for AI coding agents, informed by:

**Dex Horthy's R-P-I Workflow (HumanLayer)** - The primary inspiration
- The "Dumb Zone": Performance degrades after ~40% context usage
- R-P-I pattern: Research -> Plan -> Implement in separate contexts
- Sub-agents as context isolation with compressed summaries
- Source: [No Vibes Allowed: Solving Hard Problems in Complex Codebases](https://www.youtube.com/watch?v=rmvDxxNubIg)

**Anthropic's Harness Research**
- Agents fail via over-ambition (run out of context) or premature victory (declare done too early)
- Initializer agent + coding agent pattern with progress tracking
- Source: [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

**Research on Context Limitations**
- Models degrade well before advertised limits (~130k effective for 200k windows)
- Working memory: LLMs track 5-10 variables before degrading
- Sources: [Context Rot (Chroma)](https://research.trychroma.com/context-rot), [Long Context Reasoning](https://nrehiew.github.io/blog/long_context/)

## Contributing

Improvements welcome:

1. Fork the repo
2. Create a feature branch
3. Use the plugin itself to plan and implement changes
4. Submit a PR

## License

MIT
