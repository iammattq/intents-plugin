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

Display hierarchical tree with status indicators.

**Note:** Tree view shows graph nodes only. Enhancements are not displayed here (they're "neighborhood detail", not "subway stops"). Use `status <feature>` to see enhancements for a specific feature.

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

Enhancements: [list or none]
```

**Inheritance:** Walk up parent chain, collect all capabilities. Children inherit all parent capabilities.

### Enhancement Discovery

When showing detail for a feature, scan filesystem for enhancement plans:

1. Look for `docs/plans/<feature-id>/*/PLAN.md`
2. Each subdirectory with a PLAN.md is an enhancement
3. Display as sub-items under "Enhancements"

```
Enhancements:
  - sorting [planned] -> docs/plans/admin-galleries/sorting/PLAN.md
  - batch-upload [implemented]
```

Read enhancement status from PLAN.md frontmatter if present, otherwise show as "planned".

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
