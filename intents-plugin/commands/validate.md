---
description: Detect and fix structural issues in feature graph. Use for graph maintenance.
argument-hint: [--fix]
---

# /intents:validate

Detect and optionally fix structural issues in the feature graph.

## Usage

```
/intents:validate        # Report issues only
/intents:validate --fix  # Interactive fix prompts
```

## Prerequisites

Read all `.intents/` files:
- `graph.yaml` - Feature tree
- `capabilities.yaml` - Capability definitions
- `tech.yaml` - Technology dependencies

If `.intents/` doesn't exist: Tell user to run `/intents:init`.

## Issue Types

| Issue | Detection |
|-------|-----------|
| `MISSING_PLAN` | Feature has `plan:` field but file doesn't exist |
| `UNDEFINED_CAPABILITY` | Feature uses capability not in capabilities.yaml |
| `ORPHANED_FEATURE` | Feature has no valid parent (missing or not found) |
| `BROKEN_CAPABILITY_REF` | Capability references tech not in tech.yaml |

## Report Mode (default)

List all issues found:

```
Found 2 issues:

1. MISSING_PLAN: ok-themes
   References: docs/plans/ok-themes/plan.md
   File not found

2. UNDEFINED_CAPABILITY: admin-galleries
   Uses: custom-auth
   Not in capabilities.yaml

Run /intents:validate --fix to resolve.
```

If no issues: `Graph structure is valid.`

## Fix Mode (--fix)

Prompt for each issue with fix options:

### MISSING_PLAN
```
(r) Remove plan reference
(s) Skip
```

### UNDEFINED_CAPABILITY
```
(r) Remove from feature
(a) Add to capabilities.yaml
(s) Skip
```

### ORPHANED_FEATURE
```
(r) Remove from graph
(p) Set parent [prompts for parent ID]
(s) Skip
```

### BROKEN_CAPABILITY_REF
```
(r) Remove tech reference
(a) Add to tech.yaml
(s) Skip
```

## Summary

After all issues processed:

```
Validation complete. Fixed 2 issues, skipped 1.

Remaining issues (1):
  - MISSING_PLAN: ok-themes (skipped)
```

Or if all fixed: `Graph structure is now valid.`
