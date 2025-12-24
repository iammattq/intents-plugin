# /intents:plan

Orchestrate the Research-to-Plan workflow and create a graph node.

## Usage

```
/intents:plan [feature-description]
/intents:plan [feature-description] --parent [parent-feature]
/intents:plan [feature-description] --skip-brainstorm
/intents:plan [feature-description] --skip-research
```

## What This Command Does

This command orchestrates the complete R-P (Research-Plan) workflow by running multiple agents in sequence. At the end, a structured PLAN.md is created and a feature node is added to the graph.

## Workflow Steps

When you run `/intents:plan`, execute these steps:

### Step 1: Understand the Feature

Parse the command arguments:
- `[feature-description]` - What the user wants to build
- `--parent [feature]` - Parent feature for graph inheritance (optional)
- `--skip-brainstorm` - Skip ideation phase (idea is already clear)
- `--skip-research` - Skip codebase/technical research (context already known)

If the description is vague, ask for clarification before proceeding.

### Step 2: Brainstorm (unless --skip-brainstorm)

**Agent:** `feature-brainstorm`

Spawn the brainstorm skill for divergent ideation:

```
Task: feature-brainstorm

Explore possibilities for: [feature-description]

Context:
- Project: [read from .intents/graph.yaml root if available]
- Parent feature: [if specified]

Generate 3-5 different approaches, then help narrow to the most promising direction.
```

**Output:** A refined direction to research further.

If user already has a clear direction, they can use `--skip-brainstorm` to proceed directly to research.

### Step 3: Internal Research

**Agent:** `codebase-researcher`

Understand where this feature fits in the existing codebase:

```
Task: codebase-researcher

Research how to implement: [feature/direction from brainstorm]

Questions to answer:
1. What existing code can we leverage?
2. What patterns should we follow?
3. What files will be affected?
4. Are there any blocking dependencies?

Focus on architecture fit and impact analysis.
```

**Output:** Codebase context for planning.

### Step 4: External Research (if needed)

**Agent:** `technical-researcher`

Only spawn if the feature requires new technology, external APIs, or unfamiliar patterns:

```
Task: technical-researcher

Research: [specific technology or API needed]

Questions:
1. How does this technology work?
2. What are the best practices?
3. Are there examples to follow?
4. What are the gotchas?
```

**Output:** Technical context for planning.

Skip this step if the feature uses only existing patterns and technologies.

### Step 5: Refinement

**Agent:** `feature-refine`

Pressure-test the approach through advocate/critic debate:

```
Task: feature-refine

Refine approach for: [feature-description]

Context from research:
- [Key findings from codebase-researcher]
- [Key findings from technical-researcher, if applicable]

Run advocate/critic debate to:
1. Surface trade-offs and risks
2. Identify rejected alternatives
3. Arrive at a defensible approach
```

**Output:** Refined approach with trade-offs documented.

### Step 6: Planning

**Agent:** `feature-plan`

Create the structured plan:

```
Task: feature-plan

Create plan for: [feature-description]

Refined approach:
- [Output from feature-refine]

Codebase context:
- [Output from codebase-researcher]

Parent feature: [if specified, or ask user]

Create PLAN.md with:
- Problem statement and goals
- Phases with tasks
- Session chunks for implementation
- MEMORY.md scaffold

After writing, update .intents/graph.yaml with new feature node.
```

**Output:** PLAN.md, MEMORY.md, and graph node created.

### Step 7: Confirm Completion

Report the results:

```
/intents:plan complete

Plan created:
  - docs/plans/[feature]/PLAN.md
  - docs/plans/[feature]/MEMORY.md

Graph updated:
  - Added: [feature-id]
  - Status: planned
  - Parent: [parent-feature]
  - Capabilities: [list]

Next steps:
  1. Review the plan: docs/plans/[feature]/PLAN.md
  2. Run test-spec to define tests (recommended)
  3. When ready: /intents:implement [feature-id]
```

## Options

| Option | Effect |
|--------|--------|
| `--parent [feature]` | Specify parent feature for inheritance |
| `--skip-brainstorm` | Skip ideation (idea already clear) |
| `--skip-research` | Skip codebase/technical research (context known) |

## Example Session

```
User: /intents:plan image optimization for galleries --parent admin-galleries

Claude: [Starting R-P workflow for image optimization]

Step 1: Understanding feature
- Feature: Image optimization for galleries
- Parent: admin-galleries (inherits: session-auth, persistence:read-write, images:manage)

Step 2: Brainstorming (skipping - idea is specific)

Step 3: Internal research
[Spawns codebase-researcher]
- Found: src/lib/images.ts handles current image processing
- Found: Sharp library already in use for basic transforms
- Impact: Will modify upload flow and add optimization step

Step 4: External research
[Spawns technical-researcher]
- Researched: Sharp optimization options, WebP/AVIF formats
- Best practice: Generate multiple sizes, serve with srcset

Step 5: Refinement
[Spawns feature-refine]
- Trade-off: Storage cost vs bandwidth savings
- Risk: Processing time on large uploads
- Decision: Async processing with progress indicator

Step 6: Planning
[Spawns feature-plan]
- Created: docs/plans/image-optimization/PLAN.md
- Created: docs/plans/image-optimization/MEMORY.md
- Updated: .intents/graph.yaml (added image-optimization node)

/intents:plan complete

Plan created:
  - docs/plans/image-optimization/PLAN.md
  - docs/plans/image-optimization/MEMORY.md

Graph updated:
  - Added: image-optimization
  - Status: planned
  - Parent: admin-galleries
  - Capabilities: images:manage (optimized)

Next steps:
  1. Review the plan: docs/plans/image-optimization/PLAN.md
  2. Run test-spec to define tests (recommended)
  3. When ready: /intents:implement image-optimization
```

## When to Use This Command

Use `/intents:plan` when you have:
- A feature idea that needs research and planning
- Enough context to describe what you want to build
- Time to go through the full R-P workflow (can be done incrementally)

For quick features that don't need research:
- Write PLAN.md manually
- Add graph node manually
- Run `/intents:implement` directly

## After Planning

1. **Review the plan** - Read PLAN.md, adjust if needed
2. **Define tests** - Run `test-spec` for TDD (recommended)
3. **Implement** - Run `/intents:implement [feature]` when ready

## Error Handling

### No .intents/ folder

```
No .intents/ folder found.

Run /intents:init first to bootstrap the graph.
```

### Feature already exists

```
Feature 'admin-galleries' already exists in graph.

Current status: implemented
Plan: docs/plans/admin-galleries/PLAN.md

Options:
1. View existing plan
2. Create new plan with different name
3. Cancel
```

### Vague description

```
The feature description is too vague to plan effectively.

You said: "make it better"

Please provide more context:
- What user problem does this solve?
- What's the expected behavior?
- What part of the app is affected?
```

### Parent feature not found

```
Parent feature 'bad-parent' not found in graph.

Available parent features:
  - root
  - admin
  - work
  - goodies

Use --parent to specify a valid parent.
```

### Brainstorm diverged too far

```
Brainstorm generated many directions. Please narrow down:

1. Option A: [description]
2. Option B: [description]
3. Option C: [description]

Which direction should we pursue? (1/2/3)
```

## Related Commands

- `/intents:status` - Check if feature already exists
- `/intents:implement <feature>` - Implement after planning
- `/intents:init` - Bootstrap graph if missing
