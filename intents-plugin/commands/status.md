# /intents:status

Show the current state of the feature graph with status indicators and capability inheritance.

## Usage

```
/intents:status              # Show full feature tree
/intents:status [feature-id] # Show detail for specific feature
```

## Implementation

When the user invokes `/intents:status`, follow this process:

### Step 1: Locate and Parse Graph Files

Read the intents files from the project root:

```
.intents/graph.yaml        # Feature tree
.intents/capabilities.yaml # Capability definitions
```

If `.intents/` folder doesn't exist, respond:

```
No .intents/ folder found in this project.

Run /intents:init to bootstrap the feature graph.
```

### Step 2: Build Feature Tree

Parse `graph.yaml` to extract:

1. **Root node** - The `root:` entry at top level
2. **Features** - All entries under `features:`
3. **Parent-child relationships** - From `parent:` and `children:` fields

Build the tree structure by:
1. Start with root node
2. For each feature, find its parent
3. Construct nested tree (parent -> children)

### Step 3: Compute Capability Inheritance

For each feature, compute effective capabilities:

1. **Direct capabilities** - Listed in the feature's `capabilities:` field
2. **Inherited capabilities** - Walk up parent chain, collect all parent capabilities

Parse capability modes (e.g., `persistence:read` vs `persistence:read-write`):
- `capability:mode` format indicates specific mode
- Plain `capability` inherits all modes

### Step 4: Display Tree (Default View)

If no feature-id argument provided, show the full tree:

```
Intents Status

Features:
root (Portfolio) [implemented]
|-- home [implemented]
|-- work [implemented]
|   |-- work-list [implemented]
|   |-- work-detail [implemented]
|   +-- work-timeline [implemented]
|-- photography [implemented]
|   |-- gallery-list [implemented]
|   +-- gallery-detail [implemented]
|-- journal [implemented]
|   |-- journal-list [implemented]
|   +-- journal-detail [implemented]
|-- design-system-docs [implemented]
|   |-- component-catalog [implemented]
|   |-- component-detail [implemented]
|   +-- foundations [implemented]
|-- goodies [implemented]
|   |-- cardopia [implemented]
|   |-- ok-themes [planned] -> docs/plans/ok-themes/plan.md
|   |-- dot-matrix [implemented]
|   +-- typester [implemented]
+-- admin [implemented]
    |-- admin-dashboard [implemented]
    |-- admin-galleries [implemented]
    |-- admin-journal [implemented]
    |   |-- journal-editor [implemented]
    |   +-- tag-manager [implemented]
    +-- admin-images [implemented]

Summary:
  Implemented: 24
  Planned: 1
  In Progress: 0
  Broken: 0

Legend: [implemented] | [planned] -> plan link | [in-progress] | [broken] | [new]
```

**Display rules:**
- Use `|--` for intermediate children, `+--` for last child
- Show status in brackets after name
- For `planned` status with a `plan:` field, show `-> plan/path`
- For broken status, prefix with "!" (e.g., "! broken-feature [broken]")

### Step 5: Display Detail View (with feature-id)

If a feature-id is provided (e.g., `/intents:status admin-galleries`), show detailed view:

```
Feature: admin-galleries

Name: Gallery Management
Status: implemented
Intent: Create, edit, organize photo galleries
Parent: admin
Plan: (none)

Capabilities (direct):
  - images:manage
  - upload
  - reorder

Capabilities (inherited from admin):
  - session-auth
  - persistence:read-write

Effective Capabilities (all):
  - session-auth
  - persistence:read-write
  - images:manage
  - upload
  - reorder

Children:
  (none)

Related:
  - Parent: admin (Admin)
  - Siblings: admin-dashboard, admin-journal, admin-images
```

If feature not found:

```
Feature 'bad-id' not found in graph.

Available features:
  - admin-galleries
  - admin-journal
  - ...

Use /intents:status to see full tree.
```

### Step 6: Sync Checking (Warnings)

Check for potential issues and append warnings if found:

**Missing plan file:**
```
Warning: Feature 'ok-themes' references plan at docs/plans/ok-themes/plan.md but file not found.
```

**Undefined capability:**
```
Warning: Feature 'admin-galleries' uses capability 'undefined-cap' not defined in capabilities.yaml.
```

**Orphaned feature (no parent, not root):**
```
Warning: Feature 'orphan-feature' has no parent defined and is not root.
```

Display warnings at the end of output:

```
---
Warnings (2):
  - ok-themes: Plan file not found
  - admin-galleries: Undefined capability 'undefined-cap'

Run /intents:validate --fix to resolve these issues.
```

