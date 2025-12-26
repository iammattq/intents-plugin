---
description: Bootstrap .intents/ folder from existing codebase. Use on new projects or after major refactoring.
argument-hint: [--force]
---

# /intents:init

Bootstrap the `.intents/` folder by analyzing your codebase.

## Usage

```
/intents:init           # Bootstrap (fails if .intents/ exists)
/intents:init --force   # Overwrite existing .intents/
```

## Prerequisites

Check before proceeding:

1. **No existing .intents/** (unless `--force` in $ARGUMENTS):
   - If `.intents/` exists and no `--force`: Stop and inform user:
     - View current: `/intents:status`
     - Overwrite: `/intents:init --force`
     - Delete manually and re-run

2. **Recognizable project** - package.json, pyproject.toml, or similar config should exist

## Process

Spawn the `codebase-analyzer` agent with context:

```
Analyze this codebase and bootstrap the .intents/ folder.

Force mode: [yes if --force in args, otherwise no]
```

The agent will:
1. Survey project structure
2. Research features, capabilities, entities, tech (parallel)
3. Compile graph YAML files
4. Present for review
5. Write .intents/ (after approval)

## After Success

- `/intents:status` - View the feature tree
- `/intents:plan [feature]` - Plan new features
