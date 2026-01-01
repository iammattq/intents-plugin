# Intents Plugin for Claude Code

A Claude Code plugin that teaches Claude the R-P-I (Research-Plan-Implement) workflow with graph-based architecture tracking.

## What is this?

Large features break Claude. The context window fills up, performance degrades, and you end up with inconsistent implementations. The **R-P-I workflow** solves this by:

1. **Research** - Understand the problem space before committing
2. **Plan** - Break work into context-sized chunks with clear ship criteria
3. **Implement** - Execute chunk by chunk, maintaining progress in MEMORY.md

The `.intents/` folder captures your architecture as a graph:
- **Features** with status (planned, in-progress, implemented)
- **Capabilities** that features consume (auth, storage, media)
- **Inheritance** so children get parent capabilities automatically

This plugin automates the workflow that was previously manual orchestration.

## Installation

### Option 1: Plugin Mode (Recommended)

Load the plugin using the `--plugin-dir` flag:

```bash
cd /path/to/your/project
claude --plugin-dir /path/to/intents-plugin/intents-plugin
```

Commands are namespaced: `/intents:init`, `/intents:plan`, `/intents:implement`, etc.

### Option 2: Standalone Mode

Symlink contents into your project's `.claude/` directory:

```bash
mkdir -p /path/to/your/project/.claude
ln -s /path/to/intents-plugin/intents-plugin/commands /path/to/your/project/.claude/commands
ln -s /path/to/intents-plugin/intents-plugin/agents /path/to/your/project/.claude/agents
ln -s /path/to/intents-plugin/intents-plugin/skills /path/to/your/project/.claude/skills
```

Commands are unprefixed: `/init`, `/plan`, `/implement`, etc.

**Note:** Standalone mode may conflict with existing `.claude/` configurations.

## Quick Start

```bash
# Bootstrap your project
/intents:init

# Plan a feature
/intents:plan user-settings --parent admin

# Implement it
/intents:implement user-settings
```

## Documentation

See **[intents-plugin/README.md](intents-plugin/README.md)** for:
- Complete command reference and options
- Graph schema (all 4 YAML files)
- Agent and skill details
- Plan structure and chunking
- Best practices and troubleshooting

## Development

The implementation plan and session logs are in:
- [`docs/plans/intents-plugin/PLAN.md`](docs/plans/intents-plugin/PLAN.md)
- [`docs/plans/intents-plugin/MEMORY.md`](docs/plans/intents-plugin/MEMORY.md)

## Background & Credits

The R-P-I workflow is informed by research on context window limitations and agent orchestration:

**Anthropic's Harness Research**
- Problem: Agents fail via over-ambition (run out of context) or premature victory (declare done too early)
- Solution: Initializer agent + coding agent pattern with progress tracking
- Source: [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

**Dex Horthy's Context Engineering (HumanLayer)**
- The "Dumb Zone": Performance degrades after ~40% context usage
- R-P-I Workflow: Research → Plan → Implement in separate contexts
- Sub-agents as context isolation with compressed summaries
- Source: [Advanced Context Engineering for Coding Agents](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents)

**Research on Context Limitations**
- Models degrade well before advertised limits (~130k effective for 200k windows)
- Working memory: LLMs track 5-10 variables before degrading to random guessing
- Problem is reasoning, not retrieval—needle tests pass but complex reasoning fails
- Sources: [Context Rot (Chroma)](https://research.trychroma.com/context-rot), [Long Context Reasoning](https://nrehiew.github.io/blog/long_context/)

**Key Insight**
> "The more you use the context window, the worse outcomes you'll get."

This plugin automates the orchestration patterns that keep Claude in the "smart zone."

## License

MIT
