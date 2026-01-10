# Research 002: Best-in-Class Claude Code Agents

**Date:** 2025-12-26

**Status:** Complete

**Related:** Agent architecture for intents-plugin

## Problem Statement

How do we create best-in-class Claude Code agents? This research covers agent architecture, AGENT.md structure, agent-skill interaction, command integration, and patterns from real-world implementations.

## Constraints

- Agents must work within Claude Code's context window limitations
- Must integrate with `.claude/agents/` directory structure
- Should follow official Anthropic patterns
- Need to balance capability with cost (model selection)
- Must support both automatic and explicit invocation

---

## Part 1: Agent Architecture & Structure

### What Are Agents (Subagents)?

Agents are specialized AI assistants with **isolated context windows** that Claude delegates tasks to. Unlike the main conversation, each agent:

- Starts fresh without conversation history
- Has its own context window separate from the parent
- Returns only compressed/relevant findings to the orchestrator
- Can be configured with specific tools and system prompts

**Key benefits:**
1. **Context Preservation** - Main conversation stays clean
2. **Parallelization** - Multiple agents can work simultaneously
3. **Specialization** - Fine-tuned prompts for specific domains
4. **Reusability** - Share across projects and teams

### File Locations

| Type | Location | Scope | Priority |
|------|----------|-------|----------|
| Project agents | `.claude/agents/` | Current project | Highest |
| User agents | `~/.claude/agents/` | All projects | Lower |
| Plugin agents | `<plugin>/agents/` | Plugin-specific | Lowest |

Project-level agents override user-level agents with the same name.

### Agent File Structure

**Important:** Agents are **flat markdown files**, not folders. Use `agents/code-reviewer.md`, NOT `agents/code-reviewer/AGENT.md`. The folder structure is for Skills only.

| Type | Structure | Example |
|------|-----------|---------|
| Agents | Flat file | `agents/code-reviewer.md` |
| Skills | Folder with SKILL.md | `skills/my-skill/SKILL.md` |

```yaml
---
name: agent-name
description: Use WHEN [trigger]. Does [what]. Specialized for [domain]. [Access level]-only.
tools: Read, Grep, Glob
model: haiku
permissionMode: default
skills: skill1, skill2
---

You are a [role]. Begin responses with: `[EMOJI AGENT NAME]`

[Read-only | Full access] - [what you do/don't do].

## Before Starting
[Prerequisites: files to read, context to gather]

## Process
1. **Phase 1** - [Clear action]
2. **Phase 2** - [Clear action]
3. **Phase 3** - [Clear action]

## Checklist (for reviewers)
### Category 1
- [ ] Specific verifiable item
- [ ] Another item with clear criteria

## Output Format
## Summary
[1-2 sentences: main finding]

## Findings
### Category
- `file.tsx:42` - Finding with location
  - Context: [why it matters]
  - Fix: [guidance]

## Verdict (if applicable)
[Clear recommendation]
```

### Frontmatter Fields

| Field | Required | Description | Default |
|-------|----------|-------------|---------|
| `name` | Yes | Unique identifier (lowercase, hyphens only) | - |
| `description` | Yes | When to invoke + what it does | - |
| `tools` | No | Comma-separated tool list | Inherits all |
| `model` | No | `haiku`, `sonnet`, `opus`, or `inherit` | Configured default |
| `permissionMode` | No | `default`, `acceptEdits`, `bypassPermissions`, `plan`, `ignore` | `default` |
| `skills` | No | Comma-separated skill names to auto-load | None |

### Model Selection Guide

| Model | Use For | Speed | Cost |
|-------|---------|-------|------|
| `haiku` | Pattern matching, simple checks, scaffolding, scouts | Fastest | Lowest |
| `sonnet` | Code review, security audit, standard implementation | Balanced | Medium |
| `opus` | Orchestrators, complex protocols, deep reasoning | Slower | Highest |
| `inherit` | Research needing parent's full context | Variable | Variable |

**Selection rules:**
- Design review, pattern scanning -> `haiku`
- Code review, security audit -> `sonnet`
- Codebase research, exploration -> `inherit`
- **Orchestrators that spawn/validate agents -> `opus`**

**Why Opus for orchestrators?** According to Anthropic, Opus "requires fewer steps" and "follows instructions more effectively." For multi-step protocols where skipping validation is catastrophic, the instruction adherence justifies the cost.

