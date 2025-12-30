# Research 005: Claude Code Stop Hooks

**Date:** 2025-12-29

**Status:** Complete

**Related:** intents-plugin harness design, agent orchestration

## Problem Statement

How can Claude Code hooks, particularly Stop hooks, be used to control agent execution in AI harness/orchestration systems? This research focuses on understanding hook types, Stop hook mechanics, and patterns for using hooks to enforce quality gates, validate agent output, and control multi-agent workflows.

## Constraints

- Hooks must work within Claude Code's lifecycle events
- Stop hooks need to avoid infinite loops when blocking agent termination
- Integration must support multi-agent orchestration (subagents via Task tool)
- Should support both command-based and prompt-based (LLM-evaluated) hooks
- Need deterministic control that doesn't rely on LLM "remembering" to do something

---

## Part 1: Hook Types Overview

Claude Code hooks are shell commands (or LLM prompts) that execute automatically at specific points in Claude Code's lifecycle. They provide **deterministic control** over agent behavior—guarantees rather than suggestions.

### Available Hook Events

| Hook Event | When It Fires | Primary Use Cases |
|------------|---------------|-------------------|
| `SessionStart` | When Claude Code starts or resumes | Load context, set env vars, install deps |
| `UserPromptSubmit` | When user submits prompt (before processing) | Validate prompts, inject context, security filtering |
| `PreToolUse` | Before tool execution | Block dangerous operations, modify tool inputs |
| `PostToolUse` | After tool completes successfully | Auto-format, logging, quick validations |
| `PermissionRequest` | When permission dialog would show (v2.0.45+) | Programmatic allow/deny decisions |
| `Stop` | When main agent finishes responding | End-of-turn quality gates, validation |
| `SubagentStop` | When a subagent (Task tool) finishes | Validate subagent output, orchestration control |
| `PreCompact` | Before context compaction | Custom compaction logic |
| `SessionEnd` | When session terminates | Cleanup, final logging |

### Hook Configuration Location

Hooks are defined in settings files:

```
~/.claude/settings.json          # User settings (global)
.claude/settings.json            # Project settings (shared)
.claude/settings.local.json      # Local project settings (not committed)
```

**Security Note:** Hook changes require review via the `/hooks` menu before taking effect. This prevents malicious hook modifications from affecting current sessions.

---

## Part 2: Stop Hooks Deep Dive

### When Stop Hooks Run

Stop hooks fire when the main Claude Code agent completes a response and is about to return control to the user. They do **not** run on user interrupts (Ctrl+C).

### Stdin Payload

Stop hooks receive JSON via stdin:

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "permission_mode": "default",
  "hook_event_name": "Stop",
  "stop_hook_active": false
}
```

Key field: `stop_hook_active` indicates whether Claude is already continuing due to a previous Stop hook block. This is critical for preventing infinite loops.

### Output Modes

#### Exit Code Communication

| Exit Code | Meaning | Behavior |
|-----------|---------|----------|
| 0 | Success | stdout shown in transcript, Claude stops normally |
| 2 | Blocking error | stderr fed back to Claude, Claude continues working |
| Other | Non-blocking error | Hook failed but Claude stops normally |

#### JSON Output (exit code 0 only)

For sophisticated control, hooks can output JSON to stdout:

```json
{
  "decision": "block",
  "reason": "Tests are failing. Please fix the errors before stopping.",
  "continue": true,
  "stopReason": "Quality gate failed",
  "suppressOutput": false,
  "systemMessage": "Running quality checks..."
}
```

**Field Meanings:**

- `decision`: "approve" (allow stop) or "block" (prevent stop)
- `reason`: Shown to Claude when blocking (so it knows what to fix)
- `continue`: If `false`, stops Claude entirely (overrides `decision`)
- `stopReason`: Message shown to user when `continue` is false
- `suppressOutput`: Hide stdout from transcript
- `systemMessage`: Optional message shown to user

### Preventing Infinite Loops

The `stop_hook_active` field prevents infinite continuation loops:

```bash
#!/bin/bash
# Read stdin
input=$(cat)
stop_hook_active=$(echo "$input" | jq -r '.stop_hook_active')

# If we're already in a continue cycle, allow the stop
if [ "$stop_hook_active" = "true" ]; then
  echo '{"decision": "approve"}'
  exit 0
fi

# Otherwise, run quality checks
if ! npm test; then
  echo '{"decision": "block", "reason": "Tests failed. Please fix them."}'
  exit 0
fi

echo '{"decision": "approve"}'
```

### Default Behavior

Stop hooks use `blocking?: false` by default to prevent infinite loops. When a Stop hook fails, it provides informational feedback without blocking Claude.

---

## Part 3: Prompt-Based Hooks

Claude Code supports prompt-based hooks (`type: "prompt"`) that use an LLM (Haiku) to evaluate decisions. **Only supported for Stop and SubagentStop hooks.**

### Configuration Example

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Evaluate if Claude has completed all requested tasks. Check if the code compiles and tests pass. Respond with 'approve' if done, 'block' with reason if more work needed. $ARGUMENTS"
          }
        ]
      }
    ]
  }
}
```

