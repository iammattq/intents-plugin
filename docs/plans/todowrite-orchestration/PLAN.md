# Plan: TodoWrite Orchestration for Progress Visibility

**Feature:** todowrite-orchestration
**Status:** planned
**Created:** 2026-01-02
**Research:** [010-todowrite-progress-visibility.md](../../research/010-todowrite-progress-visibility.md)

---

## Problem Statement

When feature-implementer runs, users see no progress. The agent processes multiple chunks internally, but sub-agent TodoWrite is invisible to users. They wait with a black box:

```
> /implement feature-x

[Task: feature-implementer] Implementing feature...

# User sees NOTHING for potentially long periods
# No indication of which chunk is being worked on
# No sense of progress or remaining work

[Task: feature-implementer] Completed.
```

**Current state:** feature-implementer owns the chunk loop internally. It spawns general-purpose agents for each chunk, updates MEMORY.md, and enforces phase gates. But all this happens in an opaque sub-agent context.

**Desired state:** Users see real-time progress. TodoWrite shows each chunk transitioning from pending to in_progress to completed. Phase structure is visible upfront.

---

## Goals

1. **Real-time progress visibility** - Users see TodoWrite progress during implementation
2. **Maintain orchestration quality** - Validation, MEMORY.md updates, phase gates preserved
3. **Preserve hook compatibility** - `.chunk-complete` marker still written for SubagentStop hooks
4. **Clean architecture** - Single-responsibility: command orchestrates, agent implements one chunk

## Non-Goals

- Changing the validation protocol (keep as-is)
- Modifying phase gate behavior (keep manual pause)
- Adding new hook types
- Parallel chunk execution

---

## Architecture Change

### Before (Current)

```
/implement → feature-implementer (ALL chunks, opaque)
               ├── For each chunk:
               │     ├── Spawn general-purpose agent
               │     ├── Validate, update MEMORY.md
               │     └── Write .chunk-complete marker
               └── Phase gates (invisible to user)
```

**Problem:** User sees only "Implementing feature..." until completion.

### After (Proposed)

```
/implement (owns loop + TodoWrite)
  ├── TodoWrite: init all phases/chunks
  ├── For each chunk:
  │     ├── TodoWrite: mark in_progress
  │     ├── Spawn chunk-implementer (ONE chunk)
  │     ├── Validate, update MEMORY.md
  │     ├── Write .chunk-complete marker
  │     └── TodoWrite: mark completed
  └── Phase gate pauses (visible to user)
```

**Result:** User sees real-time progress with clear visibility of what is being worked on.

---

## Trade-offs

| Trade-off | Decision | Rationale |
|-----------|----------|-----------|
| Command complexity | Accept increase | Progress visibility worth the trade-off |
| Per-chunk spawns | Accept overhead | Each spawn lets command update TodoWrite |
| Validation location | Move to command | Command can verify before marking complete |
| MEMORY.md updates | Move to command | Deterministic updates after each chunk |
| Marker file writes | Keep in command | Command controls timing, hooks see it |

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Command becomes too complex | Medium | Medium | Extract validation to utility functions |
| Context overflow in command | Low | High | Command only orchestrates, agent does work |
| Hook timing issues | Low | Medium | Write marker after MEMORY.md update |
| TodoWrite overhead | Low | Low | One call per chunk transition, acceptable |

---

## Phase 1: Restructure (Single Phase MVP)

Complete restructure in one phase since components are tightly coupled.

| Chunk | Scope | Files | Estimated Size |
|-------|-------|-------|----------------|
| 1A | Create chunk-implementer agent (single-chunk worker) | `agents/chunk-implementer/AGENT.md` | Small |
| 1B | Update implement.md with chunk loop + TodoWrite | `commands/implement.md` | Medium |
| 1C | Delete feature-implementer, update references | Delete `agents/feature-implementer/`, update refs | Small |

### Chunk 1A: Create chunk-implementer Agent

**Purpose:** Implement exactly ONE chunk. No loop, no orchestration.

**Key differences from feature-implementer:**
- No chunk loop
- No MEMORY.md updates (command handles)
- No phase gate logic (command handles)
- No .chunk-complete marker (command handles)
- Focuses purely on implementation + validation

