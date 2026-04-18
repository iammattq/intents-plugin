# Agent Teams in Claude Code

> Source: https://code.claude.com/docs/en/agent-teams

## Decision Outcome (2026-04-18)

We explored agent teams as the refinement mechanism for `/intents:plan` (advocate + critic debating peer-to-peer) and **decided against it**. The `plan-critic` single-subagent approach replaced it. See `agents/plan-critic.md` and `commands/plan.md` Phase 4.

**Why:**

- Token cost: each teammate is a separate Claude instance with its own context window. For plan review — which is independent rubric application, not negotiation — this was 3-5× the cost of a single critic for marginal quality gain.
- Anthropic's docs explicitly recommend subagents ("quick, focused workers that report back") for verification/review work and reserve teams for cases where teammates must negotiate and challenge each other in real time.
- Debate shines with competing hypotheses for unknown root causes (the canonical team example). Plan critique is closer to parallel lens application, which single-pass rubric-driven critique handles well.
- Experimental status: teams require `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` and have known limitations (no session resumption, task status lag, tmux dependency for split panes).

**What we kept:** The multi-lens rubric (Code Reviewer / Security / Pragmatist / YAGNI / Design), the Refinement Summary output format, and the "concerns must include resolutions" rule — all distilled into `agents/plan-critic.md`.

The rest of this doc is the original research on how teams work and when they'd apply — still useful reference if we revisit for a different use case (e.g., multi-reviewer code review, competing-hypothesis debugging).

---

## Overview

Agent teams coordinate multiple Claude Code instances working together. One session acts as the **team lead**, coordinating work, assigning tasks, and synthesizing results. Teammates work independently, each in its own context window, and communicate directly with each other.

Unlike subagents (which run within a single session and can only report back to the main agent), you can interact with individual teammates directly without going through the lead.

