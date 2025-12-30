# 001: Graph Node Classification

**Date:** 2025-12-27
**Status:** Refined - Ready for implementation

## Problem

Agents create new graph nodes for every feature/idea, but most work is enhancements to existing nodes. This bloats the graph and misrepresents the architecture.

**How we know this is a problem:** Direct observation during experimentation - running `/intents:plan` for changes that should enhance existing nodes instead creates new nodes.

**What happens if we do nothing:** Graph becomes noisy, loses its value as an orientation tool, agents make poor decisions about where work belongs.

## Key Insight

The graph is a **subway map** - major destinations only. This is an information architecture exercise, not implementation tracking.

- **Nodes = subway stops** (where users go)
- **Capabilities = city utilities** (reusable infrastructure available everywhere)
- **Neighborhoods = code around a stop** (explored on-demand via `codebase-researcher`, not pre-mapped)
- **Enhancements = improvements to existing stops** (plans exist, but no new node)

**Critical realization:** Plans can exist without nodes. The 1:1 coupling between plans and graph nodes was an assumption, not a requirement. Graph is for orientation; plans are for implementation guidance. They serve different purposes.

## Ideas Explored

### A. Add Triage Step to Plan Command

- **Core concept**: Before planning, agent asks "Is this a new stop or enhancement?"
- **Why interesting**: Simple, localized change to one file
- **Complexity cost**: Another decision point, potential friction
- **Skepticism**: User has to understand the mental model to answer correctly

### B. Separate Commands

- **Core concept**: `/intents:plan` = new node, `/intents:enhance` = enhancement
- **Why interesting**: Clear separation, explicit intent
- **Complexity cost**: Two commands to learn, user must know upfront
- **Skepticism**: What if they pick wrong? Duplication of workflow logic

### C. Information Architecture Decision Tree

- **Core concept**: Ask about user destinations and routes, derive classification
- **Why interesting**: Grounds decision in user-facing reality, not implementation
- **Complexity cost**: More questions during brainstorm phase
- **Skepticism**: May feel bureaucratic for obvious cases

### D. --enhance Flag

- **Core concept**: Single command with explicit flag: `/intents:plan feature` vs `/intents:plan feature --enhance parent`
- **Why interesting**: Explicit signal, LLMs follow flags reliably
- **Complexity cost**: User must know upfront whether it's an enhancement
- **Skepticism**: Adds a flag to learn, but clearer than nuanced questions

### E. Post-Brainstorm Classification (Chosen)

- **Core concept**: Agent infers classification after brainstorm, recommends to user, user confirms
- **Why interesting**: User doesn't need to know upfront; brainstorm provides context for informed decision
- **Complexity cost**: One additional confirmation step after brainstorm
- **Skepticism**: LLM inference might suggest wrong parent, but user can correct

## Heuristics Evaluated

### Route-Based ("Has its own URL")
- **Rejected**: Implementation-dependent, breaks for modals/SPAs, creates 1:1 mapping between routes and nodes

### Onboarding Test ("Would you explain in first hour?")
- **Rejected**: Too subjective (whose onboarding?), produces "maybe" results, arbitrary timing

### Independent Value ("Can users derive value in isolation?")
- **Rejected**: Recursive problem - all value is contextual

### Changelog-Worthy ("Would it be a headline?")
- **Rejected**: Marketing framing, not architectural

### Navigate TO vs Use WHILE
- **Considered**: Better but still route-biased

### Work Assignment Test (Chosen)
- **Accepted**: Grounded in concrete behavior - how you'd assign work to a team member

## Decision

**Chosen: Post-brainstorm classification with agent recommendation**

### Classification Flow

After brainstorm completes, the command orchestration layer:

1. Reads `.intents/graph.yaml` to get existing feature nodes
2. Analyzes user input + brainstorm summary for classification signals
3. Recommends classification to user
4. User confirms or corrects

```
Based on your input and our discussion:

This looks like: Enhancement to admin-galleries
  "Manage content and settings" (from graph intent)

Plan will be created at: docs/plans/admin-galleries/sorting/

Correct?
  (y) Yes, proceed as enhancement
  (n) No, this is a new feature
```

### Inference Signals

Agent uses these signals to recommend classification:
- **Keywords**: "add X to Y", "improve X", "enhance X" → enhancement to X
- **Problem scope**: Issue scoped to existing feature → enhancement
- **New destination**: New user flow or page → new feature

### Edge Cases

**No graph exists**: Tell user to run `/intents:init` first.

**User unsure**: Fall back to two-question heuristic:
1. "Does this enable other features, or is it something users directly experience?"
2. "If assigning this work, would you say 'Work on X' or 'Add X to Y'?"

### Command Shape

```bash
/intents:plan gallery-sorting                    # Brainstorm → classification → confirm
/intents:plan sorting --enhance admin-galleries  # Skip classification (power user shortcut)
```

