---
description: Implement a planned feature with quality checks. Use when ready to build.
argument-hint: <feature-id | parent/enhancement | capabilities/name> [--skip-tests] [--skip-review]
---

# /intents:implement

Orchestrate implementation of a planned feature.

## Usage

```
/intents:implement <feature-id>
/intents:implement <parent>/<enhancement>
/intents:implement capabilities/<capability>
/intents:implement <feature-id> --skip-tests
```

## Workflow

<constraints>
You are an ORCHESTRATOR, not an implementer.
You MUST use the Task tool to spawn agents - do NOT perform implementation, testing, or review work yourself.
Stage 4 and 6 spawn agents. Stage 5 orchestrates the chunk loop (spawning chunk-implementer for each chunk).
</constraints>

### Stage 1: Validate Prerequisites

Determine lookup method based on argument format:

**If argument contains `/` (path format):**
```
Parse as path (e.g., parent/enhancement or capabilities/name)
Read plan directly from docs/plans/<path>/PLAN.md
Skip graph lookup (enhancements and capabilities don't have graph nodes)
```

**If no `/` (feature-id format):**
```
Read .intents/graph.yaml → find feature by ID
Verify docs/plans/<feature>/PLAN.md exists
Status must be: planned | broken
```

**Error → STOP.** Inform user. If no plan, suggest `/intents:plan <feature>`.

### Stage 2: Git Prep

```bash
git branch --show-current  # Must not be main/master
git status --short         # Warn if uncommitted changes
```

If on main: create feature branch `feature/<feature-id>` and switch to it.

**Error → STOP.** Inform user.

### Stage 3: Update Graph Status

**If feature (not enhancement):**
```yaml
# .intents/graph.yaml
feature-id:
  status: in-progress
```

**If path format (enhancement or capability):**
- Skip graph update (no graph nodes for these)

**Error → STOP.** Inform user.

### Stage 4: Test Spec (unless --skip-tests)

**MUST spawn** the `test-spec` agent using the Task tool:

```
Task: test-spec

Feature: <feature-id>
Plan: docs/plans/<feature>/PLAN.md
```

**✓ CHECKPOINT:** Show results, ask user to continue.
**Error →** Resume agent to fix, then checkpoint again.

### Stage 5: Implementation Loop

**Command orchestrates chunks with visible TodoWrite progress.**

#### 5.1: Parse Plan Structure

```
Read: docs/plans/<feature>/PLAN.md
Read: docs/plans/<feature>/MEMORY.md

Extract:
- All phases and their chunks
- Chunk IDs, scopes, files, ship criteria
- Which chunks are already complete (from MEMORY.md)
```

#### 5.2: Initialize TodoWrite

Create TodoWrite with all chunks visible to user:

```json
{
  "todos": [
    {"id": "1a", "content": "Chunk 1A: [scope]", "status": "completed"},
    {"id": "1b", "content": "Chunk 1B: [scope]", "status": "pending"},
    {"id": "1c", "content": "Chunk 1C: [scope]", "status": "pending"}
  ]
}
```

Mark already-completed chunks from MEMORY.md as "completed".

#### 5.3: Chunk Loop

For each pending chunk:

**a. Mark in_progress:**
```json
{"id": "1b", "content": "Chunk 1B: [scope]", "activeForm": "Implementing [scope]", "status": "in_progress"}
```

**b. Spawn chunk-implementer:**
```
Task: chunk-implementer

chunk: 1B
feature: <feature-id>
plan_excerpt: [Chunk 1B section from PLAN.md]
files: [List of files for this chunk]
ship_criteria: [Definition of done]
```

**c. Validate returned work:**
- Read the validation report from chunk-implementer
- If FAIL: STOP, show issues to user, ask: Fix? Skip? Abort?
- If PASS: continue

**d. Update MEMORY.md:**
```markdown
| 1B | complete | [summary] |
```
Add to session log with validation evidence.

**e. Mark completed in TodoWrite:**
```json
{"id": "1b", "content": "Chunk 1B: [scope]", "status": "completed"}
```

#### 5.4: Phase Gates

**After completing all chunks in a phase, STOP:**

```
Phase [N] Complete

Ship Criteria:
- [x] Criteria 1 - [evidence]

Manual Testing Required:
- [ ] Test item 1
- [ ] Test item 2

Say "continue" when ready for next phase.
```

Wait for user confirmation before starting next phase.

**Resume:** Re-running the command reads MEMORY.md and skips completed chunks.

### Stage 6: Review Loop (unless --skip-review)

**MUST spawn** review agents using the Task tool (same pattern as Stage 4):

| Agent | When |
|-------|------|
| `code-reviewer` | Always |
| `security-auditor` | Auth, API, payment, admin, data handling |
| `accessibility-reviewer` | UI components |

**Review loop:**
1. Run applicable reviewers
2. If issues found → STOP, show issues to user
3. User decides: **fix** / **skip issue** / **abort**
4. If fix: spawn `chunk-implementer` with fix task
5. Re-run failed reviewers
6. Repeat until clean or user says proceed

### Stage 7: Finalize

**If feature (not enhancement):**
Update graph status:
- Success → `implemented`
- User abort → `broken` (log reason)

**If path format (enhancement or capability):**
- No graph update needed
- If capability: verify added to `.intents/capabilities.yaml`
- Report completion with plan path

## Options

| Option | Effect |
|--------|--------|
| `--skip-tests` | Skip Stage 4 |
| `--skip-review` | Skip Stage 6 |

## Resume

Re-run command to resume. Stage 5 reads MEMORY.md and skips completed chunks, continuing from where it left off.

## Completion

```
✅ Feature implemented: <feature-id>

Graph: status → implemented
Files: [list of created/modified]

Next:
  - Test manually
  - Merge to main
```
