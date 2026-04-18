---
description: Create a feature plan with research workflow. Use when planning new features.
argument-hint: <description> [--skip-brainstorm] [--skip-research]
---

# /intents:plan

Facilitate the Research-to-Plan workflow with user as DECIDER.

## Usage

```
/intents:plan <feature-description>
/intents:plan <description> --skip-brainstorm
/intents:plan <description> --skip-research
```

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

### Start: Check for --skip-brainstorm

Parse the user's input for `--skip-brainstorm`:
- **If present:** Skip to Phase 1.5 (slug creation) then Phase 2
- **If absent:** Brainstorming is MANDATORY. Do not skip it, even if the idea seems clear.

Brainstorming validates assumptions and surfaces options the user may not have considered. Default to doing it.

### Phase 1: Brainstorm (required unless --skip-brainstorm)

Use the `feature-brainstorm` skill. Follow its three phases:
1. **Problem Validation** - Confirm the problem before solutioning
2. **Divergent Exploration** - Expand options without judgment
3. **Probing and Challenging** - Stress-test and converge

Offer small research assists during brainstorming to clarify unknowns.

<checkpoint>
STOP. Present the Brainstorm Summary (see skill handoff template):
- Problem (validated with specifics)
- Options: do nothing, minimal, full
- Your recommendation

Wait for user to pick a direction before proceeding.
</checkpoint>

### Phase 1.5: Create Slug

After brainstorm, create a slug for the feature.

### Phase 2-3: Research (unless --skip-research)

Determine research scope from the brainstorm output:

**Codebase-only** (default): Feature uses existing tech, familiar patterns, no external integrations.

**Codebase + External** (parallel): Brainstorm mentions new technology/APIs, unfamiliar patterns, or external integrations.

#### Path A: Codebase-only

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

**Output:** Store findings in the Research Artifact structure (see above). This artifact passes forward to plan-critic and feature-plan agents, eliminating redundant codebase exploration.

#### Path B: Parallel Research (codebase + external)

Spawn both agents in parallel:
1. `codebase-researcher` -- same scope as Path A
2. `technical-researcher` -- focused on the external technology, APIs, or unfamiliar patterns identified in the brainstorm

Wait for both to complete, then merge outputs into a single Research Artifact:
- **Architecture Fit**: codebase-researcher findings, supplemented by technical-researcher integration points
- **Existing Patterns**: codebase-researcher findings
- **Dependencies**: combine internal (codebase-researcher) and external (technical-researcher) dependencies
- **Test Infrastructure**: codebase-researcher findings, supplemented by technical-researcher testing recommendations

#### Capturing and Passing the Artifact

After research completes (either path), extract the Research Artifact as markdown text. When spawning plan-critic and feature-plan, include it as the `research_artifact` parameter.

### Phase 4: Refinement Critique

Spawn the `plan-critic` subagent (single pass) to pressure-test the chosen direction from multiple lenses and return a Refinement Summary.

**Spawn with:**
- `problem_statement` — what we're solving
- `chosen_direction` — the approach selected during brainstorming
- `research_artifact` — complete Research Artifact from Phase 2-3

The critic applies relevant lenses (code review, security, pragmatist, YAGNI, design) in one pass and returns the Refinement Summary. No debate, no rounds — a single rubric-driven critique. See `agents/plan-critic.md` for the full rubric and output format.

**Handling the result:**

- If the Refinement Summary raises open questions the user needs to resolve, surface them before the checkpoint.
- If a risk is flagged as a blocker (High likelihood + High impact with no viable mitigation), present it to the user with options: (a) address the blocker and re-critique, (b) revise the chosen direction, (c) abort planning.
- Otherwise present the Refinement Summary directly.

<checkpoint>
STOP. Present refinement summary to user:
- Recommendation with confidence level
- Trade-offs accepted
- Risks identified with mitigations
- Rejected alternatives
- Open questions (if any)

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

## Options

| Option | Effect |
|--------|--------|
| `--skip-brainstorm` | Idea already clear, skip ideation |
| `--skip-research` | Context known, skip codebase/technical research |
