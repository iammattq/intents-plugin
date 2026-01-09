# Intents Plugin for Claude Code

A plugin that keeps Claude Code agents in the context "smart zone" through chunked planning, sub-agent orchestration, and shared memory.

Inspired by [Dex Horthy's R-P-I workflow](https://www.youtube.com/watch?v=rmvDxxNubIg).

## The Problem

Claude Code works brilliantly in the "smart zone" (roughly the first 40% of context), but performance degrades on large features. This plugin solves it by:

1. **Chunked implementation** - Plans break work into context-sized pieces
2. **Sub-agent orchestration** - Research, reviews, and implementation run in isolated contexts
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

### Enabling Metrics Tracking (Optional)

To see elapsed time and token usage during `/intents:plan` and `/intents:implement`, add hooks to your project's `.claude/settings.local.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "python3 /path/to/intents-plugin/intents-plugin/hooks/user_prompt_submit.py"
      }]
    }],
    "Stop": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "python3 /path/to/intents-plugin/intents-plugin/hooks/stop.py"
      }]
    }]
  }
}
```

Replace `/path/to/intents-plugin` with the actual path. After setup, you'll see metrics like:

```
⏱️  feature-name
    Planning:     15m │ 52,103 in / 14,221 out
    Implementing:  8m │ 31,847 in /  9,432 out
    ────────────────────────────────────────────
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
- Workers implement → validate → update kanban → commit
- Pauses at phase gates for manual testing

**Parallel execution:** Spawn multiple chunk-workers for independent Ready chunks.

**Options:**
```
/intents:implement sorting --use-purple   # Purple team A/B iteration
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
- `--fast` - Consolidate checkpoints for streamlined workflow

**`/intents:implement`**
- `--skip-review` - Skip code review
- `--use-purple` - Use purple team workflow (Team A implements, Team B validates)

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
| `feature-plan` | Plan | Create PLAN.md with dependency graph and inline test specs |
| `chunk-worker` | Implement | Stateless worker: implement → validate → update kanban → commit |
| `purple-team-a` | Implement | Write code (purple team workflow) |
| `purple-team-b` | Implement | Validate and fix gaps (purple team workflow) |
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
- **1C** (M): Core component → needs 1A
- **1D** (S): Integration → needs 1A, 1B

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

  hooks/
    user_prompt_submit.py # Starts tracking on /plan or /implement
    stop.py               # Updates tokens and displays metrics

  agents/
    chunk-worker/AGENT.md        # Stateless chunk implementation
    codebase-researcher/AGENT.md
    code-reviewer/AGENT.md
    doc-reviewer/AGENT.md
    feature-plan/AGENT.md
    feature-refine/AGENT.md
    performance-reviewer/AGENT.md
    purple-team-a/AGENT.md
    purple-team-b/AGENT.md
    security-auditor/AGENT.md
    technical-researcher/AGENT.md
    accessibility-reviewer/AGENT.md

  skills/
    feature-brainstorm/SKILL.md

  commands/
    plan.md
    implement.md
    ccpp.md

  README.md
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

## Contributing

Improvements welcome:

1. Fork the repo
2. Create a feature branch
3. Use the plugin itself to plan and implement changes
4. Submit a PR

## License

MIT
