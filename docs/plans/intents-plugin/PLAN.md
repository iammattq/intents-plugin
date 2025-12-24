# Intents Plugin for Claude Code

## Problem Statement

Claude Code works brilliantly in the "smart zone" (~40% context) but degrades on large features. Manual R-P-I (Research-Plan-Implement) workflow with `.intents/` graph works but requires orchestration knowledge. Need a reusable Claude Code plugin that teaches Claude the schema and orchestrates the workflow automatically.

**User pain**: "I've been doing this manually on my portfolio. I want Claude to understand `.intents/` automatically and guide me through bootstrap, planning, and implementation without manual handholding."

## Goals

1. Package R-P-I workflow as installable Claude Code plugin
2. Bootstrap `.intents/` folder from existing codebases via `codebase-analyzer` agent
3. Teach Claude the graph schema (features, capabilities, entities, tech) via skill
4. Integrate with existing agents (feature-plan, feature-implementer, etc.)
5. Keep graph in sync: create nodes during planning, update status during implementation
6. Validate on portfolio site (first test case)

## Non-Goals

- Graph visualization UI (defer to future)
- Orchestrator agent (evaluate in Phase 2 - may not be needed for MVP)
- Claude API integration for sub-agents (use existing Claude Code agent spawning)
- Context budget estimation (start with manual chunking)
- Multi-project support (single project for MVP)

## Proposed Approach

### Architecture

Complete R-P-I workflow packaged as a self-contained plugin:

```
intents-plugin/
├── .claude-plugin/
│   └── plugin.json                  # Plugin manifest
│
├── skills/
│   ├── intents-system/
│   │   └── SKILL.md                 # NEW: Teaches graph schema
│   └── feature-brainstorm/
│       └── SKILL.md                 # COPY: Research ideation
│
├── agents/
│   ├── codebase-analyzer/
│   │   └── AGENT.md                 # NEW: Bootstrap .intents/ (orchestrator pattern)
│   ├── codebase-researcher/
│   │   └── AGENT.md                 # COPY: Internal exploration
│   ├── technical-researcher/
│   │   └── AGENT.md                 # COPY: External research
│   ├── feature-refine/
│   │   └── AGENT.md                 # COPY: Advocate/critic debate
│   ├── feature-plan/
│   │   └── AGENT.md                 # MODIFIED: Create graph node
│   ├── test-spec/
│   │   └── AGENT.md                 # COPY: TDD specs
│   ├── feature-implementer/
│   │   └── AGENT.md                 # MODIFIED: Update graph status
│   ├── code-reviewer/
│   │   └── AGENT.md                 # COPY: Code validation
│   ├── security-auditor/
│   │   └── AGENT.md                 # COPY: Security review
│   └── accessibility-reviewer/
│       └── AGENT.md                 # COPY: A11y review
│
├── commands/
│   ├── init.md                      # /intents:init
│   ├── status.md                    # /intents:status
│   ├── plan.md                      # /intents:plan
│   ├── implement.md                 # /intents:implement
│   └── validate.md                  # /intents:validate
│
├── templates/
│   ├── graph.yaml                   # Empty feature tree scaffold
│   ├── capabilities.yaml            # Empty capability catalog
│   ├── entities.yaml                # Empty entity schema
│   └── tech.yaml                    # Empty tech dependencies
│
└── README.md
```

### Key Components

**1. Skills**

| Skill | Purpose | Action |
|-------|---------|--------|
| `intents-system` | Teaches graph schema, inheritance, when to read/write | NEW |
| `feature-brainstorm` | Research phase: divergent ideation | COPY |

**2. Agents (Complete R-P-I Workflow)**

