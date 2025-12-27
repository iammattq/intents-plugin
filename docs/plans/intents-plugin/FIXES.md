# Intents Plugin Bug Fixes

Tracking bug fixes discovered during real-world usage.

---

## FIX-001: codebase-analyzer outputs wrong schema format

**Status:** Fixed
**Priority:** High
**Discovered:** 2024-12-24
**Fixed:** 2024-12-24

### Problem

The `codebase-analyzer` agent generates `.intents/` files in a different schema than what the `intents-system` skill and templates define.

**Expected (per templates + intents-system skill):**
```yaml
root:
  name: Portfolio
  type: feature
  status: implemented
  intent: Demonstrate skills and thinking through interactive work
  capabilities:
    - design-system
    - theming

features:
  home:
    name: Home
    type: feature
    status: implemented
    intent: Create memorable first impression
    parent: root
```

**Actual (what codebase-analyzer generates):**
```yaml
features:
  home:
    path: /
    status: implemented
    description: Public landing page with intro
    capabilities: [themes]
```

### Why Old Format is Correct

The `.intents/` system is about capturing **architectural intent**, not file structure:

| Field | Old (Correct) | New (Wrong) |
|-------|---------------|-------------|
| `intent:` | Purpose-focused: "What it enables for users" | Missing |
| `description:` | N/A | Structure-focused: "What it is" |
| `name:` | Human-readable name | Missing |
| `type:` | Explicit typing (feature/capability/entity) | Missing |
| `parent:` | Graph traversable both ways | Implicit via nesting |
| `adr:` | Links to architectural decisions | Missing |
| `category:` | Grouping for capabilities | Missing |

The new format is just a route map. The old format captures WHY things exist.

### Root Cause

The `codebase-analyzer` AGENT.md doesn't include the schema definition. It tells the agent WHAT to generate but not the exact FORMAT. The agent improvises a schema.

### Fix Plan

**Chunk 1: Add schema reference to codebase-analyzer**

Edit `intents-plugin/agents/codebase-analyzer/AGENT.md`:

1. Add explicit schema examples in Phase 3 (Compile Findings)
2. Reference the template files for exact format
3. Include all required fields: `name`, `type`, `intent`, `parent`, `adr`, `category`

**Chunk 2: Add schema validation**

The agent should validate its output matches the expected schema before presenting to user:

- `root:` section exists
- All features have `name`, `type`, `status`, `intent`
- All capabilities have `name`, `type`, `category`, `intent`, `tech`
- Parent references are valid

**Chunk 3: Update templates with complete examples**

Ensure `intents-plugin/templates/*.yaml` have comprehensive examples that the agent can reference.

### Files to Modify

| File | Change |
|------|--------|
| `agents/codebase-analyzer/AGENT.md` | Add schema examples in Phase 3 |
| `templates/graph.yaml` | Ensure complete example |
| `templates/capabilities.yaml` | Ensure complete example |
| `templates/entities.yaml` | Ensure complete example |
| `templates/tech.yaml` | Ensure complete example |

### Acceptance Criteria

- [ ] Running `/intents:init` generates files matching template schema
- [ ] All features have `name`, `type`, `status`, `intent`, `parent`
- [ ] All capabilities have `name`, `type`, `category`, `intent`, `tech`
- [ ] `root:` section exists in graph.yaml
- [ ] `/intents:status` parses the output correctly
- [ ] `/intents:validate` finds no schema errors

### Notes

- The codebase-analyzer previously had a bug where it merged from existing `.intents/` folders (fixed in commit 4783115)
- The schema mismatch was discovered when comparing fresh bootstrap output to hand-crafted `.intents/`

### Resolution

Modified `agents/codebase-analyzer/AGENT.md`:

1. **Added explicit schema examples** in Phase 3 showing exact YAML format for all 4 files
2. **Added self-validation checklist** before presenting to user
3. Each schema shows required fields, valid values, and inline comments

The agent now has unambiguous schema documentation and must verify output matches before proceeding.

---

## FIX-002: feature-implementer doesn't validate output against plan schema

**Status:** Fixed
**Priority:** High
**Discovered:** 2024-12-24
**Fixed:** 2024-12-24

### Problem

The `feature-implementer` agent built `codebase-analyzer` without validating that its output matched the schema defined in PLAN.md. The plan explicitly defined the graph.yaml schema, but the implementer didn't check that the generated code would produce that format.

