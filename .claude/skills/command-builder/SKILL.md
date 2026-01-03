---
name: command-builder
description: Create Claude Code slash commands with proper structure, frontmatter, and patterns. Use when building commands, writing .md command files, or designing command workflows.
---

# Command Builder

Guide for creating effective Claude Code slash commands.

## Quick Start

```bash
# Project command (shared with team)
mkdir -p .claude/commands

# User command (personal, all projects)
mkdir -p ~/.claude/commands

# Plugin command (distributed via plugin)
# <plugin>/commands/my-command.md
```

## Command Template

```markdown
---
description: Brief description shown in /help
argument-hint: [required-arg] [optional-arg]
allowed-tools: Bash(git:*), Read, Write
model: claude-3-5-haiku-20241022
---

# Command Title

[Instructions for what Claude should do]

## Context
- Current branch: !`git branch --show-current`
- File contents: @src/relevant-file.ts

## Process
1. Step one
2. Step two

## Output Format
[Expected output structure]
```

## Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `description` | Recommended | Shown in `/help`. Defaults to first line |
| `argument-hint` | No | Shows expected args (e.g., `[message]`) |
| `allowed-tools` | No | Restrict tools. Inherits from conversation if omitted |
| `model` | No | Specific model. Inherits if omitted |
| `disable-model-invocation` | No | Prevent Skill tool from calling this command |

## Argument Syntax

**All arguments as single string:**
```markdown
Fix issue #$ARGUMENTS following our standards
```
Usage: `/fix 123 high-priority` → `$ARGUMENTS` = "123 high-priority"

**Individual arguments:**
```markdown
---
argument-hint: [pr-number] [priority]
---
Review PR #$1 with priority $2.
```
Usage: `/review 456 high` → `$1`="456", `$2`="high"

## Dynamic Content

**Bash execution (prefix `!`):**
```markdown
## Context
- Git status: !`git status --short`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -5`
```

**File inclusion (prefix `@`):**
```markdown
Review the implementation in @src/utils/helpers.js
Compare @src/old.js with @src/new.js
```

## Command Types

### Simple Command
Single-purpose, quick execution:

```markdown
---
description: Show git status with branch info
---

Show current git status:
!`git status`

Current branch: !`git branch --show-current`
```

### Orchestrating Command
Spawns agents, coordinates workflow:

```markdown
---
description: Implement feature with full workflow
argument-hint: <feature-id>
---

# Implement Feature: $1

## Phase 1: Research
Spawn the `codebase-researcher` agent to explore:
- Existing patterns for similar features
- Files that will need modification
- Dependencies and constraints

## Phase 2: Plan Review
Read the plan at `docs/plans/$1/PLAN.md`
Validate all prerequisites are met.

## Phase 3: Implementation
For each chunk in plan, spawn `chunk-implementer` with:
- Chunk ID, plan excerpt, files list
- Update TodoWrite progress between chunks

## Phase 4: Review
Spawn `code-reviewer` agent on changed files.
```

## Best Practices

| Avoid | Do Instead |
|-------|------------|
| Vague description | Include WHAT and WHEN |
| No output format | Define expected output structure |
| Over-scoped commands | Single purpose per command |
| Hardcoded values | Use `$1`, `$2`, `$ARGUMENTS` |
| Missing context | Use `!` and `@` for dynamic context |
| Unrestricted tools | Grant only what's needed |

## Examples

See [examples.md](examples.md) for complete command examples.
