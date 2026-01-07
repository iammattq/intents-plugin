# Intents Plugin for Claude Code

**⚠️ Experimental** - This plugin is under active development. Expect breaking changes.

A Claude Code plugin that keeps agents in the context "smart zone" through chunked planning, sub-agent orchestration, and shared memory.

Inspired by [Dex Horthy's R-P-I workflow](https://www.youtube.com/watch?v=rmvDxxNubIg) and research on context window limitations.

## What is this?

Large features break Claude. The context window fills up, performance degrades, and you end up with inconsistent implementations. This plugin solves it by:

1. **Chunked planning** - Break work into context-sized pieces with clear ship criteria
2. **Sub-agent orchestration** - Offload research, reviews, and implementation to isolated contexts
3. **Shared memory** - `MEMORY.md` tracks progress across sub-agents and sessions

## Installation

### Option 1: Plugin Mode (Recommended)

Load the plugin using the `--plugin-dir` flag:

```bash
cd /path/to/your/project
claude --plugin-dir /path/to/intents-plugin/intents-plugin
```

Commands are namespaced: `/intents:plan`, `/intents:implement`, etc.

### Option 2: Standalone Mode

Symlink contents into your project's `.claude/` directory:

```bash
mkdir -p /path/to/your/project/.claude
ln -s /path/to/intents-plugin/intents-plugin/commands /path/to/your/project/.claude/commands
ln -s /path/to/intents-plugin/intents-plugin/agents /path/to/your/project/.claude/agents
ln -s /path/to/intents-plugin/intents-plugin/skills /path/to/your/project/.claude/skills
```

Commands are unprefixed: `/plan`, `/implement`, etc.

**Note:** Standalone mode may conflict with existing `.claude/` configurations.

## Quick Start

```bash
# Plan a feature (brainstorm → research → refine → plan)
/intents:plan user-settings

# Implement it (you orchestrate the kanban, workers do chunks)
/intents:implement user-settings
```

## Documentation

See **[intents-plugin/README.md](intents-plugin/README.md)** for:
- Complete command reference and options
- Agent and skill details
- Kanban-based chunking with dependency graphs
- Best practices and troubleshooting

## Development

The implementation plan and session logs are in:
- [`docs/plans/intents-plugin/PLAN.md`](docs/plans/intents-plugin/PLAN.md)
- [`docs/plans/intents-plugin/MEMORY.md`](docs/plans/intents-plugin/MEMORY.md)

## Background & Credits

This plugin is my experiment building a "harness" for AI coding agents, informed by:

**Dex Horthy's R-P-I Workflow (HumanLayer)** - The primary inspiration
- The "Dumb Zone": Performance degrades after ~40% context usage
- R-P-I pattern: Research → Plan → Implement in separate contexts
- Sub-agents as context isolation with compressed summaries
- Source: [No Vibes Allowed: Solving Hard Problems in Complex Codebases](https://www.youtube.com/watch?v=rmvDxxNubIg)
- Repo: [Advanced Context Engineering for Coding Agents](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents)

**Anthropic's Harness Research**
- Agents fail via over-ambition (run out of context) or premature victory (declare done too early)
- Initializer agent + coding agent pattern with progress tracking
- Source: [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

**Research on Context Limitations**
- Models degrade well before advertised limits (~130k effective for 200k windows)
- Working memory: LLMs track 5-10 variables before degrading to random guessing
- Sources: [Context Rot (Chroma)](https://research.trychroma.com/context-rot), [Long Context Reasoning](https://nrehiew.github.io/blog/long_context/)

## License

MIT