This is a **process bug** in the R-P-I workflow itself.

### Evidence

- PLAN.md (and intents-system skill) defined explicit schema with `root:`, `name:`, `type:`, `intent:`, `parent:`
- feature-implementer built codebase-analyzer
- codebase-analyzer outputs completely different schema
- No validation caught this mismatch
- Bug only discovered during real-world usage

### Root Cause

The `feature-implementer` AGENT.md has validation steps but they focus on:
- Code runs without errors
- Tests pass
- Code review passes

Missing: **Schema/contract validation** - does the output match the spec?

### Why This Matters

The whole point of R-P-I is:
1. **Research** - understand the problem
2. **Plan** - define the solution (including schemas, contracts, formats)
3. **Implement** - build what the plan says

If implementation doesn't validate against the plan's specifications, we lose the benefit of planning. The plan becomes documentation, not a contract.

### Fix Plan

**Chunk 1: Add "Validate Against Plan" step to feature-implementer**

Edit `intents-plugin/agents/feature-implementer/AGENT.md`:

Add explicit step after implementation, before marking complete:

```markdown
### Step N: Validate Against Plan

Before marking a chunk complete:

1. Re-read the relevant section of PLAN.md
2. For each specification in the plan:
   - Schema definitions → verify output matches
   - API contracts → verify signatures match
   - File formats → verify structure matches
   - Acceptance criteria → verify each is met
3. If ANY specification doesn't match:
   - Do NOT mark complete
   - Fix the implementation
   - Re-validate
```

**Chunk 2: Add schema validation to codebase-analyzer specifically**

The codebase-analyzer should validate its own output:
- Parse generated YAML
- Check required fields exist
- Compare against template structure

**Chunk 3: Add "Contract Testing" concept to test-spec agent**

The `test-spec` agent should generate tests that verify:
- Output schemas match specifications
- API contracts are honored
- File formats are correct

### Files to Modify

| File | Change |
|------|--------|
| `agents/feature-implementer/AGENT.md` | Add "Validate Against Plan" step |
| `agents/codebase-analyzer/AGENT.md` | Add self-validation of output schema |
| `agents/test-spec/AGENT.md` | Add contract/schema test generation |

### Acceptance Criteria

- [ ] feature-implementer explicitly validates output against plan specs
- [ ] Implementer refuses to mark complete if specs don't match
- [ ] codebase-analyzer validates its output before presenting
- [ ] test-spec generates schema validation tests
- [ ] This class of bug (output doesn't match spec) is caught during implementation, not usage

### Broader Lesson

The R-P-I workflow needs a **contract enforcement** mechanism:
- Plans define contracts (schemas, formats, APIs)
- Implementation must honor contracts
- Validation must verify contracts
- "Done" requires contract compliance

Without this, planning is just wishful thinking.

### Resolution

Added **Contract Validation** section to Step 6 (Validate Chunk Completion) in `feature-implementer/AGENT.md`.

The validation now checks artifact-type-specific contracts:
- AGENT specs → verify spec documents the schema
- Code → run and verify output matches plan
- APIs → verify signatures match spec
- File formats → verify structure matches spec

Simpler fix than originally planned (skipped test-spec changes - YAGNI). The core fix is mandatory contract checking before marking chunks complete.

### Decision Process

Ran three options through `feature-refine` agent:
- **Option A**: Add reminder to spawn prompt (Step 5)
- **Option B**: Add validation to Step 6
- **Option C**: Both A and B

Feature-refine rejected Option A as "too vague to be actionable" - a generic reminder doesn't distinguish artifact types. Key insight: validating an AGENT.md spec means checking the spec *documents* the schema, not running code.

Chose Option B with artifact-type-specific examples. The pragmatism lens reduced scope from the original 3-chunk plan (implementer + analyzer + test-spec) to a single targeted change.

---

## Template: Future Fixes

```markdown
## FIX-XXX: Brief description

**Status:** Open | In Progress | Fixed
**Priority:** High | Medium | Low
**Discovered:** YYYY-MM-DD

### Problem
What's broken and how it manifests.

### Root Cause
Why it's happening.

### Fix Plan
Step-by-step fix approach.

### Files to Modify
List of files.

### Acceptance Criteria
- [ ] How to verify the fix works
```
