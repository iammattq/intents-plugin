---
description: Update MEMORY.md with session progress and commit recent changes
argument-hint: <feature> [commit-message]
---

# /save-mem

Capture session progress in MEMORY.md and commit the work.

## Usage

```
/save-mem <feature>
/save-mem <feature> "commit message"
```

## Process

### 1. Locate Memory File

```
docs/plans/<feature>/MEMORY.md
```

If not found, inform user and stop.

### 2. Analyze Work Since Last Update

Read the last session entry in MEMORY.md to understand where things left off.

Then review only the work done **since that point** to identify:
- What was completed since the last MEMORY.md update
- Key decisions made
- Files created/modified
- Any blockers or deviations from plan
- Next steps

### 3. Update MEMORY.md

Add a new session entry at the end of the Session Log:

```markdown
### Session: <brief description>
**Date:** {today}
**Status:** Complete | In Progress | Blocked

#### Completed
- [task summaries]

#### Files
- path/to/file.ts - [what changed]
```

If working on chunks, also update the kanban:
- Move completed chunks from Ready to Done
- Unblock any dependent chunks

Update "Current State" section at the top if status changed.

### 4. Stage and Show Changes

```bash
git add -A
git status --short
git diff --staged --stat
```

### 5. Commit

If commit message provided via `$ARGUMENTS`, use it.
Otherwise, draft a message based on session work:

```
<type>: <description>

Co-Authored-By: Claude <noreply@anthropic.com>
```

Ask user to confirm before committing.

## Output

```
✅ Updated: docs/plans/<feature>/MEMORY.md
✅ Committed: <hash> <message>
```

## Error Handling

| Error | Action |
|-------|--------|
| Feature MEMORY.md not found | Inform user, suggest creating with `/intents:plan` |
| No changes to commit | Update MEMORY.md only, inform user |
| Commit fails | Show error, leave changes staged |