### LLM Response Format

The LLM must respond with JSON:

```json
{
  "decision": "block",
  "reason": "Task list shows 2 items incomplete. Please finish implementing the validation logic.",
  "continue": true
}
```

### Use Cases for Prompt Hooks

- **Intelligent task completion checking**: Have LLM read transcript and determine if all tasks are done
- **Quality assessment**: Evaluate if code quality meets standards
- **Context-aware decisions**: Make decisions that require understanding the conversation history

### Known Limitation

Prompt-based hooks receive only metadata via `$ARGUMENTS`. The evaluating LLM does not automatically receive transcript content. Your hook script may need to read and parse the transcript file from `transcript_path`.

---

## Part 4: SubagentStop Hooks

SubagentStop hooks fire when subagents (created via Task tool) complete. They work identically to Stop hooks but target subagent execution.

### Configuration

```json
{
  "hooks": {
    "SubagentStop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/validate_subagent.py"
          }
        ]
      }
    ]
  }
}
```

### Orchestration Use Cases

1. **Validate subagent output quality**: Check if subagent completed its specific task correctly
2. **Log subagent completion**: Track which subagents have run and their results
3. **Chain subagent results**: Use SubagentStop to determine if more subagents need to spawn
4. **Aggregate multi-subagent results**: Collect outputs from parallel subagents

---

## Part 5: AI Harness/Orchestration Patterns

### Pattern 1: Quality Gate Enforcement

Use Stop hooks to ensure code quality before Claude reports success:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "npm run lint && npm run typecheck && npm run test",
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

If any check fails with exit code 2, Claude receives the error and continues working.

### Pattern 2: Checklist Validation

Verify all tasks are complete before allowing stop:

```python
#!/usr/bin/env python3
import json
import sys
import re

input_data = json.load(sys.stdin)
transcript_path = input_data.get('transcript_path')

# Read transcript to find task list
with open(transcript_path) as f:
    content = f.read()

# Check for incomplete tasks
incomplete = re.findall(r'\[ \]', content)

if incomplete and not input_data.get('stop_hook_active'):
    print(json.dumps({
        "decision": "block",
        "reason": f"Found {len(incomplete)} incomplete tasks. Please complete all tasks before finishing."
    }))
else:
    print(json.dumps({"decision": "approve"}))
```

### Pattern 3: Multi-Agent Pipeline Control

For orchestration systems with specialized subagents:

```json
{
  "hooks": {
    "SubagentStop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/pipeline_controller.py"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/verify_pipeline_complete.py"
          }
        ]
      }
    ]
  }
}
```

### Pattern 4: Context Injection for Long-Running Agents

Use SessionStart to provide context, and Stop hooks to persist state:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "cat docs/plans/*/MEMORY.md 2>/dev/null || echo 'No active plans'"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/update_memory.py"
          }
        ]
      }
    ]
  }
}
```

---

## Part 6: Best Practices

### 1. Start Simple, Expand Gradually

Begin with a lightweight PostToolUse hook (e.g., auto-format), then add Stop hooks for quality gates as confidence grows.

### 2. Use Exit Code 2 for Blocking Failures

```bash
if ! npm test; then
  echo "Tests failed. Please fix:" >&2
  npm test 2>&1 >&2  # Show errors to Claude
  exit 2
fi
```

### 3. Always Check `stop_hook_active`

Prevent infinite loops by checking this flag:

```python
if input_data.get('stop_hook_active'):
    print('{"decision": "approve"}')
    sys.exit(0)
```

### 4. Keep Hooks Fast and Idempotent

- Default timeout is 60 seconds (configurable per command)
- Hooks should produce same result on repeated runs
- Consider caching expensive operations

### 5. Security Considerations

- Validate and sanitize all inputs
- Always quote shell variables: `"$VAR"` not `$VAR`
- Block path traversal (check for `..` in paths)
- Use absolute paths for scripts
- Skip sensitive files (.env, .git/, keys)

### 6. Complement with CI

Don't rely solely on hooks—duplicate critical checks in CI for non-interactive safety.

### 7. Version Control Your Hooks

Treat hooks as production code:
- Keep them in version control
- Test them in safe environments first
- Document expected behavior

---

## Part 7: Recommendations for intents-plugin Harness

Based on this research, here are specific recommendations for the intents-plugin multi-agent workflow:

### 1. Add Stop Hook for Plan Validation

After feature-implementer completes, verify against PLAN.md:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/validate_plan_completion.py"
          }
        ]
      }
    ]
  }
}
```

Hook script reads PLAN.md, checks all tasks marked complete, and blocks if discrepancies found.

