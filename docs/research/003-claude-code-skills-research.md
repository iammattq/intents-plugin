# Research 003: Best-in-Class Claude Code Skills

**Date:** 2025-12-26

**Status:** Complete (Verified)

**Related:** Skill creation patterns for intents-plugin

## Problem Statement

How do we create best-in-class Claude Code skills? This research covers skill architecture, SKILL.md format, progressive disclosure, skill discovery, skill-agent integration, skill-command integration, and real-world patterns from official documentation and community examples.

## Constraints

- Skills must work within Claude Code's context window limitations
- Must integrate with `.claude/skills/` directory structure
- Should follow official Anthropic patterns and best practices
- Need to support both simple single-file skills and complex multi-file skills
- Must enable effective skill-agent orchestration

---

## Part 1: Skill Architecture

### What Are Skills?

Skills are **model-invoked** modular capabilities that extend Claude's functionality. Unlike slash commands (user-invoked via `/command`), skills are autonomously triggered by Claude based on task context and the skill's description. [Source: [Claude Platform Docs - Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)]

Each skill consists of:
- A `SKILL.md` file with YAML frontmatter and instructions
- Optional supporting files (reference docs, scripts, templates)
- A directory structure enabling progressive disclosure

### Key Characteristics

| Aspect | Skills | Commands | Agents |
|--------|--------|----------|--------|
| **Invocation** | Model-invoked (autonomous) | User-invoked (`/command`) | Model-delegated or explicit |
| **Context** | Main conversation | Main conversation | Isolated context window |
| **Structure** | Directory with SKILL.md + resources | Single .md file | AGENT.md file |
| **Discovery** | Description-based matching | Terminal autocomplete | Description matching |
| **Purpose** | Domain expertise, patterns | Repeatable workflows | Research, review, orchestration |