| Agent | Role | Phase | Action |
|-------|------|-------|--------|
| `codebase-analyzer` | Bootstrap `.intents/` from existing code | Bootstrap | NEW (orchestrator) |
| `codebase-researcher` | Internal codebase exploration | Research | COPY |
| `technical-researcher` | External research (docs, APIs) | Research | COPY |
| `feature-refine` | Advocate/critic debate for PRD | Research | COPY |
| `feature-plan` | Create PLAN.md + graph node | Plan | MODIFIED |
| `test-spec` | TDD specifications | Plan | COPY |
| `feature-implementer` | Orchestrate implementation chunks | Implement | MODIFIED |
| `code-reviewer` | Code validation | Implement | COPY |
| `security-auditor` | Security review | Implement | COPY |
| `accessibility-reviewer` | A11y review | Implement | COPY |

**3. Commands**
- `/intents:init` - runs `codebase-analyzer`, writes `.intents/` folder
- `/intents:status` - shows graph state, feature status, what's implemented/planned/broken
- `/intents:plan [feature]` - spawns research → plan workflow + creates graph node
- `/intents:implement [feature]` - spawns `feature-implementer` + updates status
- `/intents:validate` - detect and fix structural issues in graph

**4. Graph Access Patterns**

| Phase | Access | What Changes |
|-------|--------|--------------|
| Research | READ | Nothing — gathers context from graph |
| Plan | WRITE | Creates feature node, status: `planned` |
| Implement | WRITE | Updates status: `in-progress` → `implemented` |

**5. codebase-analyzer Orchestrator Pattern**

Unlike `codebase-researcher` (answers specific questions), `codebase-analyzer`:
1. Gets birds-eye view of project structure
2. Spawns **parallel** `codebase-researcher` agents to explore different branches
3. Each researcher returns compressed findings (200-400 words)
4. Analyzer compiles all findings into `.intents/` graph files

### File System as Contract

The plugin doesn't create a new interface—it reads/writes to `.intents/` and `docs/plans/`. Claude Code already understands file systems. The graph schema IS the API.

### Complete R-P-I Workflow

**Bootstrap (one-time setup):**
```
User: /intents:init
  → codebase-analyzer spawns parallel codebase-researcher agents
  → Each researcher explores different branches (200-400 word summaries)
  → Analyzer compiles findings into .intents/ graph files
  → User reviews and confirms generated structure
```

**Research → Plan:**
```
User: /intents:plan new-feature
  → feature-brainstorm: divergent ideation
  → codebase-researcher: explore internal context
  → technical-researcher: research external docs/APIs
  → feature-refine: advocate/critic debate
  → feature-plan: synthesize into PLAN.md
  → Graph updated: add feature node, status: planned
```

**Implementation:**
```
User: /intents:implement new-feature
  → Graph updated: status → in-progress
  → test-spec: generate TDD specs
  → feature-implementer: orchestrate chunks
  → code-reviewer: validate implementation
  → security-auditor: security review
  → accessibility-reviewer: a11y review
  → Graph updated: status → implemented
```

**Query:**
```
User: /intents:status
  → Show feature tree, capabilities, inheritance
  → Flag out-of-sync or broken features
```

**Repair:**
```
User: /intents:validate
  → Detect structural issues (missing plans, undefined capabilities, etc.)
  → With --fix: prompt user, apply approved fixes
```

## Trade-offs & Decisions

| Decision | Rationale | Trade-off |
|----------|-----------|-----------|
| File-based (not API/DB) | Simple, versionable, readable | Manual sync required |
| Skill vs hardcoded | Teachable, debuggable, transparent | Relies on model following instructions |
| Bootstrap via analyzer | Automates tedious manual work | May need human correction |
| Commands invoke agents | Reuses existing agent patterns | Adds layer vs direct invocation |
| Defer orchestrator | Simpler MVP, may not be needed | Manual chunk management initially |

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Schema too complex for LLM to follow | High | Progressive disclosure, examples in skill |
| Graph gets out of sync with code | Medium | Status checking commands, validation helpers |
| Bootstrap produces wrong structure | Medium | Review step before writing, easy to regenerate |
| Portfolio site structure is too unique | Low | Test on 2nd project in Phase 2 |
| Capability modes confusing | Medium | Clear examples, default to no modes |

## Technical Approach

### Components Affected

