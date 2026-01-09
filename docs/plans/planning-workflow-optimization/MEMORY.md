# Planning Workflow Optimization - Implementation Progress

## Kanban

### Ready

- **3** (M): Update feature-plan to accept research artifact

### Blocked

- **4** (M): Inline test-spec into feature-plan → needs 3
- **5** (M): Update plan.md orchestration → needs 4
- **6** (S): Add --fast flag → needs 5

### Done

- **1** (S): Expand Phase 2 research scope ✓
- **2** (M): Update feature-refine to accept research artifact ✓

---

## Session Log

### Session: Chunk 1
**Date:** 2026-01-09
**Status:** Complete

#### Completed
- Added extended scope questions to Phase 2 (architecture, similar features, test patterns)
- Defined research artifact structure with 4 sections (Architecture Fit, Existing Patterns, Dependencies, Test Infrastructure)
- Added instruction for storing findings and passing to downstream phases

#### Files
- intents-plugin/commands/plan.md - Added "Research Artifact" section after Metrics Tracking, expanded Phase 2 with extended scope questions and output instruction

### Session: Chunk 2
**Date:** 2026-01-09
**Status:** Complete

#### Completed
- Added `research_artifact` input parameter to agent spec with 4 sections (Architecture Fit, Existing Patterns, Dependencies, Test Infrastructure)
- Replaced "Gather Codebase Context" section with "Use Research Artifact" section
- Added gap-fill mode allowing narrow targeted lookups only when debate surfaces unanswered questions
- Updated DO guidelines to use research artifact for facts
- Updated DON'T guidelines to prohibit spawning codebase-researcher or re-researching

#### Files
- intents-plugin/agents/feature-refine/AGENT.md - Replaced codebase-researcher spawn with research artifact usage, added gap-fill mode, updated guidelines
