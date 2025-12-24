# /intents:implement

Implement a planned feature with graph status tracking.

## What This Does

1. Reads the feature's PLAN.md
2. Orchestrates chunk-by-chunk implementation
3. Runs quality checks (code review, security, a11y)
4. Updates graph status throughout the process

## Usage

```
/intents:implement [feature-name]
/intents:implement [path-to-plan]
```

## Workflow

The `feature-implementer` agent orchestrates:

### 1. Initialize
- Read PLAN.md and MEMORY.md
- Check git branch (create feature branch if needed)
- Report current state

### 2. Graph Update: Start
Update `.intents/graph.yaml`:
```yaml
feature-name:
  status: in-progress  # Changed from planned
```

### 3. Test Spec (if not done)
`test-spec` - Define test cases before implementation (TDD)

### 4. Implement Chunks
For each chunk in PLAN.md:
- Spawn implementation agent with chunk context
- Validate completion against plan tasks
- Update MEMORY.md with progress
- Ask before continuing to next chunk

### 5. Quality Checks
After implementation:
- `code-reviewer` - Code quality and patterns
- `security-auditor` - Security review (for auth/API/data features)
- `accessibility-reviewer` - A11y compliance (for UI features)

### 6. Phase Gates
At end of each phase:
- Stop for manual testing
- User verifies behavior
- User confirms to continue

### 7. Graph Update: Complete
Update `.intents/graph.yaml`:
```yaml
feature-name:
  status: implemented  # Changed from in-progress
```

## Status Transitions

```
planned → in-progress → implemented
                    ↓
                  broken (if tests fail later)
```

## Example Session

```
> /intents:implement ok-themes

[🔧 FEATURE IMPLEMENTER]

## Resuming: OK Themes

**Plan:** docs/plans/ok-themes/PLAN.md
**Memory:** docs/plans/ok-themes/MEMORY.md

### Current State
- Chunks Complete: 0 of 7
- Status: planned → in-progress
- Next Chunk: 1A - Foundation (types, config, page route)

Ready to implement Chunk 1A?

> yes

[Implements chunk...]

✅ Chunk 1A complete.

**Progress:** 1 of 7 chunks
**Next:** Chunk 1B - Brand Colors component

Continue to next chunk? Or pause here?
```

## Handling Issues

### Blockers
If implementation hits a blocker:
- Logged in MEMORY.md
- Reported to user
- Options: fix now, skip, or pause

### Plan Deviation
If the plan needs adjustment:
- Agent reports the issue
- User decides how to proceed
- Decision logged in MEMORY.md

### Test Failures
If tests fail after implementation:
- Graph status set to `broken`
- Investigation needed before continuing

## Output

```
✅ Feature implemented: feature-name

Graph updated:
  - Status: implemented (was: planned)

Quality checks:
  - Code review: ✅ Approved
  - Security audit: ✅ No issues
  - Accessibility: ✅ Compliant

Files created/modified:
  - src/app/feature/page.tsx
  - src/components/Feature.tsx
  - [etc.]

Commits: 3 commits on feature/feature-name branch
```

## After Implementation

- Test the feature manually
- Consider merging to main
- Graph status now `implemented`
