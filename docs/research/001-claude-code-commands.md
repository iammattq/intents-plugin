# Research 001: Claude Code Commands Architecture

**Date:** 2025-12-26

**Status:** Complete

**Related:** intents-plugin command design

## Problem Statement

How do we create best-in-class Claude Code commands (slash commands)? This research covers command architecture, the relationship between commands/skills/agents, SKILL.md and AGENT.md patterns, progressive disclosure, and real-world examples.

## Constraints

- Commands must work within Claude Code's context window limitations
- Must integrate with existing `.claude/` directory structure
- Should follow official Anthropic patterns and best practices
- Need to support both simple prompts and complex orchestration workflows

---

## Part 1: Command Architecture

### What Are Slash Commands?

Slash commands are frequently-used prompts stored as Markdown files that Claude Code executes during interactive sessions. They provide explicit, user-controlled entry points for workflows.

### File Locations

| Type | Location | Scope | Priority |
|------|----------|-------|----------|
| Project commands | `.claude/commands/` | Repository-specific, shared with team | Highest |
| User commands | `~/.claude/commands/` | Available across all projects | Lower |
| Plugin commands | `<plugin>/commands/` | Distributed via plugins | Lowest |

### Naming Conventions

- Command name derives from filename (without `.md` extension)
- Subdirectories create namespaces without affecting command names
- Project commands take precedence over personal commands with the same name

**Example:**
```
.claude/commands/frontend/component.md  ->  /component (project:frontend)
.claude/commands/backend/test.md        ->  /test (project:backend)
```

### Command File Structure

```markdown
---
allowed-tools: Bash(git add:*), Bash(git status:*)
argument-hint: [message]
description: Brief command description
model: claude-3-5-haiku-20241022
disable-model-invocation: false
---

# Command Title

Your prompt content here.

Use $ARGUMENTS for all arguments or $1, $2, etc. for specific arguments.

## Context (optional)

Include file contents with @src/file.js
Execute bash with !`git status`
```

### Frontmatter Fields

| Field | Required | Description | Default |
|-------|----------|-------------|---------|
| `description` | Recommended | Brief command description, shown in `/help` | First line of prompt |
| `allowed-tools` | No | Tools available to the command | Inherits from conversation |
| `argument-hint` | No | Expected arguments hint (e.g., `[message]`) | None |
| `model` | No | Specific model to use | Inherits from conversation |
| `disable-model-invocation` | No | Prevent SlashCommand tool from calling | false |

### Argument Syntax

**All arguments:**
```markdown
Fix issue #$ARGUMENTS following our coding standards
```
Usage: `/fix-issue 123 high-priority` -> `$ARGUMENTS` = "123 high-priority"

**Individual arguments:**
```markdown
---
argument-hint: [pr-number] [priority] [assignee]
---

Review PR #$1 with priority $2 and assign to $3.
```
Usage: `/review-pr 456 high alice` -> `$1`="456", `$2`="high", `$3`="alice"

### Advanced Features

**Bash execution (prefixed with `!`):**
```markdown
## Context
- Current git status: !`git status`
- Current branch: !`git branch --show-current`
```

**File references (prefixed with `@`):**
```markdown
Review the implementation in @src/utils/helpers.js
Compare @src/old-version.js with @src/new-version.js
```

---

## Part 1B: Plugin Commands vs Standalone Commands

### Overview

Commands can be distributed two ways:

| Aspect | Standalone | Plugin |
|--------|-----------|--------|
| **Location** | `.claude/commands/` or `~/.claude/commands/` | `<plugin>/commands/` |
| **Scope** | Single project or user | Shareable across teams |
| **Command invocation** | `/hello` | `/plugin-name:hello` |
| **Distribution** | Manual copying | Marketplace installation |
| **Version control** | Git with project | Semantic versioning in manifest |