**Status:** Experimental, disabled by default. Enable via `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in settings.json or environment.

## Agent Teams vs Subagents

These are two different systems. Do not conflate them.

|                   | Subagents                                        | Agent teams                                         |
| :---------------- | :----------------------------------------------- | :-------------------------------------------------- |
| **What they are** | Helper agents within a single session            | Independent Claude Code instances                   |
| **Context**       | Own context window; results return to the caller | Own context window; fully independent               |
| **Communication** | Report results back to the main agent only       | Teammates message each other directly               |
| **Coordination**  | Main agent manages all work                      | Shared task list with self-coordination             |
| **How spawned**   | `Task` tool with `subagent_type`                 | Natural language ("create a team with...")           |
| **Best for**      | Focused tasks where only the result matters      | Complex work requiring discussion and collaboration |
| **Token cost**    | Lower: results summarized back to main context   | Higher: each teammate is a separate Claude instance |

**Key distinction:** Subagents are spawned programmatically via the Task tool. Agent teams are described in natural language and Claude handles the mechanics.

## Best Use Cases for Teams

- Research and review (parallel investigation, challenge each other's findings)
- New modules or features (each teammate owns a separate piece)
- Debugging with competing hypotheses (test different theories in parallel)
- Cross-layer coordination (frontend, backend, tests each owned by a teammate)

**When NOT to use teams:** Sequential tasks, same-file edits, or work with many dependencies. Coordination overhead isn't worth it.

## Architecture

| Component     | Role                                                                                       |
| :------------ | :----------------------------------------------------------------------------------------- |
| **Team lead** | The main Claude Code session that creates the team, spawns teammates, and coordinates work |
| **Teammates** | Separate Claude Code instances that each work on assigned tasks                            |
| **Task list** | Shared list of work items that teammates claim and complete                                |
| **Mailbox**   | Messaging system for communication between agents                                          |

**Storage:**
- Team config: `~/.claude/teams/{team-name}/config.json`
- Task list: `~/.claude/tasks/{team-name}/`

## How to Create a Team

Tell Claude to create a team in natural language. Claude handles the spawning, task creation, and coordination.

**Examples from docs:**

```
I'm designing a CLI tool that helps developers track TODO comments across
their codebase. Create an agent team to explore this from different angles: one
teammate on UX, one on technical architecture, one playing devil's advocate.
```

```
Create a team with 4 teammates to refactor these modules in parallel.
Use Sonnet for each teammate.
```

```
Spawn a security reviewer teammate with the prompt: "Review the authentication
module at src/auth/ for security vulnerabilities. Focus on token handling,
session management, and input validation."
```

Claude will: create a team with shared task list → spawn teammates → have them work → synthesize findings → clean up when finished.

**You can also specify:**
- Number of teammates
- Model to use per teammate
- Whether to require plan approval before implementation

## Display Modes

- **In-process** (default): All teammates run inside the main terminal. Use `Shift+Up/Down` to select a teammate. Works in any terminal.
- **Split panes**: Each teammate gets its own pane. Requires tmux or iTerm2.

Configure:
```json
{ "teammateMode": "in-process" }  // or "tmux" or "auto" (default)
```

## Communication

Teammates message each other directly via SendMessage. Message types:
- **Direct message**: Send to one specific teammate
- **Broadcast**: Send to all teammates (use sparingly, costs scale linearly)

Messages are delivered automatically. Lead doesn't need to poll.

**Idle notifications:** When a teammate finishes a turn, the lead is automatically notified. Peer DM summaries appear in idle notifications (lead has visibility into teammate-to-teammate communication).

## Task Coordination

Shared task list that all teammates can access:
- Lead creates tasks and assigns them
- Teammates can self-claim unassigned, unblocked tasks
- Task claiming uses file locking (no race conditions)
- Tasks have states: pending → in progress → completed
- Tasks can depend on other tasks (blocked until dependencies complete)

## Plan Approval (Optional)

Require teammates to plan before implementing:
```
Spawn an architect teammate to refactor the auth module.
Require plan approval before they make changes.
```

Teammate works in read-only plan mode → sends plan approval request to lead → lead approves/rejects → teammate proceeds or revises.

## Delegate Mode

Prevents the lead from implementing tasks itself. Restricts lead to coordination-only: spawning, messaging, shutting down, and managing tasks.

Enable by pressing `Shift+Tab` after starting a team.

Useful when you want the lead to focus entirely on orchestration without touching code.

## Shutdown and Cleanup

**Shutdown:** Ask the lead to shut down specific teammates. They can approve (exit) or reject (continue working). They finish current work before shutting down.

**Cleanup:** Ask the lead to clean up. Removes shared team resources. Will fail if active teammates still exist — shut them down first. Always use the lead to clean up (not teammates).

## Permissions

Teammates start with the lead's permission settings. Can change individual teammate modes after spawning, but can't set per-teammate modes at spawn time.

## Limitations

- **No session resumption** with in-process teammates (`/resume` and `/rewind` don't restore them)
- **Task status can lag** — teammates sometimes fail to mark tasks complete
- **Shutdown can be slow** — teammates finish current request first
- **One team per session** — clean up before starting a new one
- **No nested teams** — teammates cannot spawn their own teams
- **Lead is fixed** — can't promote a teammate to lead
- **Permissions set at spawn** — all teammates start with lead's mode
- **Split panes require tmux or iTerm2** — not supported in VS Code terminal, Windows Terminal, or Ghostty

## Best Practices (from docs)

1. **Give enough context at spawn** — teammates don't inherit conversation history. Include task-specific details in the spawn prompt.
2. **Size tasks appropriately** — too small = coordination overhead exceeds benefit; too large = risk of wasted effort. Self-contained units with clear deliverables.
3. **5-6 tasks per teammate** keeps everyone productive and lets lead reassign if someone gets stuck.
4. **Start with research and review** — clear boundaries, no code writes, shows value without coordination complexity.
5. **Avoid file conflicts** — two teammates editing the same file leads to overwrites. Each teammate should own different files.
6. **Monitor and steer** — check progress, redirect approaches that aren't working, synthesize findings as they come in.

## Lessons from Our Testing

**What failed:** Spawning teammates using `Task(subagent_type: "intents:debate-advocate", team_name: ...)`. The agents couldn't SendMessage each other or write to files. They functioned as isolated subagents despite the `team_name` parameter.

**What the docs actually say:** Create teams through natural language description, not programmatic Task tool calls with custom `subagent_type`. The docs show the user describing the team ("create a team with an advocate and a critic") and Claude handling the spawning mechanics internally.

**Open question:** How does plan.md (a command file interpreted by Claude) correctly instruct the lead to create a team? Does it describe the team in natural language and let Claude choose the mechanics, or does it prescribe specific tool calls? Our first test suggests natural language is the intended approach.

## Relevance to intents-plugin

The debate workflow (advocate/critic/synthesis) maps to the "competing hypotheses" pattern from the docs:
- Advocate and critic are teammates that debate directly (genuine context separation)
- Team lead monitors for convergence, then handles synthesis
- The docs explicitly describe this pattern: "teammates test different theories in parallel and converge on the answer faster"

The purple team review pattern (cross-referencing reviewer findings) is another natural fit, matching the "research and review" use case.