## Status Values

| Status | Display | Meaning |
|--------|---------|---------|
| `new` | `[new]` | Identified but not analyzed |
| `planned` | `[planned]` | Has PLAN.md, ready for implementation |
| `in-progress` | `[in-progress]` | Currently being implemented |
| `implemented` | `[implemented]` | Working in production |
| `broken` | "! [broken]" | Was implemented, now failing |

## Algorithm Reference

### Building the Tree

```
function buildTree(graph):
  root = graph.root
  features = graph.features

  # Create lookup by ID
  nodes = { 'root': root }
  for id, feature in features:
    nodes[id] = feature

  # Build children arrays
  for id, node in nodes:
    node.children = []

  for id, feature in features:
    parentId = feature.parent or 'root'
    if parentId in nodes:
      nodes[parentId].children.append(id)

  return nodes['root']
```

### Computing Inherited Capabilities

```
function getInheritedCapabilities(featureId, graph):
  feature = graph.features[featureId]
  if not feature.parent:
    return []

  parentId = feature.parent
  if parentId == 'root':
    parent = graph.root
  else:
    parent = graph.features[parentId]

  # Get parent's direct + inherited
  parentCaps = parent.capabilities or []
  grandparentCaps = getInheritedCapabilities(parentId, graph)

  return unique(parentCaps + grandparentCaps)
```

### Rendering the Tree

```
function renderTree(node, prefix="", isLast=true):
  connector = "+--" if isLast else "|--"
  status = formatStatus(node.status)
  planLink = " -> " + node.plan if node.status == "planned" and node.plan else ""

  print(prefix + connector + " " + node.name + " " + status + planLink)

  children = node.children
  for i, child in enumerate(children):
    isChildLast = (i == len(children) - 1)
    newPrefix = prefix + ("    " if isLast else "|   ")
    renderTree(child, newPrefix, isChildLast)
```

## Examples

### Tree View

```
> /intents:status

Intents Status

Features:
root (Portfolio) [implemented]
|-- home [implemented]
|-- work [implemented]
|   |-- work-list [implemented]
|   |-- work-detail [implemented]
|   +-- work-timeline [implemented]
+-- admin [implemented]
    |-- admin-dashboard [implemented]
    +-- admin-galleries [implemented]

Summary:
  Implemented: 8
  Planned: 0
  In Progress: 0
  Broken: 0
```

### Detail View

```
> /intents:status admin-galleries

Feature: admin-galleries

Name: Gallery Management
Status: implemented
Intent: Create, edit, organize photo galleries
Parent: admin
Plan: (none)

Capabilities (direct):
  - images:manage
  - upload
  - reorder

Capabilities (inherited from admin):
  - session-auth
  - persistence:read-write

Effective Capabilities (all):
  - session-auth
  - persistence:read-write
  - images:manage
  - upload
  - reorder

Children:
  (none)

Related:
  - Parent: admin (Admin)
  - Siblings: admin-dashboard, admin-journal, admin-images
```

### With Warnings

```
> /intents:status

Intents Status

Features:
root (Portfolio) [implemented]
+-- goodies [implemented]
    +-- ok-themes [planned] -> docs/plans/ok-themes/plan.md

Summary:
  Implemented: 1
  Planned: 1

---
Warnings (1):
  - ok-themes: Plan file 'docs/plans/ok-themes/plan.md' not found

Run /intents:validate --fix to resolve these issues.
```

## Next Steps After Status

Based on what you see:

- **Feature is `new`?** - Run `/intents:plan [feature]` to create a plan
- **Feature is `planned`?** - Run `/intents:implement [feature]` to implement
- **Feature is `broken`?** - Investigate, fix, update status manually
- **Want to add a feature?** - Add to `graph.yaml` or run `/intents:plan [new-feature]`
- **Capability missing?** - Add to `.intents/capabilities.yaml`

## Error Handling

### No .intents/ folder

```
No .intents/ folder found in this project.

Run /intents:init to bootstrap the feature graph.
```

### Feature not found

```
Feature 'bad-feature-id' not found in graph.

Available features:
  - admin
  - admin-galleries
  - admin-journal
  - home
  - work

Use /intents:status to see full tree.
```

### Invalid graph.yaml

```
Error parsing .intents/graph.yaml

Problem: Missing 'root' entry
Line: 1

Fix the YAML syntax and try again.
```

## Related Commands

- `/intents:init` - Bootstrap graph if it doesn't exist
- `/intents:plan <feature>` - Plan a new feature
- `/intents:implement <feature>` - Implement a planned feature
- `/intents:validate` - Detect and fix structural issues
