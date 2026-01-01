# Research 007: Agent Spawning Patterns

**Date:** 2026-01-01

**Status:** Complete

**Related:** `/implement` command agent delegation, feature-implementer orchestration

## Problem Statement

Commands like `/implement` are designed to spawn specialized agents (e.g., `feature-implementer`, `test-spec`, `code-reviewer`), but Claude often performs the work itself instead of delegating to these agents. This research investigates what prompt patterns, structures, and mechanisms make Claude more likely to actually use the Task tool to spawn agents.

## Constraints

- Subagents cannot spawn other subagents (hard limitation in Claude Code)
- Commands run in the main Claude context (not as agents themselves)
- Agent delegation decisions are made by Claude based on context matching
- Token efficiency matters for complex orchestration workflows

---

## Findings

### Approach 1: Explicit Task Delegation Instructions

**The Core Problem:** Claude uses the Task tool cautiously by default. Without explicit instructions, Claude will often complete work directly rather than delegating.

**How it works:**

The most reliable pattern is to provide explicit step-by-step instructions specifying *which operations will be handled by sub-agents*. Like multi-threaded programming, explicit orchestration yields the best results.

**Command example:**

```markdown
# /implement command

## Stage 4: Test Spec

**ACTION: Spawn the `test-spec` agent using the Task tool.**

```
Task: test-spec

Create test specifications for feature: $FEATURE_ID

Plan file: docs/plans/$FEATURE/PLAN.md

Follow the agent's process to define test cases and update the plan.
```

Wait for agent to complete before proceeding.
```

**Key pattern elements:**

1. **Explicit "Spawn" language** - Use words like "Spawn", "Use the Task tool to invoke", or "Delegate to"
2. **Task block format** - Show the exact Task tool invocation format
3. **Agent name specification** - Reference the agent by exact name
4. **Context passing** - Include what information the agent needs
5. **Blocking instruction** - "Wait for agent to complete"

**Pros:**
- Most reliable method for forcing delegation
- Clear audit trail of what should happen
- Matches how Claude Code's Task tool actually works

**Cons:**
- Verbose command files
- Claude may still skip if it judges the task "simple enough"
- Requires careful instruction ordering

**Evidence:** ClaudeLog states "explicit orchestration of which steps get delegated to sub-agents yields the best results" and emphasizes that Claude "uses Task agents cautiously unless you provide detailed delegation instructions."

---

### Approach 2: Agent Description Field Optimization ("Tool SEO")

**How it works:**

Claude's delegation decisions rely heavily on matching the task description against agent `description` fields. Optimizing these fields improves automatic delegation reliability.

**Effective description patterns:**

```yaml
# Strong - explicit triggers and action language
---
name: feature-implementer
description: MUST BE USED when implementing planned features. Use PROACTIVELY for chunk-by-chunk implementation. Orchestrates sub-agents, validates against plan. Full access.
---

# Strong - specific domain and trigger
---
name: test-spec
description: Use IMMEDIATELY after feature-plan approval. MUST define test specifications before any implementation begins. Updates PLAN.md with test cases.
---

# Weak - vague, no trigger
---
name: code-reviewer
description: Reviews code quality.
---
```

**Key phrases that improve delegation:**

| Phrase | Effect |
|--------|--------|
| `MUST BE USED when...` | Strongest trigger signal |
| `Use PROACTIVELY for...` | Encourages automatic delegation |
| `Use IMMEDIATELY after...` | Temporal trigger |
| `ALWAYS invoke for...` | Unconditional trigger |
| `Specialized for [domain]` | Domain matching |

**Pros:**
- Works for automatic delegation without explicit commands
- Reduces command verbosity
- Can be combined with explicit instructions

**Cons:**
- Still probabilistic, not deterministic
- Requires experimentation to find effective wording
- Agent naming can interfere (see Approach 4)

**Evidence:** Anthropic documentation states: "To encourage proactive subagent use, include phrases like 'use PROACTIVELY' or 'MUST BE USED' in your description field."

---

### Approach 3: Structured Command Format with XML Tags

**How it works:**

Use XML tags in command definitions to clearly separate different instruction types and improve Claude's instruction adherence.

**Command structure:**

