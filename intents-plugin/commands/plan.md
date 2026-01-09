---
description: Create a feature plan with research workflow. Use when planning new features.
argument-hint: <description> [--skip-brainstorm] [--skip-research] [--fast]
---

# /intents:plan

Facilitate the Research-to-Plan workflow with user as DECIDER.

## Usage

```
/intents:plan <feature-description>
/intents:plan <description> --skip-brainstorm
/intents:plan <description> --skip-research
/intents:plan <description> --fast
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

Spawn `feature-refine` agent with:
- `problem_statement`: Validated problem from brainstorm
- `chosen_direction`: User's selected approach
- `research_artifact`: Complete Research Artifact from Phase 2

The agent uses the research artifact directly (no re-research) and will:
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

Spawn `feature-plan` agent with:
- `path`: docs/plans/<feature>/
- `research_artifact`: Complete Research Artifact from Phase 2
- `refinement_summary`: Output from Phase 4

The agent will:
1. Create plan with inline test specifications
2. Present draft plan for user approval
3. Write PLAN.md and MEMORY.md

<checkpoint>
STOP. Present plan summary to user:
- Proposed chunks with dependencies
- Test coverage summary
- Any open questions or risks

Wait for user approval before finalizing.
</checkpoint>

## Completion

After user approves at all 3 checkpoints (brainstorm, refinement, plan):

```
Plan created:
  - docs/plans/<feature>/PLAN.md (includes inline test specifications)
  - docs/plans/<feature>/MEMORY.md

Next: /intents:implement <feature>
```

## --fast Mode

When `--fast` is specified, checkpoints are consolidated for a streamlined workflow:

| Standard | --fast |
|----------|--------|
| Checkpoint 1: Brainstorm approval | Auto-proceed after presenting summary |
| Checkpoint 2: Refinement approval | Combined into single final approval |
| Checkpoint 3: Plan approval | Combined into single final approval |

**Behavior:**
- **Checkpoint 1 (brainstorm):** Present summary, then automatically proceed to research. User can still interrupt if needed.
- **Checkpoints 2+3 (refinement + plan):** Combined into a single final approval checkpoint. Present both refinement summary and draft plan together for one approval decision.

### When to Use --fast

**Recommended for:**
- Experienced users familiar with the codebase
- Small, well-defined features
- Quick iterations on known patterns
- Features similar to existing implementations

**Avoid when:**
- Complex features with many unknowns
- Unfamiliar codebases requiring exploration
- High-risk changes needing careful review
- Features requiring significant architectural decisions

## Options

| Option | Effect |
|--------|--------|
| `--skip-brainstorm` | Idea already clear, skip ideation |
| `--skip-research` | Context known, skip codebase/technical research |
| `--fast` | Consolidate checkpoints: auto-proceed brainstorm, combine refinement+plan approval |
