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

Copy the plugin to your project:

```bash
cp -r intents-plugin/ /path/to/your/project/
```

Or symlink it:

```bash
ln -s /path/to/this-repo/intents-plugin /path/to/your/project/intents-plugin
```

Then restart Claude Code. The plugin activates when it detects `.claude-plugin/plugin.json`.

## Quick Start

```bash
# 1. Bootstrap your project's architecture graph
/intents:init

# 2. See the feature tree
/intents:status

# 3. Plan a new feature
/intents:plan user-settings --parent admin

# 4. Implement it
/intents:implement user-settings

# 5. Fix any structural issues
/intents:validate --fix
```

## Commands

| Command | Description |
|---------|-------------|
| `/intents:init` | Bootstrap `.intents/` from your codebase |
| `/intents:status` | Show feature tree with status |
| `/intents:status <feature>` | Show detail for specific feature |
| `/intents:plan <feature>` | Research + Plan workflow |
| `/intents:implement <feature>` | Implementation with tracking |
| `/intents:validate` | Check for structural issues |
| `/intents:validate --fix` | Fix issues interactively |

## What's Included

**12 Agents** for the complete workflow:
- `codebase-analyzer` - Bootstrap graph from existing code
- `codebase-researcher` - Explore internal codebase
- `technical-researcher` - Research external docs/APIs
- `feature-refine` - Advocate/critic debate
- `feature-plan` - Create PLAN.md + graph node
- `test-spec` - TDD specifications
- `feature-implementer` - Chunk-by-chunk implementation
- `code-reviewer` - Quality validation
- `security-auditor` - OWASP review
- `accessibility-reviewer` - WCAG compliance
- `performance-reviewer` - Performance analysis
- `doc-reviewer` - Documentation drift detection

**2 Skills:**
- `intents-system` - Teaches Claude the graph schema
- `feature-brainstorm` - Ideation patterns

**5 Commands** as documented above.

## The Graph

```yaml
# .intents/graph.yaml
root:
  name: My App
  status: implemented
  capabilities:
    - design-system

features:
  admin:
    name: Admin Dashboard
    status: implemented
    parent: root
    capabilities:
      - session-auth
      - persistence:read-write

  admin-galleries:
    name: Gallery Management
    status: implemented
    parent: admin           # inherits session-auth, persistence
    capabilities:
      - images:manage       # adds this capability
```

Features inherit capabilities from parents. Status tracks progress: `new` → `planned` → `in-progress` → `implemented`.

## Documentation

See [`intents-plugin/README.md`](intents-plugin/README.md) for:
- Complete command reference
- Graph schema documentation
- Best practices
- Troubleshooting

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
