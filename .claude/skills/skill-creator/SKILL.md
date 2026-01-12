---
name: skill-creator
description: Create and validate Claude Code Skills. Use when building skills, writing SKILL.md files, designing skill architecture, or troubleshooting skill discovery issues.
---

# Skill Creator

Guide for creating effective Claude Code Skills.

## Quick Start

```bash
# Create skill directory
mkdir -p .claude/skills/my-skill-name

# Create SKILL.md with required frontmatter
```

## SKILL.md Template

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

## Frontmatter Rules

| Field         | Requirements                                                               |
| ------------- | -------------------------------------------------------------------------- |
| `name`        | Lowercase, numbers, hyphens only. Max 64 chars. No "anthropic" or "claude" |
| `description` | 1-1024 chars. Must include WHAT it does AND WHEN to use it                 |

**Optional:** `allowed-tools: Read, Grep, Glob` (restricts tool access)

## Description Formula

```
[Action verbs describing capabilities]. Use when [specific triggers/contexts].
```

**Good:**

```yaml
description: Extract text from PDFs, fill forms, merge documents. Use when working with PDF files or when the user mentions document extraction.
```

**Bad:**

```yaml
description: Helps with documents
```

## Core Principles

### 1. YAGNI First

Start with just SKILL.md. Add supporting files only when you hit real pain:

- Don't pre-create TEMPLATES.md, TROUBLESHOOTING.md, scripts/
- Add them when you actually need them
- A skill that's "too simple" is usually right-sized

### 2. Concise is Key

Context window is shared. Only add what Claude doesn't know.

**Ask yourself:**

- Does Claude need this explanation?
- Does this paragraph justify its token cost?

### 3. Degrees of Freedom

| Freedom | When                             | Example                                           |
| ------- | -------------------------------- | ------------------------------------------------- |
| High    | Multiple valid approaches        | "Analyze code structure and suggest improvements" |
| Medium  | Preferred pattern with variation | Pseudocode with parameters                        |
| Low     | Fragile/critical operations      | "Run exactly: `python migrate.py --verify`"       |

### 4. Progressive Disclosure

```
my-skill/
├── SKILL.md          # Overview (loaded when triggered)
├── reference.md      # Details (loaded as needed)
└── scripts/          # Executed, not loaded into context
```

Keep SKILL.md under 500 lines. Split larger content into referenced files.

## File Organization

**One level deep references only:**

```markdown
# SKILL.md

See [reference.md](reference.md) for details
See [examples.md](examples.md) for patterns
```

Avoid: SKILL.md → advanced.md → details.md (too deep)

## Workflow Pattern

For complex tasks, provide checkable steps:

```markdown
## Process

1. **Analyze** - Run `python scripts/analyze.py input`
2. **Validate** - Run `python scripts/validate.py output.json`
3. **Execute** - Only after validation passes
4. **Verify** - Check results
```

## Anti-Patterns

| Avoid                 | Do Instead                 |
| --------------------- | -------------------------- |
| Verbose explanations  | Assume Claude knows basics |
| Multiple tool options | Recommend one default      |
| Time-sensitive info   | Use "old patterns" section |
| Windows paths (`\`)   | Unix paths (`/`)           |
| Vague descriptions    | Specific triggers          |
| Deep file nesting     | One-level references       |

## Validation Checklist

Before deploying:

- [ ] Description includes what AND when
- [ ] SKILL.md under 500 lines
- [ ] Consistent terminology
- [ ] No time-sensitive content
- [ ] Forward slashes in paths
- [ ] Tested with actual queries
