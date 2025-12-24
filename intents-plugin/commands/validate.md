# /intents:validate

Detect and optionally fix structural issues in the feature graph.

## Usage

```
/intents:validate           # Report issues only
/intents:validate --fix     # Interactive fix prompts
```

## Implementation

When the user invokes `/intents:validate`, follow this process:

### Step 1: Locate and Parse Graph Files

Read all intents files from the project root:

```
.intents/graph.yaml        # Feature tree
.intents/capabilities.yaml # Capability definitions
.intents/tech.yaml         # Technology dependencies
```

If `.intents/` folder doesn't exist, respond:

```
No .intents/ folder found in this project.

Run /intents:init to bootstrap the feature graph.
```

### Step 2: Run All Validation Checks

Scan for the following issue types:

| Issue Type | Detection |
|------------|-----------|
| `MISSING_PLAN` | Feature has `plan:` field but referenced file doesn't exist |
| `UNDEFINED_CAPABILITY` | Feature uses capability not defined in capabilities.yaml |
| `ORPHANED_FEATURE` | Feature has no parent and isn't root |
| `BROKEN_CAPABILITY_REF` | Capability references tech not defined in tech.yaml |

**Detection algorithms:**

```
# MISSING_PLAN
for feature in graph.features:
  if feature.plan:
    if not fileExists(feature.plan):
      issues.add(MISSING_PLAN, feature.id, feature.plan)

# UNDEFINED_CAPABILITY
for feature in [graph.root] + graph.features:
  for cap in feature.capabilities:
    capName = cap.split(':')[0]  # Handle modes like "images:manage"
    if capName not in capabilities.yaml:
      issues.add(UNDEFINED_CAPABILITY, feature.id, capName)

# ORPHANED_FEATURE
for feature in graph.features:
  if not feature.parent:
    issues.add(ORPHANED_FEATURE, feature.id)
  elif feature.parent != 'root' and feature.parent not in graph.features:
    issues.add(ORPHANED_FEATURE, feature.id)

# BROKEN_CAPABILITY_REF
for cap in capabilities.yaml:
  for tech in cap.tech:
    if tech not in tech.yaml:
      issues.add(BROKEN_CAPABILITY_REF, cap.id, tech)
```

### Step 3: Report Mode (default)

If no `--fix` flag, display all issues in structured format:

```
/intents:validate

Validating .intents/ graph...

Found 3 issues:

1. MISSING_PLAN: ok-themes
   References: docs/plans/ok-themes/plan.md
   File not found

2. UNDEFINED_CAPABILITY: admin-galleries
   Uses: undefined-cap
   Not in capabilities.yaml

3. BROKEN_CAPABILITY_REF: images
   References tech: imaginary-service
   Not in tech.yaml

Run /intents:validate --fix to resolve interactively.
```

If no issues found:

```
/intents:validate

Validating .intents/ graph...

No issues found. Graph structure is valid.
```

### Step 4: Fix Mode (--fix)

If `--fix` flag provided, prompt for each issue:

```
/intents:validate --fix

Validating .intents/ graph...

Found 3 issues:

1. MISSING_PLAN: ok-themes
   References: docs/plans/ok-themes/plan.md
   File not found

   (r) Remove plan reference
   (s) Skip

   Choice:
```

Wait for user input, then apply the fix and continue to next issue.

## Issue Types and Fix Options

### MISSING_PLAN

**Detection:** Feature has `plan:` field but the referenced file doesn't exist on disk.

**Output:**
```
MISSING_PLAN: {feature-id}
References: {plan-path}
File not found

(r) Remove plan reference
(s) Skip
```

**Fix actions:**
- `(r) Remove plan reference` - Delete the `plan:` field from the feature in graph.yaml
- `(s) Skip` - Take no action, move to next issue

### UNDEFINED_CAPABILITY

**Detection:** Feature lists a capability in its `capabilities:` array that is not defined in capabilities.yaml.

**Output:**
```
UNDEFINED_CAPABILITY: {feature-id}
Uses: {capability-name}
Not in capabilities.yaml

(r) Remove from feature
(a) Add to capabilities.yaml
(s) Skip
```

**Fix actions:**
- `(r) Remove from feature` - Remove the capability from the feature's capabilities list in graph.yaml
- `(a) Add to capabilities.yaml` - Add a placeholder entry for the capability:
  ```yaml
  {capability-name}:
    name: {Capability Name}
    type: capability
    category: unknown
    intent: TODO - describe what this capability enables
  ```
