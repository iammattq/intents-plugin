---
description: Create a feature plan with research workflow. Use when planning new features.
argument-hint: <description> [--parent feature] [--skip-brainstorm] [--skip-research]
---

# /intents:plan

Facilitate the Research-to-Plan workflow with user as DECIDER.

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

**User is the DECIDER at each phase.** Present findings and wait for approval before proceeding.

### Phase 1: Brainstorm (unless --skip-brainstorm)

Use the `feature-brainstorm` skill patterns to explore with the user:
- Understand the actual problem (not assumed solution)
- Explore 3-5 approaches with honest skepticism
- Surface the real options: do nothing, minimal, full

<checkpoint>
STOP. Present brainstorm summary to user:
- Problem statement (validated)
- Options with trade-offs
- Your recommendation

Wait for user to pick a direction before proceeding.
</checkpoint>

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

Spawn `feature-refine` agent with full context from prior phases:
- Include: problem statement, chosen direction, Phase 2/3 research findings
- The agent will do its own targeted research to inform the debate
- Two research perspectives may surface different considerations

The agent will:
- Run advocate/critic debate
- Surface trade-offs and risks
- Document rejected alternatives

<checkpoint>
STOP. Present refinement summary to user:
- Recommendation with confidence level
- Trade-offs accepted
- Risks identified
- Rejected alternatives

Wait for user approval before planning.
</checkpoint>

### Phase 5: Planning

Spawn `feature-plan` agent with all context:
- Creates `docs/plans/<feature>/PLAN.md`
- Creates `docs/plans/<feature>/MEMORY.md`
- Adds node to `.intents/graph.yaml` with `status: planned`

The agent will present draft plan for user approval before writing files.

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
