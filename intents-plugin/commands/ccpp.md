---
description: Run checks (lint, type, test), commit, push, and create PR
argument-hint: [commit-message]
---

# Check, Commit, Push, PR

Complete the development cycle: run quality checks, commit changes, push branch, and create a pull request.

## Current State

- Branch: !`git branch --show-current`
- Status: !`git status --short`

## Process

### Stage 1: Quality Checks

Run available checks based on project setup:

```
If package.json exists:
  - npm run lint (if script exists)
  - npm run typecheck OR npm run type-check (if script exists)
  - npm run test (if script exists)

If pyproject.toml or setup.py exists:
  - ruff check . OR flake8 (if available)
  - mypy . (if available)
  - pytest (if available)
```

**If any check fails → STOP.** Show errors and ask user how to proceed.

### Stage 2: Commit

If checks pass (or no checks configured):

1. Show `git diff --stat` summary
2. If commit message provided via `$ARGUMENTS`, use it
3. Otherwise, analyze changes and draft a commit message
4. Ask user to confirm before committing

Commit format:
```
<type>: <description>

[optional body]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

### Stage 3: Push

```bash
git push -u origin <current-branch>
```

### Stage 4: Create PR

1. Get commits since main: `git log main..HEAD --oneline`
2. Get diff stats: `git diff main --stat`
3. Create PR using the template at `.github/PULL_REQUEST_TEMPLATE.md`:
   - Title from branch name or primary commit
   - Fill in Why, What, How to test sections

```bash
gh pr create --title "<title>" --body "<filled template>"
```

## Output

```
✅ Checks passed
✅ Committed: <commit-hash> <message>
✅ Pushed to origin/<branch>
✅ PR created: <url>
```
