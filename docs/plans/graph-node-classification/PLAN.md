# Plan: Graph Node Classification

**Feature:** graph-node-classification
**Type:** Enhancement (to intents-plugin)
**Brainstorm:** [001-graph-node-classification.md](../../brainstorms/001-graph-node-classification.md)

## Problem Statement

Agents create new graph nodes for every feature/idea, but most work is enhancements to existing nodes. This bloats the graph and misrepresents the architecture.

**Key insight:** The graph is a **subway map** - major destinations only. Plans can exist without nodes. Graph is for orientation; plans are for implementation guidance.

## Goals

1. Add classification checkpoint to plan command - after brainstorm, agent recommends "new feature" or "enhancement to X"
2. User confirms classification before planning proceeds
3. Enhancement plans create files at `docs/plans/<parent>/<enhancement>/PLAN.md` (no graph node)
4. Add `--enhance <parent>` flag as power user shortcut
5. Document the subway map mental model in skill and README

## Non-Goals

- Neighborhood/sub-feature representation in graph
- Automatic LLM classification without user confirmation
- Archive/cleanup of old enhancement plans
- Adding enhancements to graph (even with type field) - codebase is source of truth

## Approach

### Classification Flow (post-brainstorm)

```
Based on your input and our discussion:

This looks like: Enhancement to admin-galleries
  "Create and organize photo galleries" (from graph intent)

Plan will be created at: docs/plans/admin-galleries/sorting/

Correct?
  (y) Yes, proceed as enhancement
  (n) No, this is a new feature
```

### Inference Signals

- **Keywords**: "add X to Y", "improve X", "enhance X" → enhancement to X
- **Problem scope**: Issue scoped to existing feature → enhancement
- **New destination**: New user flow or page → new feature

### Edge Cases

- **No graph exists**: Tell user to run `/intents:init`
- **User unsure**: Two-question heuristic fallback

---

## Phase 1: Skill Update

**Focus:** Add subway map mental model and classification guidance to `intents-system` skill

**Ship Criteria:**
- Skill documents subway map mental model
- Classification examples added (node-worthy vs enhancement vs capability)
- Inference signals documented

| Chunk | Scope | Files | Notes |
|-------|-------|-------|-------|
| 1A | Add mental model + classification to skill | `intents-plugin/skills/intents-system/SKILL.md` | Use `/skill-creator` patterns |

### 1A Details

Add to `intents-system` skill:

1. **New section: "Subway Map Mental Model"**
   - Graph = major destinations (subway stops)
   - Capabilities = city utilities (reusable infrastructure)
   - Enhancements = neighborhood improvements (no new node)

2. **New section: "Classification Guide"**
   - When to create a node vs enhancement
   - Work assignment heuristic: "Work on X" vs "Add X to Y"
   - Examples table

3. **Update "Graph Hygiene" section**
   - Reference classification guide
   - Add "not every plan needs a node" guidance

---

## Phase 2: Command Update

**Focus:** Add classification checkpoint and `--enhance` flag to plan command

**Ship Criteria:**
- Classification checkpoint appears after brainstorm
- Reads graph.yaml to present recommendation with intent
- Handles no-graph case
- `--enhance <parent>` flag skips classification
- Enhancement plans created in nested location without graph node

| Chunk | Scope | Files | Notes |
|-------|-------|-------|-------|
| 2A | Add classification checkpoint + flag to command | `intents-plugin/commands/plan.md` | Use `/command-builder` patterns |
| 2B | Update agent for enhancement mode | `intents-plugin/agents/feature-plan/AGENT.md` | Skip graph node, nested path |

### 2A Details

Update `plan.md` command:

1. **Add to argument-hint**: `[--enhance <parent>]`

2. **New section after Phase 1 (Brainstorm): "Phase 1.5: Classification"**
   ```markdown
   ### Phase 1.5: Classification (unless --enhance provided)

   After brainstorm, classify the work:

   1. Read `.intents/graph.yaml` for existing features
   2. If no graph exists: Stop, tell user to run `/intents:init`
   3. Analyze user input + brainstorm for classification signals
   4. Present recommendation with node intent
   5. User confirms: enhancement or new feature

   If enhancement: set parent, skip graph node creation in Phase 5
   ```

3. **Update Phase 5 (Planning)**
   - Pass `is_enhancement` and `parent_node` to feature-plan agent
   - Plan path: `docs/plans/<parent>/<feature>/` for enhancements

### 2B Details

