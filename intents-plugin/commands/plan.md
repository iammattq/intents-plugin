# /intents:plan

Run the research-to-plan workflow and create a graph node.

## What This Does

1. Orchestrates the full R-P (Research-Plan) workflow
2. Uses multiple agents for comprehensive analysis
3. Creates PLAN.md for the feature
4. Adds a feature node to the graph with `status: planned`

## Usage

```
/intents:plan [feature-name]
/intents:plan [feature-name] --parent [parent-feature]
```

## Workflow

The command orchestrates these agents in sequence:

### 1. Brainstorm (optional)
`feature-brainstorm` - If the idea is rough, explore possibilities first

### 2. Internal Research
`codebase-researcher` - Understand where this fits in the existing codebase:
- Architecture patterns to follow
- Existing code to leverage
- Files that will be affected

### 3. External Research (if needed)
`technical-researcher` - Research external docs, APIs, libraries if the feature requires new technology

### 4. Refinement
`feature-refine` - Pressure-test the approach:
- Run advocate/critic debate
- Surface trade-offs and risks
- Identify rejected alternatives

### 5. Planning
`feature-plan` - Create the structured plan:
- Problem statement and goals
- Phases with tasks
- Session chunks for implementation
- MEMORY.md scaffold

### 6. Graph Update
Add feature node to `.intents/graph.yaml`:

```yaml
feature-name:
  name: Feature Name
  type: feature
  status: planned
  intent: What users get from this
  parent: parent-feature
  plan: docs/plans/feature-name/PLAN.md
  capabilities:
    - identified-capability
```

## Example

```
/intents:plan image-optimization --parent admin-galleries
```

This would:
1. Research how images are currently handled
2. Explore optimization approaches
3. Plan implementation phases
4. Create `docs/plans/image-optimization/PLAN.md`
5. Add `image-optimization` node under `admin-galleries` in graph

## Output

```
✅ Plan created: docs/plans/feature-name/PLAN.md

Graph updated:
  - Added: feature-name (status: planned)
  - Parent: parent-feature
  - Capabilities: [list]

Next steps:
  - Review the plan at docs/plans/feature-name/PLAN.md
  - Run test-spec to define tests (recommended)
  - When ready: /intents:implement feature-name
```

## Options

- `--skip-brainstorm` - Jump straight to research (idea is already clear)
- `--skip-research` - Skip codebase/technical research (context already known)
- `--parent [feature]` - Specify parent feature for inheritance

## After Planning

- Review `PLAN.md` and adjust if needed
- Run `test-spec` to define test cases (TDD)
- When ready: `/intents:implement [feature]`