```markdown
# /implement command

<constraints>
You are an ORCHESTRATOR, not an implementer.
You MUST spawn agents for all implementation work.
You do NOT write code yourself.
</constraints>

<delegation_rules>
## Stage 4: Test Spec
SPAWN: test-spec agent
CONTEXT: Feature plan at docs/plans/$FEATURE/PLAN.md
WAIT: Until agent completes

## Stage 5: Implementation
SPAWN: feature-implementer agent
CONTEXT: Plan + Memory files
WAIT: Until agent completes with validation report
</delegation_rules>

<process>
1. Validate prerequisites
2. Execute Stage 4 (SPAWN test-spec)
3. Execute Stage 5 (SPAWN feature-implementer)
4. Execute Stage 6 (SPAWN review agents)
</process>
```

**Pros:**
- XML tags improve instruction parsing
- Clear separation of concerns
- `<constraints>` at top gets high attention weight

**Cons:**
- No guarantee of adherence
- More complex command syntax
- Requires consistent formatting

**Evidence:** Community patterns show XML tags like `<constraints>`, `<process>`, and `<checkpoint>` improve instruction following. The "Lost in the Middle" research confirms LLMs prioritize beginning/end of prompts.

---

### Approach 4: Non-Descriptive Agent Naming

**How it works:**

Claude infers agent function based on naming conventions. When you name an agent `code-reviewer`, Claude may apply pre-built code review behavior that overrides your specific instructions. Using non-descriptive names prevents this inference.

**Problematic pattern:**

```yaml
---
name: code-reviewer  # Claude infers "standard code review" behavior
description: Only check for TODO comments
---
# Agent often does full code review, ignoring instruction to only check TODOs
```

**Workaround pattern:**

```yaml
---
name: todo-finder  # Non-descriptive, prevents inference
description: Scans for TODO comments only. Nothing else.
---
# Agent follows instructions more reliably
```

**Alternative - mnemonic names:**

```yaml
name: rudy     # "Rudy the Reviewer"
name: sigma    # "Security Investigator"
name: tessa    # "Test Spec Agent"
```

**Pros:**
- Prevents Claude from overriding instructions with inferred behavior
- Can improve instruction adherence significantly

**Cons:**
- Less discoverable agent names
- Requires documentation to remember what each agent does
- May reduce automatic delegation accuracy

**Evidence:** Community reports that "as soon as you remove that meaningful keyword from the name, Claude stops trying to be 'smart' and actually follows the instructions you gave it."

---

### Approach 5: Hook-Based Orchestration

**How it works:**

Rather than relying on Claude to delegate, use hooks to enforce workflow structure externally. The Stop or SubagentStop hooks can validate that delegation occurred and block completion if it didn't.

**Hook validation example:**

```python
# hooks/validate_delegation.py
import json
import os

def check_delegation_occurred():
    """Check that agents were actually spawned, not bypassed."""

    memory_file = find_memory_file()
    if not memory_file:
        return {"decision": "block", "reason": "No MEMORY.md found - delegation may have been skipped"}

    with open(memory_file) as f:
        memory = f.read()

    # Check for agent completion markers
    required_agents = ["test-spec", "feature-implementer"]
    missing = []

    for agent in required_agents:
        if f"[{agent}]" not in memory.lower():
            missing.append(agent)

    if missing:
        return {
            "decision": "block",
            "reason": f"These agents were not invoked: {missing}. Re-run with proper delegation."
        }

    return {"decision": "approve"}
```

**Pros:**
- Deterministic enforcement
- Can't be bypassed by Claude's judgment
- Provides clear feedback on failures

**Cons:**
- Reactive, not preventive
- Requires careful marker/evidence design
- Adds complexity to workflow

**Evidence:** Hook-based validation provides "deterministic quality gates without relying on Claude remembering" to follow instructions.

---

### Approach 6: External Orchestration (Python/Bash)

**How it works:**

Since subagents cannot spawn other subagents, and commands run in the main context, an external orchestrator can chain Claude Code invocations to enforce agent usage.

**External orchestrator pattern:**