### Plugin Directory Structure

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # REQUIRED - manifest only
├── commands/                # Slash commands
│   └── hello.md
├── agents/                  # Custom agents
│   └── reviewer.md
├── skills/                  # Agent skills
│   └── skill-name/
│       └── SKILL.md
├── hooks/                   # Event handlers
│   └── hooks.json
├── .mcp.json               # MCP server configs
└── README.md
```

**Critical**: Only `plugin.json` goes inside `.claude-plugin/`. All other directories must be at plugin root.

### Plugin Manifest (plugin.json)

```json
{
  "name": "my-first-plugin",
  "description": "A greeting plugin to learn the basics",
  "version": "1.0.0",
  "author": {
    "name": "Your Name"
  },
  "repository": {
    "type": "git",
    "url": "https://github.com/user/my-plugin"
  },
  "license": "MIT"
}
```

| Field | Required | Purpose |
|-------|----------|---------|
| `name` | Yes | Unique identifier and slash command namespace |
| `description` | Yes | Shown in plugin manager |
| `version` | Yes | Semantic versioning (MAJOR.MINOR.PATCH) |
| `author` | No | Attribution object with `name` field |
| `repository` | No | Git repository details |
| `license` | No | License type |

### Command Namespacing

Plugin commands are automatically namespaced:

| Plugin Name | Command File | Invoked As |
|-------------|--------------|-----------|
| `my-plugin` | `commands/hello.md` | `/my-plugin:hello` |
| `intents` | `commands/status.md` | `/intents:status` |
| `code-review` | `commands/analyze.md` | `/code-review:analyze` |

### When to Use Each

**Use Plugins When:**
- Sharing functionality with team or community
- Same configuration needed across multiple projects
- Want version control and easy updates
- Distributing through a marketplace
- Okay with namespaced commands

**Use Standalone Configuration When:**
- Customizing for a single project
- Configuration is personal/experimental
- Want short command names (`/hello` vs `/plugin:hello`)
- Iterating before packaging

### Converting Standalone to Plugin

```bash
# 1. Create plugin structure
mkdir -p my-plugin/.claude-plugin

# 2. Create manifest
cat > my-plugin/.claude-plugin/plugin.json << 'EOF'
{
  "name": "my-plugin",
  "description": "Migrated from standalone",
  "version": "1.0.0"
}
EOF

# 3. Copy files (at plugin root, NOT in .claude-plugin/)
cp -r .claude/commands my-plugin/
cp -r .claude/agents my-plugin/
cp -r .claude/skills my-plugin/
```

### Testing Plugins

```bash
# Load during development
claude --plugin-dir ./my-plugin

# Load multiple plugins
claude --plugin-dir ./plugin-one --plugin-dir ./plugin-two
```

Restart Claude Code to pick up changes to plugin files.

---

## Part 2: Commands vs Skills vs Agents

### Comparison Table

| Aspect | Slash Commands | Skills | Subagents |
|--------|----------------|--------|-----------|
| **Trigger** | Manual (`/command`) | Auto-discovered | Delegated by Claude |
| **Context** | Main conversation | Main conversation | Isolated context window |
| **Packaging** | Single .md file | Directory with SKILL.md + resources | Directory with AGENT.md |
| **Discovery** | Terminal autocomplete | Task recognition | Description matching |
| **Complexity** | Simple prompts | Complex capabilities | Specialized tasks |
| **When to use** | Repeatable workflows | Auto-apply expertise | Context-heavy delegation |

### When to Use Each

**Slash Commands:**
- Quick, frequently-used prompts
- User-initiated workflows
- Simple tasks with clear triggers
- Examples: `/review`, `/commit`, `/test`

**Skills:**
- Complex workflows requiring multiple files
- Auto-applied expertise based on context
- Reusable team knowledge
- Examples: coding standards, framework patterns, testing guidelines

**Subagents:**
- Research-heavy tasks
- Tasks requiring extensive codebase exploration
- Isolated context to prevent main thread pollution
- Parallel execution of independent tasks
- Examples: codebase analysis, security audits, documentation research

### How Commands Invoke Skills and Agents

Commands can orchestrate workflows that leverage both:

```markdown
# /implement-feature command

## Process