[Source: [alexop.dev - Claude Code customization guide](https://alexop.dev/posts/claude-code-customization-guide-claudemd-skills-subagents/)]

### Skill Locations

| Type | Location | Scope | Sharing |
|------|----------|-------|---------|
| Project skills | `.claude/skills/` | Current repository | Git (shared with team) |
| Personal skills | `~/.claude/skills/` | All projects | Local only |
| Plugin skills | Installed via `/plugin` | Plugin scope | Plugin marketplace |

Project skills take precedence over personal skills with the same name. [Source: [Claude Code Docs - Skills](https://code.claude.com/docs/en/skills)]

---

## Part 2: SKILL.md Format

### Basic Template

```yaml
---
name: lowercase-with-hyphens
description: What it does AND when to use it. Include trigger keywords.
---

# Skill Name

## Instructions
[Concise guidance - Claude is smart, skip obvious explanations]

## Examples
[Concrete input/output pairs if helpful]
```

[Source: [Claude Code Docs - Skills](https://code.claude.com/docs/en/skills)]

### Frontmatter Fields

| Field | Required | Constraints | Purpose |
|-------|----------|-------------|---------|
| `name` | Yes | Max 64 chars, lowercase letters/numbers/hyphens only, no "anthropic" or "claude", no XML tags | Unique identifier |
| `description` | Yes | Max 1024 chars, non-empty, no XML tags | Discovery and trigger matching |
| `allowed-tools` | No | Comma-separated tool names | Restrict tool access (Claude Code only) |

[Source: [Claude Platform Docs - Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)]

**Note:** The constraints are explicitly documented:
- `name`: "Maximum 64 characters", "Must contain only lowercase letters, numbers, and hyphens", "Cannot contain reserved words: 'anthropic', 'claude'"
- `description`: "Must be non-empty", "Maximum 1024 characters", "Cannot contain XML tags"

### Naming Conventions

Use **gerund form** (verb + -ing) for skill names: [Source: [Claude Platform Docs - Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)]

**Good:**
- `processing-pdfs`
- `analyzing-spreadsheets`
- `managing-databases`
- `writing-documentation`

**Avoid:**
- Vague names: `helper`, `utils`, `tools`
- Overly generic: `documents`, `data`, `files`
- Reserved words: `anthropic-helper`, `claude-tools`

### Description Formula

The description is **critical for discovery**. Claude uses it to decide when to trigger the skill. [Source: [Claude Platform Docs - Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)]

**Formula:**
```
[Action verbs describing capabilities]. Use when [specific triggers/contexts].
```

**Good examples:**

```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

```yaml
description: Analyze Excel spreadsheets, create pivot tables, generate charts. Use when analyzing Excel files, spreadsheets, tabular data, or .xlsx files.
```

**Bad examples:**

```yaml
description: Helps with documents
```

```yaml
description: Processes data
```

**Important:** Write in third person. The description is injected into the system prompt. [Source: [Claude Platform Docs - Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)]
- Good: "Processes Excel files and generates reports"
- Avoid: "I can help you process Excel files"
- Avoid: "You can use this to process Excel files"

---

## Part 3: Progressive Disclosure

### The Core Design Principle

Progressive disclosure is the foundational architecture principle for skills. It enables skills to contain unbounded amounts of context while consuming minimal tokens until needed. [Source: [Anthropic Engineering - Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)]

As the documentation states: "Like a well-organized manual that starts with a table of contents, then specific chapters, and finally a detailed appendix, skills let Claude load information only as needed."

### Three-Layer Loading Model

| Layer | When Loaded | Token Impact | Content Type |
|-------|-------------|--------------|--------------|
| **Layer 1: Metadata** | At startup | ~100 tokens/skill | YAML frontmatter (name + description) |
| **Layer 2: Instructions** | When skill triggered | Under 5,000 tokens | SKILL.md body content |
| **Layer 3: Resources** | As needed | Effectively unlimited | Additional .md files, scripts |

[Source: [Claude Platform Docs - Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)]

**Verified:** The official documentation confirms:
- "Level 1: Metadata (always loaded) - ~100 tokens per Skill"
- "Level 2: Instructions (loaded when triggered) - Under 5k tokens"
- "Level 3+: Resources (loaded as needed) - Effectively unlimited"

### Directory Structure

**Simple skill:**
```
my-skill/
└── SKILL.md
```

**Complex skill with progressive disclosure:**
```
pdf-processing/
├── SKILL.md              # Overview (loaded when triggered)
├── FORMS.md              # Form-filling guide (loaded as needed)
├── REFERENCE.md          # API reference (loaded as needed)
├── examples.md           # Usage examples (loaded as needed)
└── scripts/
    ├── analyze_form.py   # Executed, not loaded into context
    ├── fill_form.py      # Executed, not loaded into context
    └── validate.py       # Executed, not loaded into context
```

[Source: [Claude Platform Docs - Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)]

### Referencing Additional Files

In SKILL.md, reference supporting files with clear context:

```markdown
## Quick start

Extract text with pdfplumber:
```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

## Advanced features

**Form filling**: See [FORMS.md](FORMS.md) for complete guide
**API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
**Examples**: See [examples.md](examples.md) for common patterns
```

Claude reads FORMS.md, REFERENCE.md, or examples.md only when the user's request requires it.

### Best Practices for Progressive Disclosure

1. **Keep SKILL.md under 500 lines** - Split larger content into referenced files [Source: [Claude Platform Docs - Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)]

2. **One level deep references only** - Avoid SKILL.md -> advanced.md -> details.md chains [Source: [Claude Platform Docs - Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)]
   - Good: SKILL.md -> reference.md (direct)
   - Bad: SKILL.md -> advanced.md -> details.md (too deep)

   The documentation explicitly warns: "Claude may partially read files when they're referenced from other referenced files... Keep references one level deep from SKILL.md."

3. **Use table of contents for long reference files** - Helps Claude navigate even with partial reads:
   ```markdown
   # API Reference

   ## Contents
   - Authentication and setup
   - Core methods (create, read, update, delete)
   - Advanced features
   - Error handling patterns
   ```

4. **Scripts are executed, not loaded** - Keep deterministic logic in scripts:
   - Make clear: "Run `analyze_form.py`" (execute)
   - Not: "Read analyze_form.py for the algorithm" (loads into context)

---

## Part 4: Skill-Agent Integration

### Key Relationship

Skills and agents serve complementary purposes:

| Use Skills When | Use Agents When |
|-----------------|-----------------|
| Knowledge should persist in main conversation | Extensive reading would pollute main context |
| No need for isolated context | Task can run in parallel with others |
| Domain expertise for current work | Specialized toolset needed |
| Progressive disclosure is valuable | Results should be compressed |

[Inferred from architecture differences - not explicitly documented as a comparison table]

### Skills Auto-Loading in Agents

Agents can auto-load skills using the `skills` frontmatter field: [Source: [Claude Code Docs - Subagents](https://code.claude.com/docs/en/sub-agents)]

```yaml
---
name: feature-implementer
description: Description of when this subagent should be invoked
tools: tool1, tool2, tool3
model: sonnet
skills: coding-standards, testing-guidelines
---
```

**Verified:** The documentation confirms: "Skills auto-load when the subagent starts. Skills are loaded into the subagent's context automatically."

The `skills` field is:
- Optional (not required for agent configuration)
- Comma-separated list of skill names
- Automatically loaded into subagent context when the agent is invoked

### Skills Invoking Agents

Skills can instruct Claude to spawn agents for specific work: [Community pattern - skills provide guidance, Claude decides to invoke Task tool]

```markdown
# Research Skill

## When research is needed

For deep codebase exploration, spawn the `codebase-researcher` agent:

Task: codebase-researcher

Research the authentication patterns in this codebase.

Questions:
1. Where is auth implemented?
2. What libraries are used?

Return: Concise summary with file locations.
```

### Orchestration Pattern: Skill + Agents

A skill can orchestrate a multi-agent workflow:

```markdown
---
name: feature-planning
description: Create comprehensive feature plans. Use when planning new features or major refactors.
---

# Feature Planning

## Process

### Phase 1: Research
Spawn parallel `codebase-researcher` agents:
- Agent 1: Explore existing patterns for similar features
- Agent 2: Map dependencies and integration points
- Agent 3: Identify testing patterns

### Phase 2: Synthesis
Combine findings into a structured plan.

### Phase 3: Review
Spawn `architecture-reviewer` agent to validate the plan.
```

### Skills Cannot Spawn Agents Directly

Important limitation: Skills are prompt expansions, not executable code. They **guide Claude** to spawn agents, but the actual spawning happens via Claude's Task tool invocation. [Source: [mikhail.io - Inside Claude Code Skills](https://mikhail.io/2025/10/claude-code-skills/)]

The workflow is:
1. User request triggers skill (based on description match)
2. Skill provides instructions that include agent spawning guidance
3. Claude decides to invoke Task tool based on skill instructions
4. Agent runs in isolated context, returns findings
5. Claude continues with skill workflow using agent findings

As noted in technical analysis: "Skills aren't separate processes but injected instructions within the main conversation flow."

---

## Part 5: Skill-Command Integration

### How Commands Use Skills

Commands can reference skills for domain expertise: [Community pattern]

```markdown
---
description: Implement a planned feature end-to-end
argument-hint: <feature-id>
---

# Implement Feature: $1

## Phase 1: Apply Standards
Load the `coding-standards` skill for consistent implementation patterns.

## Phase 2: Research
Spawn `codebase-researcher` to explore existing patterns for $1.

## Phase 3: Implementation
Follow the implementation guidelines from the skill.
Apply TDD patterns from `testing-guidelines` skill.
```

### Relationship: Commands -> Skills -> Agents

The typical flow for complex workflows:

```
/implement-feature (command)
    |
    +-> coding-standards skill (loaded for expertise)
    |
    +-> codebase-researcher agent (spawned for research)
    |
    +-> feature-implementer agent (spawned for implementation)
    |
    +-> code-reviewer agent (spawned for review)
```

Commands are the explicit entry points. Skills provide the domain knowledge. Agents do the isolated work.

### When to Put Logic in Skills vs Commands

| Put in Skill | Put in Command |
|--------------|----------------|
| Reusable domain knowledge | Specific workflow orchestration |
| Patterns and guidelines | Argument handling ($1, $ARGUMENTS) |
| Reference material | Dynamic context (! and @ prefixes) |
| Auto-applicable expertise | User-triggered actions |

[Inferred from documented differences between skills and commands]

---

## Part 6: Best Practices

### Core Principles

#### 1. Concise is Key

The context window is shared. Only add what Claude doesn't already know. [Source: [Claude Platform Docs - Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)]

**Challenge each piece of information:**
- "Does Claude really need this explanation?"
- "Can I assume Claude knows this?"
- "Does this paragraph justify its token cost?"

**Good (concise):**
```markdown
## Extract PDF text

Use pdfplumber for text extraction:

```python
import pdfplumber

with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```
```

**Bad (verbose):**
```markdown
## Extract PDF text

PDF (Portable Document Format) files are a common file format that contains
text, images, and other content. To extract text from a PDF, you'll need to
use a library. There are many libraries available for PDF processing, but we
recommend pdfplumber because it's easy to use...
```

#### 2. Appropriate Degrees of Freedom

Match specificity to task fragility: [Source: [Claude Platform Docs - Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)]

| Freedom Level | When to Use | Example |
|--------------|-------------|---------|
| **High** | Multiple valid approaches | "Analyze code structure and suggest improvements" |
| **Medium** | Preferred pattern with variation | Pseudocode with parameters |
| **Low** | Fragile/critical operations | "Run exactly: `python migrate.py --verify`" |

The documentation provides an analogy: "Think of Claude as a robot exploring a path: Narrow bridge with cliffs on both sides - provide specific guardrails. Open field with no hazards - give general direction."

#### 3. Keep Skills Focused

**Focused (good):**
- "PDF form filling"
- "Excel data analysis"
- "Git commit messages"

**Too broad (split into separate skills):**
- "Document processing"
- "Data tools"

#### 4. Test with All Models

What works for Opus might need more detail for Haiku: [Source: [Claude Platform Docs - Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)]

| Model | Testing Question |
|-------|-----------------|
| Haiku (fast) | Does the skill provide enough guidance? |
| Sonnet (balanced) | Is the skill clear and efficient? |
| Opus (powerful) | Does the skill avoid over-explaining? |

### Workflow Patterns

#### Checklist Pattern

For complex tasks, provide a checklist Claude can track: [Source: [Claude Platform Docs - Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)]

```markdown
## Form filling workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Step 1: Analyze the form
- [ ] Step 2: Create field mapping
- [ ] Step 3: Validate mapping
- [ ] Step 4: Fill the form
- [ ] Step 5: Verify output
```
```

#### Feedback Loop Pattern

Run validator -> fix errors -> repeat: [Source: [Claude Platform Docs - Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)]

```markdown
## Document editing process

1. Make edits to `word/document.xml`
2. **Validate immediately**: `python scripts/validate.py`
3. If validation fails:
   - Fix the issues
   - Run validation again
4. **Only proceed when validation passes**
5. Rebuild document
```

#### Template Pattern

Provide output templates with appropriate strictness: [Source: [Claude Platform Docs - Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)]

```markdown
## Report structure

Use this template:

```markdown
# [Analysis Title]

## Executive summary
[One-paragraph overview]

## Key findings
- Finding 1 with data
- Finding 2 with data

## Recommendations
1. Actionable recommendation
2. Actionable recommendation
```
```

### Anti-Patterns to Avoid

| Don't | Do Instead |
|-------|------------|
| Vague descriptions | Specific triggers with action verbs |
| Windows-style paths (`\`) | Unix-style paths (`/`) |
| Multiple tool options | Recommend one default |
| Time-sensitive info | Use "old patterns" section |
| Deep file nesting | One-level references |
| Verbose explanations | Assume Claude knows basics |
| Magic numbers in scripts | Self-documenting constants |

[Source: [Claude Platform Docs - Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)]

---

## Part 7: Advanced Patterns

### Domain-Specific Organization

For skills with multiple domains, organize by domain to avoid loading irrelevant context: [Source: [Claude Platform Docs - Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)]

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md (revenue metrics)
    ├── sales.md (pipeline data)
    ├── product.md (usage analytics)
    └── marketing.md (campaigns)
```

SKILL.md provides navigation:

```markdown
# BigQuery Data Analysis

## Available datasets

**Finance**: Revenue, ARR, billing -> See [reference/finance.md](reference/finance.md)
**Sales**: Opportunities, pipeline -> See [reference/sales.md](reference/sales.md)
**Product**: API usage, features -> See [reference/product.md](reference/product.md)
```

### Script Automation Pattern

Offload complex operations to scripts: [Source: [Claude Platform Docs - Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)]

```markdown
## Utility scripts

**analyze_form.py**: Extract all form fields from PDF

```bash
python scripts/analyze_form.py input.pdf > fields.json
```

**validate_boxes.py**: Check for overlapping bounding boxes

```bash
python scripts/validate_boxes.py fields.json
# Returns: "OK" or lists conflicts
```
```

**Benefits:**
- More reliable than generated code
- Save tokens (no code generation)
- Ensure consistency across uses

### Conditional Workflow Pattern

Guide Claude through decision points:

```markdown
## Document modification workflow

1. Determine the modification type:

   **Creating new content?** -> Follow "Creation workflow" below
   **Editing existing content?** -> Follow "Editing workflow" below

2. Creation workflow:
   - Use docx-js library
   - Build document from scratch

3. Editing workflow:
   - Unpack existing document
   - Modify XML directly
   - Validate after each change
```

### MCP Tool References

If your skill uses MCP tools, use fully qualified names: [Source: [Claude Platform Docs - Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)]

```markdown
Use the BigQuery:bigquery_schema tool to retrieve table schemas.
Use the GitHub:create_issue tool to create issues.
```

Format: `ServerName:tool_name`

---

## Part 8: Evaluation and Iteration

### Build Evaluations First

Create evaluations BEFORE writing extensive documentation: [Source: [Claude Platform Docs - Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)]

1. **Identify gaps**: Run Claude on representative tasks without a skill
2. **Create evaluations**: Build 3+ scenarios testing these gaps
3. **Establish baseline**: Measure performance without the skill
4. **Write minimal instructions**: Just enough to pass evaluations
5. **Iterate**: Execute evaluations, compare, refine

### Develop Skills Iteratively with Claude

The most effective process involves Claude itself: [Source: [Claude Platform Docs - Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)]

1. **Complete a task without a skill** - Work through a problem, noting what context you provide
2. **Identify the reusable pattern** - What knowledge would help similar future tasks?
3. **Ask Claude to create a skill** - "Create a skill that captures this pattern"
4. **Review for conciseness** - Remove unnecessary explanations
5. **Test on similar tasks** - Use the skill with fresh Claude instances
6. **Iterate based on observation** - If Claude struggles, refine with specific feedback

### Observation Checklist

When iterating, watch for:
- Unexpected exploration paths (structure might not be intuitive)
- Missed connections (links might need to be more explicit)
- Overreliance on certain sections (content might need restructuring)
- Ignored content (might be unnecessary or poorly signaled)

---

## Part 9: Real-World Examples

### Example 1: Simple Skill (Single File)

```yaml
---
name: generating-commit-messages
description: Generates clear commit messages from git diffs. Use when writing commit messages or reviewing staged changes.
---

# Generating Commit Messages

## Instructions

1. Run `git diff --staged` to see changes
2. Generate a commit message with:
   - Summary under 50 characters
   - Detailed description
   - Affected components

## Best practices

- Use present tense
- Explain what and why, not how
```

### Example 2: Skill with Tool Restrictions

```yaml
---
name: code-reviewer
description: Review code for best practices and potential issues. Use when reviewing code, checking PRs, or analyzing code quality.
allowed-tools: Read, Grep, Glob
---

# Code Reviewer

Read-only - report findings, never modify code.

## Review checklist

1. Code organization and structure
2. Error handling
3. Performance considerations
4. Security concerns
5. Test coverage
```

### Example 3: Multi-File Skill with Progressive Disclosure

```
pdf-processing/
├── SKILL.md
├── FORMS.md
├── REFERENCE.md
└── scripts/
    ├── analyze_form.py
    ├── fill_form.py
    └── validate.py
```

**SKILL.md:**
```yaml
---
name: processing-pdfs
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
---

# PDF Processing

## Quick start

Extract text:
```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

## Advanced features

**Form filling**: See [FORMS.md](FORMS.md) for complete guide
**API reference**: See [REFERENCE.md](REFERENCE.md) for all methods

## Utility scripts

**Analyze form**: `python scripts/analyze_form.py input.pdf`
**Fill form**: `python scripts/fill_form.py input.pdf fields.json output.pdf`
**Validate**: `python scripts/validate.py fields.json`
```

### Example 4: Skill That Orchestrates Agents

```yaml
---
name: feature-implementation
description: Implement features with research, planning, and review. Use when implementing new features or major changes.
---

# Feature Implementation

## Process

### Phase 1: Research
Spawn `codebase-researcher` agent to explore:
- Existing patterns for similar features
- Files that will need modification
- Testing patterns used

### Phase 2: Implementation
Work chunk by chunk. After each chunk:
- Run tests
- Validate against plan

### Phase 3: Review
Spawn review agents:
- `code-reviewer` - Always
- `security-auditor` - If auth/API involved
- `accessibility-reviewer` - If UI involved

## Validation

<checkpoint>
STOP. Before marking complete:
[ ] All tests passing
[ ] Code review approved
[ ] Security review passed (if applicable)
</checkpoint>
```

---

## Part 10: Checklist for Effective Skills

### Core Quality
- [ ] Description is specific and includes trigger keywords
- [ ] Description includes both WHAT it does and WHEN to use it
- [ ] Description written in third person
- [ ] SKILL.md body is under 500 lines
- [ ] Additional details split into separate files (if needed)
- [ ] No time-sensitive information
- [ ] Consistent terminology throughout
- [ ] File references one level deep only
- [ ] Progressive disclosure used appropriately

### Structure
- [ ] Name uses gerund form (verb + -ing) or clear noun phrase
- [ ] Name uses lowercase letters, numbers, and hyphens only
- [ ] Name avoids reserved words (anthropic, claude)
- [ ] All file paths use forward slashes (Unix style)
- [ ] Supporting files have descriptive names

### Code and Scripts
- [ ] Scripts handle errors explicitly (don't punt to Claude)
- [ ] No magic numbers (all values documented)
- [ ] Required packages listed in instructions
- [ ] Clear distinction: execute vs read as reference

### Testing
- [ ] Tested with Haiku, Sonnet, and Opus (if applicable)
- [ ] Tested with real usage scenarios
- [ ] Team feedback incorporated (if applicable)
- [ ] Evaluations created for key scenarios

---

## Recommendations

### For This Project (intents-plugin)

1. **Current skills are well-structured** - The existing skill-creator, agent-builder, and command-builder skills follow best practices

2. **Consider skill-agent integration patterns** - Skills could include explicit guidance for spawning agents:
   ```markdown
   ## When deep research is needed
   Spawn `codebase-researcher` agent with specific questions.
   ```

3. **Add progressive disclosure for complex skills** - If skills grow beyond 500 lines, split into reference files

4. **Ensure description specificity** - Each skill description should include action verbs AND trigger conditions

### General Best Practices Summary

1. **Start with SKILL.md only** - Add supporting files when you hit real pain
2. **Write specific descriptions** - Include WHAT and WHEN
3. **Use progressive disclosure** - SKILL.md is the table of contents
4. **Keep one level of references** - No deep nesting
5. **Test with all target models** - What works for Opus may need more detail for Haiku
6. **Build evaluations first** - Identify gaps before writing extensive docs
7. **Iterate with Claude** - Use Claude to help create and refine skills

---

## Sources

### Official Documentation
- [Agent Skills - Claude Code Docs](https://code.claude.com/docs/en/skills) - Official Claude Code skills documentation
- [Agent Skills Overview - Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) - Skills architecture and structure
- [Skill Authoring Best Practices - Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) - Comprehensive authoring guide
- [Subagents - Claude Code Docs](https://code.claude.com/docs/en/sub-agents) - Agent spawning, Task tool, and skills frontmatter field

### Anthropic Engineering
- [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) - Skills architecture deep dive, progressive disclosure design
- [Claude Code: Best practices for agentic coding](https://www.anthropic.com/engineering/claude-code-best-practices) - Overall best practices
- [Introducing Agent Skills](https://www.anthropic.com/news/skills) - Skills announcement and overview

### Repositories
- [GitHub - anthropics/skills](https://github.com/anthropics/skills) - Official Anthropic skills repository (~27k stars as of Dec 2025)
- [GitHub - travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) - Curated list of Claude Skills

### Community Guides
- [Claude Agent Skills: A First Principles Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/) - Technical architecture analysis
- [Inside Claude Code Skills: Structure, prompts, invocation](https://mikhail.io/2025/10/claude-code-skills/) - Skills invocation mechanics
- [Claude Code customization guide](https://alexop.dev/posts/claude-code-customization-guide-claudemd-skills-subagents/) - Skills, commands, agents comparison

---

## Validation Summary

| Category | Claims | Confidence | Verification Notes |
|----------|--------|------------|-------------------|
| SKILL.md format and frontmatter | Fully verified | **High** | All constraints (64 char name, 1024 char description, reserved words, no XML tags) confirmed in official docs |
| Progressive disclosure architecture | Fully verified | **High** | Three-layer model with specific token recommendations (~100/skill metadata, <5k for SKILL.md) confirmed |
| Token recommendations | Verified | **High** | "~100 tokens per Skill" for metadata and "Under 5k tokens" for instructions explicitly stated in platform docs |
| 500-line and one-level-deep rules | Fully verified | **High** | Best practices doc explicitly states "Keep SKILL.md body under 500 lines" and "Keep references one level deep" |
| Skill-agent integration (skills: field) | Verified | **High** | Subagents doc confirms `skills: skill1, skill2` frontmatter field with auto-loading behavior |
| Skills invoking agents | Verified with nuance | **High** | Skills provide guidance; Claude invokes Task tool. Skills are "injected instructions" not executable code |
| Best practices (gerund naming, description formula) | Fully verified | **High** | All patterns confirmed in official best practices documentation |
| Workflow patterns (checklist, feedback loop, template) | Fully verified | **High** | All three patterns with examples in official best practices |
| Skill-command relationship | Community patterns | **Medium** | Not extensively documented officially; inferred from documented differences |
| GitHub repository stars | Verified | **High** | ~27k stars confirmed (was 27.5k in search results, Anthropic stated "crossed 20k" in Dec 2025) |

**Research completed:** 2025-12-26

**Last validation:** 2025-12-26