### 2. Add SubagentStop for Implementation Chunk Validation

When implementation agents complete chunks:

```python
#!/usr/bin/env python3
# .claude/hooks/validate_chunk.py
import json, sys

data = json.load(sys.stdin)
# Parse transcript to find which chunk was implemented
# Run relevant tests for that chunk
# Block with specific feedback if tests fail
```

### 3. Use SessionStart for Memory Loading

Auto-load MEMORY.md at session start:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "cat docs/plans/*/MEMORY.md 2>/dev/null | head -100"
          }
        ]
      }
    ]
  }
}
```

### 4. Consider Prompt-Based Stop for Intelligent Validation

For complex validation that requires understanding context:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Review the implementation against the plan in docs/plans/. Verify each task is truly complete, not just 'code compiles'. Check: 1) Does the code match plan requirements? 2) Are all edge cases handled? 3) Is the MEMORY.md accurate? $ARGUMENTS"
          }
        ]
      }
    ]
  }
}
```

### 5. Gate Architecture for Feature Workflow

```
+-------------------------------------------------------------+
|                     intents-plugin Workflow                 |
+-------------------------------------------------------------+
|                                                             |
|  /plan command                                              |
|       |                                                     |
|       v                                                     |
|  +---------------------+                                    |
|  |  feature-plan       |---> SubagentStop: validate plan    |
|  +---------------------+                                    |
|       |                                                     |
|       v                                                     |
|  /implement command                                         |
|       |                                                     |
|       v                                                     |
|  +-------------------------+                                |
|  | feature-implementer     | (orchestrator)                 |
|  +-------------------------+                                |
|       |                                                     |
|       +---> Task: chunk-1 ---> SubagentStop: lint + test    |
|       +---> Task: chunk-2 ---> SubagentStop: lint + test    |
|       +---> Task: chunk-n ---> SubagentStop: lint + test    |
|       |                                                     |
|       v                                                     |
|  Stop hook: verify all chunks complete                      |
|       |                                                     |
|       v                                                     |
|  Stop hook: run full test suite                             |
|       |                                                     |
|       v                                                     |
|  Return to user (or continue if blocked)                    |
|                                                             |
+-------------------------------------------------------------+
```

---

## Part 8: Current intents-plugin Architecture (Codebase Research)

Based on codebase analysis, the current harness uses:

### Command-Agent Separation Pattern
- **Commands** (`intents-plugin/commands/*.md`): Orchestration layers defining multi-stage workflows with user checkpoints
- **Agents** (`intents-plugin/agents/*/AGENT.md`): Specialized workers spawned via Task tool

### Current Checkpoint Mechanism
- `<checkpoint>` XML blocks mark mandatory user approval points
- `STOP` keywords in commands require user input before proceeding
- Phase gates in `feature-implementer` pause between phases for manual testing
- MEMORY.md tracks session state for resumption

### Gaps That Hooks Could Address

1. **Deterministic Quality Gates**: Currently relies on Claude "remembering" to run tests. Stop hooks would guarantee it.
2. **Subagent Validation**: No automatic validation when implementation subagents complete chunks.
3. **Session Continuity**: MEMORY.md loading is manual. SessionStart hook could auto-inject.
4. **Plan Completion Verification**: Currently trust-based. Stop hook could verify against PLAN.md.

---

## Sources

### Official Documentation
- [Hooks reference - Claude Code Docs](https://docs.anthropic.com/en/docs/claude-code/hooks) - Primary documentation for hook types, configuration, and behavior
- [Claude Code power user customization: How to configure hooks](https://claude.com/blog/how-to-configure-hooks) - Official blog post on hook configuration

### Tutorials and Guides
- [Claude Code Hook Control Flow - Steve Kinney](https://stevekinney.com/courses/ai-development/claude-code-hook-control-flow) - Detailed explanation of hook control flow and exit codes
- [Use Hooks to Enforce End-of-Turn Quality Gates - JP Caparas](https://jpcaparas.medium.com/claude-code-use-hooks-to-enforce-end-of-turn-quality-gates) - Quality gate patterns with Stop hooks
- [Automate Your AI Workflows with Claude Code Hooks - GitButler](https://blog.gitbutler.com/automate-your-ai-workflows-with-claude-code-hooks) - Workflow automation patterns

### SDK and Orchestration
- [Building Agents with the Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk) - Official guide on agent harness architecture
- [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) - Patterns for multi-context-window agents

### Examples and Repositories
- [disler/claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery) - Comprehensive hook examples and patterns
- [GitButler Claude Code Hooks](https://docs.gitbutler.com/features/ai-integration/claude-code-hooks) - Real-world integration example

### Community Discussions
- [Claude Code enters infinite loop when hooks are enabled - Issue #10205](https://github.com/anthropics/claude-code/issues/10205) - Infinite loop prevention discussion