**New files:**
- `/home/mq/Projects/agents-and-skills/intents-plugin/.claude-plugin/plugin.json`
- `/home/mq/Projects/agents-and-skills/intents-plugin/skills/intents-system/SKILL.md`
- `/home/mq/Projects/agents-and-skills/intents-plugin/agents/codebase-analyzer/AGENT.md`
- `/home/mq/Projects/agents-and-skills/intents-plugin/commands/*.md` (5 files)
- `/home/mq/Projects/agents-and-skills/intents-plugin/templates/*.yaml` (4 files)
- `/home/mq/Projects/agents-and-skills/intents-plugin/README.md`

**Copied files (unmodified):**
- Skills:
  - `/home/mq/Projects/agents-and-skills/skills/feature-brainstorm/SKILL.md` → plugin
- Agents:
  - `/home/mq/Projects/agents-and-skills/agents/codebase-researcher.md` → plugin
  - `/home/mq/Projects/agents-and-skills/agents/technical-researcher.md` → plugin
  - `/home/mq/Projects/agents-and-skills/agents/feature-refine.md` → plugin
  - `/home/mq/Projects/agents-and-skills/agents/test-spec.md` → plugin
  - `/home/mq/Projects/agents-and-skills/agents/code-reviewer.md` → plugin
  - `/home/mq/Projects/agents-and-skills/agents/security-auditor.md` → plugin
  - `/home/mq/Projects/agents-and-skills/agents/accessibility-reviewer.md` → plugin

**Modified files (copied + graph integration added):**
- `/home/mq/Projects/agents-and-skills/agents/feature-plan.md` → plugin (adds graph node creation)
- `/home/mq/Projects/agents-and-skills/agents/feature-implementer.md` → plugin (adds status updates)

**Total plugin files:**
- 2 skills
- 10 agents (8 copied, 2 modified, 1 new)
- 5 commands
- 4 templates
- 1 plugin manifest
- 1 README

**Dependencies:**
- No external packages (pure Claude Code)
- Self-contained: all R-P-I agents included in plugin

### Data Model

**graph.yaml schema:**
```yaml
features:
  feature-id:
    name: Feature Name
    type: feature
    status: new | planned | in-progress | implemented | broken
    intent: User-facing value description
    parent: parent-feature-id
    capabilities:
      - capability-name
      - capability-name:mode
    plan: docs/plans/feature-id/plan.md  # optional
```

**capabilities.yaml schema:**
```yaml
capability-id:
  name: Capability Name
  type: capability
  category: ui | storage | media | auth | content | export | sync
  intent: What this enables
  adr: docs/decisions/XXX-capability.md
  tech:
    - tech-dependency-id
  interface: |
    What functions/APIs available
  modes:  # optional
    mode-name: Description of what's available
```

**entities.yaml schema:**
```yaml
entity-id:
  name: EntityName
  type: entity
  capabilities:  # invoked based on state
    - capability-name
  state:
    - field: type
```

**tech.yaml schema:**
```yaml
tech-id:
  name: Tech Name
  type: tech
  category: database | cloud | auth | ui | processing | state
  config: path/to/config
  docs: docs/guides/tech.md  # optional
  purpose: What it does  # if no docs
```

## Implementation Phases

### Phase 1: Foundation (Bootstrap + Skills + Base Agents)

**Intent:** Create plugin structure, copy all workflow agents/skills, implement bootstrap logic

**Ship Criteria:**
- Plugin structure complete with all agents/skills copied
- `/intents:init` command creates valid `.intents/` folder
- `intents-system` skill loaded when `.intents/` detected
- Graph validates against portfolio site structure
- All R-P-I agents available in plugin

**Tasks:**

1. **Plugin scaffold** (plugin.json, README, folder structure)
2. **Template files** (empty graph.yaml, capabilities.yaml, entities.yaml, tech.yaml with comments)
3. **Copy all existing agents** (8 agents: codebase-researcher, technical-researcher, feature-refine, test-spec, code-reviewer, security-auditor, accessibility-reviewer, feature-plan, feature-implementer)
4. **Copy feature-brainstorm skill**
5. **Create `intents-system` skill** (schema teaching, examples from portfolio)
6. **Create `codebase-analyzer` agent** (spawns researchers, compiles graph)
7. **`/intents:init` command** (runs analyzer, writes files, prompts for review)
8. **Validation on portfolio site** (run init, review output, refine)