```python
#!/usr/bin/env python3
# orchestrator.py

import subprocess
import sys

def run_claude_command(command, args=""):
    """Run a Claude Code command and wait for completion."""
    result = subprocess.run(
        ["claude", "-p", f"/{command} {args}"],
        capture_output=True,
        text=True
    )
    return result.stdout

def implement_feature(feature_id):
    """Orchestrate feature implementation externally."""

    # Stage 1: Validate (main Claude)
    print(f"Validating {feature_id}...")
    run_claude_command("validate-plan", feature_id)

    # Stage 2: Test spec (forces agent via separate invocation)
    print("Running test-spec agent...")
    subprocess.run([
        "claude", "-p",
        f"Use the test-spec agent to create test specifications for {feature_id}"
    ])

    # Stage 3: Implementation (forces agent via separate invocation)
    print("Running feature-implementer agent...")
    subprocess.run([
        "claude", "-p",
        f"Use the feature-implementer agent to implement {feature_id}"
    ])

    # Stage 4: Review
    print("Running code-reviewer agent...")
    subprocess.run([
        "claude", "-p",
        f"Use the code-reviewer agent to review the implementation"
    ])

if __name__ == "__main__":
    implement_feature(sys.argv[1])
```

**Pros:**
- Complete control over workflow
- Can't be bypassed
- Works around subagent nesting limitation

**Cons:**
- Loses conversational context between stages
- More complex setup
- Each invocation starts fresh

**Evidence:** The "Orchestrator" approach uses external Python scripts to "chain Claude Code slash commands together, extracting file paths from Claude's output and passing them as context to subsequent commands."

---

### Approach 7: Parallel Task Specification

**How it works:**

Explicitly request parallel agent spawning in a single message. This pattern is useful for review phases or research tasks.

**Pattern:**

```markdown
## Stage 6: Review Loop

Spawn these review agents **in parallel** using the Task tool:

**Task 1: Code Review**
```
Task: code-reviewer

Review changes for feature: $FEATURE_ID
Changed files: [list from git diff]
Plan: docs/plans/$FEATURE/PLAN.md
```

**Task 2: Security Audit** (if auth/payment involved)
```
Task: security-auditor

Audit security for feature: $FEATURE_ID
Focus areas: [auth flows, API endpoints]
```

**Task 3: Accessibility Review** (if UI components)
```
Task: accessibility-reviewer

Review accessibility for: [component list]
Standards: WCAG 2.1 AA
```

Spawn all applicable agents in a single message, then wait for all to complete.
```

**Pros:**
- Efficient parallel execution
- Clear structure for which agents to spawn
- Reduces sequential delays

**Cons:**
- Parallelism capped at ~10 agents
- More complex coordination
- May overwhelm context with multiple returns

**Evidence:** Documentation confirms "you can run multiple subagents in parallel" and suggests patterns like "7-parallel-Task method for efficiency."

---

## Why Claude Doesn't Delegate

Based on research, Claude skips agent delegation for these reasons:

| Reason | Evidence | Solution |
|--------|----------|----------|
| **Task seems simple** | Claude judges it can do the work faster directly | Use "MUST delegate" language |
| **Vague agent descriptions** | Claude can't match task to agent | Improve description with explicit triggers |
| **No explicit delegation instruction** | Command doesn't say to spawn agents | Add explicit "Spawn agent X" instructions |
| **Agent name triggers inference** | Claude applies default behavior for `code-reviewer` | Use non-descriptive names |
| **Context already sufficient** | Claude has enough info without spawning | Structure commands to require agent expertise |
| **Token efficiency judgment** | Claude avoids overhead of spawning | Add constraints that prevent direct work |

---

## Recommendation

For the `/implement` command, use a **layered approach**:

1. **Command structure** - Use explicit spawn instructions with Task block format
2. **Agent descriptions** - Add "MUST BE USED" and "PROACTIVELY" triggers
3. **Constraints section** - Put "You are an orchestrator, NOT an implementer" at the TOP
4. **Hook validation** - Add SubagentStop hook to verify delegation occurred

**Recommended command structure:**

```markdown
---
description: Implement a planned feature with quality checks.
---

# /implement

<constraints>
You are an ORCHESTRATOR. You coordinate agents, you do NOT implement code yourself.
For each stage below, you MUST spawn the specified agent using the Task tool.
Do NOT perform implementation, testing, or review work directly.
</constraints>

## Stage 4: Test Spec

**SPAWN** the `test-spec` agent:

```
Task: test-spec

Feature: $FEATURE_ID
Plan: docs/plans/$FEATURE/PLAN.md
```

Wait for completion. Show results to user.

## Stage 5: Feature Implementation

**SPAWN** the `feature-implementer` agent:

```
Task: feature-implementer