- `(s) Skip` - Take no action, move to next issue

### ORPHANED_FEATURE

**Detection:** Feature has no `parent:` field, or its parent doesn't exist in the graph (and it's not the root node).

**Output:**
```
ORPHANED_FEATURE: {feature-id}
No valid parent (parent field missing or parent not found)

(r) Remove from graph
(p) Set parent
(s) Skip
```

**Fix actions:**
- `(r) Remove from graph` - Delete the feature entry from graph.yaml
- `(p) Set parent` - Prompt for parent feature ID:
  ```
  Enter parent feature ID (or 'root'):
  ```
  Then add `parent: {input}` to the feature
- `(s) Skip` - Take no action, move to next issue

### BROKEN_CAPABILITY_REF

**Detection:** Capability references a tech dependency in its `tech:` array that is not defined in tech.yaml.

**Output:**
```
BROKEN_CAPABILITY_REF: {capability-id}
References tech: {tech-name}
Not in tech.yaml

(r) Remove tech reference
(a) Add to tech.yaml
(s) Skip
```

**Fix actions:**
- `(r) Remove tech reference` - Remove the tech from the capability's tech list in capabilities.yaml
- `(a) Add to tech.yaml` - Add a placeholder entry for the tech:
  ```yaml
  {tech-name}:
    name: {Tech Name}
    type: tech
    category: unknown
    purpose: TODO - describe what this technology does
  ```
- `(s) Skip` - Take no action, move to next issue

## Fix Application

When applying fixes, make changes directly to the YAML files:

1. Read the current file content
2. Parse as YAML
3. Apply the modification
4. Write back with preserved formatting (comments, ordering)
5. Report success:

```
Choice: r
Removed plan reference from ok-themes
```

After all issues processed, show summary:

```
Validation complete. Fixed 2 issues, skipped 1.

Remaining issues (1):
  - ORPHANED_FEATURE: orphan-widget (skipped)

Run /intents:validate again to see current state.
```

If all fixed:

```
Validation complete. Fixed 3 issues, skipped 0.

Graph structure is now valid.
```

## Algorithm Reference

### Collecting All Issues

```
function validateGraph():
  issues = []

  # Load files
  graph = parseYaml('.intents/graph.yaml')
  capabilities = parseYaml('.intents/capabilities.yaml')
  tech = parseYaml('.intents/tech.yaml')

  # Check MISSING_PLAN
  for id, feature in graph.features:
    if feature.plan and not fileExists(feature.plan):
      issues.append({
        type: 'MISSING_PLAN',
        featureId: id,
        planPath: feature.plan
      })

  # Check UNDEFINED_CAPABILITY
  allFeatures = [('root', graph.root)] + list(graph.features.items())
  for id, feature in allFeatures:
    for cap in (feature.capabilities or []):
      capName = cap.split(':')[0]
      if capName not in capabilities:
        issues.append({
          type: 'UNDEFINED_CAPABILITY',
          featureId: id,
          capability: capName
        })

  # Check ORPHANED_FEATURE
  for id, feature in graph.features:
    if not feature.parent:
      issues.append({
        type: 'ORPHANED_FEATURE',
        featureId: id
      })
    elif feature.parent != 'root' and feature.parent not in graph.features:
      issues.append({
        type: 'ORPHANED_FEATURE',
        featureId: id,
        missingParent: feature.parent
      })

  # Check BROKEN_CAPABILITY_REF
  for capId, cap in capabilities:
    for techRef in (cap.tech or []):
      if techRef not in tech:
        issues.append({
          type: 'BROKEN_CAPABILITY_REF',
          capabilityId: capId,
          techRef: techRef
        })

  return issues
```

### Applying Fixes

