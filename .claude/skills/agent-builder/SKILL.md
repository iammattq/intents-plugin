---
name: agent-builder
description: Create Claude Code agents with proper structure and best practices. Use when building agents, writing agent definitions, or improving existing agents. For skills, use skill-creator instead.
---

# Agent Builder

Create effective agents (subagents spawned via Task tool). Agents run in isolated context and return compressed findings.

**Not sure if you need an agent?** Use `extension-picker` skill first.

## YAGNI Principles

Before creating an agent, ask:

1. **Do I need isolated context?** If not, a skill might be better
2. **Will this be reused?** One-off tasks don't need agents
3. **Is this the simplest solution?** Don't over-engineer

**Start minimal.** Add complexity only when you hit real pain.

## Agent Template

```yaml
---
name: agent-name
description: Use WHEN [trigger]. Does [what]. [Domain] specialized. Read-only.
tools: Read, Grep, Glob  # Minimum needed
model: haiku  # Match to complexity
---

You are a [role]. Begin responses with: `[EMOJI NAME]`

[Access level] - [what you do/don't do].

## Process
1. **Step 1** - [Action]
2. **Step 2** - [Action]

## Checklist (if reviewing)
- [ ] Specific verifiable item
- [ ] Another item

## Output Format
## Summary
[Template]

## Findings
- `file.tsx:42` - Finding with location
```

## Key Decisions

### Model Selection

| Model     | Use For                                          | Cost     |
| --------- | ------------------------------------------------ | -------- |
| `haiku`   | Pattern matching, simple checks, scaffolding     | Lowest   |
| `sonnet`  | Code review, security audit, standard impl       | Medium   |
| `opus`    | Orchestrators, complex protocols, deep reasoning | Higher   |
| `inherit` | Research needing parent's full context           | Variable |

**When to use each:**

- **`haiku`** - Default for focused tasks. Fast, cheap. Reviewers, scouts, simple validators.
- **`sonnet`** - Workhorse for 90% of development. Code review, security, implementation.
- **`opus`** - When instruction adherence is critical. Orchestrators that must follow complex multi-step protocols precisely. Opus "requires fewer steps" and "follows instructions more effectively" (per Anthropic). Use for agents that:
  - Spawn and validate other agents
  - Must not skip validation steps
  - Handle ambiguity and trade-offs autonomously
  - Run long-horizon autonomous tasks
- **`inherit`** - When agent needs same reasoning power as parent. Research tasks exploring unfamiliar code.

**Cost rule:** Use the cheapest model that reliably completes the task. Opus costs ~5x sonnet, but saves tokens by needing fewer retries on complex protocols.

### Tool Permissions

```yaml
# Read-only (most agents)
tools: Read, Grep, Glob

# Can run commands
tools: Read, Grep, Glob, Bash

# Can spawn other agents (orchestrators)
tools: Read, Grep, Glob, Bash, Task, Write, Edit

# Full access (rarely needed)
tools: *
```

**Restrict to minimum needed.** Read-only is safest.

### Output Format

Every agent needs a clear output format. This ensures:

- Consistent results
- Easy parsing by parent agent
- Clear communication

```markdown
## Output Format

## Summary

[1-2 sentences: main finding]

## [Category]

### [Severity] (if applicable)

- `file.tsx:42` - Issue with location
  - Context: [why it matters]
  - Fix: [guidance]

## Verdict (if applicable)

[Clear recommendation]
```

## Agent Archetypes

### Reviewer (Read-Only)

Evaluates code/content against standards.

```yaml
tools: Read, Grep, Glob
model: haiku or sonnet
```

Key sections: Process, Checklist, Output Format, Verdict

### Researcher

Explores unfamiliar code, returns compressed findings.

```yaml
tools: Read, Grep, Glob, Bash
model: inherit
```

Key sections: Process (Plan → Explore → Synthesize), Output Format

### Scout

Finds patterns, candidates for extraction.

```yaml
tools: Read, Grep, Glob
model: haiku
```

Key sections: Detection Strategies, Evaluation Criteria, Output Format

### Orchestrator

Coordinates multi-step workflows, spawns and validates sub-agents.

```yaml
tools: Read, Grep, Glob, Bash, Task, Write, Edit
model: opus
```

Key sections: **Critical Protocol (at top)**, Process, Validation Checkpoints, Output Format

**Why opus:** Orchestrators must follow complex protocols without skipping steps. The validation failure mode (claiming success without verifying) is prevented by opus's superior instruction adherence.

**Structure pattern:**
```markdown
## CRITICAL: [Protocol Name]
[Most important instructions AT THE TOP - LLMs prioritize beginning/end]

<checkpoint>
STOP. Before proceeding:
□ Did I complete step X?
□ Did I verify Y?
</checkpoint>

## Process
[Rest of workflow...]
```

### Instruction Following

Use XML tags to improve Claude's instruction adherence:

```markdown
<constraints>
COMPLETE ALL STEPS. DO NOT SKIP ANY STEP.
</constraints>

<process>
## Step 1: [Action]
Verify: [condition] → proceed.
</process>

<output_format>
[Template]
</output_format>
```

Key patterns:
- `<constraints>` at top with explicit completion requirement
- `<process>` wrapping sequential steps
- "Verify: X → proceed" after each step

## Error Handling

Every agent should handle edge cases:

```markdown
## If Nothing Found
Report "No issues found" with confidence:
- High: Comprehensive review completed
- Medium: Some areas not accessible
- Low: Limited scope reviewed

## If Blocked
1. Log the blocker
2. Report with context
3. Ask: Fix now? Skip? Pause?
```

## Anti-Patterns

| Don't                              | Do Instead                 |
| ---------------------------------- | -------------------------- |
| `tools: *` for a reviewer          | `tools: Read, Grep, Glob`  |
| `model: inherit` for simple checks | `model: haiku`             |
| No output format                   | Always define structure    |
| Vague description                  | Include "Use WHEN" trigger |
| Over-explaining to Claude          | It's smart, be concise     |

## Detailed Patterns

See [AGENTS.md](AGENTS.md) for:

- Complete archetype examples
- Delegation patterns
- Testing guidance
