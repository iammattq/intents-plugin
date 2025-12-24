# /intents:init

Bootstrap the `.intents/` folder from an existing codebase.

## Usage

```
/intents:init
/intents:init --force    # Overwrite existing .intents/ folder
```

## What This Does

1. Analyzes your codebase structure
2. Identifies features, capabilities, entities, and tech stack
3. Generates the four graph files:
   - `graph.yaml` - Feature tree
   - `capabilities.yaml` - Reusable interfaces
   - `entities.yaml` - Domain models
   - `tech.yaml` - Technology dependencies
4. Presents for your review before writing

## Options

| Option | Description |
|--------|-------------|
| `--force` | Overwrite existing `.intents/` folder without prompting |

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

## Example Session

```
> /intents:init

Analyzing codebase...

Spawning parallel researchers:
  - Feature mapping (routes, components)
  - Capability discovery (auth, storage, media)
  - Entity identification (domain models)
  - Tech stack analysis (dependencies)

[Research complete]

Proposed .intents/ structure:

graph.yaml:
  root: Portfolio Site
  features:
    - home [implemented]
    - work [implemented]
      - work-list [implemented]
      - work-detail [implemented]
    - admin [implemented]
      - admin-galleries [implemented]
      - admin-journal [implemented]

capabilities.yaml:
  - session-auth (NextAuth)
  - persistence (DynamoDB)
  - images (S3, Sharp)

entities.yaml:
  - Gallery
  - JournalEntry
  - WorkItem

tech.yaml:
  - next-auth, dynamodb, s3, sharp, tailwind

---

Does this look correct? [y/n/edit]

> y

Writing .intents/ folder...
  - .intents/graph.yaml
  - .intents/capabilities.yaml
  - .intents/entities.yaml
  - .intents/tech.yaml

Bootstrap complete.

Next steps:
  - /intents:status to view the feature tree
  - /intents:plan [feature] to plan new features
```

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

## Error Handling

### .intents/ already exists

```
.intents/ folder already exists.

Options:
1. View current graph: /intents:status
2. Overwrite: /intents:init --force
3. Delete manually and re-run

Existing graph created: 2024-01-15
```

### No recognizable project structure

```
Unable to identify project structure.

Possible reasons:
- Empty or minimal codebase
- Unusual project layout
- Missing package.json or config files

Consider creating .intents/ manually using the templates.
```

### Research agent timeout

```
Research took longer than expected.

Partial results available:
  - Features: 12 found
  - Capabilities: (incomplete)
  - Entities: 5 found
  - Tech: 8 found

Options:
1. Use partial results
2. Retry research
3. Cancel and investigate
```

## After Init

Once `.intents/` is created:
- `/intents:status` - View the feature tree and status
- `/intents:plan [feature]` - Plan new features
- `/intents:implement [feature]` - Implement planned features

The `intents-system` skill activates automatically when `.intents/` is detected.

## Related Commands

- `/intents:status` - View the generated graph
- `/intents:plan` - Plan a new feature (creates graph node)
