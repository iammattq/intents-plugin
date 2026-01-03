# Research 010: TodoWrite Tool and Progress Visibility in Multi-Step Agent Workflows

**Date:** 2026-01-02

**Status:** Complete

**Related:** `feature-implementer` agent progress visibility, orchestrator UX improvements

## Problem Statement

When running sub-agents like `feature-implementer` that work through multiple phases and chunks, users cannot see what phase/chunk is currently being worked on. We need to understand:

1. How TodoWrite works in Claude Code (API/format)
2. Whether sub-agents can use TodoWrite to display progress to users
3. Best practices for orchestrator agents using TodoWrite
4. Limitations in nested agent contexts

## Constraints

- Sub-agents cannot spawn other sub-agents (hard limitation)
- Sub-agents have isolated context windows
- Only final results are returned to parent agent
- Current `feature-implementer` updates MEMORY.md but users don't see real-time progress

---

## Findings

### Approach 1: TodoWrite in Main Context (Works)

**How it works:**

TodoWrite is a built-in Claude Code tool for creating and managing structured task lists. When used in the main Claude context (not a sub-agent), it displays a real-time progress UI to the user.

**Tool parameters:**

```json
{
  "todos": [
    {
      "id": "1",
      "content": "Imperative description (e.g., 'Implement hook utilities')",
      "activeForm": "Present continuous (e.g., 'Implementing hook utilities')",
      "status": "pending" | "in_progress" | "completed",
      "priority": "high" | "medium" | "low"
    }
  ]
}
```

**Key behaviors:**

1. **Complete replacement**: Each TodoWrite call provides the entire todo list - no incremental updates
2. **Single in_progress**: Exactly one task should be `in_progress` at any time (exception: parallel execution)
3. **Immediate updates**: Mark tasks completed immediately after finishing, don't batch
4. **Initialize first**: Create the complete task list as step 0, before beginning work

**Example for chunk-based implementation:**

```json
{
  "todos": [
    {"id": "1a", "content": "Chunk 1A: Hook utilities", "status": "completed", "priority": "high"},
    {"id": "1b", "content": "Chunk 1B: Config system", "activeForm": "Implementing config system", "status": "in_progress", "priority": "high"},
    {"id": "1c", "content": "Chunk 1C: Error handling", "status": "pending", "priority": "high"},
    {"id": "1d", "content": "Chunk 1D: Tests", "status": "pending", "priority": "medium"}
  ]
}
```

**Pros:**
- Real-time UI visibility to users
- Built-in to Claude Code, no setup required
- Users can see progress like "2/4 completed"
- Shows what's currently being worked on via `activeForm`

**Cons:**
- Only works in main context, not sub-agents
- Does not persist across sessions
- Large token overhead (2,167 tokens for tool description)

---

### Approach 2: Sub-Agent TodoWrite (Limited Visibility)

**How it works:**