**Session Chunks:**

| Chunk | Scope | Files |
|-------|-------|-------|
| 1A | Plugin scaffold + templates | 6 files (plugin.json, README, 4 templates) |
| 1B | Copy existing agents to plugin (no modifications) | 8 agent files |
| 1C | Copy feature-brainstorm skill | 1 skill file |
| 1D | `intents-system` skill (schema + examples) | 1 file (SKILL.md) |
| 1E | `codebase-analyzer` agent (orchestrator pattern) | 1 file (AGENT.md) |
| 1F | `/intents:init` command | 1 file (init.md) |
| 1G | Portfolio site bootstrap test | Testing/refinement |

### Phase 2: Status + Query (Read Operations)

**Intent:** Query graph state, show what's implemented/planned

**Ship Criteria:**
- `/intents:status` shows feature tree with status
- `/intents:status [feature]` shows capabilities, plan link, dependencies
- Output is human-readable and actionable

**Tasks:**

1. **`/intents:status` command** (parse graph, display tree)
2. **Status display logic** (resolve inheritance, show effective capabilities)
3. **Validation on portfolio** (run status, verify output matches reality)

**Session Chunks:**

| Chunk | Scope | Files |
|-------|-------|-------|
| 2A | `/intents:status` command (basic tree display) | 1 file (status.md) |
| 2B | Status detail view (capabilities + inheritance) | 1 file (modify status.md) |
| 2C | Testing on portfolio | Testing/refinement |

### Phase 3: Plan Integration (Write Operations)

**Intent:** `/intents:plan` orchestrates R-P workflow and creates graph nodes

**Ship Criteria:**
- `/intents:plan [feature]` orchestrates full research → plan workflow
- Uses existing agents: feature-brainstorm, codebase-researcher, technical-researcher, feature-refine
- After PLAN.md written, feature node created in graph.yaml
- Node includes capabilities extracted from plan
- Inheritance calculated correctly

**Tasks:**

1. **Modify `feature-plan` agent for graph integration**
2. **Add graph node creation logic** (parse plan, extract capabilities, create node)
3. **`/intents:plan` command** (orchestrates: brainstorm → research → refine → plan → graph update)
4. **Test on portfolio** (plan a new feature, verify graph updated)

**Session Chunks:**

| Chunk | Scope | Files |
|-------|-------|-------|
| 3A | Modify `feature-plan` for graph node creation | 1 file (agents/feature-plan/AGENT.md) |
| 3B | `/intents:plan` command (orchestrates R-P workflow) | 1 file (plan.md) |
| 3C | Test on portfolio (plan new feature) | Testing/validation |

### Phase 4: Implementation Integration (Status Updates)

**Intent:** `/intents:implement` orchestrates implementation with graph status tracking

**Ship Criteria:**
- `/intents:implement [feature]` invokes `feature-implementer`
- Uses existing agents: test-spec, code-reviewer, security-auditor, accessibility-reviewer
- Status transitions: new → planned → in-progress → implemented
- Graph stays in sync with actual code state
- Broken features flagged on test failure

**Tasks:**

1. **Modify `feature-implementer` for graph integration**
2. **Add status update hooks** (start, complete, error)
3. **`/intents:implement` command** (orchestrates implementation workflow)
4. **Test on portfolio** (implement a feature, verify status updates)

**Session Chunks:**

| Chunk | Scope | Files |
|-------|-------|-------|
| 4A | Modify `feature-implementer` for graph status updates | 1 file (agents/feature-implementer/AGENT.md) |
| 4B | `/intents:implement` command | 1 file (implement.md) |
| 4C | Test on portfolio (full R-P-I cycle) | Testing/validation |