Feature: $FEATURE_ID
Plan: docs/plans/$FEATURE/PLAN.md
Memory: docs/plans/$FEATURE/MEMORY.md
```

Wait for completion. Validate against plan.

## Stage 6: Code Review

**SPAWN** review agents in parallel:
- `code-reviewer` - Always
- `security-auditor` - If auth/API/payment involved
- `accessibility-reviewer` - If UI components
```

---

## Implementation Notes for This Codebase

### Current `/implement` Command Issues

Looking at `/home/mq/Projects/intents-plugin/intents-plugin/commands/implement.md`:

1. **Uses "Spawn" language but lacks Task block format** - Says "Spawn `test-spec` agent" but doesn't show the actual Task tool invocation format

2. **No constraints section at top** - Missing explicit "you are an orchestrator" framing

3. **Agent descriptions may lack strength** - The `feature-implementer` agent uses good language but could be stronger

### Recommended Changes

1. **Add constraints block at the top of `/implement` command:**

```markdown
<constraints>
You are an ORCHESTRATOR for this workflow.
You MUST use the Task tool to spawn each specified agent.
You do NOT write implementation code, tests, or reviews yourself.
Each stage requires spawning the designated agent.
</constraints>
```

2. **Update Stage 4 to show explicit Task format:**

```markdown
### Stage 4: Test Spec (unless --skip-tests)

**ACTION: Use the Task tool to spawn the test-spec agent.**

```
Task: test-spec

Create test specifications for: $FEATURE_ID
Plan location: docs/plans/$FEATURE/PLAN.md
```

Wait for the agent to complete and return its report.
```

3. **Update agent descriptions with stronger triggers:**

```yaml
# feature-implementer AGENT.md
---
name: feature-implementer
description: MUST BE USED for all planned feature implementation. ALWAYS spawn this agent - never implement features directly. Orchestrates chunk-by-chunk implementation with validation.
---
```

4. **Consider hook validation** to catch cases where delegation is skipped

---

## Limitation: Subagents Cannot Spawn Subagents

A critical limitation affects orchestrator design: **subagents cannot spawn other subagents**. This means:

- The `feature-implementer` agent cannot spawn `code-reviewer` agents
- All agent spawning must happen from the main thread (command context)
- The `/implement` command itself must handle the review loop, not delegate it to `feature-implementer`

**Current design issue:** The `/implement` command says "Spawn `feature-implementer` agent" and that agent is supposed to handle implementation. But if `feature-implementer` needs to spawn validation agents, it cannot. The command itself must orchestrate the full workflow.

**Workaround options:**

1. **Keep orchestration in command** - Command spawns each agent sequentially
2. **External orchestrator script** - Python/bash handles the workflow
3. **Flatten agent hierarchy** - Don't have agents that need to spawn agents

---

## Sources

### Official Documentation
- [Subagents - Claude Code Docs](https://code.claude.com/docs/en/sub-agents) - Official documentation on agent configuration and invocation patterns

### Community Guides
- [ClaudeLog - Task/Agent Tools](https://claudelog.com/mechanics/task-agent-tools/) - Detailed analysis of Task tool mechanics and delegation patterns
- [ClaudeLog - Agent Engineering](https://claudelog.com/mechanics/agent-engineering/) - "Tool SEO" concept and description optimization
- [Claude Sub-Agents: The Secret Delegation Technique](https://www.theaistack.dev/p/orchestrating-claude-sub-agents) - Analysis of why Claude doesn't delegate and solutions
- [Slash Commands vs Subagents](https://jxnl.co/writing/2025/08/29/context-engineering-slash-commands-subagents/) - When to use each approach

### Technical References
- [Fix Common Claude Code Sub-Agent Problems](https://www.arsturn.com/blog/fixing-common-claude-code-sub-agent-problems) - Non-descriptive naming workaround and other fixes
- [Sub-Agent Task Tool Limitation - GitHub Issue #4182](https://github.com/anthropics/claude-code/issues/4182) - Documentation of nested agent spawning limitation
- [The Orchestrator: Automating Claude Code Workflows](https://albertsikkema.com/ai/llm/development/productivity/2025/11/21/orchestrator-automating-claude-code-workflows.html) - External orchestration patterns

### Example Repositories
- [GitHub - wshobson/agents](https://github.com/wshobson/agents) - 99 specialized agents with tiered model selection
- [GitHub - Piebald-AI/claude-code-system-prompts](https://github.com/Piebald-AI/claude-code-system-prompts) - Reverse-engineered system prompts including Task tool