1. **Research Phase** (spawns subagent)
   Use the codebase-researcher agent to understand existing patterns.

2. **Planning Phase** (uses skill)
   Apply the feature-planning skill to create a structured plan.

3. **Implementation Phase** (spawns subagent)
   Use the feature-implementer agent to implement chunk by chunk.
```

---

## Part 3: SKILL.md Patterns

### File Structure

Minimum:
```
my-skill/
└── SKILL.md
```

Complex:
```
my-skill/
├── SKILL.md              # Overview (loaded when triggered)
├── reference.md          # Details (loaded as needed)
├── examples.md           # Patterns and examples
├── scripts/
│   └── validate.py       # Executable code
└── templates/
    └── output.md         # Output templates
```

### SKILL.md Template

```yaml
---
name: lowercase-with-hyphens
description: What it does AND when to use it. Include trigger keywords.
allowed-tools: Read, Grep, Glob  # Optional
---

# Skill Name

You are a [role]. [Brief context].

## Core Principles

- [Key principle 1]
- [Key principle 2]

## Process

1. **Step 1** - [Action]
2. **Step 2** - [Action]
3. **Step 3** - [Action]

## Output Format

[Structured output template]

## Examples

[Concrete input/output demonstrations]
```

### Frontmatter Rules

| Field | Requirements |
|-------|--------------|
| `name` | Lowercase, numbers, hyphens only. Max 64 chars. No "anthropic" or "claude" |
| `description` | 1-1024 chars. Must include WHAT it does AND WHEN to use it |
| `allowed-tools` | Optional. Restricts tool access if specified |

### Description Formula

```
[Action verbs describing capabilities]. Use when [specific triggers/contexts].
```

**Good:**
```yaml
description: Extract text from PDFs, fill forms, merge documents. Use when working with PDF files or when the user mentions document extraction.
```

**Bad:**
```yaml
description: Helps with documents
```

### Progressive Disclosure

Skills support progressive disclosure - Claude only loads supplementary files when needed:

1. **At startup**: Claude scans skill metadata (name + description)
2. **On trigger**: Claude loads SKILL.md primary file
3. **As needed**: Claude reads referenced supplementary files

**Keep SKILL.md under 500 lines.** Split larger content into referenced files.

### Best Practices

1. **YAGNI First**: Start with just SKILL.md. Add supporting files only when you hit real pain.

2. **Concise is Key**: Context window is shared. Only add what Claude doesn't know.

3. **Degrees of Freedom**:
   - High freedom: Multiple valid approaches ("analyze and suggest")
   - Medium freedom: Preferred pattern with variation (pseudocode with params)
   - Low freedom: Fragile/critical operations (exact commands)

4. **One-level deep references only**: SKILL.md -> reference.md (not SKILL.md -> advanced.md -> details.md)

---

## Part 4: AGENT.md Patterns

### File Structure

```
.claude/agents/
└── agent-name.md
```

Or for plugins:
```
<plugin>/agents/
└── agent-name/
    └── AGENT.md
```

### AGENT.md Template

```yaml
---
name: agent-name
description: Use WHEN [trigger]. Does [what]. [Domain] specialized. [Access level]-only.
tools: Read, Grep, Glob, Bash  # Optional - inherits all if omitted
model: haiku | sonnet | opus | inherit
permissionMode: default  # Optional
skills: skill1, skill2  # Optional
---

You are a [role]. Begin responses with: `[EMOJI AGENT NAME]`

