# Intents Plugin for Claude Code

A plugin that teaches Claude Code the R-P-I (Research-Plan-Implement) workflow with graph-based architecture tracking via `.intents/`.

## The Problem

Claude Code works brilliantly in the "smart zone" (roughly the first 40% of context), but performance degrades on large features. The R-P-I workflow with `.intents/` graph solves this by:

1. **Externalizing architecture** - The graph captures what the system IS
2. **Chunked implementation** - Plans break work into context-sized pieces
3. **Status tracking** - Progress persists across sessions via MEMORY.md and graph status

This plugin automates the orchestration that was previously manual.

## Installation

### Option 1: Copy to Project

Copy the `intents-plugin/` folder to your project root:

```bash
cp -r intents-plugin/ /path/to/your/project/
```

### Option 2: Clone and Link

Clone this repo and symlink to your projects:

```bash
git clone https://github.com/your-org/intents-plugin.git
ln -s /path/to/intents-plugin /path/to/your/project/intents-plugin
```

### Verify Installation

The plugin is detected when Claude Code sees the `.claude-plugin/plugin.json` file in your project. After installation:

1. Restart Claude Code (or open a new conversation)
2. The `intents-system` skill will activate when `.intents/` exists
3. Commands become available: `/intents:init`, `/intents:status`, `/intents:plan`, `/intents:implement`

## Quick Start

### 1. Bootstrap your project

```
/intents:init
```

This analyzes your codebase and generates the `.intents/` folder with:
- `graph.yaml` - Feature tree with status
- `capabilities.yaml` - Reusable interfaces (auth, storage, etc.)
- `entities.yaml` - Domain models
- `tech.yaml` - Technology dependencies

### 2. Check the graph

```
/intents:status
```

See the feature tree, status of each feature, and any sync warnings.

### 3. Plan a new feature

```
/intents:plan user-preferences --parent admin
```

This runs the full R-P workflow:
- Brainstorm approaches
- **Classify as new feature or enhancement** (you confirm)
- Research codebase for fit
- Research external tech if needed
- Refine via advocate/critic debate
- Create PLAN.md with chunked phases
- Add feature node to graph (new features only)

**Enhancement shortcut:** If you already know this enhances an existing feature:
```
/intents:plan sorting --enhance admin-galleries
```
This skips classification and creates the plan at `docs/plans/admin-galleries/sorting/` without a graph node.

### 4. Implement the feature

```
/intents:implement user-preferences
```

For enhancements, use the path format:
```
/intents:implement admin-galleries/sorting
```

This orchestrates implementation:
- Generate test specs (TDD)
- Implement chunk by chunk
- Pause at phase gates for manual testing
- Run code review, security audit, accessibility check
- Update graph status when complete

## Commands

| Command | Description |
|---------|-------------|
| `/intents:init` | Bootstrap `.intents/` from existing codebase |
| `/intents:status` | Show feature tree with status |
| `/intents:status <feature>` | Show detail for specific feature (includes enhancements) |
| `/intents:plan <feature>` | Run R-P workflow, create plan + graph node |
| `/intents:implement <feature>` | Implement with status tracking |
| `/intents:implement <parent>/<enhancement>` | Implement an enhancement plan |

### Command Options

**`/intents:plan`**
- `--parent <feature>` - Specify parent for inheritance
- `--enhance <parent>` - Create as enhancement (no graph node, nested path)
- `--skip-brainstorm` - Skip ideation (idea already clear)
- `--skip-research` - Skip codebase/tech research

**`/intents:implement`**
- `--skip-tests` - Skip test-spec generation
- `--skip-review` - Skip code review
- `--skip-security` - Skip security audit
- `--skip-a11y` - Skip accessibility review

## Workflow Overview

```
                    +------------------+
                    |  /intents:init   |
                    |  (Bootstrap)     |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    | .intents/ folder |
                    | graph.yaml       |
                    +--------+---------+
                             |
              +--------------+--------------+
              |                             |
              v                             v
     +------------------+          +------------------+
     | /intents:plan    |          | /intents:status  |
     | (Research-Plan)  |          | (Query)          |
     +--------+---------+          +------------------+
              |
              | Creates PLAN.md
              | Adds graph node
              v
     +------------------+
     |/intents:implement|
     | (Implementation) |
     +--------+---------+
              |
              | Updates status:
              | planned -> in-progress -> implemented
              v
     +------------------+
     | Feature Complete |
     +------------------+
```

## Graph Schema

The `.intents/` folder contains four YAML files that form the architectural graph:

### graph.yaml - Feature Tree

```yaml
root:
  name: My Project
  type: feature
  status: implemented
  intent: What this project does for users
  capabilities:
    - persistence:read

features:
  admin:
    name: Admin Dashboard
    type: feature
    status: implemented
    intent: Manage content and settings
    parent: root
    capabilities:
      - session-auth
      - persistence:read-write

  admin-galleries:
    name: Gallery Management
    type: feature
    status: implemented
    intent: Create and organize photo galleries
    parent: admin
    capabilities:
      - images:manage
      - upload
```

**Key concepts:**
- **Status**: `new` | `planned` | `in-progress` | `implemented` | `broken`
- **Inheritance**: Children inherit parent capabilities (admin-galleries inherits session-auth from admin)
- **Capability modes**: `capability:mode` syntax (e.g., `images:consume` vs `images:manage`)

### capabilities.yaml - Reusable Interfaces

```yaml
session-auth:
  name: Session Authentication
  type: capability
  category: auth
  intent: Protect routes requiring login
  tech:
    - next-auth
  interface: |
    useSession() - client auth state
    getServerSession() - server auth check

images:
  name: Image Processing
  type: capability
  category: media
  intent: Upload, process, serve images
  tech:
    - s3
    - sharp
  modes:
    consume: Display images (read-only)
    manage: Upload, delete, reorder (write)
```

