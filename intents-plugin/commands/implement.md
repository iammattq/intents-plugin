# /intents:implement

Implement a planned feature with full workflow orchestration and graph status tracking.

## Usage

```
/intents:implement <feature-id>
/intents:implement <path-to-plan>
```

**Examples:**
```
/intents:implement ok-themes
/intents:implement docs/plans/ok-themes/
```

## Prerequisites

Before running this command:

1. **Feature must exist in graph** - Run `/intents:plan` first
2. **PLAN.md must exist** - The feature needs a plan with chunks defined
3. **Status should be `planned`** (or `broken` for retry)

## What This Command Does

1. Verifies feature exists in `.intents/graph.yaml`
2. Verifies PLAN.md exists for the feature
3. Updates graph status to `in-progress`
4. Orchestrates the full implementation workflow
5. Updates graph status to `implemented` (or `broken` on failure)

## Workflow Steps

### Step 1: Validate Feature

Check that the feature is ready for implementation:

```
Read .intents/graph.yaml
Find feature node by ID
Verify PLAN.md exists at the path specified in graph (or default path)
```

**If feature not found:**
```
Feature 'feature-id' not found in .intents/graph.yaml.

Run `/intents:plan feature-id` to create a plan first.
```

**If PLAN.md missing:**
```
Feature 'feature-id' exists but has no PLAN.md.

Expected: docs/plans/feature-id/PLAN.md

Run `/intents:plan feature-id` to create the plan.
```

### Step 2: Update Graph Status - Start

Update `.intents/graph.yaml`:
```yaml
feature-id:
  status: in-progress  # Changed from planned
```

Report:
```
Graph Status Update:
  Feature: feature-id
  Status: planned → in-progress
```

### Step 3: Test Spec (TDD)

**If test specs don't exist**, spawn `test-spec` agent:

```
Task: test-spec agent

Create TDD test specifications for: feature-id

Context:
- PLAN.md: docs/plans/feature-id/PLAN.md
- Feature intent: [from graph]
- Capabilities: [from graph]

Output: Test cases to validate before/during implementation
```

**If tests already exist**, skip this step.

### Step 4: Feature Implementer

Spawn `feature-implementer` agent to orchestrate chunk-by-chunk implementation:

```
Task: feature-implementer agent

Implement: feature-id

Plan: docs/plans/feature-id/PLAN.md
Memory: docs/plans/feature-id/MEMORY.md
Graph: .intents/graph.yaml

The graph status has been set to in-progress.
Update it to implemented when complete, or broken if tests fail.
```

The feature-implementer will:
- Read PLAN.md and MEMORY.md
- Implement chunks sequentially
- Validate each chunk
- Update MEMORY.md with progress
- Stop at phase gates for testing
- Run quality checks

### Step 5: Quality Checks

After implementation completes, spawn review agents as appropriate:

**Always run:**
```
Task: code-reviewer agent

Review implementation for: feature-id

Files: [list from PLAN.md]
Focus: Code quality, patterns, maintainability
```

**If feature involves auth, API, or data:**
```
Task: security-auditor agent

Security review for: feature-id

Focus: Auth patterns, data handling, API security
```

**If feature involves UI:**
```
Task: accessibility-reviewer agent

Accessibility review for: feature-id

Focus: WCAG compliance, keyboard navigation, screen readers
```

### Step 6: Update Graph Status - Complete

**On success:**
```yaml
feature-id:
  status: implemented  # Changed from in-progress
```

Report:
```
Graph Status Update:
  Feature: feature-id
  Status: in-progress → implemented
```

**On failure:**
```yaml
feature-id:
  status: broken  # Changed from in-progress
```

Report:
```
Graph Status Update:
  Feature: feature-id
  Status: in-progress → broken
  Reason: [test failure / quality check failed / blocker]
```

## Status Transitions

```
Valid transitions:
  planned → in-progress (normal start)
  new → in-progress (skipping plan - not recommended)
  broken → in-progress (retry after fix)
  in-progress → implemented (success)
  in-progress → broken (failure)
```

## Options

| Option | Description |
|--------|-------------|
| `--skip-tests` | Skip test-spec step (if tests already exist) |
| `--skip-review` | Skip code-reviewer step |
| `--skip-security` | Skip security-auditor step |
| `--skip-a11y` | Skip accessibility-reviewer step |

