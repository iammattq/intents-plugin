# Plan: Purple Team - Collaborative Iteration Experiment

**Feature:** purple-implementer
**Status:** implemented
**Created:** 2026-01-05
**Updated:** 2026-01-05

## Problem Statement

Current `feature-implementer` spawns agents that claim "done" based on "code compiles" not "code does what plan says." The validation catches issues, but the fix cycle is adversarial — validation fails, spawns fixer, claims done again, repeat.

## Goals

1. Collaborative iteration within chunk implementation
2. Agent pair assesses using steel-man/gaps structure
3. Up to 3 iterations per chunk (most issues caught by iteration 2)
4. Same goal throughout: complete the chunk correctly
5. Not adversarial "builder vs fixer" but progressive refinement

## Non-Goals

- Replacing feature-refine (different phase)
- Automated rollback on failure
- Hooks integration (future enhancement)

## Research

- Ralph plugin (self-referential iteration)
- Productive debate frameworks (docs/research/009-productive-debate-frameworks.md)
- Claude Code agent constraints (docs/research/002-claude-code-agents.md line 582: "Subagents cannot spawn subagents")

## Approach

### Architecture

**Key constraint:** Subagents cannot spawn subagents. The orchestration happens at the command level.

```
/intents:implement <feature> --use-purple
  └── main conversation orchestrates
        ├── spawns purple-team-a (implements chunk)
        │     └── writes code directly
        │     └── appends notes to MEMORY.md
        │
        ├── spawns purple-team-b (assesses)
        │     └── reads MEMORY.md + actual code
        │     └── steel-man/gaps assessment
        │     └── fixes gaps directly if possible
        │     └── appends assessment to MEMORY.md
        │
        └── if GAPS_REMAIN and iteration < 3:
              └── resumes purple-team-a with gaps
              └── resumes purple-team-b to re-assess
```

**Named agents (from pool):**
- purple-team-a — implementer (writes code, no spawning)
- purple-team-b — verifier (checks requirements, fixes gaps, no spawning)

**No generic spawns** — both agents do their work directly.

### Why Two Agents?

1. **Fresh eyes**: Team B reads Team A's work with no confirmation bias
2. **Plan as checklist**: Team B verifies each requirement against actual code
3. **Direct fixes**: Team B fixes gaps directly rather than just reporting them
4. **Shared workspace**: Both agents read/write MEMORY.md

### Iteration Cycle

1. Command initializes chunk section in MEMORY.md
2. Spawn purple-team-a:
   - Read plan and MEMORY.md
   - Implement chunk tasks
   - Append implementation notes to MEMORY.md
   - Return summary
3. Spawn purple-team-b:
   - Read Team A's notes from MEMORY.md
   - Read actual code files
   - Assess with steel-man (what works) and gaps (what's missing)
   - Fix gaps directly if possible
   - Append assessment to MEMORY.md
   - Return PASS or GAPS_REMAIN
4. If GAPS_REMAIN and iteration < 3:
   - Resume purple-team-a with gaps from Team B
   - Resume purple-team-b to re-assess
5. Update MEMORY.md chunk status
6. Ask user: Continue to next chunk?

### MEMORY.md Format (Implementation Log Section)

```markdown
## Implementation Log

### Chunk 1A: {scope}

#### Team A - Iteration 1
**Implemented:**
- [What was built]
**Files:**
- path/to/file.ts - [what changed]
**Notes:**
- [Uncertainty, things for Team B to check]

#### Team B - Iteration 1
**Steel-Man:**
- `file.tsx:45` - [What works well]
**Gaps:**
- [Gap 1] OR "None"
**Fixed:**
- [What Team B fixed, if anything]
**Status:** PASS | GAPS_REMAIN

#### Team A - Iteration 2 (if needed)
...

**Chunk Status:** ✅ | ⚠️ (with remaining gaps)
```

## Agent Specs

### purple-team-a

Per agent-builder patterns:
- **Archetype:** Implementer (not orchestrator)
- **Model:** sonnet
- **Tools:** Read, Grep, Glob, Bash, Write, Edit

**Key behaviors:**
1. Read PLAN.md and MEMORY.md
2. If iteration > 1, read Team B's gaps
3. Implement chunk tasks directly
4. Follow existing codebase patterns
5. Append implementation notes to MEMORY.md
6. Return summary for Team B

**Does NOT spawn other agents.**

### purple-team-b

Per agent-builder patterns:
- **Archetype:** Verifier + Fixer (not orchestrator)
- **Model:** sonnet
- **Tools:** Read, Grep, Glob, Bash, Write, Edit

**Key behaviors:**
1. Read plan requirements (source of truth)
2. Read Team A's notes from MEMORY.md
3. Read actual code files (not just trust notes)
4. Check each requirement: verified / missing / wrong with file:line evidence
5. Fix gaps directly if possible
6. Append verification report to MEMORY.md
7. Return PASS or GAPS_REMAIN

**Does NOT spawn other agents.**

### Comparison: v1 vs Purple Team

| Behavior | feature-implementer (v1) | purple team (--use-purple) |
|----------|--------------------------|----------------------------|
| Implementation | Agent spawns general-purpose | Team A implements directly |
| Validation | Agent validates itself | Team B verifies against plan checklist |
| Fixing gaps | Agent spawns fix agent | Team B fixes directly, or Team A gets another pass |
| Iteration | 1 pass + fixes | Up to 3 A↔B iterations |
| Progress log | MEMORY.md | MEMORY.md (includes Implementation Log) |
| Spawning | Nested (didn't work) | Flat (command orchestrates) |

## Phases

### Phase 1: Create Agents ✅

| Chunk | Scope | Files |
|-------|-------|-------|
| 1A | purple-team-a agent | `intents-plugin/agents/purple-team-a/AGENT.md` |
| 1B | purple-team-b agent | `intents-plugin/agents/purple-team-b/AGENT.md` |

**Ship Criteria:**
- [x] purple-team-a implements directly (no spawning)
- [x] purple-team-b assesses with steel-man/gaps
- [x] Both agents write to MEMORY.md as shared workspace
- [x] Agents use sonnet model (not opus, no orchestration)
- [x] implement.md updated with --use-purple flag

### Phase 2: Test on Real Feature

Run on a multi-chunk feature and compare results with v1 approach.

**Ship Criteria:**
- [ ] Successfully implements feature
- [ ] Iteration history useful for understanding what happened
- [ ] Context stays bounded (no compaction mid-chunk)

## Resolved Questions

1. **Subagent spawning:** Subagents cannot spawn subagents. Solution: Command orchestrates, agents don't spawn.

2. **IMPLEMENTATION.md:** Not needed. Merged into MEMORY.md Implementation Log section.

3. **Max iterations:** 3 (most issues caught by iteration 2, 3rd is final attempt).

4. **Resume pattern:** Use agentId to resume agents across iterations.