### entities.yaml - Domain Models

```yaml
Gallery:
  name: Gallery
  type: entity
  capabilities:
    - images:manage
  state:
    - published: boolean
    - images: Image[]
```

### tech.yaml - Technology Dependencies

```yaml
s3:
  name: AWS S3
  type: tech
  category: cloud
  config: src/lib/s3.ts
  purpose: Object storage for images

next-auth:
  name: NextAuth.js
  type: tech
  category: auth
  config: src/app/api/auth/[...nextauth]/route.ts
  docs: docs/guides/auth.md
```

## Agents Included

This plugin includes 10 agents for the complete R-P-I workflow:

| Agent | Phase | Purpose |
|-------|-------|---------|
| `codebase-analyzer` | Bootstrap | Analyze codebase, generate initial graph |
| `codebase-researcher` | Research | Explore internal codebase for context |
| `technical-researcher` | Research | Research external docs and APIs |
| `feature-brainstorm` | Research | Divergent ideation for new features |
| `feature-refine` | Research | Advocate/critic debate to refine approach |
| `feature-plan` | Plan | Create PLAN.md, add graph node |
| `test-spec` | Plan/Implement | Generate TDD test specifications |
| `feature-implementer` | Implement | Orchestrate chunk-by-chunk implementation |
| `code-reviewer` | Implement | Validate code quality and patterns |
| `security-auditor` | Implement | OWASP security review |
| `accessibility-reviewer` | Implement | WCAG compliance check |

## Skills Included

| Skill | Purpose |
|-------|---------|
| `intents-system` | Teaches Claude the graph schema, when to read/write |
| `feature-brainstorm` | Divergent ideation patterns for research phase |

## Plan Structure

When you run `/intents:plan`, it creates:

```
docs/plans/<feature>/
  PLAN.md    # Problem, goals, phases, chunks
  MEMORY.md  # Session progress, decisions, blockers
```

Plans are chunked for context management:

```
## Phase 1: Foundation
| Chunk | Scope | Files |
|-------|-------|-------|
| 1A | Types + config | 2 files |
| 1B | Page route | 1 file |
| 1C | Core component | 2 files |

Ship Criteria:
- Route accessible at /feature
- Core UI renders
```

Each phase ends with a **phase gate** for manual testing before continuing.

## Status Flow

```
new         - Feature identified but not analyzed
     |
     v (after /intents:plan)
planned     - Has PLAN.md, ready for implementation
     |
     v (start of /intents:implement)
in-progress - Currently being implemented
     |
     +--> implemented  (success)
     |
     +--> broken       (failure - tests or quality checks failed)
           |
           v (retry /intents:implement after fixing)
           in-progress
```

## Directory Structure

```
intents-plugin/
  .claude-plugin/
    plugin.json           # Plugin manifest

  agents/
    codebase-analyzer/AGENT.md
    codebase-researcher/AGENT.md
    technical-researcher/AGENT.md
    feature-refine/AGENT.md
    feature-plan/AGENT.md
    feature-implementer/AGENT.md
    test-spec/AGENT.md
    code-reviewer/AGENT.md
    security-auditor/AGENT.md
    accessibility-reviewer/AGENT.md

  skills/
    intents-system/SKILL.md
    feature-brainstorm/SKILL.md

  commands/
    init.md
    status.md
    plan.md
    implement.md

  templates/
    graph.yaml
    capabilities.yaml
    entities.yaml
    tech.yaml

  README.md
```

## Best Practices

### When to use this plugin

- **Large features** that span multiple sessions
- **Complex architecture** that benefits from explicit mapping
- **Team projects** where the graph serves as documentation
- **Refactoring** where you need to understand dependencies

### When NOT to use it

- **Quick fixes** - Just edit the code directly
- **Trivial features** - Overhead not worth it for small changes
- **Exploratory work** - R-P-I assumes you know what you're building

### Tips

1. **Review generated graph** - The analyzer makes educated guesses; correct any errors
2. **Keep graph in sync** - Update manually if you make changes outside the workflow
3. **Use phase gates** - Don't skip manual testing between phases
4. **Trust the chunking** - Smaller chunks keep Claude in the smart zone

### Node vs Enhancement

Think of the graph as a **subway map** - it shows major destinations, not every street corner.

**Create a graph node when:**
- Building a new user-facing page or flow
- Adding a distinct domain area
- Work is described as "Build X" or "Work on X"

**Use enhancement (`--enhance`) when:**
- Adding functionality to an existing feature
- Work is described as "Add X to Y" or "Improve Y"
- The change is a "neighborhood improvement", not a new destination

**Examples:**
| Idea | Type | Why |
|------|------|-----|
| "User preferences page" | New feature | New destination |
| "Add sorting to galleries" | Enhancement | Adds to existing feature |
| "Dark mode toggle" | Enhancement (usually) | Adds to settings/UI |
| "Payment system" | New feature | New domain area |

Enhancement plans live at `docs/plans/<parent>/<enhancement>/` and don't clutter the graph. Use `/intents:status <feature>` to see enhancements for a specific feature.

## Troubleshooting

### "No .intents/ folder found"

Run `/intents:init` to bootstrap the graph.

### Feature not found in graph

Either:
1. Run `/intents:plan <feature>` to create it
2. Add manually to `.intents/graph.yaml`

### Graph out of sync

Use `/intents:status` to check for warnings, then:
1. Update status values manually in `graph.yaml`
2. Or run `/intents:init` to regenerate (will overwrite)

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
