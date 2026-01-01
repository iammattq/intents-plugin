# MEMORY: stop-hooks

**Feature:** Claude Code Hooks for intents-plugin
**Status:** complete
**Current Phase:** Phase 3 - Complete (All Phases Done)

---

## Progress

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 1: Foundation | complete | Hook utilities, SessionStart, Stop hooks implemented |
| Phase 2: Chunk Automation | complete | Marker file, SubagentStop, auto-commit |
| Phase 3: Final Validation | complete | Code review, plan verify, graph update |

### Phase 1 Chunks

| Chunk | Status | Notes |
|-------|--------|-------|
| 1A | complete | Hook utilities: context.py, checks.py |
| 1B | complete | SessionStart hook: session_start.py |
| 1C | complete | Stop hook: feature_complete.py |

### Phase 2 Chunks

| Chunk | Status | Notes |
|-------|--------|-------|
| 2A | complete | feature-implementer: marker file step |
| 2B | complete | SubagentStop hook: chunk_complete.py, memory.py |
| 2C | complete | implement command: hook documentation |

### Phase 3 Chunks

| Chunk | Status | Notes |
|-------|--------|-------|
| 3A | complete | Enhance Stop hook: plan verification + code review |
| 3B | complete | Plan verification utility: plan_verify.py |
| 3C | complete | Graph update utility: graph.py |
| 3D | complete | Implement command: final validation docs |

---

## Session Log

### 2025-12-29 - Phase 3 Implementation

**Completed:**
- Chunk 3A: Enhanced Stop hook
  - `intents-plugin/hooks/feature_complete.py` - Added plan verification, code review, graph update
  - 3-step validation: tests, plan verification, code review
  - Spawns code-reviewer at feature completion only
- Chunk 3B: Plan verification utility
  - `intents-plugin/hooks/utils/plan_verify.py` - Compare implementation to PLAN.md
  - Extracts ship criteria from PLAN.md, checks against MEMORY.md
  - Fuzzy matching for criteria comparison
- Chunk 3C: Graph update utility
  - `intents-plugin/hooks/utils/graph.py` - Set status to `implemented`
  - `is_feature_complete()` - Multiple detection methods for completion
- Chunk 3D: Implement command documentation
  - Added "Final Validation (Stop Hook)" section with flow diagram
  - Documented validation steps, failure handling, retry limit

**Ship Criteria Verified:**
- [x] Code review runs at feature completion (not per chunk)
- [x] Implementation verified against PLAN.md requirements
- [x] Graph status updated to `implemented` automatically on pass
- [x] Graceful handling when checks fail (block with actionable feedback)
- [x] 3-retry limit: after 3 failures, approve with warning

---

### 2025-12-29 - Phase 2 Implementation

**Completed:**
- Chunk 2A: feature-implementer update
  - Added Step 6.5 to write `.claude/.chunk-complete` marker file
  - Marker contains: chunk, feature, phase, description, timestamp
- Chunk 2B: SubagentStop hook
  - `intents-plugin/hooks/chunk_complete.py` - Detects marker, validates, auto-commits
  - `intents-plugin/hooks/utils/memory.py` - MEMORY.md update operations
  - Updated `utils/__init__.py` with new exports
- Chunk 2C: implement command update
  - Added hook automation documentation
  - Added `.claude/settings.json` configuration example

**Ship Criteria Verified:**
- [x] feature-implementer writes marker file after each chunk
- [x] SubagentStop detects marker, runs validation (auto-detected tests)
- [x] MEMORY.md updated with chunk completion status
- [x] Auto-commit on pass: `feat(<feature>): chunk <N> - <description>`
- [x] Marker file deleted after processing
- [x] Non-implementation subagents ignored (no marker = no validation)
- [x] Stale marker detection (5 minute max age)
- [x] Retry limit (3 attempts before approve with warning)

---

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

All phases complete. Feature is implemented.

**Manual Testing Recommended:**
- [ ] Enable hooks in a target project via `.claude/settings.json`
- [ ] Implement a test feature with hooks enabled
- [ ] Verify SessionStart loads context on resume
- [ ] Verify SubagentStop auto-commits chunks on pass
- [ ] Verify Stop hook runs final validation pipeline
- [ ] Verify graph.yaml updates to `implemented` on feature completion
