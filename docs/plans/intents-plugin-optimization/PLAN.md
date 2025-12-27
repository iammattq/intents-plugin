# Intents Plugin Optimization

## Problem Statement

1. **Commands are bloated** (1847 lines) - duplicate agent logic instead of being thin wrappers
2. **Agents have instruction-following risks** - middle content gets deprioritized ("Lost in the Middle"), critical instructions not at top, inconsistent structure

**Root cause:**
Commands and agents were created without using the `command-builder` and `agent-builder` skills. This resulted in bloated files with unnecessary context that dilutes the model's instruction following.

## Goals

1. Rebuild commands as thin wrappers using `command-builder` skill guidance
2. Rebuild agents using `agent-builder` skill guidance + research principles
3. Ensure effective guidance without context bloat (line count is secondary to structure)
4. Validate refactored plugin works end-to-end

## Non-Goals

- Modifying the 7 copied agents (created with care, already optimized)
- Validating skills (already compliant)
- Adding new features

## Scope

### Commands (5) - Need Rebuilding
| Command | Current Lines | Issue |
|---------|---------------|-------|
| status.md | 401 | Duplicates agent logic |
| validate.md | 543 | Duplicates agent logic |
| init.md | 175 | Duplicates agent logic |
| plan.md | 321 | Duplicates agent logic |
| implement.md | 407 | Duplicates agent logic |
| **Total** | **1847** | |

### Agents (3) - Need Rebuilding
| Agent | Current Lines | Issue |
|-------|---------------|-------|
| codebase-analyzer | 336 | Not built with skill, templates in middle, no description trigger |
| feature-plan | 402 | Not built with skill, 68-line template in middle, graph logic buried |
| feature-implementer | 265 | Not built with skill, needs structural review |

### Already Optimized (No Changes)
- 7 copied agents (82-180 lines each, built with care)
- 2 skills (under 500 lines, proper WHAT+WHEN descriptions)

## Research Principles

From `docs/research/002-claude-code-agents.md`:

1. **"Lost in the Middle"** - LLMs deprioritize middle content
2. **Critical instructions at TOP** - Front-load important rules
3. **Checkpoints for orchestrators** - Explicit STOP signals prevent skipped steps
4. **Progressive disclosure** - Teach when needed, not upfront

**Key insight:** Effective guidance is about structure, not just line count. An agent can be short but poorly structured, or longer but well-organized.

## Implementation

Commands and agents are decoupled (commands invoke agents, don't contain agent logic). Order doesn't matter - work on whichever is ready.

---

## Commands

**Goal:** Thin wrappers that parse args, check prerequisites, and invoke agents.

**Process per command:**
1. Invoke `command-builder` skill via Skill tool
2. Read current command file
3. Rebuild following skill guidance
4. Test by running the command
5. Verify it invokes the agent correctly

### Command Chunks

| Chunk | File | Test |
|-------|------|------|
| C1 | init.md | Run `/intents:init` |
| C2 | status.md | Run `/intents:status` |
| C3 | plan.md | Run `/intents:plan` |
| C4 | implement.md | Run `/intents:implement` |
| C5 | validate.md | Run `/intents:validate` |

---

## Agents

**Goal:** Clear, well-structured guidance that follows research principles.

**Process per agent:**
1. Invoke `agent-builder` skill via Skill tool
2. Read current agent file
3. Rebuild following skill guidance + research principles
4. Validate structure:
   - Critical instructions at TOP
   - No bloat in middle (templates, verbose examples)
   - Checkpoints before critical operations (for orchestrators)
   - Clear "Use WHEN" trigger in description
5. Test by spawning the agent

### Agent Chunks

| Chunk | File | Role |
|-------|------|------|
| A1 | codebase-analyzer/AGENT.md | Orchestrator - bootstraps .intents/ |
| A2 | feature-plan/AGENT.md | Planner - creates PLAN.md + graph node |
| A3 | feature-implementer/AGENT.md | Orchestrator - implements chunks |

### Agent-Specific Notes

**codebase-analyzer:**
- Orchestrator pattern (spawns parallel researchers)
- Needs checkpoint before presenting findings to user
- Description needs "Use WHEN" trigger

**feature-plan:**
- Has MEMORY.md template that's too verbose (68 lines → ~15)
- Graph integration logic buried at line 270
- Needs checkpoint before graph update

**feature-implementer:**
- Has validation protocol (good) but review placement
- Orchestrator pattern (spawns implementation agents)
- Review checkpoint coverage

---

## Integration Testing

After all files rebuilt:

1. Run complete workflow: init → status → plan → implement → validate
2. Verify agents follow checkpoints
3. Fix any issues discovered

---

## Commit

Single cohesive commit with all changes after integration testing passes.

---

## Session Protocol

### Before Each File

1. Invoke the appropriate skill via Skill tool:
   - Commands → `skill: "command-builder"`
   - Agents → `skill: "agent-builder"`
2. Read current file
3. Rebuild following skill guidance
4. Test immediately
5. Continue or fix

### Validation Questions

For each rebuilt file, ask:
- Does this follow the skill's recommended structure?
- Are critical instructions at the TOP?
- Is there any bloat in the middle that could be trimmed or moved?
- For orchestrators: are there checkpoints before critical operations?
- Does the description include a clear "Use WHEN" trigger?

### End of Session

1. Update MEMORY.md with completed chunks
2. Note blockers or decisions made
3. DO NOT commit until all files rebuilt and tested

---

## Files to Modify

**Commands (5):**
- `intents-plugin/commands/init.md`
- `intents-plugin/commands/status.md`
- `intents-plugin/commands/plan.md`
- `intents-plugin/commands/implement.md`
- `intents-plugin/commands/validate.md`

**Agents (3):**
- `intents-plugin/agents/codebase-analyzer/AGENT.md`
- `intents-plugin/agents/feature-plan/AGENT.md`
- `intents-plugin/agents/feature-implementer/AGENT.md`

---

## Reference

This plan incorporates findings from:
- `docs/research/001-claude-code-commands.md` - Command thin wrapper pattern
- `docs/research/002-claude-code-agents.md` - "Lost in the Middle", checkpoints, critical-at-top
- `docs/research/003-claude-code-skills-research.md` - Progressive disclosure principles
- Skills: `command-builder`, `agent-builder` - Structural guidance for each file type
