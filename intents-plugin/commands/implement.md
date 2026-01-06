---
description: Implement a planned feature with quality checks. Use when ready to build.
argument-hint: <feature-id | parent/enhancement | capabilities/name> [--skip-review] [--use-purple]
---

# /intents:implement

Orchestrate implementation of a planned feature.

## Usage

```
/intents:implement <feature-id>
/intents:implement <parent>/<enhancement>
/intents:implement capabilities/<capability>
/intents:implement <feature-id> --use-purple
/intents:implement <feature-id> --skip-review
```

## Workflow

<constraints>
You are an ORCHESTRATOR, not an implementer.
You MUST use the Task tool to spawn each agent below - do NOT perform implementation or review work yourself.
Stages 4 and 5 require spawning the designated agent(s).
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

### Stage 4: Feature Implementer

**Select workflow based on flags:**
- Default: Spawn `feature-implementer` (single-pass per chunk)
- With `--use-purple`: Run purple team workflow (see below)

#### Default Workflow (feature-implementer)

**MUST spawn** the `feature-implementer` agent:

```
Feature: <feature-id or path>
Plan: docs/plans/<feature>/PLAN.md
Memory: docs/plans/<feature>/MEMORY.md
```

Agent handles chunk-by-chunk implementation, validation, MEMORY.md updates, phase gates.

**✓ CHECKPOINT:** Show results, ask user to continue.

#### Purple Team Workflow (--use-purple)

Orchestrate collaborative iteration between two agents per chunk. **You (the command) orchestrate this loop.**

**For each chunk:**

```
1. Initialize chunk section in MEMORY.md:

   ### Chunk {chunk_id}: {scope}

   #### Implementation Log

2. Spawn purple-team-a:

   Task: purple-team-a

   feature: <path>
   chunk: <chunk_id>
   tasks: <from PLAN.md>
   files: <from PLAN.md>
   ship_criteria: <from PLAN.md>

   Wait for return. Save agentId for resume.

3. Spawn purple-team-b:

   Task: purple-team-b

   feature: <path>
   chunk: <chunk_id>
   tasks: <from PLAN.md>
   ship_criteria: <from PLAN.md>

   Wait for return. Check status.

4. If GAPS_REMAIN and iteration < 3:
   Resume purple-team-a with gaps
   Resume purple-team-b to re-assess
   Repeat until PASS or iteration == 3

5. Update MEMORY.md chunk status:
   - PASS → ✅
   - GAPS_REMAIN after 3 → ⚠️ (note remaining gaps)

6. Ask user: Continue to next chunk?
```

**Phase Gates:** After completing all chunks in a phase, STOP for manual testing.

| Behavior | feature-implementer | purple team (--use-purple) |
|----------|---------------------|----------------------------|
| Implementation | Agent does it all | Team A implements |
| Validation | Agent validates | Team B validates with steel-man/gaps |
| Fixing gaps | Agent spawns fix agent | Team B fixes, or Team A gets another pass |
| Iteration | 1 pass + fixes | Up to 3 A↔B iterations |
| Progress log | MEMORY.md | MEMORY.md (includes iteration log) |

**✓ CHECKPOINT:** After each chunk, show results and ask user to continue.

### Stage 5: Review Loop (unless --skip-review)

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
4. If fix: resume `feature-implementer` with feedback
5. Re-run failed reviewers
6. Repeat until clean or user says proceed

### Stage 6: Finalize

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
| `--skip-review` | Skip Stage 5 |
| `--use-purple` | Use purple team workflow (Team A implements, Team B validates/fixes, up to 3 iterations) |

## Resume

Re-run command to resume. The `feature-implementer` reads MEMORY.md and continues from last completed chunk.


## Completion

```
✅ Feature implemented: <feature-id>

Graph: status → implemented
Files: [list of created/modified]

Next:
  - Test manually
  - Merge to main
```
