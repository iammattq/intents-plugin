# Memory: Graph Node Classification

## Status

**Current Phase:** Complete
**Current Chunk:** All done

## Progress

| Chunk | Status | Notes |
|-------|--------|-------|
| 1A | Complete | Skill update - subway map + classification guide added |
| 2A | Complete | Plan command - classification checkpoint + --enhance flag |
| 2B | Complete | Feature-plan agent - enhancement_parent param + conditional graph |
| 3A | Complete | Implement command - path-based lookup for enhancements |
| 4A | Complete | Status command - enhancement discovery in detail view |
| 5A | Complete | README update - classification flow + node vs enhancement guide |

## Session Log

### 2025-12-28 - Added Capability Classification

Extended three-way classification (feature/enhancement/capability):
- Updated `intents-system/SKILL.md` with two-question heuristic and capability examples
- Updated `commands/plan.md` with (f)/(e)/(c) options
- Updated `agents/feature-plan/AGENT.md` with `is_capability` parameter

Capabilities now:
- Path: `docs/plans/capabilities/<capability>/`
- Added to `.intents/capabilities.yaml` instead of graph

### 2025-12-27 - Implementation Complete

All 6 chunks implemented in single session:

**Chunk 1A** - Updated `intents-system/SKILL.md`:
- Added "Subway Map Mental Model" section
- Added "Classification Guide" with work assignment heuristic
- Updated "Graph Hygiene" to reference classification

**Chunk 2A** - Updated `commands/plan.md`:
- Added `--enhance <parent>` flag to argument-hint
- Added Phase 1.5: Classification checkpoint
- Updated Phase 5 for enhancement mode (nested path, skip graph)

**Chunk 2B** - Updated `agents/feature-plan/AGENT.md`:
- Added `enhancement_parent` input parameter
- Conditional path in Step 6 (Write Files)
- Conditional in Step 7 (Graph Update) - skip for enhancements

**Chunk 3A** - Updated `commands/implement.md`:
- Added path format `<parent>/<enhancement>` to argument-hint
- Added path detection logic in Stage 1
- Updated Stage 3, 5, 7 for enhancement handling

**Chunk 4A** - Updated `commands/status.md`:
- Added "Enhancements" field to detail view
- Added Enhancement Discovery section (filesystem scan)
- Clarified tree view is graph-only

**Chunk 5A** - Updated `README.md`:
- Quick Start: classification note + enhancement shortcut
- Commands: `--enhance` option + path-based implement
- Best Practices: "Node vs Enhancement" section

### 2025-12-27 - Brainstorm + Planning + Refinement

- Completed brainstorm session exploring node classification problem
- Key insight: Graph is a subway map, plans can exist without nodes
- Evaluated multiple heuristics, chose "work assignment" test
- Decided on post-brainstorm classification with agent recommendation
- Created initial plan with 3 phases

**Refinement round 1**: Identified gaps in implement/status commands
- Implement needs path-based lookup for enhancements
- Status needs to show enhancements when viewing feature detail

**Refinement round 2**: Debated `type: enhancement` vs node-less approach
- type:enhancement: adds field to graph, simpler lookups
- node-less: keeps graph clean, filesystem is source of truth

**Decision**: Keep node-less approach. Codebase is source of truth; graph is for orientation only. Accept the implement/status changes as necessary.

- Expanded plan to 5 phases, 6 chunks

## Decisions Made

1. **Classification timing**: After brainstorm, before research (user has context)
2. **User interaction**: Agent recommends, user confirms (y/n)
3. **Power user path**: `--enhance <parent>` flag skips classification
4. **Plan location**: `docs/plans/<parent>/<enhancement>/PLAN.md` for enhancements
5. **Graph impact**: Enhancements don't create nodes (codebase is truth)
6. **Implement**: Accepts `parent/enhancement` path format
7. **Status**: Feature detail view shows enhancements via filesystem scan

## Blockers

None currently.

## Open Items

- [ ] Confirm skill-creator patterns for SKILL.md updates
- [ ] Confirm command-builder patterns for command updates
