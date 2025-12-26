---
description: Create a feature plan with research workflow. Use when planning new features.
argument-hint: <description> [--parent feature] [--skip-brainstorm] [--skip-research]
---

# /intents:plan

Orchestrate Research-to-Plan workflow and create a graph node.

## Usage

```
/intents:plan <feature-description>
/intents:plan <description> --parent <parent-feature>
/intents:plan <description> --skip-brainstorm
/intents:plan <description> --skip-research
```

## Prerequisites

- `.intents/` folder must exist (run `/intents:init` if not)
- If `--parent` specified, parent must exist in graph
- If feature already exists in graph, ask user how to proceed

## Workflow

Execute these phases in sequence, passing context forward:

### Phase 1: Brainstorm (unless --skip-brainstorm)

Spawn `feature-brainstorm` skill:
- Explore 3-5 approaches
- Narrow to promising direction
- Skip if user has clear direction

### Phase 2: Codebase Research (unless --skip-research)

Spawn `codebase-researcher` agent:
- What existing code to leverage?
- What patterns to follow?
- What files affected?
- Any blocking dependencies?

### Phase 3: External Research (if needed)

Spawn `technical-researcher` agent only if feature requires:
- New technology/APIs
- Unfamiliar patterns
- External integrations

### Phase 4: Refinement

Spawn `feature-refine` skill:
- Advocate/critic debate
- Surface trade-offs and risks
- Document rejected alternatives

### Phase 5: Planning

Spawn `feature-plan` agent with all context:
- Creates `docs/plans/<feature>/PLAN.md`
- Creates `docs/plans/<feature>/MEMORY.md`
- Adds node to `.intents/graph.yaml` with `status: planned`

## Completion

Report results:

```
Plan created:
  - docs/plans/<feature>/PLAN.md
  - docs/plans/<feature>/MEMORY.md

Graph updated:
  - Added: <feature-id>
  - Status: planned
  - Parent: <parent>

Next: /intents:implement <feature-id>
```

## Options

| Option | Effect |
|--------|--------|
| `--parent <feature>` | Specify parent for capability inheritance |
| `--skip-brainstorm` | Idea already clear, skip ideation |
| `--skip-research` | Context known, skip codebase/technical research |