Sub-agents DO have access to TodoWrite (confirmed in tool list from GitHub issue #4182), but their todo lists are **isolated within their context window**.

**The visibility problem:**

Sub-agents operate in isolated context windows. Only final results are returned to the parent agent. This means:

- Sub-agent's TodoWrite updates are NOT visible to the user
- Parent agent cannot see sub-agent's todo progress
- Using `ctrl-o` can expand history to see some sub-agent context, but this is not real-time

**What users see when a sub-agent runs:**

```
> /implement feature-x

✻ [Task: feature-implementer] Implementing feature...

# User sees NOTHING about internal progress
# Just waiting for completion...

✓ [Task: feature-implementer] Completed. [View Summary]
```

**Pros:**
- Sub-agents can use TodoWrite internally for their own planning
- May help sub-agent stay organized

**Cons:**
- **Users see nothing** - TodoWrite in sub-agents provides no user-facing visibility
- No real-time progress feedback
- Parent agent is unaware of sub-agent's todo state
- "Black box" behavior

**Evidence:** GitHub Issue #6007 confirms "sub-agents currently operate with full encapsulation, making their internal processes completely opaque to users."

---

### Approach 3: Parent Orchestrator TodoWrite (Recommended Pattern)

**How it works:**

Keep TodoWrite in the **parent orchestrator** (command or main context), not in sub-agents. The orchestrator updates the todo list as it spawns and receives results from sub-agents.

**Pattern for `/implement` command:**

```markdown
# /implement command

## Process

1. **Initialize TodoWrite** with all phases and chunks BEFORE spawning any agents:

   TodoWrite([
     {id: "phase1", content: "Phase 1: Infrastructure", status: "in_progress"},
     {id: "1a", content: "  Chunk 1A: Hook utilities", status: "in_progress"},
     {id: "1b", content: "  Chunk 1B: Config system", status: "pending"},
     ...
   ])

2. **Spawn feature-implementer agent** for Chunk 1A

3. **On agent completion**, update TodoWrite:
   - Mark 1A completed
   - Mark 1B in_progress

4. **Repeat** for each chunk

5. **Final update** marking all complete
```

**Implementation for feature-implementer workflow:**

```markdown
## Stage 5: Feature Implementation

### Before spawning feature-implementer:

Use TodoWrite to display the phase/chunk structure:

TodoWrite([
  {id: "p1", content: "Phase 1: Infrastructure (0/4)", status: "in_progress"},
  {id: "1a", content: "  1A: Hook utilities", status: "pending"},
  {id: "1b", content: "  1B: Config system", status: "pending"},
  {id: "1c", content: "  1C: Error handling", status: "pending"},
  {id: "1d", content: "  1D: Tests", status: "pending"},
  {id: "p2", content: "Phase 2: Core Features (0/3)", status: "pending"},
  ...
])

### For EACH chunk, the orchestrator:

1. Update TodoWrite to mark chunk in_progress
2. Spawn feature-implementer for ONE chunk
3. Wait for completion
4. Update TodoWrite to mark chunk completed
5. Proceed to next chunk

### This means feature-implementer does ONE chunk, returns, orchestrator updates progress, spawns again for next chunk.
```

**Pros:**
- Real-time user visibility
- Users see exactly which chunk is in progress
- Works with existing Claude Code architecture
- No workarounds needed

**Cons:**
- Requires orchestration to be in main context (not a sub-agent)
- Each chunk spawn has context overhead
- Orchestrator must manage the loop, not delegate it entirely

---

### Approach 4: File-Based Progress (Workaround for Sub-Agent Visibility)

**How it works:**

If you must use sub-agents for extended work, use a file-based progress mechanism that hooks can read and report.

**Pattern:**

1. Sub-agent writes progress to a known file (e.g., `.claude/progress.json`)
2. Hook reads this file and can report/block based on state
3. Parent agent can read the file between sub-agent invocations

**progress.json structure:**

```json
{
  "phase": 1,
  "phase_name": "Infrastructure",
  "chunk": "1B",
  "chunk_name": "Config system",
  "status": "in_progress",
  "completed_chunks": ["1A"],
  "total_chunks": 4,
  "percent_complete": 25
}
```

**Hook example (SubagentStop):**

```python
#!/usr/bin/env python3
import json
import sys

def main():
    # Read sub-agent completion context
    input_data = json.loads(sys.stdin.read())

    # Read progress file
    try:
        with open('.claude/progress.json') as f:
            progress = json.load(f)
    except FileNotFoundError:
        return json.dumps({"decision": "approve"})

    # Inject progress summary into parent context
    summary = f"Progress: Phase {progress['phase']} ({progress['phase_name']}), " \
              f"Chunk {progress['chunk']} - {progress['percent_complete']}% complete"

    # Using the "block with reason" pattern to inject context
    # (workaround from GitHub Issue #5812)
    return json.dumps({
        "decision": "approve",
        # Note: additionalParentContext is a proposed feature, not yet available
        # For now, the reason field in a block decision is one way to inject context
    })

if __name__ == "__main__":
    print(main())
```

**Pros:**
- Works across sub-agent boundaries
- Persistent progress state
- Can be read by hooks and external tools

**Cons:**
- Indirect - requires sub-agent to remember to update file
- No real-time UI integration
- Complex coordination required
- Still no live progress bar in Claude Code UI

---

### Approach 5: TodoWrite Orchestration Pattern (Best Practice)

**How it works:**

Based on the [TodoWrite Orchestration skill](https://claude-plugins.dev/skills/@Microck/ordinary-claude-skills/todowrite-orchestration), this is a formalized pattern for using TodoWrite in complex workflows.

**Core principles:**

1. **Initialize upfront**: Create complete task list as step 0
2. **Appropriate granularity**: 1-5 minutes per task, 8-12 tasks for 5-15 minute workflows
3. **Real-time updates**: Mark completed immediately (30-50% reduction in perceived wait time)
4. **Single in_progress**: One task active at a time (except parallel execution)
5. **Visible iterations**: For loops, track each iteration separately

**Example for chunk implementation:**

```
User sees:
[x] PHASE 1: Infrastructure (2/4 complete)
    [x] Chunk 1A: Hook utilities
    [->] Chunk 1B: Config system (in_progress)
    [ ] Chunk 1C: Error handling
    [ ] Chunk 1D: Tests
[ ] PHASE 2: Core Features (0/3)
[ ] PHASE 3: Integration (0/2)
```

**Recommended workflow structure:**

```markdown
# Orchestrator Pattern

## Step 0: Initialize Progress
TodoWrite with ALL phases and chunks visible upfront

## For each phase:
  ### For each chunk:
    1. TodoWrite: Mark chunk in_progress
    2. EITHER:
       a. Do the work directly (if orchestrator has capacity)
       b. Spawn specialized agent for just this chunk
    3. TodoWrite: Mark chunk completed
    4. Continue to next chunk

## Final: Mark all complete
```

**Pros:**
- Best user experience
- Clear visibility at all times
- Users know full scope upfront
- Matches user expectations for progress tracking

**Cons:**
- Requires orchestrator to manage granular updates
- Token overhead for each TodoWrite call
- Cannot fully delegate multi-chunk work to a single sub-agent

---

## Critical Limitation: Sub-Agent Visibility Is a Known Gap

Multiple GitHub issues document this limitation:

| Issue | Title | Status |
|-------|-------|--------|
| #5812 | Context Bridging Between Sub-Agents and Parent | Open |
| #6007 | View and Navigate Sub-agent Task Sessions | Closed (dup of #5974) |
| #5974 | UI for Subagent Execution Transparency | Open |
| #4182 | Sub-Agent Task Tool Not Exposed | Closed (dup) |

**The fundamental problem:** Sub-agents are "fire-and-forget" tools with opaque execution. There is currently no official mechanism for sub-agents to communicate progress back to users in real-time.

**Workarounds documented in Issue #5812:**

1. **Direct feedback loop**: Use `{"decision": "block", "reason": "summary"}` in SubagentStop hook to inject summary into parent context
2. **State file decoupling**: SubagentStop saves to file, UserPromptSubmit reads and injects
3. **Git side-effects**: Auto-commit changes, parent runs `git status` to discover

None of these provide real-time UI progress visibility.

---

## Recommendation

For the `feature-implementer` workflow, use **Approach 3 (Parent Orchestrator TodoWrite)** with modifications:

### Recommended Architecture

**Current (problematic):**
```
/implement command
  └── spawns feature-implementer (does ALL chunks)
        └── updates MEMORY.md (user doesn't see)
```

**Recommended:**
```
/implement command (manages TodoWrite)
  ├── TodoWrite: Initialize all phases/chunks
  ├── For each chunk:
  │     ├── TodoWrite: Mark chunk in_progress
  │     ├── Spawn general-purpose agent for THIS chunk only
  │     ├── Wait for completion
  │     └── TodoWrite: Mark chunk completed
  └── TodoWrite: All complete
```

### Key Changes

1. **Move orchestration to the command level**, not feature-implementer agent
2. **Spawn agents per-chunk**, not for entire implementation
3. **Update TodoWrite between each agent spawn**
4. **Use feature-implementer as a single-chunk worker**, not a multi-chunk orchestrator

### Implementation Notes

The `/implement` command should:

1. Read the plan to get all phases and chunks
2. Initialize TodoWrite with the full structure
3. Loop through chunks, spawning `general-purpose` or `feature-implementer` for each
4. Update TodoWrite after each completion
5. Continue until all chunks done

If `feature-implementer` must remain a multi-chunk agent:

1. Have it update a `.claude/progress.json` file after each chunk
2. Add a SubagentStop hook to read this file and report progress
3. Accept that this won't provide real-time UI updates, only end-of-agent summaries

---

## Sources

### Official Documentation
- [Todo Lists - Claude Docs](https://platform.claude.com/docs/en/agent-sdk/todo-tracking) - SDK documentation for todo tracking
- [Subagents - Claude Code Docs](https://code.claude.com/docs/en/sub-agents) - Official subagent documentation

### GitHub Issues
- [Sub-Agent Task Tool Not Exposed (Issue #4182)](https://github.com/anthropics/claude-code/issues/4182) - Confirms sub-agents cannot spawn sub-agents
- [Context Bridging Feature Request (Issue #5812)](https://github.com/anthropics/claude-code/issues/5812) - Workarounds for parent-subagent communication
- [View Sub-agent Sessions (Issue #6007)](https://github.com/anthropics/claude-code/issues/6007) - Documents visibility limitations

### Community Resources
- [Agent Design Lessons from Claude Code](https://jannesklaas.github.io/ai/2025/07/20/claude-code-agent-design.html) - TodoWrite patterns and agent design
- [Claude Code Built-in Tools Reference](https://www.vtrivedy.com/posts/claudecode-tools-reference) - TodoWrite parameters documentation
- [TodoWrite Orchestration Skill](https://claude-plugins.dev/skills/@Microck/ordinary-claude-skills/todowrite-orchestration) - Best practices for progress visibility
- [ClaudeLog - Task/Agent Tools](https://claudelog.com/mechanics/task-agent-tools/) - Detailed Task tool mechanics
- [Claude Code System Prompts (GitHub)](https://github.com/Piebald-AI/claude-code-system-prompts) - Extracted system prompts including TodoWrite