### Phase 5: Polish + Documentation (Ship MVP)

**Intent:** Plugin ready for sharing, documented, validated

**Ship Criteria:**
- README explains installation, usage, workflow
- All commands documented with examples
- Tested on portfolio site end-to-end
- Published to GitHub (if desired)

**Tasks:**

1. **Complete README** (installation, commands, workflow, examples)
2. **Command documentation** (each command has usage examples)
3. **End-to-end test on portfolio** (init → plan → implement cycle)
4. **Refinements based on testing**

**Session Chunks:**

| Chunk | Scope | Files |
|-------|-------|-------|
| 5A | README.md (installation + overview) | 1 file |
| 5B | Command docs + examples | 4 files (modify commands/*.md) |
| 5C | End-to-end portfolio test | Testing |
| 5D | Bug fixes + refinements | Various |

### Phase 6: Validation (Graph Repair)

**Intent:** Add `/intents:validate` command that detects and optionally fixes structural issues in the graph

**Ship Criteria:**
- `/intents:validate` reports all structural issues in structured format
- `/intents:validate --fix` prompts user for each issue with fix options
- Reuses detection logic from `/intents:status` sync checking (Step 6)
- Adds one new check: broken capability reference (tech not in tech.yaml)
- All fixes are non-destructive (prompts before any write)
- Output format matches specification

**Tasks:**

1. **Create `/intents:validate` command** - detect and report issues
2. **Add broken capability reference check** - capability references tech not in tech.yaml
3. **Add `--fix` mode** - interactive prompts for each issue type
4. **Implement fix actions**:
   - Remove plan reference from feature
   - Add capability to capabilities.yaml (placeholder)
   - Remove capability from feature
   - Remove feature from graph (orphaned)
   - Add tech to tech.yaml (placeholder)
   - Remove tech reference from capability
5. **Update status command** - add hint to run validate when issues found

**Issue Types and Fix Options:**

| Issue Type | Detection | Fix Options |
|------------|-----------|-------------|
| `MISSING_PLAN` | Feature has `plan:` field but file doesn't exist | (r) Remove reference, (s) Skip |
| `UNDEFINED_CAPABILITY` | Feature uses capability not in capabilities.yaml | (r) Remove from feature, (a) Add to capabilities.yaml, (s) Skip |
| `ORPHANED_FEATURE` | Feature has no parent and isn't root | (r) Remove from graph, (s) Skip |
| `BROKEN_CAPABILITY_REF` | Capability references tech not in tech.yaml | (r) Remove tech reference, (a) Add to tech.yaml, (s) Skip |

**Session Chunks:**

| Chunk | Scope | Files |
|-------|-------|-------|
| 6A | `/intents:validate` command (detect + fix modes, all 4 issue types) | 1 file (commands/validate.md) |
| 6B | Testing + status.md update (add validate hint) | 1 file (status.md) + testing |

## Session Protocol

### Start of Session
1. Read `/home/mq/Projects/agents-and-skills/docs/plans/intents-plugin/MEMORY.md`
2. Check current chunk status
3. Resume from last completed step

### During Session
1. Update MEMORY.md with decisions, blockers, deviations
2. Test incrementally (don't wait until end)
3. Flag uncertainty or questions immediately

### End of Session
1. Mark chunk complete in MEMORY.md
2. Note next steps explicitly
3. Commit progress with descriptive message
4. Update graph status if testing on portfolio

## Open Questions

1. **Orchestrator necessity**: Do we need `intents-orchestrator` agent in MVP? Or can commands handle coordination?
   - **Decision point**: After Phase 2, assess if manual coordination is painful

2. **Capability detection**: How does `codebase-analyzer` identify capabilities vs tech?
   - **Approach**: Look for patterns (hooks = capability, packages = tech), prompt user for confirmation

3. **Graph validation**: Should plugin validate graph on load?
   - **MVP answer**: No. Trust file system. Add validation in Phase 5 if needed.

4. **Multi-file updates**: How to safely update graph.yaml when multiple agents might touch it?
   - **MVP answer**: Sequential only. Parallel updates are post-MVP.

5. **Status sync failures**: What if implementation completes but graph isn't updated?
   - **Mitigation**: `/intents:status` includes "out of sync?" check

## Implementation Guide

### Required Skills
- `agent-builder` - for creating new agents (codebase-analyzer)
- `context-management` - understanding `.intents/` schema aligns with CLAUDE.md patterns

### Post-Implementation Reviewers
- `code-reviewer` - validate agent logic, command structure
- Manual testing on portfolio site (primary validation)

### Testing Strategy

**Per Phase:**
1. Unit: Does the component work in isolation?
2. Integration: Does it work with existing agents?
3. Portfolio: Does it work on real codebase?

**Phase 1 Test:**
- Run `/intents:init` on portfolio
- Verify graph.yaml matches existing structure
- Check capabilities.yaml has auth, images, persistence, etc.

**Phase 2 Test:**
- Run `/intents:status`
- Verify tree shows admin, goodies, journal, work branches
- Check capability inheritance displays correctly

**Phase 3 Test:**
- Run `/intents:plan test-feature`
- Verify PLAN.md created AND graph node added
- Check capabilities extracted correctly

**Phase 4 Test:**
- Run `/intents:implement test-feature`
- Verify status transitions (planned → in-progress → implemented)
- Check graph reflects actual code state

**Phase 5 Test:**
- Complete R-P-I cycle on real portfolio feature
- Document any friction points
- Refine based on real usage

**Phase 6 Test:**
- Introduce intentional issues in graph (missing plan, undefined capability)
- Run `/intents:validate` and verify detection
- Run `/intents:validate --fix` and verify interactive prompts work
- Confirm fixes are applied correctly

## Success Metrics

**MVP Success:**
- Portfolio site has valid `.intents/` folder (bootstrapped)
- Can plan a new feature via `/intents:plan`
- Graph stays in sync during implementation
- README clear enough for user to install + use on different project

**Quality Indicators:**
- Graph matches human mental model of architecture
- Commands feel natural (not fighting the tool)
- Less manual graph editing than current workflow
- User says "this is easier than doing it manually"

## Future Enhancements (Post-MVP)

1. **Graph visualization** - Web UI showing tree structure
2. **Context budget estimation** - Auto-chunk based on token counts
3. **Orchestrator agent** - Full automation of R-P-I
4. **Multi-project support** - Plugin works across any codebase
5. **Validation layer** - Schema validation on graph mutations
6. **Conflict resolution** - Handle concurrent graph updates
7. **Export formats** - Mermaid diagrams, JSON API, etc.

---

## Appendix: Schema Examples

### Feature Node (from portfolio)
```yaml
admin-galleries:
  name: Gallery Management
  type: feature
  status: implemented
  intent: Create, edit, organize photo galleries
  parent: admin
  plan: docs/plans/admin/galleries/plan.md
  capabilities:
    - images:manage
    - upload
    # inherits: persistence:read-write, session-auth (from admin)
```

### Capability Node (from portfolio)
```yaml
images:
  name: Image Processing
  type: capability
  category: media
  intent: Upload, process, serve optimized images
  adr: docs/decisions/003-image-pipeline.md
  tech:
    - s3
    - sharp
    - blur-hash
  interface: |
    buildImageUrl(key: string, transforms?: ImageTransforms): string
    useImage(key: string): { url, blurhash, loading }
  modes:
    consume: Display images (buildImageUrl, useImage hook)
    manage: Upload, delete, reorder (processImageUpload, deleteObject)
```

### Entity Node (from portfolio)
```yaml
Gallery:
  name: Gallery
  type: entity
  capabilities:
    - images:manage  # when published=true and user is admin
  state:
    - published: boolean
    - protected: boolean
    - images: Image[]
```

### Tech Node (from portfolio)
```yaml
s3:
  name: AWS S3
  type: tech
  category: cloud
  config: src/lib/s3.ts
  docs: docs/guides/image-storage.md
  purpose: Object storage for uploaded images
```
