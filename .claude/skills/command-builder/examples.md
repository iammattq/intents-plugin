# Command Examples

Concrete examples of well-structured Claude Code commands.

## Simple Commands

### Status Check

```markdown
---
description: Show project status with git info
---

# Project Status

## Git Status
!`git status --short`

## Current Branch
!`git branch --show-current`

## Recent Commits
!`git log --oneline -5`

## Uncommitted Changes
!`git diff --stat`
```

### Quick Review

```markdown
---
description: Review a specific file for issues
argument-hint: <file-path>
allowed-tools: Read, Grep
---

# Review: $1

Read and review @$1 for:
- Code quality issues
- Potential bugs
- Style violations

## Output Format

## Summary
[1-2 sentence assessment]

## Issues Found
- `line:N` - Issue description
```

### Commit Helper

```markdown
---
description: Stage and commit with message
argument-hint: [commit-message]
allowed-tools: Bash(git:*)
---

# Commit Changes

## Current State
!`git status --short`

## Instructions

1. Review the changes above
2. If $ARGUMENTS is provided, use it as the commit message
3. If no message provided, generate one based on the changes
4. Stage all changes and commit

Commit message format:
- type(scope): description
- Types: feat, fix, docs, style, refactor, test, chore
```

## Orchestrating Commands

### Feature Implementation

```markdown
---
description: Implement a planned feature end-to-end
argument-hint: <feature-id>
---

# Implement Feature: $1

## Phase 1: Validate
Confirm feature is ready:
- [ ] Feature exists in graph (if using .intents/)
- [ ] PLAN.md exists at expected path
- [ ] No blockers or missing dependencies

## Phase 2: Research
Spawn `codebase-researcher` agent to explore:
- Similar existing implementations
- Files that will need modification
- Testing patterns used

## Phase 3: Implementation
Spawn `feature-implementer` agent with:
- Feature: $1
- Plan: docs/plans/$1/PLAN.md
- Work chunk by chunk, validate each step

## Phase 4: Quality Checks
Spawn review agents based on feature type:
- `code-reviewer` - Always
- `security-auditor` - If auth/API/data handling
- `accessibility-reviewer` - If UI components

## Phase 5: Finalize
- Run tests: `npm test`
- Run lint: `npm run lint`
- Update feature status if using graph
```

### PR Review

```markdown
---
description: Comprehensive PR review workflow
argument-hint: <pr-number>
allowed-tools: Bash(gh:*), Read, Grep, Glob, Task
---

# Review PR #$1

## Phase 1: Gather Context
!`gh pr view $1 --json title,body,files`
!`gh pr diff $1 --name-only`

## Phase 2: Understand Changes
Read each changed file and understand the modification.

## Phase 3: Code Review
Spawn `code-reviewer` agent on the changed files.

## Phase 4: Security Check
If changes touch auth, API, or data handling:
Spawn `security-auditor` agent.

## Phase 5: Synthesize
Combine findings into a single review:

## Summary
[Overall assessment]

## Approval Status
[Approved | Changes Requested | Needs Discussion]

## Required Changes
- [ ] Change 1
- [ ] Change 2

## Suggestions (non-blocking)
- Suggestion 1
- Suggestion 2
```

### Test-Driven Feature

```markdown
---
description: TDD workflow for new feature
argument-hint: <feature-name>
---

# TDD: $1

## Phase 1: Understand Requirements
Read the feature spec/plan for $1.
Clarify any ambiguities before proceeding.

## Phase 2: Test Specification
Spawn `test-spec` agent to create test specs for $1:
- Define test cases BEFORE implementation
- Cover: happy path, edge cases, error states

## Phase 3: Write Failing Tests
Implement the test cases from Phase 2.
Run tests to confirm they fail (red phase).

## Phase 4: Implement
Write minimal code to make tests pass (green phase).
Run tests after each change.

## Phase 5: Refactor
Clean up implementation while keeping tests green.
Spawn `code-reviewer` for quality check.

## Output
- All tests passing
- Clean implementation
- Code review approved
```

## Utility Commands

### Search and Replace

```markdown
---
description: Find and replace across codebase
argument-hint: <search-pattern> <replacement>
allowed-tools: Grep, Read, Edit
---

# Search and Replace

Find: `$1`
Replace with: `$2`

## Phase 1: Find Occurrences
Search for all occurrences of the pattern.
List files and line numbers.

## Phase 2: Confirm
Show the user what will be changed.
Wait for confirmation before proceeding.

## Phase 3: Replace
Make replacements one file at a time.
Show each change as it's made.

## Phase 4: Verify
Run lint and typecheck to catch any issues.
```

### Documentation Generator

```markdown
---
description: Generate docs for a module
argument-hint: <module-path>
allowed-tools: Read, Grep, Glob, Write
---

# Document: $1

## Phase 1: Analyze
Read all files in @$1
Identify:
- Exported functions/classes
- Public APIs
- Dependencies

## Phase 2: Generate
Create documentation covering:
- Overview and purpose
- Installation/setup (if applicable)
- API reference
- Usage examples

## Output Format
Write to: docs/$1/README.md

Use JSDoc-style for inline docs if the codebase uses it.
```

## Namespace Examples

Commands can be organized in subdirectories:

```
.claude/commands/
├── git/
│   ├── status.md      → /status (project:git)
│   ├── commit.md      → /commit (project:git)
│   └── pr.md          → /pr (project:git)
├── test/
│   ├── run.md         → /run (project:test)
│   └── coverage.md    → /coverage (project:test)
└── docs/
    └── generate.md    → /generate (project:docs)
```

The namespace appears in autocomplete but doesn't affect the command name.
