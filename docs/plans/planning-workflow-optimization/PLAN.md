# Planning Workflow Token Optimization

## Problem Statement

The `/intents:plan` command spawns codebase-researcher 3-4 times asking nearly identical questions, wasting ~70% of file read tokens.

| Agent | Questions Asked |
|-------|-----------------|
| Phase 2 `codebase-researcher` | patterns, files affected, dependencies |
| `feature-refine` | where does this live, what patterns exist, what would this touch |
| `feature-plan` | architecture fit, files touched, dependencies |
| `test-spec` | test patterns, test utilities |

Questions overlap ~80%. Isolation benefit doesn't justify 4x file reads.

## Goals

1. Reduce codebase-researcher spawns from 4 to 1
2. Pass research artifact forward to downstream agents
3. Inline test-spec into feature-plan
4. Preserve workflow structure, agent separation, and user checkpoints

## Non-Goals

- Merging feature-refine + feature-plan (different cognitive tasks)
- Removing checkpoints by default (user control matters)
- Changing model assignments

## Approach

- Expand Phase 2 scope to answer all downstream questions in one pass
- Define research artifact structure for explicit context passing
- Update feature-refine and feature-plan to accept artifact (no re-research)
- Inline test-spec logic into feature-plan
- Add --fast flag for checkpoint consolidation (opt-in)

## Trade-offs

| Trade-off | Accepting | Because |
|-----------|-----------|---------|
| Research may miss edge cases | Less comprehensive | Gap-fill mode allows targeted lookups |
| Loss of fresh context per agent | Isolation benefit | 70% token savings outweighs |
| Larger Phase 2 scope | More upfront work | Amortized across phases |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Research artifact missing info | Medium | Gap-fill mode in agents |
| Inlined test-spec quality drop | Low | Same logic, just not spawned |

---

## Chunks

| Chunk | Size | Depends | Scope | Files |
|-------|------|---------|-------|-------|
| 1 | S | - | Expand Phase 2 research scope | commands/plan.md |
| 2 | M | 1 | Update feature-refine to accept research artifact | agents/feature-refine/AGENT.md |
| 3 | M | 1 | Update feature-plan to accept research artifact | agents/feature-plan/AGENT.md |
| 4 | M | 3 | Inline test-spec into feature-plan | agents/feature-plan/AGENT.md |
| 5 | M | 2,4 | Update plan.md orchestration wiring | commands/plan.md |
| 6 | S | 5 | Add --fast flag | commands/plan.md |

---

## Chunk Details

### Chunk 1: Expand Phase 2 Research Scope

**Files:** `intents-plugin/commands/plan.md`

**Tasks:**
- Add extended scope questions to codebase-researcher prompt:
  - Architecture: "Where would this feature live?"
  - Similar features: "What similar features exist to model after?"
  - Test patterns: "What test patterns/utilities does this codebase use?"
- Define research artifact structure in command doc
- Add instruction to store findings for downstream phases

### Chunk 2: Update feature-refine to Accept Research Artifact

**Files:** `intents-plugin/agents/feature-refine/AGENT.md`

**Tasks:**
- Add `research_artifact` input parameter to agent spec
- Remove Section "Gather Codebase Context" that spawns codebase-researcher
- Replace with: "Use provided research artifact from Phase 2"
- Add gap-fill mode: Allow narrow targeted lookups only if debate surfaces unanswered questions
- Update DO/DON'T guidelines

### Chunk 3: Update feature-plan to Accept Research Artifact

**Files:** `intents-plugin/agents/feature-plan/AGENT.md`

**Tasks:**
- Add `research_artifact` input parameter to agent spec
- Remove "Deep Codebase Research" section that spawns codebase-researcher
- Replace with: "Use provided research artifact"
- Update process to reference artifact

### Chunk 4: Inline test-spec into feature-plan

**Files:** `intents-plugin/agents/feature-plan/AGENT.md`

**Tasks:**
- Remove Step 8 that spawns test-spec agent
- Add inline test specification section:
  - Analyze plan for testable components
  - Define unit test cases
  - Define integration tests (if applicable)
  - Add acceptance criteria
- Add Test Specification section to plan output template
- Merge test approval into plan checkpoint

### Chunk 5: Update plan.md Orchestration

**Files:** `intents-plugin/commands/plan.md`

**Tasks:**
- Phase 4: Pass research artifact to feature-refine
- Phase 5: Pass research artifact to feature-plan
- Remove Phase 5 sub-step for test-spec spawn
- Remove Checkpoint 4 (test-spec approval) - merged into Checkpoint 3
- Update completion output

### Chunk 6: Add --fast Flag

**Files:** `intents-plugin/commands/plan.md`

**Tasks:**
- Add --fast to argument-hint
- Add --fast behavior section:
  - Checkpoint 1 (brainstorm): Auto-proceed after summary
  - Checkpoints 2+3: Combined into single final approval
- Add recommendation guidance
- Update options table

---

## Validation

| Check | Method |
|-------|--------|
| No codebase-researcher spawn in feature-refine | Grep for "codebase-researcher" |
| No codebase-researcher spawn in feature-plan | Grep for "codebase-researcher" |
| No test-spec spawn in feature-plan | Grep for "test-spec" |
| Research artifact documented | Read plan.md |
| --fast flag documented | Read plan.md options table |
| 3 checkpoints (not 4) | Count checkpoint blocks |

---

## Files to Modify

- `intents-plugin/commands/plan.md`
- `intents-plugin/agents/feature-refine/AGENT.md`
- `intents-plugin/agents/feature-plan/AGENT.md`