[Read-only | Full access] - [what you do/don't do].

## Before Starting

[Prerequisites: files to read, context to gather]

## Process

1. **Phase 1** - [Clear action]
2. **Phase 2** - [Clear action]
3. **Phase 3** - [Clear action]

## Checklist (if reviewing)

### Category 1
- [ ] Specific verifiable item
- [ ] Another item with clear criteria

## Output Format

## Summary
[1-2 sentences: main finding]

## Findings
### Category
- `file.tsx:42` - Finding with location
  - Context: [why it matters]
  - Fix: [guidance]

## Verdict (if applicable)
[Clear recommendation]
```

### Configuration Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier using lowercase letters and hyphens |
| `description` | Yes | Natural language description + when to invoke |
| `tools` | No | Comma-separated tools. Inherits all if omitted |
| `model` | No | `haiku`, `sonnet`, `opus`, or `inherit` |
| `permissionMode` | No | `default`, `acceptEdits`, `bypassPermissions`, `plan`, `ignore` |
| `skills` | No | Auto-load specific skills when agent starts |

### Model Selection Guide

| Model | Use For | Cost | Speed |
|-------|---------|------|-------|
| `haiku` | Pattern matching, simple checks, fast operations | Lowest | Fast |
| `sonnet` | Code review, security audit, moderate reasoning | Medium | Balanced |
| `opus` / `inherit` | Complex research, architecture, deep analysis | Highest | Slower |

**Rules of thumb:**
- Design review -> `haiku`
- Code review -> `sonnet`
- Security audit -> `sonnet`
- Codebase research -> `inherit`
- Architecture planning -> `inherit`

### Tool Permission Patterns

```yaml
# Read-only (most reviewers)
tools: Read, Grep, Glob

# Review with command execution (git, tests)
tools: Read, Grep, Glob, Bash

# Research with web access
tools: Read, Grep, Glob, Bash, WebFetch, WebSearch

# Orchestrator (can spawn other agents)
tools: Read, Grep, Glob, Bash, Task, Write

# Full access (rarely needed)
tools: *
```

### Agent Archetypes

**1. Reviewer (Read-Only)**
- Purpose: Evaluate code/content against standards
- Tools: `Read, Grep, Glob`
- Model: `haiku` or `sonnet`
- Key sections: Process, Checklist, Output Format, Verdict

**2. Researcher**
- Purpose: Explore code, return compressed findings
- Tools: `Read, Grep, Glob, Bash`
- Model: `inherit`
- Key sections: Process (Plan -> Explore -> Synthesize), Output Format

**3. Scout**
- Purpose: Find patterns, candidates for extraction
- Tools: `Read, Grep, Glob`
- Model: `haiku`
- Key sections: Detection Strategies, Evaluation Criteria, Output Format

**4. Orchestrator**
- Purpose: Coordinate multi-agent workflows
- Tools: `Read, Grep, Glob, Bash, Task, Write`
- Model: `opus` or `inherit`
- Key sections: Process phases, Agent spawn templates, Validation checkpoints

---

## Part 5: Progressive Disclosure Patterns

### Why It Matters

Context window is finite. Progressive disclosure ensures:
- Only relevant information is loaded
- Main context stays clean
- Specialists get deep context in isolation

### Implementation Strategies

**1. Skill File Organization**
```
skill/
├── SKILL.md          # 500 lines max - loaded first
├── reference.md      # Loaded when details needed
├── advanced.md       # Loaded for edge cases
└── scripts/          # Executed, not loaded
```

**2. Agent Delegation**
```
Main conversation
    |
    +-> Research subagent (explores, returns summary)
    |
    +-> Review subagent (audits, returns findings)
    |
    +-> Implementation subagent (works in isolation)
```

**3. Command Orchestration**
```markdown
# /complex-workflow

## Phase 1: Gather Context
Spawn research agent to explore codebase.
[Agent returns compressed findings]

## Phase 2: Apply Expertise
Load relevant skill for domain knowledge.
[Skill provides patterns]

## Phase 3: Execute
Spawn implementation agent with context from phases 1-2.
```

### Best Practices

1. **Subagents for research**: Keep main context clean by delegating exploration

2. **Skills for expertise**: Auto-loaded domain knowledge without explicit invocation

3. **Commands for workflows**: User-initiated entry points that orchestrate skills + agents

4. **CLAUDE.md for constants**: Always-on project context that doesn't require loading

---

## Part 6: Real-World Examples

### Example 1: Simple Command (Status Check)

```markdown
# /intents:status

Show the current state of the feature graph with status indicators.

## Usage
/intents:status              # Show full feature tree
/intents:status [feature-id] # Show detail for specific feature

## Implementation

When invoked:

1. Read `.intents/graph.yaml`
2. Build feature tree from parent-child relationships
3. Compute inherited capabilities
4. Display tree with status indicators

## Output Format

Features:
root (Project Name) [implemented]
|-- feature-a [implemented]
|   +-- sub-feature [planned] -> docs/plans/sub/PLAN.md
+-- feature-b [in-progress]

Summary:
  Implemented: 5
  Planned: 2
```

### Example 2: Orchestrating Command

```markdown
# /intents:implement

Implement a planned feature with full workflow orchestration.

## Usage
/intents:implement <feature-id>

## Workflow Steps

### Step 1: Validate Feature
Check that the feature is ready for implementation:
- Feature exists in graph
- PLAN.md exists
- Status is `planned` or `broken`

### Step 2: Update Graph Status
```yaml
feature-id:
  status: in-progress  # Changed from planned
```

### Step 3: Test Spec (TDD)
Spawn `test-spec` agent:
```
Task: test-spec agent

Create TDD test specifications for: feature-id

Context:
- PLAN.md: docs/plans/feature-id/PLAN.md
- Feature intent: [from graph]
```

### Step 4: Feature Implementer
Spawn `feature-implementer` agent:
```
Task: feature-implementer agent

Implement: feature-id
Plan: docs/plans/feature-id/PLAN.md
Memory: docs/plans/feature-id/MEMORY.md
```

### Step 5: Quality Checks
Spawn review agents:
- `code-reviewer` - Always
- `security-auditor` - If auth/API/data involved
- `accessibility-reviewer` - If UI involved

### Step 6: Update Graph Status
On success: `status: implemented`
On failure: `status: broken`
```

### Example 3: Skill (Domain Expertise)

```yaml
---
name: intents-system
description: Graph schema teaching and inheritance rules. Activated when .intents/ folder detected. Teaches how to read, write, and maintain the feature graph.
---

# Intents System

You are working with a codebase that uses the `.intents/` graph system.

## Overview

| File | Purpose | Priority |
|------|---------|----------|
| `graph.yaml` | Feature tree with status | High |
| `capabilities.yaml` | Reusable interfaces | High |
| `entities.yaml` | Domain models | Medium |
| `tech.yaml` | Technology dependencies | Low |

## When to Read vs Write

| Phase | Access | What Changes |
|-------|--------|--------------|
| Research | READ | Nothing |
| Plan | WRITE | Create feature node, status: `planned` |
| Implement | WRITE | Update status: `in-progress` -> `implemented` |

## Inheritance Rules

Features inherit capabilities from their parent:
- Children inherit all parent capabilities
- Children can add additional capabilities
- Modes are inherited if parent uses same capability
```

### Example 4: Agent (Specialized Task)

```yaml
---
name: code-reviewer
description: Use AFTER implementing code. Reviews for quality and patterns. Next.js 15, TypeScript, Tailwind specialized. Read-only.
tools: Read, Grep, Glob, Bash
model: sonnet
---

You are a senior code reviewer. Begin responses with: `[CODE REVIEWER]`

Read-only - report findings, never modify code.

## Process

1. **Gather context** - Read plan/spec, run `git diff --name-only`
2. **Review systematically** - Work through checklist
3. **Report findings** - Use output format with file:line refs

## Checklist

### Next.js 15
- [ ] `params`/`searchParams` awaited (they're Promises)
- [ ] `'use client'` only where necessary
- [ ] Server Components fetch data, not Client Components

### TypeScript
- [ ] No `any` types
- [ ] Props interfaces defined
- [ ] Explicit return types on async functions

### Code Quality
- [ ] No `console.log` left in
- [ ] Error/loading/empty states handled

## Output Format

## Summary
[1-2 sentences: assessment and merge readiness]

## Issues Found

### Critical (must fix)
- **[Category]** `file.tsx:42` - Issue description
  - Suggested fix: [guidance]

### Important (should fix)
- **[Category]** `file.tsx:87` - Issue description

## Verdict
[Approved | Changes requested]
```

---

## Part 7: Anti-Patterns to Avoid

### Command Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Vague description | Include WHAT and WHEN |
| No output format | Always define expected output |
| Over-scoped commands | Single purpose per command |
| Hardcoded values | Use arguments ($1, $ARGUMENTS) |

### Skill Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Verbose explanations | Assume Claude knows basics |
| Multiple tool options | Recommend one default |
| Time-sensitive info | Use "old patterns" section |
| Deep file nesting | One-level references |

### Agent Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| `tools: *` for a reviewer | `tools: Read, Grep, Glob` |
| `model: inherit` for simple checks | `model: haiku` |
| No output format | Always define structure |
| Vague description | Include "Use WHEN" trigger |
| Over-explaining to Claude | It's smart, be concise |

---

## Recommendations

### For This Project (intents-plugin)

1. **Keep current command structure**: The existing `/intents:*` commands are well-designed orchestrators

2. **Enhance descriptions**: Ensure all agents have "Use WHEN" triggers in their descriptions

3. **Add model selection**: Specify appropriate models for each agent (haiku for simple, sonnet for review, opus for orchestration)

4. **Document output formats**: Every agent should have a clear output format section

5. **Consider plugin distribution**: Package as a Claude Code plugin for easy team adoption

### General Best Practices

1. **Start simple**: Begin with a single command.md, add complexity only when needed

2. **Test incrementally**: Validate each component before building on it

3. **Match model to task**: Don't use opus for simple pattern matching

4. **Limit tool access**: Grant only necessary tools to improve security and focus

5. **Use progressive disclosure**: Keep main context clean, delegate research to subagents

6. **Include validation**: Commands that orchestrate should validate state at each step

---

## Sources

### Primary Sources (Verified)

These sources were directly fetched and validated on 2025-12-26:

| Source | URL | What Was Verified |
|--------|-----|-------------------|
| **Slash Commands Docs** | [code.claude.com/docs/en/slash-commands](https://code.claude.com/docs/en/slash-commands) | File locations, frontmatter fields, argument syntax, `!` and `@` syntax |
| **Subagents Docs** | [code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents) | AGENT.md structure, frontmatter fields, model options, tool patterns |
| **Skills Docs** | [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills) | SKILL.md structure, frontmatter fields, discovery mechanism, constraints |
| **Plugins Docs** | [code.claude.com/docs/en/plugins](https://code.claude.com/docs/en/plugins) | Plugin structure, manifest fields, command namespacing, distribution |
| **Anthropic Best Practices** | [anthropic.com/engineering/claude-code-best-practices](https://www.anthropic.com/engineering/claude-code-best-practices) | Multi-turn workflows, CLAUDE.md guidance, subagent usage patterns |
| **Alex Op Guide** | [alexop.dev/posts/claude-code-customization-guide...](https://alexop.dev/posts/claude-code-customization-guide-claudemd-skills-subagents/) | Commands vs Skills vs Agents comparison, progressive disclosure |

### Secondary Sources (Referenced but not fetched)

- [Understanding Claude Code's Full Stack](https://alexop.dev/posts/understanding-claude-code-full-stack/) - MCP, Skills, Subagents, Hooks architecture
- [Claude Skills Tutorial](https://www.siddharthbharath.com/claude-skills/) - SKILL.md structure and examples
- [Cooking with Claude Code: The Complete Guide](https://www.siddharthbharath.com/claude-code-the-complete-guide/) - Comprehensive usage guide
- [GitHub - wshobson/commands](https://github.com/wshobson/commands) - Production-ready slash command examples
- [GitHub - wshobson/agents](https://github.com/wshobson/agents) - Multi-agent orchestration patterns
- [Task/Agent Tools - ClaudeLog](https://claudelog.com/mechanics/task-agent-tools/) - Task tool mechanics
- [Customize Claude Code with plugins](https://claude.com/blog/claude-code-plugins) - Plugin system overview

---

## Validation Status

### ✅ Verified Against Official Documentation

The following claims were directly confirmed from primary sources:

| Section | Claim | Source |
|---------|-------|--------|
| Part 1 | Commands in `.claude/commands/` and `~/.claude/commands/` | Slash Commands Docs |
| Part 1 | Frontmatter fields: `allowed-tools`, `argument-hint`, `description`, `model`, `disable-model-invocation` | Slash Commands Docs |
| Part 1 | Argument syntax: `$ARGUMENTS`, `$1`, `$2`, etc. | Slash Commands Docs |
| Part 1 | Bash execution with `!` prefix, file references with `@` | Slash Commands Docs |
| Part 2 | Commands = manual, Skills = auto-discovered, Agents = delegated | All three official docs |
| Part 2 | Subagents run in isolated context windows | Subagents Docs |
| Part 3 | Skills in `.claude/skills/skill-name/SKILL.md` | Skills Docs |
| Part 3 | Skill frontmatter: `name` (64 chars), `description` (1-1024 chars), `allowed-tools` | Skills Docs |
| Part 3 | Name constraints: lowercase, numbers, hyphens only | Skills Docs |
| Part 3 | Progressive disclosure: files loaded as-needed | Skills Docs |
| Part 4 | Agents in `.claude/agents/` | Subagents Docs |
| Part 4 | Agent frontmatter: `name`, `description`, `tools`, `model`, `permissionMode`, `skills` | Subagents Docs |
| Part 4 | Model options: `haiku`, `sonnet`, `opus`, `inherit` | Subagents Docs |
| Part 5 | Subagents for research to keep main context clean | Anthropic Best Practices |
| Part 1B | Plugin structure with `.claude-plugin/plugin.json` | Plugins Docs |
| Part 1B | Plugin manifest fields: `name`, `description`, `version` required | Plugins Docs |
| Part 1B | Command namespacing: `/plugin-name:command` format | Plugins Docs |
| Part 1B | Only `plugin.json` inside `.claude-plugin/`, other dirs at root | Plugins Docs |
| Part 1B | Testing with `claude --plugin-dir ./my-plugin` | Plugins Docs |

### ⚠️ Reasonable Assumptions (Not Explicitly Documented)

The following recommendations are reasonable engineering guidance based on patterns observed, but are **not explicitly stated** in official documentation:

| Section | Assumption | Rationale |
|---------|------------|-----------|
| Part 3 | "Keep SKILL.md under 500 lines" | Reasonable heuristic for context management; official docs say "split larger content" but don't specify a limit |
| Part 4 | Model selection guide (haiku for simple, sonnet for review, opus for orchestration) | Reasonable inference from model capabilities and cost/speed trade-offs; not explicitly prescribed |
| Part 4 | "Use WHEN" trigger pattern in descriptions | Best practice from community usage; official docs say "include when to invoke" but don't prescribe format |
| Part 4 | Agent archetypes (Reviewer, Researcher, Scout, Orchestrator) | Categorization by researcher for clarity; not an official taxonomy |
| Part 4 | Tool permission patterns (read-only reviewers get `Read, Grep, Glob`) | Reasonable security practice; official docs confirm tool restriction works but don't prescribe patterns |
| Part 5 | "One-level deep references only" for skills | Reasonable simplicity heuristic; not explicitly stated in docs |
| Part 7 | Anti-patterns list | Derived from best practices and inverse of documented good patterns; not an official list |

### ❌ Could Not Verify

| Claim | Status |
|-------|--------|
| `disable-model-invocation` field behavior | Field confirmed to exist but detailed behavior not verified |

---

## Methodology

1. **Initial research**: Technical-researcher agent gathered information from web searches and documentation
2. **Source validation**: Primary sources fetched directly via WebFetch to verify claims
3. **Cross-reference**: Claims compared against official documentation
4. **Uncertainty marking**: Assumptions and recommendations clearly labeled when not explicitly from official sources

**Validation date**: 2025-12-26
