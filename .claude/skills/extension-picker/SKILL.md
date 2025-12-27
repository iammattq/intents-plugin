---
name: extension-picker
description: Choose between skill, agent, slash command, or direct task. Use when deciding how to implement a new capability, automation, or workflow in Claude Code.
---

# Extension Picker

Decide which Claude Code extension type fits your need.

## Quick Decision

```
Do you want Claude to discover and use it automatically?
├─ YES → Is it reusable expertise/knowledge?
│   ├─ YES → SKILL
│   └─ NO (workflow with steps) → AGENT
└─ NO (you invoke it manually)
    ├─ Quick, repeatable prompt? → SLASH COMMAND
    └─ One-off complex task? → TASK TOOL (just ask Claude)
```

## The Four Options

| Type        | Invocation            | Context  | Best For                             |
| ----------- | --------------------- | -------- | ------------------------------------ |
| **Skill**   | Auto (Claude decides) | Shared   | Reusable expertise, knowledge packs  |
| **Agent**   | Auto or explicit      | Isolated | Specialized workflows, parallel work |
| **Command** | Manual (`/name`)      | Shared   | Quick prompts you use often          |
| **Task**    | Just ask              | Isolated | One-off complex tasks                |

## Decision Criteria

### Use a SKILL when:

- Claude should **discover it automatically** based on context
- It's **reusable expertise** (not a specific workflow)
- Multiple conversations/agents could benefit
- Examples: PDF processing, API patterns, coding standards

### Use an AGENT when:

- Task needs **isolated context** (prevents pollution)
- It's a **specialized workflow** with multiple steps
- You want **restricted tools** (e.g., read-only reviewer)
- Tasks should run **in parallel**
- Examples: code-reviewer, security-auditor, test-runner

### Use a SLASH COMMAND when:

- You **manually trigger** the same prompt repeatedly
- It's a **quick shortcut** (single file, simple)
- You want **explicit control** over when it runs
- Examples: `/review`, `/commit`, `/optimize`

### Use TASK TOOL when:

- It's a **one-off** complex task
- You don't need to reuse it
- Just ask Claude directly

## Key Differences

**Skill vs Agent:**

- Skills = recipes (portable expertise)
- Agents = specialized coworkers (isolated execution)
- Skills share context; agents have their own

**Skill vs Command:**

- Skills activate automatically when relevant
- Commands require you to type `/command`
- Both are markdown files, but different discovery

**Agent vs Command:**

- Agents have isolated context windows
- Commands run in main conversation
- Agents can have tool restrictions

## Anti-Patterns

| Don't                          | Do Instead      |
| ------------------------------ | --------------- |
| Agent for simple knowledge     | Skill           |
| Skill for manual workflow      | Command         |
| Command for auto-discovery     | Skill           |
| New extension for one-off task | Just ask Claude |

## File Locations

```
.claude/
├── skills/name/SKILL.md    # Auto-discovered capabilities
├── agents/name.md          # Specialized workers
└── commands/name.md        # Manual shortcuts
```