Update `feature-plan` agent:

1. **New input parameter**: `enhancement_parent` (optional)

2. **Conditional in Step 7 (Graph Update)**
   ```markdown
   If enhancement_parent is set:
   - Skip adding node to graph.yaml
   - Create plan at docs/plans/<enhancement_parent>/<feature>/PLAN.md
   Else:
   - Add node to graph.yaml as before
   - Create plan at docs/plans/<feature>/PLAN.md
   ```

---

## Phase 3: Implement Command Update

**Focus:** Enable implement command to work with enhancement plans (path-based lookup)

**Ship Criteria:**
- Implement accepts `parent/enhancement` path format
- Reads plan directly from filesystem path when path format detected
- Falls back to graph lookup for feature IDs

| Chunk | Scope | Files | Notes |
|-------|-------|-------|-------|
| 3A | Add path-based plan lookup | `intents-plugin/commands/implement.md` | Use `/command-builder` patterns |

### 3A Details

Update `implement.md` command:

1. **Update argument-hint**: `<feature-id | parent/enhancement>`

2. **Add path detection logic**
   ```markdown
   If argument contains '/':
   - Parse as parent/enhancement path
   - Read plan from docs/plans/<parent>/<enhancement>/PLAN.md
   - Skip graph lookup
   Else:
   - Look up feature in graph.yaml (existing behavior)
   ```

3. **Update Stage 1 (Load Context)**
   - Support both lookup methods
   - Same downstream flow once plan is loaded

---

## Phase 4: Status Command Update

**Focus:** Enable status command to show enhancement plans under features

**Ship Criteria:**
- `status <feature>` shows enhancement plans nested under that feature
- Top-level `status` unchanged (shows graph nodes only)
- Enhancements discovered via filesystem scan

| Chunk | Scope | Files | Notes |
|-------|-------|-------|-------|
| 4A | Add enhancement discovery to detail view | `intents-plugin/commands/status.md` | Use `/command-builder` patterns |

### 4A Details

Update `status.md` command:

1. **When showing feature detail (`status <feature>`)**
   - Scan `docs/plans/<feature>/*/PLAN.md` for enhancement plans
   - Display as sub-items under the feature
   - Show enhancement name and status from PLAN.md frontmatter (if present)

2. **Top-level status unchanged**
   - Only reads graph.yaml
   - Enhancements not shown (they're neighborhood detail, not subway stops)

---

## Phase 5: Documentation

**Focus:** Update README with classification flow and examples

**Ship Criteria:**
- README explains classification flow
- Examples of node vs enhancement clear
- `--enhance` flag documented
- Path-based implement usage documented

| Chunk | Scope | Files | Notes |
|-------|-------|-------|-------|
| 5A | Update README | `intents-plugin/README.md` | Add to Quick Start and Commands sections |

### 5A Details

Update README:

1. **Quick Start section**
   - Add note about classification checkpoint
   - Example showing enhancement flow

2. **Commands section**
   - Add `--enhance <parent>` to plan options table
   - Brief explanation of when to use

3. **New section: "Node vs Enhancement"** (or add to Best Practices)
   - When work deserves a node
   - When to use --enhance
   - Quick examples

---

## Trade-offs

| Trade-off | Accepting | Because |
|-----------|-----------|---------|
| LLM inference might be wrong | Agent recommends, user confirms | User has clear correction opportunity |
| Extra confirmation step | One question after brainstorm | Classification affects entire flow |
| Enhancement plans without nodes | Some plans have no graph representation | Graph is for orientation, plans are for implementation |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Agent suggests wrong parent | Medium | Low | Show node intent; clear y/n choice |
| User rubber-stamps wrong recommendation | Medium | Low | Show full plan path |
| No graph exists | Low | Low | Tell user to run `/intents:init` |
| Parent doesn't exist in graph | Medium | Medium | Validate parent exists before creating enhancement plan |
| Orphaned enhancement plans | Low | Low | Validate command can detect orphans (parent removed from graph) |

---

## Validation

After implementation:

1. `/intents:plan test-enhancement --enhance some-feature` - should skip classification, create nested plan
2. `/intents:plan new-thing` - should show classification checkpoint after brainstorm
3. Verify enhancement plans don't create graph nodes
4. Verify new feature plans still create graph nodes
5. `/intents:implement parent/enhancement` - should find and use nested plan
6. `/intents:status some-feature` - should show enhancements under that feature
7. `/intents:status` (no args) - should NOT show enhancements (graph only)
