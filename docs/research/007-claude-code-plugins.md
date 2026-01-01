# Research: Claude Code Plugins

**Date:** 2025-12-30
**Source:** https://code.claude.com/docs/en/plugins

---

## Overview

Plugins are custom extensions for Claude Code that can be shared across projects and teams. They support:
- Custom slash commands
- Custom agents
- Agent skills
- Hooks (event handlers)
- MCP servers
- LSP servers

## Plugin vs Standalone Configuration

| Aspect | Standalone (`.claude/`) | Plugins |
|--------|------------------------|---------|
| **Best For** | Personal workflows, project-specific | Sharing with teams, distribution |
| **Command Names** | `/hello` | `/plugin-name:hello` (namespaced) |
| **Sharing** | Manual copying | Via marketplaces with `/plugin install` |
| **Scope** | Single project | Multiple projects, reusable |

## Plugin Structure

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # REQUIRED - manifest
├── commands/                # optional - slash commands (auto-discovered)
│   └── hello.md
├── agents/                  # optional - custom agents
├── skills/                  # optional - agent skills
│   └── code-review/
│       └── SKILL.md
├── hooks/                   # optional - event handlers
│   └── hooks.json
├── .mcp.json               # optional - MCP servers
├── .lsp.json               # optional - LSP servers
└── README.md               # recommended
```

**Critical:** Do NOT put `commands/`, `agents/`, `skills/`, or `hooks/` inside `.claude-plugin/`. Only `plugin.json` goes there.

## Plugin Manifest (plugin.json)

Minimal required manifest:

```json
{
  "name": "my-plugin",
  "description": "A description of the plugin",
  "version": "1.0.0"
}
```

**Fields:**
- `name` (required): Unique identifier AND command namespace (e.g., `/my-plugin:hello`)
- `description` (required): Shown in plugin manager
- `version` (required): Semantic versioning
- `author` (optional): `{ "name": "Your Name" }`
- `homepage`, `repository`, `license` (optional)

**Important:** The `name` becomes the command prefix. If `name: "intents"`, commands are `/intents:plan`, `/intents:init`, etc.

## Auto-Discovery

Commands, agents, and skills are **auto-discovered** from their directories. You do NOT need to list them in plugin.json.

- `commands/plan.md` → `/plugin-name:plan`
- `commands/init.md` → `/plugin-name:init`
- `agents/my-agent/AGENT.md` → available as agent
- `skills/my-skill/SKILL.md` → available as skill

## Command Files

Commands use frontmatter for metadata:

```markdown
---
description: Greet the user with a friendly message
---

# Hello Command

Greet the user warmly and ask how you can help them today.
```

With arguments:

```markdown
---
description: Greet the user with a personalized message
---

# Hello Command

Greet the user named "$ARGUMENTS" warmly.
```

## Loading Plugins

### Development/Testing

```bash
claude --plugin-dir ./my-plugin
```

Multiple plugins:

```bash
claude --plugin-dir ./plugin-one --plugin-dir ./plugin-two
```

### Production

Users install via `/plugin install` from marketplaces.

## Hooks in Plugins

Create `hooks/hooks.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "command", "command": "npm run lint:fix $FILE" }
        ]
      }
    ]
  }
}
```

**Note:** This is different from standalone hooks in `.claude/settings.json`. Plugin hooks go in a separate `hooks.json` file.

## Plugin Precedence

When the same configuration exists in both standalone (`.claude/`) and plugin directories, the **plugin version takes precedence**.

## Converting Standalone to Plugin

1. Create plugin structure:
   ```bash
   mkdir -p my-plugin/.claude-plugin
   ```

2. Create manifest (`my-plugin/.claude-plugin/plugin.json`):
   ```json
   {
     "name": "my-plugin",
     "description": "Migrated from standalone",
     "version": "1.0.0"
   }
   ```

3. Move existing files:
   ```bash
   cp -r .claude/commands my-plugin/
   cp -r .claude/agents my-plugin/
   cp -r .claude/skills my-plugin/
   ```

4. Migrate hooks to `my-plugin/hooks/hooks.json`

5. Test:
   ```bash
   claude --plugin-dir ./my-plugin
   ```

---

## Key Takeaways for intents-plugin

1. **Plugin name = command prefix**: `"name": "intents"` means `/intents:plan`, `/intents:init`

2. **Auto-discovery**: Don't need to list commands/agents/skills in plugin.json

3. **Loading**: Use `claude --plugin-dir /path/to/intents-plugin/intents-plugin`

4. **Hooks**: For plugin hooks, need `hooks/hooks.json` not settings.json

5. **Standalone alternative**: Symlink to `.claude/` works but commands are unprefixed (`/plan` not `/intents:plan`)

---

## Current intents-plugin Status

**Structure:** Correct
```
intents-plugin/
├── .claude-plugin/
│   └── plugin.json         ✓
├── commands/               ✓
├── agents/                 ✓
├── skills/                 ✓
├── hooks/                  ✓ (Python scripts, not hooks.json)
└── templates/              ✓
```

**Issue:** Hooks are Python scripts for settings.json, not plugin hooks.json format. This is intentional - hooks run from target project's `.claude/settings.json`, not from plugin.

**To use:**
```bash
cd /path/to/target/project
claude --plugin-dir /path/to/intents-plugin/intents-plugin
```

Then: `/intents:plan`, `/intents:init`, `/intents:implement`, `/intents:status`, `/intents:validate`