**Haiku performance note:** Claude Haiku 4.5 achieves "90% of Sonnet 4.5's performance" ([Augment evaluation](https://www.anthropic.com/news/claude-haiku-4-5)) while running "4-5x faster at a fraction of the cost" - making it optimal for lightweight, frequently-invoked agents.

### Tool Permission Patterns

```yaml
# Read-only (reviewers, auditors)
tools: Read, Grep, Glob

# Review with command execution (git, tests)
tools: Read, Grep, Glob, Bash

# Research with web access
tools: Read, Grep, Glob, Bash, WebFetch, WebSearch

# Can spawn other agents (orchestrators)
tools: Read, Grep, Glob, Bash, Task, Write, Edit

# Full access (rarely appropriate)
tools: *
```

**IMPORTANT:** If you omit `tools`, the agent inherits **all available tools**, including MCP tools. Always explicitly scope tools to minimum needed.

---

## Part 2: Agent Archetypes

### 1. Reviewer Agent (Read-Only)

**Purpose:** Evaluate code/content against standards, report findings.

```yaml
---
name: code-reviewer
description: Use AFTER implementing code. Reviews for quality and patterns. Read-only.
tools: Read, Grep, Glob, Bash
model: sonnet
---

You are a code reviewer. Begin responses with: `[CODE REVIEWER]`

Read-only - report findings, never modify code.

## Process
1. **Gather context** - Read plan/spec, run `git diff --name-only`
2. **Review systematically** - Work through checklist
3. **Report findings** - Use output format with file:line refs

## Checklist
[Domain-specific items]

## Output Format
## Summary
[1-2 sentences: assessment and merge readiness]

## Issues Found
### Critical (must fix)
- **[Category]** `file.tsx:42` - Issue description
  - Suggested fix: [guidance]

## Verdict
[Approved | Changes requested]
```

**Key characteristics:**
- Read-only tools
- Model: `sonnet` (needs reasoning for quality assessment)
- Always includes checklist
- Always includes verdict

### 2. Research Agent

**Purpose:** Explore unfamiliar code, return compressed findings.

```yaml
---
name: codebase-researcher
description: Use BEFORE planning to explore unfamiliar code. Returns compressed findings.
tools: Read, Grep, Glob, Bash
model: inherit
---

You explore codebases and return compressed, actionable findings.

## Core Principles
- Read extensively, report concisely (50+ files -> 200-400 words)
- Epistemic honesty - say "likely" not "definitely" when inferring
- No modifications - just report what exists

## Process
### Phase 1: Planning
- What questions need answering?
- What file patterns might be relevant?

### Phase 2: Exploration
- Start broad with Glob, narrow with Read
- Parallelize when possible
- Stop early if question answered

### Phase 3: Synthesis
Compile into structured report.

## Output Format
## Summary
[2-3 sentences: main answer]

## Key Findings
### Finding Title
- **Location**: `path/to/file.ts:42-67`
- **Pattern**: What you found
- **Relevance**: Why it matters
```

**Key characteristics:**
- Model: `inherit` (needs same reasoning as parent)
- Compression is critical (extensive reading -> brief output)
- No modifications allowed

### 3. Scout Agent

**Purpose:** Find patterns, candidates for extraction.

```yaml
---
name: pattern-scout
description: Find repeated patterns that should be extracted. Scans for duplication.
tools: Read, Grep, Glob
model: haiku
---

You find extraction opportunities. Begin responses with: `[SCOUT]`

Read-only - find patterns, never create implementations.

## Detection Strategies
- Repeated class combinations: `rounded.*shadow.*p-`
- Similar component files: `*Card*.tsx`, `*Button*.tsx`
- Hardcoded values (token candidates): `#[0-9a-fA-F]{6}`

## Evaluation Criteria
| Strong Candidate | Weak Candidate |
|------------------|----------------|
| 3+ occurrences | 1-2 occurrences |
| Multi-element | Single element |
| Consistent | Divergent |

## Output Format
## High-Priority Candidates
### Pattern Name
**Frequency**: X locations
**Evidence**:
- `file.tsx:24` - `<span className="...">`
**Impact**: High - X files simplified
```

**Key characteristics:**
- Model: `haiku` (pattern matching, not deep reasoning)
- Fast and cheap for frequent invocation
- Quantified evidence

### 4. Orchestrator Agent

**Purpose:** Coordinate multi-step workflows, spawn and validate sub-agents.

```yaml
---
name: feature-implementer
description: Use WHEN ready to implement a planned feature. Orchestrates chunks, spawns agents, validates against plan.
tools: Read, Grep, Glob, Bash, Task, Write, Edit
model: opus
---

## CRITICAL: Validation Protocol
[Most important instructions AT TOP]

<checkpoint>
STOP. Before proceeding:
[ ] Did I verify X?
[ ] Did I check Y?
</checkpoint>

## Your Role
You are the **orchestrator**, not the implementer. You:
1. Read plans to understand state
2. Spawn focused implementation agents
3. **Validate agent work against plan**
4. Update memory with progress
5. Repeat until complete

**You do NOT write implementation code yourself.**

## Process
[Multi-phase workflow...]

## Validation Report Format
### Chunk [X] Validation
- [x] Task 1 - Verified: [specific evidence]
- [ ] Task 2 - FAILED: [what's wrong]
```

**Key characteristics:**
- Model: `opus` (critical for instruction adherence)
- **CRITICAL section at top** - LLMs prioritize beginning/end of prompts
- Explicit checkpoints with stop signals
- Validation-focused, not implementation-focused
- Can spawn other agents via Task tool

---

## Part 3: Agent-Skill Interaction

### Skills vs Agents

| Aspect | Skills | Agents |
|--------|--------|--------|
| Context | Main conversation | Isolated window |
| Invocation | Auto-discovered by Claude | Auto-delegated or explicit |
| Structure | SKILL.md + optional resources | AGENT.md (single file) |
| Use case | Domain expertise, patterns | Research, review, orchestration |
| Tool access | Can restrict | Can restrict |

### When to Use Skills

Skills are better when:
- Knowledge should persist in main conversation
- No need for isolated context
- Domain expertise for current work (patterns, guidelines)
- Progressive disclosure is valuable

### When to Use Agents

Agents are better when:
- Extensive reading would pollute main context
- Task can run in parallel with others
- Specialized toolset needed
- Results should be compressed

### Auto-Loading Skills in Agents

```yaml
---
name: feature-implementer
skills: coding-standards, testing-guidelines
---
```

The `skills` field auto-loads specified skills when the agent starts, providing domain expertise without re-reading skill files.

---

## Part 4: Command Integration

### How Commands Invoke Agents

Commands can spawn agents for specialized work:

```markdown
# /implement-feature command

## Phase 1: Research
Spawn `codebase-researcher` agent to explore existing patterns.
[Agent returns compressed findings]

## Phase 2: Implementation
Spawn `feature-implementer` agent with research context.
[Agent implements chunk by chunk]

## Phase 3: Review
Spawn review agents:
- `code-reviewer` - Always
- `security-auditor` - If auth/API involved
```

### Invocation Methods

**1. Automatic Delegation**

Claude routes tasks to agents based on:
- Task description in request
- Agent `description` field
- Current context and available tools

To encourage proactive use, include "Use PROACTIVELY" or "MUST BE USED" in descriptions.

**2. Explicit Invocation**

```
Use the code-reviewer agent to review my changes
Have the security-auditor examine the auth module
```

**3. Programmatic Spawning**

From an orchestrator agent:

```markdown
Task: codebase-researcher

Research the feature structure of this codebase.

Questions to answer:
1. What are the main user-facing features?
2. How are features organized?

Return a concise list with locations.
```

### Built-in Agents

Claude Code includes built-in agents:

| Agent | Model | Purpose | Tools |
|-------|-------|---------|-------|
| General-Purpose | Sonnet | Complex tasks with read/write | All |
| Plan | Sonnet | Research during plan mode | Read-only |
| Explore | Haiku | Fast codebase searching | Read-only |

**Explore subagent** is optimized for rapid file discovery. Claude automatically delegates when searching without needing modifications.

---

## Part 5: Best Practices

### Description Writing

The description is critical for automatic invocation. Use this formula:

```
Use WHEN [trigger condition]. Does [what]. Specialized for [domain]. [Access level].
```

**Good:**
```yaml
description: Use AFTER implementing code. Reviews for quality, patterns, and issues. Specialized for Next.js 15, TypeScript, Tailwind. Read-only.
```

**Bad:**
```yaml
description: Reviews code
```

### Prompt Structure

**1. Put critical instructions at the TOP**

LLMs prioritize the beginning and end of prompts. Your most important rules (validation protocols, safety constraints) should be first.

**2. Use checkpoints for orchestrators**

```markdown
<checkpoint>
STOP. Before proceeding:
[ ] Did I re-read the plan?
[ ] Did I verify actual files?
[ ] For each task: does CODE match PLAN?
</checkpoint>
```

**3. Include positive and negative examples**

```markdown
## What "Verified" Means

| Wrong | Right |
|-------|-------|
| "Agent said it's done" | "I read the file and confirmed X behavior" |
| "Lint passes" | "Code at line 45 implements the animation per plan" |
```

**4. Provide output templates**

Every agent should have a structured output format. This ensures:
- Consistent results
- Easy parsing by parent agent
- Clear communication with users

### Single Responsibility

Each agent should have ONE clear goal:

**Good:**
- `code-reviewer` - Reviews code quality
- `security-auditor` - Deep security analysis
- `test-runner` - Runs and fixes tests

**Bad:**
- `code-helper` - Reviews, fixes, tests, documents (too broad)

### Delegation Patterns

Agents can recommend other specialized agents:

```markdown
## Delegate When Needed

- **Security concerns?** -> Recommend security-auditor
- **Design system issues?** -> Recommend design-reviewer
- **Need deep research?** -> Recommend codebase-researcher
```

### Error Handling

Include guidance for edge cases:

```markdown
## If No Issues Found
Report "No issues found" with confidence level:
- High: Comprehensive review completed
- Medium: Some areas not accessible
- Low: Limited scope reviewed

## If Blocked
1. Log the blocker
2. Report to user with context
3. Ask: Fix now? Skip? Pause?
```

---

## Part 6: Anti-Patterns to Avoid

### Description Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Vague: "Helps with code" | Specific: "Use WHEN reviewing auth flows. Deep security analysis." |
| Missing trigger: "Security expert" | Include trigger: "Use AFTER implementing auth/payment code" |
| No access level | Include: "Read-only" or "Full access" |

### Tool Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Omit `tools` for reviewer | `tools: Read, Grep, Glob` (explicit read-only) |
| Grant `Write` to auditors | Keep reviewers read-only |
| Use `tools: *` | Scope to minimum needed |

### Model Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| `model: opus` for simple pattern matching | `model: haiku` |
| `model: haiku` for orchestrators | `model: opus` (instruction adherence) |
| `model: inherit` when different reasoning needed | Specify appropriate model |

### Prompt Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Put critical rules at bottom | Put critical rules at TOP |
| No output format | Always define output structure |
| Over-explain to Claude | Be concise, Claude is smart |
| Missing checkpoints in orchestrators | Add explicit STOP checkpoints |

### Architecture Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Monolithic agents (PM + Architect + Implementer) | Single responsibility per agent |
| Missing DoD checkpoints | Include completion criteria |
| No human approval gates | Add strategic approval points |
| Infinite nesting | Subagents cannot spawn subagents (enforced) |

---

## Part 7: Advanced Patterns

### Parallel Agent Spawning

From an orchestrator:

```markdown
## Phase 2: Parallel Research

Spawn these agents **in parallel**:

**1. Feature Mapping**
Task: codebase-researcher
[Research feature structure...]

**2. Capability Discovery**
Task: codebase-researcher
[Research reusable capabilities...]

**3. Entity Identification**
Task: codebase-researcher
[Research domain entities...]
```

### Chaining Agents

Sequential handoff:

```
First use the code-analyzer agent to find performance issues,
then use the optimizer agent to fix them
```

### Resumable Agents

Agents can be resumed to continue previous work:

```markdown
# Initial invocation returns agentId: "abc123"
Use the code-analyzer agent to start reviewing authentication

# Resume later
Resume agent abc123 and analyze the authorization logic
```

### Hook-Based Chaining

For production workflows, use hooks to orchestrate handoffs:

```json
{
  "hooks": {
    "SubagentStop": [
      {
        "command": "python .claude/hooks/suggest-next.py"
      }
    ]
  }
}
```

Register both `SubagentStop` and `Stop` events to reliably catch completion.

---

## Part 8: Testing Agents

### Validation Checklist

1. **Test in isolation** - Spawn agent with representative task
2. **Verify output format** - Does it follow the template?
3. **Check tool usage** - Using only allowed tools?
4. **Measure context efficiency** - Concise output from extensive reading?
5. **Test edge cases** - What if nothing found? Multiple issues?

### Iteration Process

When agents underperform:

1. Provide structured feedback: what went wrong, what should happen
2. Share the `.md` file so Claude can suggest modifications
3. Version control agent files to maintain history
4. Test changes with representative tasks

---

## Part 9: Real-World Examples

### Example 1: Code Reviewer (from this project)

```yaml
---
name: code-reviewer
description: Use AFTER implementing code. Proactively reviews for quality, patterns, and issues. Specialized for Next.js 15, TypeScript, Tailwind. Delegates to security-auditor and design-reviewer for deep dives. Read-only.
tools: Read, Grep, Glob, Bash
model: sonnet
---

You are a senior code reviewer for Next.js 15, TypeScript, and Tailwind codebases. Begin responses with: `[CODE REVIEWER]`

Read-only - report findings, never modify code.

## Process
1. **Gather context** - Read plan/spec if provided, run `git diff --name-only`
2. **Review against checklist** - Work through systematically
3. **Report findings** - Use output format with file:line references

## Checklist

### Next.js 15
- [ ] `params`/`searchParams` awaited (they're Promises in Next.js 15)
- [ ] Route handlers use Promise params
- [ ] `'use client'` only where necessary

### TypeScript
- [ ] No `any` types
- [ ] Props interfaces defined

## Output Format
## Summary
[1-2 sentences: assessment and merge readiness]

## Issues Found
### Critical (must fix)
- **[Category]** `file.tsx:42` - Issue description
  - Suggested fix: [guidance]

## Verdict
[Approved | Changes requested]
```

**What makes this effective:**
- Clear trigger condition ("Use AFTER implementing")
- Specific domain ("Next.js 15, TypeScript, Tailwind")
- Delegation guidance ("Delegates to security-auditor...")
- Access level stated ("Read-only")
- Concrete checklist with framework-specific items
- Structured output with severity levels

### Example 2: Orchestrator (from this project)

```yaml
---
name: codebase-analyzer
description: Bootstrap .intents/ folder from existing codebase. Orchestrator that spawns parallel codebase-researcher agents to explore different branches, then compiles findings into graph files.
tools: Read, Grep, Glob, Bash, Task, Write
model: opus
---

# Codebase Analyzer

Begin responses with: `[CODEBASE ANALYZER]`

You bootstrap the `.intents/` graph from an existing codebase.

## Your Role
1. Get a birds-eye view of the project structure
2. Spawn **parallel** `codebase-researcher` agents to explore different areas
3. Each researcher returns compressed findings (200-400 words)
4. Compile all findings into `.intents/` graph files
5. Present to user for review before writing

## Phase 2: Parallel Research

Spawn `codebase-researcher` agents for each major area. Run them in **parallel**:

**1. Feature Mapping**
Task: codebase-researcher

Research the feature structure of this codebase.
[Detailed instructions...]

**2. Capability Discovery**
Task: codebase-researcher

Research the reusable capabilities in this codebase.
[Detailed instructions...]

## Phase 4: Present for Review

Show the user the generated graph **before writing**.
```

**What makes this effective:**
- Clear orchestration role ("spawns parallel agents")
- Explicit parallelization instructions
- Compressed output requirements ("200-400 words")
- Human approval gate before writing
- Model: `opus` for complex multi-step protocol

---

## Recommendations

### For This Project (intents-plugin)

1. **Current agents are well-structured** - The existing agents follow best practices with clear descriptions, appropriate model selection, and structured outputs.

2. **Enhance validation protocols** - The feature-implementer already has strong validation checkpoints. Consider adding similar explicit checkpoints to other orchestrator agents.

3. **Add proactive invocation hints** - For agents that should run automatically, consider adding "PROACTIVELY" or "MUST BE USED" to descriptions.

4. **Consider agent testing** - Create a testing pattern for validating agent behavior before deployment.

### General Best Practices

1. **Start minimal** - Begin with simple agents, add complexity only when needed
2. **Match model to task** - Use haiku for simple, sonnet for standard, opus for orchestration
3. **Scope tools explicitly** - Never rely on implicit tool inheritance
4. **Put critical rules first** - Top of prompt gets highest attention
5. **Include output formats** - Every agent needs structured output
6. **Add checkpoints for orchestrators** - Explicit STOP points prevent skipped steps
7. **Test incrementally** - Validate each agent before building workflows on it

---

## Sources

### Official Documentation
- [Subagents - Claude Code Docs](https://code.claude.com/docs/en/sub-agents) - Official subagent documentation with AGENT.md format
- [Agent Skills - Claude Code Docs](https://code.claude.com/docs/en/skills) - Official skills documentation
- [Slash commands - Claude Code Docs](https://code.claude.com/docs/en/slash-commands) - Command integration

### Anthropic Engineering
- [Claude Code: Best practices for agentic coding](https://www.anthropic.com/engineering/claude-code-best-practices) - Official best practices from Anthropic
- [Building agents with the Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk) - Multi-agent patterns
- [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) - Skills architecture

### Community Guides
- [Claude Code customization guide](https://alexop.dev/posts/claude-code-customization-guide-claudemd-skills-subagents/) - Comprehensive customization guide
- [Claude Agent Skills: A First Principles Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/) - Technical architecture analysis
- [Best practices for Claude Code sub-agents](https://www.pubnub.com/blog/best-practices-for-claude-code-sub-agents/) - Pitfalls and solutions
- [ClaudeLog - Custom Agents](https://claudelog.com/mechanics/custom-agents/) - Custom agent documentation
- [ClaudeLog - Task/Agent Tools](https://claudelog.com/mechanics/task-agent-tools/) - Task tool mechanics

### Example Repositories
- [GitHub - wshobson/agents](https://github.com/wshobson/agents) - 99 specialized agents, multi-agent orchestration patterns
- [GitHub - lst97/claude-code-sub-agents](https://github.com/lst97/claude-code-sub-agents) - Collection of specialized subagents
- [GitHub - anthropics/skills](https://github.com/anthropics/skills) - Official Anthropic skills repository

---

## Appendix: Evidence Validation

This section documents the evidence basis for claims in this research, including verification status and uncertainty notes.

### ✅ Fully Verified Claims

| Claim | Evidence |
|-------|----------|
| **AGENT.md frontmatter fields** (name, description, tools, model, permissionMode, skills) | [Official Claude Code docs](https://code.claude.com/docs/en/sub-agents) - exact specification |
| **Model options: haiku, sonnet, opus, inherit** | Official docs confirm these exact aliases |
| **Tool inheritance: omitting `tools` inherits ALL including MCP** | Official docs + [PubNub](https://www.pubnub.com/blog/best-practices-for-claude-code-sub-agents/): "If you omit `tools`, the subagent inherits the thread's tools (including MCP)" |
| **Skills vs Agents context isolation** | [Official skills docs](https://code.claude.com/docs/en/skills): Skills are "model-invoked" in main context; agents have isolated windows |
| **LLMs prioritize beginning/end of prompts** | [Stanford/Berkeley research](https://arxiv.org/html/2406.15981v1): "Lost in the Middle" phenomenon confirmed |
| **Opus > Sonnet > Haiku instruction adherence** | Multiple sources confirm hierarchy; Opus "requires fewer steps" |
| **File locations: .claude/agents/ and ~/.claude/agents/** | Official docs: project-level overrides user-level |
| **Haiku achieves ~90% of Sonnet 4.5 performance** | [Anthropic announcement](https://www.anthropic.com/news/claude-haiku-4-5): "achieves 90% of Sonnet 4.5's performance" (Augment's agentic coding evaluation) |
| **Haiku runs 4-5x faster than Sonnet 4.5** | [Anthropic announcement](https://www.anthropic.com/news/claude-haiku-4-5): "runs up to 4-5 times faster than Sonnet 4.5" |
| **Opus uses fewer steps/tokens than Sonnet** | [Anthropic Opus 4.5 announcement](https://www.anthropic.com/news/claude-opus-4-5): Multiple partner quotes confirm "requires fewer steps", "uses up to 65% fewer tokens" |
| **Opus effective at multi-agent orchestration** | [Anthropic Opus 4.5](https://www.anthropic.com/news/claude-opus-4-5): "very effective at managing a team of subagents" |
| **Description field triggers proactive invocation** | [Official docs](https://code.claude.com/docs/en/sub-agents): "include phrases like 'use PROACTIVELY' or 'MUST BE USED' in your description field" |

### ⚠️ Verified with Caveats

| Claim | Status | Notes |
|-------|--------|-------|
| **"Use opus for orchestrators"** | **Verified pattern, not official doctrine** | Anthropic confirms Opus is "effective at managing subagents" and has better instruction adherence. The [wshobson/agents](https://github.com/wshobson/agents) repo uses Opus for "critical architecture" (Tier 1). This is a well-supported inference, not explicit Anthropic guidance. |
| **Checkpoint/STOP patterns** | **Community best practice** | Not in official Anthropic docs but widely recommended: [Arize](https://arize.com/blog/claude-md-best-practices-learned-from-optimizing-claude-code-with-prompt-learning/), [Medium articles](https://alirezarezvani.medium.com/claude-code-rewind-5-patterns-after-a-3-hour-disaster-a9de9bce0372). "plan-validate-execute" pattern is established. |
| **Description formula: "Use WHEN [trigger]..."** | **Partially official** | Official docs show examples like "Use immediately after writing code" and "Use proactively when encountering issues". The exact formula is a synthesis, but the pattern is grounded in official examples. |

### 📝 Uncertainty Notes

#### Model Selection for Orchestrators

**Claim**: Use `opus` for orchestrators that spawn/validate other agents.

**Evidence strength**: Strong inference, not doctrine.

- ✅ Anthropic says Opus is "very effective at managing a team of subagents"
- ✅ Opus "requires fewer steps" and uses "up to 65% fewer tokens"
- ✅ wshobson/agents uses Opus for "critical architecture, security, ALL code review"
- ⚠️ No official Anthropic statement says "always use Opus for orchestrators"

**Recommendation**: Use Opus for orchestrators when instruction adherence is critical. For simpler coordination, Sonnet may suffice.

#### Haiku Performance Claims

**Original claim**: "90% of Sonnet's agentic coding performance at 2x speed and 3x cost savings"

**Corrected evidence**:
- ✅ 90% of Sonnet 4.5 performance - [Anthropic](https://www.anthropic.com/news/claude-haiku-4-5) (Augment evaluation)
- ✅ 4-5x faster than Sonnet 4.5 - [Anthropic](https://www.anthropic.com/news/claude-haiku-4-5)
- ✅ ~1/3 the cost of Sonnet 4 - [Anthropic](https://www.anthropic.com/news/claude-haiku-4-5)

**Note**: Original "2x speed" was understated; actual is 4-5x.

#### Checkpoint Placement in Prompts

**Claim**: Put `<checkpoint>` blocks with explicit STOP signals for orchestrators.

**Evidence strength**: Community best practice, not official.

- ✅ "Lost in the Middle" research supports placing critical info at beginning/end
- ✅ Multiple community guides recommend explicit checkpoints
- ✅ [Anthropic best practices](https://www.anthropic.com/engineering/claude-code-best-practices): "Steps #1-#2 are crucial—without them, Claude tends to jump straight to coding"
- ⚠️ No official Anthropic guidance on `<checkpoint>` XML tags specifically

**Recommendation**: Use checkpoint patterns, but the exact syntax is flexible. Key principle is explicit stopping points, not specific tag format.

#### Description Writing Formula

**Claim**: Use format `Use WHEN [trigger]. Does [what]. Specialized for [domain]. [Access level].`

**Evidence strength**: Synthesis of official patterns.

**Official examples from docs**:
- "Expert code reviewer. Use immediately after writing or modifying code."
- "Debugging specialist for errors. Use proactively when encountering any issues."
- "Data analysis expert. Use proactively for data analysis tasks."

**Pattern derived**: The formula synthesizes these examples. Key elements are:
1. Role/expertise statement
2. Trigger condition ("Use when...", "Use proactively...")
3. Domain specificity

**Recommendation**: Follow the pattern but don't treat it as rigid. The core principle is clear triggers + specific domain.

---

## Validation Summary

| Category | Count | Confidence |
|----------|-------|------------|
| Fully verified | 12 claims | High - direct official sources |
| Verified with caveats | 3 claims | Medium-High - well-supported inference |
| Uncertain areas | 4 areas | Medium - community patterns, not doctrine |

**Overall assessment**: Research is reliable for practical application. Core technical claims are verified. Model selection and prompt patterns are well-supported community practices with reasonable evidence, though not official Anthropic doctrine.
