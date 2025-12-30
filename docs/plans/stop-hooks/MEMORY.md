# MEMORY: stop-hooks

**Feature:** Claude Code Hooks for intents-plugin
**Status:** in-progress
**Current Phase:** Phase 1 - Complete

---

## Progress

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 1: Foundation | complete | Hook utilities, SessionStart, Stop hooks implemented |
| Phase 2: Chunk Automation | pending | Marker file, SubagentStop, auto-commit |
| Phase 3: Final Validation | pending | Code review, plan verify, graph update |

### Phase 1 Chunks

| Chunk | Status | Notes |
|-------|--------|-------|
| 1A | complete | Hook utilities: context.py, checks.py |
| 1B | complete | SessionStart hook: session_start.py |
| 1C | complete | Stop hook: feature_complete.py |

---

## Session Log

### 2025-12-29 - Phase 1 Implementation

**Completed:**
- Chunk 1A: Hook utilities
  - `intents-plugin/hooks/utils/__init__.py` - Module exports
  - `intents-plugin/hooks/utils/context.py` - MEMORY.md/PLAN.md loading, feature detection
  - `intents-plugin/hooks/utils/checks.py` - Test command auto-detection, run_checks, retry tracking
- Chunk 1B: SessionStart hook
  - `intents-plugin/hooks/session_start.py` - Detects in-progress feature, loads context
- Chunk 1C: Stop hook
  - `intents-plugin/hooks/feature_complete.py` - Auto-runs tests, blocks on failure

**Ship Criteria Verified:**
- [x] SessionStart loads context for in-progress features only
- [x] Stop hook auto-detects project type (package.json/pyproject.toml/Cargo.toml)
- [x] Infinite loop prevention via `stop_hook_active` check
- [x] Fail open (approve) on errors
- [x] Block reasons include test output (truncated to 500 chars)
- [x] 3-retry limit with `.claude/.hook-retries` file

**Implementation Notes:**
- Feature detection: git branch `feature/*` pattern, fallback to in-progress MEMORY.md
- Test commands: npm test, pytest, cargo test based on project files
- All hooks use JSON stdin/stdout per Claude Code hook spec

---

### 2025-12-29 - Planning Session

**Completed:**
- Research completed (docs/research/005-claude-code-stop-hooks.md)
- Initial plan created
- Plan refined via advocate/critic debate

**Key Refinements from Debate:**

1. **Hook Distribution Model**
   - Hooks are templates in `intents-plugin/.claude/hooks/`
   - Copied to target project's `.claude/hooks/` during `/intents:init`
   - User can customize; plugin won't overwrite without confirmation

2. **Test Command Configuration**
   - Explicit prompts during `/intents:init` (more secure than auto-detect)
   - Detect project type (package.json, pyproject.toml, Cargo.toml) for defaults
   - Store in `.claude/settings.json`

3. **Chunk Detection**
   - Changed from fragile pattern matching to deterministic marker file
   - feature-implementer writes `.claude/.chunk-complete` after each chunk
   - SubagentStop reads marker, validates, deletes (atomic)
   - Timestamp validation prevents stale markers

4. **Infinite Loop Prevention**
   - Check `stop_hook_active` flag first
   - Add 3-retry limit: after 3 failures, approve with warning
   - Prevents Claude from getting stuck in fix loops

5. **Error Handling**
   - Include actual test output in block reasons
   - Use `systemMessage` for user feedback
   - Fail open (approve) on hook errors

**Decisions Made:**
- Python for hooks (better JSON handling)
- Per-chunk commits (granular history)
- Code review at end only (not per-chunk, too expensive)
- Command-based hooks only (no prompt-based for MVP)
- Marker file for deterministic chunk detection
- Explicit test command configuration (security)

**Open Questions Resolved:**
1. Hook location: Templates in plugin, copied to project root
2. Chunk detection: Marker file (not pattern matching)
3. Test command config: Explicit prompts during /intents:init

---

## Next Action

Phase 1 complete. Ready for Phase Gate testing:
- [ ] Test in a real project with package.json
- [ ] Start session with in-progress feature, verify context loads
- [ ] Complete a task, verify tests run and block on failure
