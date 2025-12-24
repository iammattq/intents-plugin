---
name: intents-system
description: Graph schema teaching and inheritance rules. Activated when .intents/ folder detected. Teaches how to read, write, and maintain the feature graph.
---

# Intents System

You are working with a codebase that uses the `.intents/` graph system to track features, capabilities, and architecture. This skill teaches you the schema and rules for working with it.

## Overview

The `.intents/` folder contains four YAML files that describe the system architecture:

| File | Purpose | Priority |
|------|---------|----------|
| `graph.yaml` | Feature tree with status and capabilities | High - read first |
| `capabilities.yaml` | Reusable interfaces features consume | High - understand what's available |
| `entities.yaml` | Domain models with state | Medium - context for implementation |
| `tech.yaml` | Implementation dependencies | Low - implementation details |

## When to Read vs Write

| Phase | Access | What Changes |
|-------|--------|--------------|
| Research | READ | Nothing - gather context from graph |
| Plan | WRITE | Create feature node, status: `planned` |
| Implement | WRITE | Update status: `in-progress` → `implemented` |
| Query | READ | Check current state, find out-of-sync features |

## Schema Reference

### graph.yaml

The feature tree. Shows what the system IS.

```yaml
root:
  name: Project Name
  type: feature
  status: implemented
  intent: What this project does for users
  capabilities:
    - capability-name
    - capability-name:mode

features:
  feature-id:
    name: Feature Name
    type: feature
    status: new | planned | in-progress | implemented | broken
    intent: User-facing value this feature provides
    parent: parent-feature-id
    plan: docs/plans/feature-id/plan.md  # optional
    capabilities:
      - capability-name
      - capability-name:mode
    children:
      - child-feature-id
```

**Status Values:**
- `new` - Just identified, not yet analyzed
- `planned` - Has a PLAN.md, ready for implementation
- `in-progress` - Currently being implemented
- `implemented` - Working in production
- `broken` - Was implemented, now failing

### capabilities.yaml

Reusable interfaces that features consume.

```yaml
capability-id:
  name: Capability Name
  type: capability
  category: ui | storage | media | auth | content | export | sync
  intent: What this enables for features
  adr: docs/decisions/XXX-decision.md  # optional
  tech:
    - tech-dependency-id
  interface: |
    Functions, hooks, or APIs available
  modes:  # optional
    mode-name: |
      What's available in this mode
```

**Categories:**
- `ui` - Design system, theming, components
- `storage` - Database, localStorage, persistence
- `media` - Images, files, canvas, video
- `auth` - Authentication, authorization
- `content` - MDX, rich text, content authoring
- `export` - JSON, CSS, PDF generation
- `sync` - Cross-tab, realtime coordination

### entities.yaml

Domain models with state that triggers capabilities.

```yaml
entity-id:
  name: EntityName
  type: entity
  capabilities:
    - capability-name  # invoked based on state
  state:
    - field: type
```

### tech.yaml

Implementation dependencies (lowest priority for context).

```yaml
tech-id:
  name: Tech Name
  type: tech
  category: database | cloud | auth | ui | processing | state
  config: path/to/config  # optional
  docs: docs/guides/guide.md  # optional
  purpose: What it does  # use if no docs
```

## Inheritance Rules

Features inherit capabilities from their parent:

```yaml
admin:
  capabilities:
    - session-auth
    - persistence:read-write

admin-galleries:
  parent: admin
  capabilities:
    - images:manage
    - upload
  # Effective capabilities:
  # - session-auth (inherited)
  # - persistence:read-write (inherited)
  # - images:manage
  # - upload
```

**Rules:**
1. Children inherit all parent capabilities
2. Children can add additional capabilities
3. Modes are inherited if parent uses same capability
4. To override a parent capability mode, specify explicitly

## Capability Modes

Some capabilities have modes that define access level:

```yaml
# In capabilities.yaml
images:
  modes:
    consume: |
      buildImageUrl(key, size)
      useImage() hook
    manage: |
      processImageUpload()
      deleteObject()

# In graph.yaml - using modes
photography:
  capabilities:
    - images:consume  # Can display images

admin-galleries:
  capabilities:
    - images:manage   # Can upload/delete images
```

If no mode specified, assumes full access.

## Working with the Graph

### Reading for Context

When researching or planning, read in this order:
1. `graph.yaml` - Understand feature structure
2. `capabilities.yaml` - Know what's available
3. Look up specific features/capabilities as needed

**Example queries:**
- "What capabilities does admin-galleries have?" → Read graph.yaml, check parent chain
- "How does authentication work?" → Read capabilities.yaml session-auth entry
- "What tech does images capability use?" → Read capabilities.yaml, check tech list

### Creating a Feature Node

When planning a new feature, add to graph.yaml:

```yaml
new-feature:
  name: New Feature Name
  type: feature
  status: planned
  intent: What users get from this
  parent: parent-feature
  plan: docs/plans/new-feature/plan.md
  capabilities:
    - capability-1
    - capability-2:mode
```

### Updating Status

During implementation:

```yaml
# Starting implementation
new-feature:
  status: in-progress  # Changed from planned

# After implementation complete
new-feature:
  status: implemented  # Changed from in-progress

# If tests fail later
new-feature:
  status: broken  # Flag for investigation
```

## Examples

### Feature with Inherited Capabilities

```yaml
# Admin has core capabilities
admin:
  capabilities:
    - session-auth
    - persistence:read-write

# Gallery management inherits and adds more
admin-galleries:
  parent: admin
  capabilities:
    - images:manage
    - upload
    - reorder
  # Effective: session-auth, persistence:read-write, images:manage, upload, reorder
```

### Capability with Modes

```yaml
# Persistence has read and read-write modes
persistence:
  modes:
    read: |
      prisma.findMany()
      prisma.findUnique()
    read-write: |
      Full CRUD operations
      prisma.$transaction()

# Public features get read-only
photography:
  capabilities:
    - persistence:read

# Admin features get full access
admin:
  capabilities:
    - persistence:read-write
```

### Entity with Conditional Capability

```yaml
# Project entity can trigger password protection
project:
  name: Project
  capabilities:
    - work-password  # Invoked when protected === true
  state:
    - protected: boolean
    - published: boolean
```

## Common Patterns

### Adding a New Capability

1. Define in capabilities.yaml with interface
2. List tech dependencies
3. Reference from features that use it

### Adding a New Feature

1. Identify parent feature (or root)
2. Add node to graph.yaml with status: new
3. When planning, update status: planned and add plan path
4. During implementation, update status: in-progress
5. When done, update status: implemented

### Checking Feature Status

Look for:
- `status: implemented` - Should be working
- `status: broken` - Needs investigation
- No status or `status: new` - Not analyzed yet
- `status: planned` - Has plan, not started
- `status: in-progress` - Being worked on

## Graph Hygiene

**Keep in sync:**
- When you implement a feature, update the status
- When you add capabilities to code, add them to the graph
- When tests fail for a feature, mark it broken

**Don't over-complicate:**
- Not every helper function needs a capability
- Capabilities are reusable interfaces, not implementation details
- Features are user-facing value, not internal modules
