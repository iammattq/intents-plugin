# Harness Cleanup

## Problem Statement

The intents-plugin has accumulated correctness issues, documented duplication, and dead code since its original design in December 2025. A sweep of current state surfaced:

1. **`chunk-worker` is broken by design** — it declares `Task` in its tools frontmatter and Step 3 instructs it to spawn a `general-purpose` subagent. Per [Anthropic SDK docs](https://code.claude.com/docs/en/agent-sdk/subagents) and [GitHub #19077](https://github.com/anthropics/claude-code/issues/19077), subagents cannot spawn subagents. The `Task` call is dead code; worker has been implementing directly via its `Write`/`Edit` tools despite its docstring claiming otherwise.
2. **Stale README line** — `README.md:129` references "Advocate/critic debate with YAGNI lens," leftover from the pre-plan-critic era.
3. **Non-functional metrics hooks** — `hooks/user_prompt_submit.py` and `hooks/stop.py` are documented as "WIP - Not Currently Working" in the README. Nothing depends on them.
4. **Orphaned `doc-reviewer` agent** — not wired into any command workflow (`implement.md:99-102` roster omits it). Dead weight.
5. **Duplication between `code-reviewer` and `performance-reviewer`** — same checks in both files (`code-reviewer.md:56` vs `performance-reviewer.md:23`; SSR boundary lines 35 vs 55). Two spawns per chunk, duplicated file reads.
6. **Stale commit-template model version** — `ccpp.md:52` still says `Claude Opus 4.5`; we're on 4.7.

Separately, the user has stated persistent pain around **design system consistency** in their Next.js + Vercel + Supabase + Tailwind v4 stack. A lean `design-system` skill with `DESIGN.md` loader pattern would address this without the scope creep of a full 4-skill matrix.

## Goals

- Ship evidence-backed correctness and cleanup work
- Remove dead code (broken hooks, orphaned agent, dead delegation)
- Eliminate documented duplication (perf + code reviewer)
- Pilot one stack-aware skill for the user's stated pain (design consistency)
- Validate the skills pattern pays off before committing to a broader skill rollout

## Non-Goals

Explicitly deferred pending evidence of need — do **not** include in this plan:

- `codebase-researcher` / `technical-researcher` frontmatter `inherit` → explicit `sonnet` (no documented cost problem)
- Kanban intra-worker re-read elimination (C2 — ultra-low stakes)
- `CONSTITUTION.md` project-level principles (spec-kit pattern; no evidence our plans drift)
- `[NEEDS CLARIFICATION]` markers (redundant with existing "Open Questions")
- Pre-plan YAGNI/Anti-Abstraction gates (redundant with `plan-critic`'s lenses)
- `[P]` parallel markers + Wave DAG in MEMORY.md (no evidence of phantom completions or parallel collisions)
- `nextjs-vercel`, `supabase`, `tailwind-v4` skills (wait for design-system pilot signal)
- `commands/` → `skills/` migration (no material benefit; both surfaces supported)
- Monolithic-vs-per-phase workflow restructure (no pain reported)

## Approach

Small, surgical, evidence-based. Two phases, shippable independently as separate PRs:

- **Phase 1: Plugin cleanup** — correctness fixes and duplication removal. Low risk, high hygiene value.
- **Phase 2: Design system skill pilot** — lean loader skill (`DESIGN.md` + generic fallbacks + starter template). Evaluate quality impact before scaling to other stack skills.

## Trade-offs

- **Not adopting community best practices wholesale** (spec-kit's Constitution / NEEDS CLARIFICATION / Wave DAG) — accepting we may re-evaluate later if pain surfaces; preferring to solve documented problems over speculative ones.
- **Merging `performance-reviewer` instead of keeping a dedicated lens** — accepting that performance review becomes a sub-rubric of code review; gaining model upgrade (Haiku → Opus) and eliminating duplication; risk is minor lens dilution in the merged rubric.
- **Pilot one skill instead of four** — slower skill rollout; gains evidence-based decisions; avoids the "40/47 skills made output worse" failure mode reported in April 2026 community research.

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Merged `code-reviewer` loses a performance check during consolidation | Medium | Low | Test Spec 1E validates key performance checks still flag |
| `design-system` skill activates but hurts output (skills-made-output-worse pattern) | Low-Med | Low | Starter content deliberately lean; easy to delete skill folder; evaluate on one real feature before scaling |
| Chunk-worker rewrite changes behavior subtly (e.g., implementation quality drops) | Low | Med | Worker already implements directly in practice; doc update aligns spec with reality. Run one test feature end-to-end. |
| Deleting `doc-reviewer` loses a capability we later want | Low | Low | Agent file in git history if needed; can rebuild lighter |

## Phases

### Phase 1: Plugin cleanup

Correctness + duplication fixes. Can ship as one PR (`feature/harness-cleanup` → main).

| Chunk | Size | Depends | Scope | Files |
|-------|------|---------|-------|-------|
| 1A | S | - | Fix chunk-worker correctness | 1 |
| 1B | XS | - | Fix stale README plan-critic description | 1 |
| 1C | S | - | Delete non-functional metrics hooks | 3 |
| 1D | XS | - | Delete orphaned doc-reviewer agent | 2 |
| 1E | M | - | Merge performance-reviewer into code-reviewer | 3 |
| 1F | XS | - | Fix stale ccpp.md model version | 1 |

All Phase 1 chunks are independent — can run in any order or parallel.

### Phase 2: Design system skill pilot

Ship as separate PR after Phase 1 merges, to isolate the evaluation signal.

| Chunk | Size | Depends | Scope | Files |
|-------|------|---------|-------|-------|
| 2A | M | - | `design-system` skill with DESIGN.md loader + starter template | 2 |

---

## Chunk Details

### Chunk 1A — Fix chunk-worker correctness

**Scope:** Align `chunk-worker.md` with reality. The worker already implements directly via `Write`/`Edit`; remove the broken `Task` delegation fiction.

**Files:**
- `agents/chunk-worker.md`

**Tasks:**
- Remove `Task` from `tools:` frontmatter (line 4)
- Rewrite Step 3 (lines 56-77) — replace "Spawn general-purpose agent" with direct implementation guidance (read plan's chunk section, implement via Read/Write/Edit)
- Update file header (lines 8-20) — remove "NO ORCHESTRATION" framing that implies delegation; frame as "implementer for one chunk"
- Leave Steps 1, 2, 4, 5, 6 unchanged

**Definition of Done:**
- `Task` removed from tools
- Step 3 describes direct implementation
- Worker's actual behavior matches its documentation

### Chunk 1B — Fix stale README plan-critic description

**Scope:** Single-line doc fix.

**Files:**
- `README.md`

**Tasks:**
- Line 129: replace `"**Refine** - Advocate/critic debate with YAGNI lens"` with `"**Refine** - Multi-lens critique of the chosen direction"`

**Definition of Done:**
- Line aligns with current `plan-critic` agent behavior

### Chunk 1C — Delete non-functional metrics hooks

**Scope:** Remove files and docs for the broken metrics tracking.

**Files:**
- `hooks/user_prompt_submit.py` (delete)
- `hooks/stop.py` (delete)
- `README.md` (remove "Metrics Tracking (WIP - Not Currently Working)" section ~lines 81-116)

**Tasks:**
- Delete both Python hook files
- Remove README section documenting the hooks
- Remove directory `hooks/` if empty after deletion
- Verify no remaining references to the hooks in any `.md` file via grep
- `commands/implement.md` references "Metrics Tracking" near the top — remove that block too

**Definition of Done:**
- Files deleted
- README section removed
- `grep -r "user_prompt_submit\|stop.py" --include="*.md"` returns no matches

### Chunk 1D — Delete orphaned doc-reviewer agent

**Scope:** Remove the agent and its README row.

**Files:**
- `agents/doc-reviewer.md` (delete)
- `README.md` (remove table row)

**Tasks:**
- Delete `agents/doc-reviewer.md`
- Remove the `| doc-reviewer | Review | Documentation accuracy review |` row from README.md (around line 209)
- Verify no other commands/agents reference `doc-reviewer`

**Definition of Done:**
- File deleted
- README agent table no longer lists it
- `grep -r "doc-reviewer" agents/ commands/ skills/ README.md` returns no matches (history docs are exempt)

### Chunk 1E — Merge performance-reviewer into code-reviewer

**Scope:** Fold `performance-reviewer`'s distinct content into `code-reviewer` as a Performance sub-rubric, then delete the separate agent.

**Files:**
- `agents/code-reviewer.md` (modify — add Performance section)
- `agents/performance-reviewer.md` (delete)
- `README.md` (remove performance-reviewer row from agent table)

**Tasks:**
- In `code-reviewer.md`, add a new Performance section to the Checklist covering non-duplicated items from `performance-reviewer.md`:
  - Bundle size (tree-shaking, lodash imports, `next/image`, `next/font`, `dynamic()`)
  - Memory & Runtime (event listener cleanup, timer clearing)
  - Data fetching (N+1 queries, `Promise.all`, parallel fetches)
  - SSR/Client boundary nuances (`Suspense`, data fetching location — may already overlap; de-dupe during merge)
- Update `code-reviewer.md` description frontmatter to mention performance coverage
- Remove the "Delegate When Needed → Performance concerns?" line (line 80) since we now cover it directly
- Delete `agents/performance-reviewer.md`
- Remove the performance-reviewer row from README.md agent table (around line 208)
- Verify no command or agent spawns `performance-reviewer` via grep

**Definition of Done:**
- Merged `code-reviewer.md` still passes a read-through for coherence (not a kitchen sink — organized into clear sections)
- `agents/performance-reviewer.md` no longer exists
- README reflects the change
- Bundle / N+1 / event-listener checks present in the merged agent

### Chunk 1F — Fix stale ccpp.md model version

**Scope:** Single-line fix.

**Files:**
- `commands/ccpp.md`

**Tasks:**
- Line 52: replace `Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>` with `Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>`

**Definition of Done:**
- Template matches current model

### Chunk 2A — Design system skill pilot

**Scope:** Create a lean `design-system` skill that loads `DESIGN.md` if present and falls through to minimal generic conventions if not. Include a starter `DESIGN.md` template the user can scaffold into projects.

**Files:**
- `skills/design-system/SKILL.md` (new)
- `skills/design-system/DESIGN.template.md` (new — starter template)

**Tasks:**
- Create `skills/design-system/SKILL.md` with frontmatter:
  ```yaml
  ---
  name: design-system
  description: Enforces design system consistency when working on UI components. Auto-loads on UI file changes; reads project's DESIGN.md if present, falls back to minimal conventions.
  paths:
    - "components/**/*.tsx"
    - "app/**/page.tsx"
    - "app/**/layout.tsx"
  ---
  ```
- Body:
  - Instruction: check for `DESIGN.md` at repo root or `docs/DESIGN.md`
  - If found: treat its contents as authoritative design conventions for this project; reference it when making component/token decisions
  - If absent: apply fallback conventions (do not hardcode colors/spacing; prefer existing components in `components/ui/`; use CSS custom properties/tokens over raw values; match patterns from neighboring components; no raw `px` for typography — use tokens or relative units) AND print a banner: `⚠️ No DESIGN.md — working from generic conventions`
  - Instruct: never block; never prompt interactively; report DESIGN.md status in output
  - Point to `skills/design-system/DESIGN.template.md` as the scaffold the user can copy into their project
- Create `skills/design-system/DESIGN.template.md` with sections:
  - Component Library (e.g., shadcn/ui, custom, etc.)
  - Design Tokens (location + usage rules)
  - Composition Patterns (atomic, feature-based, etc.)
  - Extension Policy (when to customize vs. create new)
  - Accessibility Baseline (WCAG level, focus rings, contrast)
  - Anti-Patterns (project-specific no-gos)
- No changes to agents or commands in this chunk — skill activates automatically via `paths:` gating across any agent that touches matching files

**Definition of Done:**
- Skill file created with correct frontmatter
- Template file created
- When invoked on a UI file with `DESIGN.md` present, skill loads and references it
- When invoked on a UI file without `DESIGN.md`, skill falls through gracefully with banner
- No agent/command file changes required

---

## Test Specification

### Risk Summary

- Critical: 0 components
- High: 2 components (1A chunk-worker, 1E merged reviewer)
- Medium: 3 components (1C hooks, 1D doc-reviewer, 2A skill)
- Low: 2 components (1B README line, 1F model string)

### Test Cases

#### Tests for Chunk 1A

| Component | Risk | Test Type |
|---|---|---|
| chunk-worker rewrite | High | Integration (run a real chunk) |

**Tests:**
- [ ] `chunk-worker.md` no longer contains `Task` in tools list
- [ ] Step 3 text no longer references "Spawn general-purpose agent"
- [ ] Run `/intents:implement` on a small test feature (1-2 chunks); confirm worker completes without Task-related errors
- [ ] Confirm git commit is made per chunk
- [ ] MEMORY.md updated correctly after chunk completion

#### Tests for Chunk 1B

| Component | Risk | Test Type |
|---|---|---|
| README line | Low | Verification |

**Tests:**
- [ ] `grep -n "Advocate/critic debate" README.md` returns no matches
- [ ] Line 129 describes multi-lens critique

#### Tests for Chunk 1C

| Component | Risk | Test Type |
|---|---|---|
| Hook deletion | Medium | Verification |

**Tests:**
- [ ] `hooks/user_prompt_submit.py` does not exist
- [ ] `hooks/stop.py` does not exist
- [ ] `hooks/` directory removed (if empty)
- [ ] `grep -r "user_prompt_submit\|stop.py" --include="*.md"` returns no matches in active docs
- [ ] README "Metrics Tracking" section removed
- [ ] `commands/implement.md` no longer references the hooks
- [ ] Plugin still loads without errors (run `claude --plugin-dir .` in a test project)

#### Tests for Chunk 1D

| Component | Risk | Test Type |
|---|---|---|
| doc-reviewer deletion | Medium | Verification |

**Tests:**
- [ ] `agents/doc-reviewer.md` does not exist
- [ ] README agent table no longer lists `doc-reviewer`
- [ ] `grep -r "doc-reviewer" agents/ commands/ skills/ README.md` returns no matches
- [ ] Historical docs under `docs/plans/*` untouched (expected)

#### Tests for Chunk 1E

| Component | Risk | Test Type |
|---|---|---|
| Merged code-reviewer | High | Integration |

**Tests:**
- [ ] `agents/performance-reviewer.md` does not exist
- [ ] `agents/code-reviewer.md` contains a Performance section covering bundle size, memory/runtime, data fetching, SSR/client boundary
- [ ] Duplicated checks (inline JSX object/array literals, Server vs Client data fetching) appear only once
- [ ] README agent table no longer lists `performance-reviewer`
- [ ] Run merged agent against a test file with known perf issues (inline object in JSX prop, sequential awaits in a loop); confirm both flagged
- [ ] Run merged agent against a file with code quality issues (stale comment, unused var, `any` type); confirm both flagged
- [ ] No command or agent file references `performance-reviewer` after the change

#### Tests for Chunk 1F

| Component | Risk | Test Type |
|---|---|---|
| Model version string | Low | Verification |

**Tests:**
- [ ] `commands/ccpp.md:52` reads `Claude Opus 4.7`

#### Tests for Chunk 2A

| Component | Risk | Test Type |
|---|---|---|
| design-system skill | Medium | Integration |

**Tests:**
- [ ] `skills/design-system/SKILL.md` exists with valid frontmatter (name, description, paths)
- [ ] `skills/design-system/DESIGN.template.md` exists with the 6 sections
- [ ] In a test project with a `DESIGN.md` at root, edit a `.tsx` file; confirm skill activates and references DESIGN.md
- [ ] In a test project without `DESIGN.md`, edit a `.tsx` file; confirm skill falls through with warning banner
- [ ] Skill does NOT activate when editing `.py` or `.sql` files (paths glob respects extension)
- [ ] No blocking prompts or interactive requests from the skill

---

## Completion

After both phases ship as their PRs:

```
✅ Phase 1 merged — plugin correctness + duplication cleaned
✅ Phase 2 merged — design-system skill pilot live
Next:
  - Use design-system on one real feature
  - Evaluate quality impact before committing to more stack skills
```

## Re-evaluation Triggers

Pop a deferred Non-Goal back into a future plan if we hit its pain:

- Plans drifting from unstated principles → `CONSTITUTION.md` (D1)
- Refinement missing ambiguity → `[NEEDS CLARIFICATION]` markers (D2)
- Parallel chunks colliding, phantom completions → Wave DAG (E1)
- `design-system` skill delivers measurable wins → expand to `nextjs-vercel`, `supabase`, `tailwind-v4` skills
- Monolithic command fatigue (wanting to re-run one phase independently) → split per-phase workflow restructure
