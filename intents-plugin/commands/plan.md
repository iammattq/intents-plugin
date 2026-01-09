---
description: Create a feature plan with research workflow. Use when planning new features.
argument-hint: <description> [--skip-brainstorm] [--skip-research] [--skip-tests]
---

# /intents:plan

Facilitate the Research-to-Plan workflow with user as DECIDER.

## Usage

```
/intents:plan <feature-description>
/intents:plan <description> --skip-brainstorm
/intents:plan <description> --skip-research
/intents:plan <description> --skip-tests
```

## Metrics Tracking

When this command starts, the `UserPromptSubmit` hook automatically creates:
`docs/plans/_drafts/<slug>/.tracking.json`

This tracks elapsed time and token usage throughout the planning process.
After classification, the tracking file moves to the feature's final location.

## Research Artifact

Phase 2 produces a research artifact that downstream phases consume. This eliminates redundant codebase exploration.

**Structure:**
```markdown
## Research Artifact

### Architecture Fit
- Target location: [where this feature would live]
- Integration points: [what existing code it touches]
- Affected files: [list of files to modify/create]

### Existing Patterns
- Similar features: [features to model after, with file paths]
- Code patterns: [relevant patterns found, with examples]
- Conventions: [naming, structure, style to follow]

### Dependencies
- Internal: [existing modules/utilities to leverage]
- External: [any new packages needed]
- Blockers: [anything that must be resolved first]

### Test Infrastructure
- Test patterns: [how similar features are tested]
- Test utilities: [existing helpers, mocks, fixtures]
- Coverage expectations: [what level of testing is standard]
```

Agents in subsequent phases receive this artifact and use it directly instead of re-researching.

## Workflow

**User is the DECIDER at each phase.** Present findings and wait for approval before proceeding.

### Phase 1: Brainstorm (unless --skip-brainstorm)

Use the `feature-brainstorm` skill patterns to explore with the user:
- Understand the actual problem (not assumed solution)
- Prompt the user to share their ideas and debate them
- Explore 3-5 approaches with honest skepticism
- Offer to do small bits of research to help clarify topics and gather insights
- Surface the real options: do nothing, minimal, full
- Allow the user to decide the path forward with you as a thinking partner and counter point.

<checkpoint>
STOP. Present brainstorm summary to user:
- Problem statement (validated)
- Options with trade-offs
- Your recommendation

Wait for user to pick a direction before proceeding.
</checkpoint>

### Phase 1.5: Create Slug

After brainstorm, create a slug for the feature and migrate the tracking file:

```bash
# Create slug from the feature description
slug="<slugified-description>"

# Move tracking from drafts to final location
if [ -f "docs/plans/_drafts/${slug}/.tracking.json" ]; then
  mkdir -p "docs/plans/${slug}"
  mv "docs/plans/_drafts/${slug}/.tracking.json" "docs/plans/${slug}/.tracking.json"
  rmdir "docs/plans/_drafts/${slug}" 2>/dev/null
fi
```

### Phase 2: Codebase Research (unless --skip-research)

Spawn `codebase-researcher` agent with expanded scope to gather all context needed by downstream phases:

**Core Questions:**
- What existing code to leverage?
- What patterns to follow?
- What files affected?
- Any blocking dependencies?

**Extended Scope (for downstream phases):**
- Architecture: "Where would this feature live? What modules/directories?"
- Similar features: "What similar features exist to model after? Provide file paths."
- Test patterns: "What test patterns/utilities does this codebase use? Where are test helpers?"

**Output:** Store findings in the Research Artifact structure (see above). This artifact passes forward to feature-refine and feature-plan agents, eliminating redundant codebase exploration.

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

- Pass `path: docs/plans/<feature>/`

**If --skip-tests:**
- Pass `skip_tests: true`

The agent will:
1. Present draft plan for user approval
2. Write PLAN.md and MEMORY.md
3. Spawn test-spec agent (unless skip_tests)

## Completion

```
Plan created:
  - docs/plans/<feature>/PLAN.md
  - docs/plans/<feature>/MEMORY.md

Next: /intents:implement <feature>
```

## Options

| Option | Effect |
|--------|--------|
| `--skip-brainstorm` | Idea already clear, skip ideation |
| `--skip-research` | Context known, skip codebase/technical research |
| `--skip-tests` | Skip test-spec step (pass to feature-plan agent) |
