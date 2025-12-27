---
description: Show feature graph status with capability inheritance. Use to view project structure.
argument-hint: [feature-id]
---

# /intents:status

Show the current state of the feature graph.

## Usage

```
/intents:status              # Full feature tree
/intents:status [feature-id] # Detail for specific feature
```

## Prerequisites

Read `.intents/graph.yaml` and `.intents/capabilities.yaml`.

If `.intents/` doesn't exist: Tell user to run `/intents:init`.

## Tree View (no args)

Display hierarchical tree with status indicators:

```
Features:
root (Project Name) [implemented]
|-- feature-a [implemented]
|   +-- sub-feature [planned] -> docs/plans/sub/PLAN.md
+-- feature-b [in-progress]

Summary:
  Implemented: 5 | Planned: 2 | In Progress: 1 | Broken: 0
```

**Rules:**
- `|--` intermediate, `+--` last child
- `[status]` after name
- `-> plan/path` for planned features with plan field
- Prefix broken features with `!`

## Detail View (with feature-id)

Show feature details including capability inheritance:

```
Feature: feature-id

Status: implemented
Intent: What this feature does
Parent: parent-id

Capabilities (direct): [from feature]
Capabilities (inherited): [from ancestors]

Children: [list or none]
Siblings: [other children of same parent]
```

**Inheritance:** Walk up parent chain, collect all capabilities. Children inherit all parent capabilities.

## Sync Warnings

Append warnings if found:
- Missing plan file (referenced but doesn't exist)
- Undefined capability (not in capabilities.yaml)
- Orphaned feature (no parent, not root)

```
---
Warnings (1):
  - feature-id: Plan file not found

Run /intents:validate --fix to resolve.
```

## Status Values

| Status | Meaning |
|--------|---------|
| `new` | Identified, not analyzed |
| `planned` | Has PLAN.md, ready to implement |
| `in-progress` | Currently implementing |
| `implemented` | Working |
| `broken` | Was working, now failing |
