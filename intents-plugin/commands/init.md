# /intents:init

Bootstrap the `.intents/` folder from an existing codebase.

## What This Does

1. Analyzes your codebase structure
2. Identifies features, capabilities, entities, and tech stack
3. Generates the four graph files:
   - `graph.yaml` - Feature tree
   - `capabilities.yaml` - Reusable interfaces
   - `entities.yaml` - Domain models
   - `tech.yaml` - Technology dependencies
4. Presents for your review before writing

## Usage

```
/intents:init
```

## Process

The `codebase-analyzer` agent will:

1. **Survey** - Get an overview of your project structure
2. **Research** - Spawn parallel researchers to explore:
   - Feature mapping (routes, components, user-facing functionality)
   - Capability discovery (auth, storage, media, UI patterns)
   - Entity identification (domain models, data shapes)
   - Tech stack analysis (dependencies, configs)
3. **Compile** - Synthesize findings into graph YAML files
4. **Review** - Present the generated structure for your approval
5. **Write** - Create `.intents/` folder with files (only after approval)

## When to Use

- **First time setup** - Bootstrap a new project or existing codebase
- **After major refactoring** - Regenerate when architecture changed significantly
- **Fresh start** - Delete `.intents/` and regenerate if it's out of sync

## What to Expect

The analyzer will identify:
- **Features** at `status: implemented` (existing code assumed working)
- **Capabilities** based on patterns found in code
- **Tech** limited to significant dependencies, not every npm package

You can adjust the generated structure before writing, or edit files after creation.

## After Init

Once `.intents/` is created:
- `/intents:status` - View the feature tree and status
- `/intents:plan [feature]` - Plan new features
- `/intents:implement [feature]` - Implement planned features

The `intents-system` skill activates automatically when `.intents/` is detected.
