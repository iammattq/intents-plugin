---
description: Create a feature plan with research workflow. Use when planning new features.
argument-hint: <description> [--parent feature] [--enhance parent] [--skip-brainstorm] [--skip-research] [--skip-tests]
---

# /intents:plan

Facilitate the Research-to-Plan workflow with user as DECIDER.

## Usage

```
/intents:plan <feature-description>
/intents:plan <description> --parent <parent-feature>
/intents:plan <description> --enhance <parent-feature>
/intents:plan <description> --skip-brainstorm
/intents:plan <description> --skip-tests
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
- Prompt the user to share their ideas and debate them 
- Explore 3-5 approaches with honest skepticism
- offer to do small bits of research to help clarify topics and gather insights
- Surface the real options: do nothing, minimal, full
- Allow the user to decide the path forward with you as a thinking partner and counter point.

<checkpoint>
STOP. Present brainstorm summary to user:
- Problem statement (validated)
- Options with trade-offs
- Your recommendation

Wait for user to pick a direction before proceeding.
</checkpoint>

### Phase 1.5: Classification (unless --enhance provided)

After brainstorm, classify the work before proceeding:

1. Read `.intents/graph.yaml` for existing features
2. If no graph exists: **STOP** - tell user to run `/intents:init`
3. Analyze user input + brainstorm for classification signals:
   - "Add X to Y", "improve X" → enhancement
   - "X service", "X system", reusable across features → capability
   - New page/flow/destination → new feature
4. Present recommendation and ask user to confirm:
   - `(f)` New feature - creates graph node
   - `(e)` Enhancement - plan only, no node
   - `(c)` Capability - adds to capabilities.yaml

5. User confirms classification

**If enhancement:**
- Set `enhancement_parent` to the parent feature ID
- Plan path: `docs/plans/<parent>/<feature>/`
- Skip graph node creation

**If capability:**
- Plan path: `docs/plans/capabilities/<capability>/`
- Add to `.intents/capabilities.yaml` instead of graph
- Skip graph node creation

**If new feature:**
- Proceed normally (graph node will be created)

<checkpoint>
STOP. Wait for user to confirm classification before proceeding.
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

**If enhancement:**
- Pass `path: docs/plans/<enhancement_parent>/<feature>/`

**If capability:**
- Pass `path: docs/plans/capabilities/<capability>/`

**If new feature:**
- Pass `path: docs/plans/<feature>/`

**If --skip-tests:**
- Pass `skip_tests: true`

The agent will:
1. Present draft plan for user approval
2. Write PLAN.md and MEMORY.md
3. Spawn test-spec agent (unless skip_tests)

### Phase 6: Graph Update (command handles this)

**After agent completes successfully:**

**If enhancement:**
- Skip graph update (enhancement plans don't get graph nodes)

**If capability:**
- Add to `.intents/capabilities.yaml`:
```yaml
capability-id:
  name: Capability Name
  interface: What it provides
  tech: [dependencies]
```

**If new feature:**
- Add node to `.intents/graph.yaml`:
```yaml
feature-id:
  name: Feature Name
  type: feature
  status: planned
  intent: What users get
  parent: parent-id
  plan: docs/plans/feature-id/PLAN.md
```

## Completion

Report results based on classification:

**For enhancements:**
```
Plan created:
  - docs/plans/<parent>/<feature>/PLAN.md
  - docs/plans/<parent>/<feature>/MEMORY.md

Enhancement to: <parent-id>
  (No graph node created - codebase is source of truth)

Next: /intents:implement <parent>/<feature>
```

**For new features:**
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
| `--enhance <parent>` | Create enhancement plan under parent (skip classification, no graph node) |
| `--skip-brainstorm` | Idea already clear, skip ideation |
| `--skip-research` | Context known, skip codebase/technical research |
| `--skip-tests` | Skip test-spec step (pass to feature-plan agent) |
