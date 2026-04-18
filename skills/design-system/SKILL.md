---
name: design-system
description: Enforces design system consistency across planning, implementation, and review. Reads project's DESIGN.md if present; raises absence as Open Question at planning time, or falls back to generic conventions at implementation time. Never blocks, never prompts, never authors DESIGN.md.
paths:
  - "components/**/*.tsx"
  - "src/components/**/*.tsx"
  - "app/**/page.tsx"
  - "app/**/layout.tsx"
---

# Design System

You're working on something involving UI — implementation, review, planning, or critique. Check for a project DESIGN.md:

1. Read `DESIGN.md` at the repo root
2. If not found, check `docs/DESIGN.md`

Then apply the section below matching your current role.

## If DESIGN.md exists

Treat it as authoritative for design decisions in this project.

**Writing or reviewing code** (e.g., chunk-worker, code-reviewer):

- Apply its tokens, components, and composition rules
- When writing: reach for the components, tokens, and patterns it names; honor its extension policy; respect its accessibility baseline
- When reviewing: flag violations (hardcoded values where tokens exist; new primitives where existing ones apply; a11y gaps against its baseline)

**Planning or critiquing a plan** (e.g., feature-plan, plan-critic):

- Reference DESIGN.md components and patterns in your output
- Plans should say "use `<Button>` from `components/ui/` per DESIGN.md §Components" rather than generic "add a button"
- Critiques should flag plans that reinvent existing primitives or ignore DESIGN.md conventions

**At the start of your output, print:**

```
✓ DESIGN.md loaded — following project conventions
```

## If DESIGN.md is absent

**Planning or critiquing a plan:** If the feature involves UI, **raise the missing DESIGN.md as an Open Question** in your output. Give the user concrete options to choose at the checkpoint:

- (a) Scaffold a project DESIGN.md from `skills/design-system/DESIGN.template.md` now
- (b) Describe conventions inline in the plan itself
- (c) Proceed with generic defaults (accept that consistency is not guaranteed)

**Writing or reviewing code:** Apply these fallback conventions —

- No hardcoded colors, spacing, or typography sizes — use CSS custom properties or design tokens
- Prefer existing components from `components/ui/` (or equivalent shared location) over creating new ones
- Match patterns from neighboring components in the same directory
- No raw `px` values for typography — use tokens or relative units (`rem`, `em`)
- Semantic HTML, keyboard reachability, visible focus states, sufficient contrast

**At the start of your output, print:**

```
⚠️ No DESIGN.md found — working from generic conventions. Consistency is not guaranteed.
```

## Always

- **Never block** — skills cannot prompt the user interactively. Report gaps as Open Questions in your output; don't stall waiting for an answer.
- **Never create or modify DESIGN.md yourself** — that's the user's decision, made at a planning checkpoint. Point to the template; don't author conventions.
- **Report DESIGN.md status at the start of every output** — the user needs to know whether you're working from project-specific conventions or generic fallbacks.