**Structure:**
```markdown
# Chunk Implementer

Input: chunk ID, feature, plan excerpt, files list, ship criteria
Output: Implementation summary, validation report

Process:
1. Read plan section for this chunk
2. Spawn general-purpose for implementation
3. Validate implementation against plan (MANDATORY)
4. Return validation report
```

### Chunk 1B: Update implement.md Command

**Add TodoWrite orchestration loop:**

```markdown
### Stage 5: Implementation Loop (Replaces Current Stage 5)

1. Read PLAN.md for all phases and chunks
2. Read MEMORY.md for current progress
3. TodoWrite: Initialize with all chunks (mark completed ones done)

4. For each remaining chunk:
   a. TodoWrite: Mark chunk in_progress
   b. Spawn chunk-implementer with:
      - Chunk ID
      - Plan excerpt for this chunk
      - Ship criteria
   c. Validate returned work
   d. Update MEMORY.md
   e. Write .chunk-complete marker
   f. TodoWrite: Mark chunk completed

5. Phase gates: STOP after completing each phase
```

**TodoWrite format:**
```json
{
  "todos": [
    {"id": "1a", "content": "Chunk 1A: [scope]", "status": "completed"},
    {"id": "1b", "content": "Chunk 1B: [scope]", "activeForm": "Implementing [scope]", "status": "in_progress"},
    {"id": "1c", "content": "Chunk 1C: [scope]", "status": "pending"}
  ]
}
```

### Chunk 1C: Clean Up

1. Delete `intents-plugin/agents/feature-implementer/` directory
2. Search for references to `feature-implementer` and update:
   - README.md mentions
   - Other agent references
   - Documentation

---

## Ship Criteria

- [ ] `/implement` displays real-time TodoWrite progress to user
- [ ] Each chunk shows pending -> in_progress -> completed transition
- [ ] Phase gates still pause between phases (user must say "continue")
- [ ] MEMORY.md updated after each chunk completion
- [ ] `.chunk-complete` marker written for hook automation
- [ ] Resume from MEMORY.md works (picks up where left off)
- [ ] Validation protocol preserved (agent doesn't mark done prematurely)

---

## Preserved Behavior (Must Not Break)

| Behavior | How Preserved |
|----------|---------------|
| MEMORY.md persistence | Command updates after each chunk |
| Phase gate pauses | Command STOPs after phase completion |
| Validation protocol | chunk-implementer validates, command verifies |
| Hook compatibility | Command writes .chunk-complete marker |
| Resume capability | Command reads MEMORY.md, skips completed chunks |
| Git failsafe | Command checks branch before proceeding |

---

## Technical Notes

### TodoWrite API

```json
{
  "todos": [
    {
      "id": "unique-id",
      "content": "Imperative description",
      "activeForm": "Present continuous (shown when in_progress)",
      "status": "pending | in_progress | completed",
      "priority": "high | medium | low"
    }
  ]
}
```

**Key behaviors:**
- Complete replacement each call (no incremental)
- Single `in_progress` at a time
- Update immediately after completion

### MEMORY.md Update Pattern

Command updates after chunk-implementer returns:
1. Read current MEMORY.md
2. Update chunk status in progress table
3. Add to session log
4. Write updated MEMORY.md
5. Then write .chunk-complete marker

### Chunk-implementer Validation Report

Agent returns structured validation:
```markdown
## Validation Report

**Chunk:** 1A
**Status:** PASS | FAIL

### Tasks
- [x] Task 1 - file.tsx:45 implements X
- [ ] Task 2 - FAILED: expected X, found Y

### Files Modified
- path/to/file.ts

### Notes
- Any issues or observations
```

---

## Implementation Notes

### Required Skills

When modifying intents-plugin components, use appropriate skills:

| Component | Skill |
|-----------|-------|
| `agents/chunk-implementer/AGENT.md` | `agent-builder` |
| `commands/implement.md` | `command-builder` |

### Dependencies

- None new. Uses existing TodoWrite tool built into Claude Code.

---

## Success Metrics

- Users see progress within seconds of chunk start
- No regressions in implementation quality
- Hook automation continues working
- Resume capability functions correctly