```
function applyFix(issue, choice):
  switch issue.type:
    case 'MISSING_PLAN':
      if choice == 'r':
        graph.features[issue.featureId].plan = null
        writeYaml('.intents/graph.yaml', graph)
        return "Removed plan reference from " + issue.featureId

    case 'UNDEFINED_CAPABILITY':
      if choice == 'r':
        caps = graph.features[issue.featureId].capabilities
        caps.remove(issue.capability)
        writeYaml('.intents/graph.yaml', graph)
        return "Removed " + issue.capability + " from " + issue.featureId
      if choice == 'a':
        capabilities[issue.capability] = {
          name: titleCase(issue.capability),
          type: 'capability',
          category: 'unknown',
          intent: 'TODO - describe what this capability enables'
        }
        writeYaml('.intents/capabilities.yaml', capabilities)
        return "Added " + issue.capability + " to capabilities.yaml"

    case 'ORPHANED_FEATURE':
      if choice == 'r':
        del graph.features[issue.featureId]
        writeYaml('.intents/graph.yaml', graph)
        return "Removed " + issue.featureId + " from graph"
      if choice == 'p':
        parentId = prompt("Enter parent feature ID (or 'root'): ")
        graph.features[issue.featureId].parent = parentId
        writeYaml('.intents/graph.yaml', graph)
        return "Set parent of " + issue.featureId + " to " + parentId

    case 'BROKEN_CAPABILITY_REF':
      if choice == 'r':
        caps = capabilities[issue.capabilityId].tech
        caps.remove(issue.techRef)
        writeYaml('.intents/capabilities.yaml', capabilities)
        return "Removed " + issue.techRef + " from " + issue.capabilityId
      if choice == 'a':
        tech[issue.techRef] = {
          name: titleCase(issue.techRef),
          type: 'tech',
          category: 'unknown',
          purpose: 'TODO - describe what this technology does'
        }
        writeYaml('.intents/tech.yaml', tech)
        return "Added " + issue.techRef + " to tech.yaml"
```

## Examples

### Report Mode - Issues Found

```
> /intents:validate

Validating .intents/ graph...

Found 2 issues:

1. MISSING_PLAN: ok-themes
   References: docs/plans/ok-themes/plan.md
   File not found

2. UNDEFINED_CAPABILITY: admin-galleries
   Uses: undefined-cap
   Not in capabilities.yaml

Run /intents:validate --fix to resolve interactively.
```

### Report Mode - No Issues

```
> /intents:validate

Validating .intents/ graph...

No issues found. Graph structure is valid.
```

### Fix Mode - Interactive

```
> /intents:validate --fix

Validating .intents/ graph...

Found 2 issues:

1. MISSING_PLAN: ok-themes
   References: docs/plans/ok-themes/plan.md
   File not found

   (r) Remove plan reference
   (s) Skip

   Choice: r
   Removed plan reference from ok-themes

2. UNDEFINED_CAPABILITY: admin-galleries
   Uses: undefined-cap
   Not in capabilities.yaml

   (r) Remove from feature
   (a) Add to capabilities.yaml
   (s) Skip

   Choice: a
   Added undefined-cap to capabilities.yaml

Validation complete. Fixed 2 issues, skipped 0.

Graph structure is now valid.
```

### Fix Mode - With Skips

```
> /intents:validate --fix

Validating .intents/ graph...

Found 3 issues:

1. MISSING_PLAN: ok-themes
   References: docs/plans/ok-themes/plan.md
   File not found

   (r) Remove plan reference
   (s) Skip

   Choice: s
   Skipped

2. ORPHANED_FEATURE: floating-widget
   No valid parent (parent field missing or parent not found)

   (r) Remove from graph
   (p) Set parent
   (s) Skip

   Choice: p
   Enter parent feature ID (or 'root'): goodies
   Set parent of floating-widget to goodies

3. BROKEN_CAPABILITY_REF: custom-auth
   References tech: magic-sso
   Not in tech.yaml

   (r) Remove tech reference
   (a) Add to tech.yaml
   (s) Skip

   Choice: r
   Removed magic-sso from custom-auth

Validation complete. Fixed 2 issues, skipped 1.

Remaining issues (1):
  - MISSING_PLAN: ok-themes (skipped)

Run /intents:validate again to see current state.
```

## Error Handling

### No .intents/ folder

```
No .intents/ folder found in this project.

Run /intents:init to bootstrap the feature graph.
```

### Invalid YAML syntax

```
Error parsing .intents/graph.yaml

Problem: Invalid YAML syntax
Line: 15

Fix the YAML syntax and try again.
```

### Missing required files

```
Error: .intents/capabilities.yaml not found

The validate command requires all intents files:
  - .intents/graph.yaml (found)
  - .intents/capabilities.yaml (missing)
  - .intents/tech.yaml (found)

Run /intents:init --force to regenerate missing files.
```

### Fix failed

```
Error applying fix: Could not write to .intents/graph.yaml

Check file permissions and try again.
```

## Related Commands

- `/intents:status` - View graph state (also shows warnings)
- `/intents:init` - Bootstrap or regenerate graph files
- `/intents:plan <feature>` - Plan a new feature (creates valid graph node)