The `--enhance` flag remains as an explicit shortcut for users who know upfront.

### Classification Examples

**NODE-WORTHY:**
- Admin Galleries → "Work on gallery management" (distinct destination)
- Login Flow → "Work on authentication flow" (distinct UX)
- User Profile → "Work on profile" (specific destination)
- Settings Dashboard → "Work on settings" (dedicated area)

**ENHANCEMENT (use --enhance):**
- Gallery sorting → "Add sorting to galleries"
- Dark mode toggle → "Add dark mode to settings"
- Pagination → "Add pagination to admin users"
- Bulk delete → "Add bulk delete to galleries"

**CAPABILITY (add to capabilities.yaml):**
- Session auth → Enables admin, protected content
- Image processing → Reusable across galleries, profiles, uploads
- Rate limiting → Protective infrastructure used everywhere
- Theme system → Applied globally, not a destination

**BOTH CAPABILITY AND NODE:**
- Auth System → Capability (session management) + Node (login/signup flow users navigate to)

## Design Decisions

### Plan Location

Enhancement plans are siblings under the parent feature:

```
docs/plans/
  admin-galleries/
    PLAN.md              # Original feature plan (has graph node)
    MEMORY.md            # Implementation tracking
    sorting/
      PLAN.md            # Enhancement plan (no graph node)
    bulk-delete/
      PLAN.md            # Enhancement plan (no graph node)
```

### Plan Lifecycle

Keep plans after implementation (for now). Revisit if cruft becomes a problem.

### Neighborhood Mapping

Don't add neighborhood/sub-feature representation to graph. Use `codebase-researcher` to explore neighborhoods on-demand. Keep graph sparse.

### Graph Node Criteria

A node should exist if an agent would need to navigate to it as a distinct destination for work. The graph contains what you'd tell a new developer in the first hour - architectural overview, not implementation log.

## Trade-offs Accepted

| Trade-off | Accepting | Because |
|-----------|-----------|---------|
| LLM inference might be wrong | Agent recommends, user confirms | User has clear correction opportunity; low friction for correct cases |
| Extra confirmation step | One question after brainstorm | Classification affects entire flow - worth one question |
| Enhancement plans without nodes | Some plans have no graph representation | Graph is for orientation, plans are for implementation - different purposes |

## Risks Identified

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Agent suggests wrong parent | Medium | Plan in wrong location | Show node intent/description for user confidence; clear y/n choice |
| User rubber-stamps wrong recommendation | Medium | Wrong classification | Show full plan path so user sees where work will go |
| No graph exists | Low | Can't recommend parent | Tell user to run `/intents:init` first |
| Edge cases not covered | Low | Confusion | Two-question heuristic as fallback |

## Rejected Alternatives

- **Upfront classification (before brainstorm)** - User doesn't have context yet to make informed decision
- **End-of-brainstorm classification** - Too late, might explore wrong scope during brainstorm
- **Four-way classification (hub/stop/capability/enhancement)** - Too complex, introduces new terminology
- **Hierarchical plan folders mirroring graph** - Adds navigation pain, contradicts simplicity goal
- **1:1 coupling of plans to nodes** - Planning needs differ from architectural representation needs
- **Separate /intents:enhance command** - Duplicates workflow logic, two commands to learn
- **Pure LLM inference without confirmation** - Too unreliable, user has no correction opportunity

## What Changes

1. **Update `intents-system` skill**
   - Add subway map mental model
   - Add classification examples (node-worthy vs enhancement)
   - Document inference signals for classification

2. **Update `plan.md` command**
   - Add classification checkpoint after brainstorm phase
   - Read graph.yaml to get existing nodes with intents
   - Present recommendation with node intent for user confidence
   - Handle "no graph exists" → tell user to run `/intents:init`
   - Add `--enhance <parent>` flag as power user shortcut
   - When enhancement: create plan at `docs/plans/<parent>/<enhancement>/PLAN.md`, no graph node

3. **Documentation**
   - Update README with classification flow
   - Add examples of node vs enhancement classification

## Open Questions (Resolved)

- ~~Exact wording of classification questions~~ → Agent recommends with confirmation; two-question heuristic as fallback
- ~~How enhancements reference their parent node~~ → Via folder location under parent feature
- ~~Whether capabilities need status tracking~~ → Capabilities don't track status (they're always "available")
- ~~When/if to archive completed enhancement plans~~ → Keep for now, revisit if cruft becomes a problem
- ~~What if graph doesn't exist~~ → Tell user to run `/intents:init` first
- ~~Should we show node description~~ → Yes, show intent from graph for user confidence

## Next Steps

1. Update `intents-system` skill with subway map mental model and classification examples
2. Update `plan.md` command with classification checkpoint and `--enhance` flag
3. Update README with new classification flow