## Example Session

```
> /intents:implement ok-themes

Validating feature: ok-themes

✓ Feature found in .intents/graph.yaml
✓ PLAN.md exists at docs/plans/ok-themes/PLAN.md
✓ Current status: planned

Graph Status Update:
  Feature: ok-themes
  Status: planned → in-progress

---

Checking for test specs...
No existing tests found. Spawning test-spec agent...

[test-spec completes]

---

Spawning feature-implementer agent...

[🔧 FEATURE IMPLEMENTER]

## Starting: OK Themes

**Plan:** docs/plans/ok-themes/PLAN.md
**Memory:** docs/plans/ok-themes/MEMORY.md
**Graph:** .intents/graph.yaml (status: in-progress)

### Current State
- Chunks Complete: 0 of 7
- Next Chunk: 1A - Foundation (types, config, page route)

Ready to implement Chunk 1A?

> yes

[Implementation proceeds chunk by chunk...]
[Phase gates pause for manual testing...]

---

## Feature Complete: ok-themes

Spawning quality check agents...

Code Review: ✓ Approved
Accessibility: ✓ Compliant

Graph Status Update:
  Feature: ok-themes
  Status: in-progress → implemented

---

✅ Feature implemented: ok-themes

Summary:
  - Phases: 3 of 3 complete
  - Chunks: 7 total
  - Quality: All checks passed

Graph: .intents/graph.yaml updated (status: implemented)

Next steps:
  - Test the feature manually
  - Merge to main when ready
  - Run `/intents:status ok-themes` to verify
```

## Handling Issues

### Feature Not Found
```
Feature 'feature-id' not found in .intents/graph.yaml.

Options:
1. Run `/intents:plan feature-id` to create the feature
2. Check spelling of feature-id
3. Run `/intents:status` to see available features
```

### Already Implemented
```
Feature 'feature-id' is already implemented.

Options:
1. Re-implement anyway (will reset to in-progress)
2. Cancel

> [user chooses]
```

### Tests Fail
```
Tests failed for feature-id.

Graph Status Update:
  Feature: feature-id
  Status: in-progress → broken

Fix the issues and run `/intents:implement feature-id` to retry.
The implementation will resume from where it stopped.
```

### Quality Check Fails
```
Code review found critical issues:
[list of issues]

Options:
1. Fix issues and re-run quality checks
2. Mark as broken and fix later
3. Override and mark as implemented anyway (not recommended)

> [user chooses]
```

## Output on Success

```
✅ Feature implemented: feature-id

Graph:
  Status: implemented (was: planned)
  Path: .intents/graph.yaml

Quality checks:
  - Code review: ✓ Approved
  - Security audit: ✓ No issues (or N/A)
  - Accessibility: ✓ Compliant (or N/A)

Files created/modified:
  - src/app/feature/page.tsx
  - src/components/Feature.tsx
  - [etc.]

Commits: X commits on feature/feature-name branch

Next:
  - Test manually
  - Merge to main
  - `/intents:status feature-id` to verify
```

## Error Handling Details

### Resume After Interruption

If implementation was interrupted (context reset, session ended):

```
> /intents:implement my-feature

Resuming implementation: my-feature

Reading MEMORY.md...
  Last session: 2024-01-15
  Progress: Phase 1 complete, Phase 2 chunk 2A in progress
  Blocker: None

Resume from chunk 2A?
```

The feature-implementer reads MEMORY.md and picks up where it left off.

### Partial Phase Completion

If a phase is partially complete:

```
Phase 1: 3 of 4 chunks complete

Remaining:
  - Chunk 1D: Sidebar controls

Continue with chunk 1D?
```

### Conflicting Changes

If someone modified files outside the workflow:

```
Warning: Files modified since last session

Modified externally:
  - src/components/Feature.tsx (manual edit detected)

Options:
1. Continue (may overwrite changes)
2. Review changes first
3. Abort and reconcile manually
```

## Related Commands

- `/intents:plan <feature>` - Create a plan (prerequisite)
- `/intents:status` - View current graph state
- `/intents:status <feature>` - View feature details
- `/intents:init` - Bootstrap graph if missing
