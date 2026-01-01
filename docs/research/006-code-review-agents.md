# Research 006: Code Review Agents for Claude Code

**Date:** 2025-12-29

**Status:** Complete

**Related:** Agent architecture for intents-plugin, existing code-reviewer agent enhancement

## Problem Statement

How do we build high-quality code review sub-agents for Claude Code? This research covers:

1. Code review agent patterns and architectures
2. Next.js, React, TypeScript code review best practices
3. Standard code review methodologies (SOLID, complexity, security)
4. Existing Claude Code review implementations
5. Effective prompt structures for code review agents

## Constraints

- Must work within Claude Code's subagent framework
- Should integrate with existing agents (security-auditor, accessibility-reviewer)
- Need to balance comprehensive coverage vs. focused, actionable feedback
- Must avoid overwhelming developers with low-signal noise
- Should complement (not replace) static analysis tools like ESLint

---

## Part 1: Code Review Agent Architecture Patterns

### Multi-Agent vs. Monolithic Review

Research consistently shows that **specialized agents outperform generalist agents** for code review:

> "The world of software development has already learned that monolithic applications don't scale. The same principle applies to AI agents--a single agent tasked with too many responsibilities becomes a 'Jack of all trades, master of none.' As the complexity of instructions increases, adherence to specific rules degrades, leading to more hallucinations."
> -- [Tanagram AI](https://tanagram.ai/news/ai-agent-architecture-patterns-for-code-review-automation-the-complete-guide)

**Recommended architecture:**

| Agent Type | Focus | Tools | Model |
|------------|-------|-------|-------|
| `code-reviewer` | General quality, patterns, DRY | Read, Grep, Glob, Bash | sonnet |
| `security-auditor` | OWASP, auth, injection | Read, Grep, Glob, Bash | sonnet |
| `accessibility-reviewer` | WCAG 2.2 AA compliance | Read, Grep, Glob | sonnet |
| `performance-reviewer` | Re-renders, bundle size, SSR | Read, Grep, Glob, Bash | haiku |

### Generator-Critic Pattern

The **Generator-Critic pattern** separates content creation from validation:

> "One agent acts as the Generator, producing a draft, while a second agent acts as the Critic, reviewing it against specific criteria."
> -- [Google Developers Blog](https://developers.googleblog.com/developers-guide-to-multi-agent-patterns-in-adk/)

**Application to Claude Code:**
- `feature-implementer` generates code
- `code-reviewer` critiques against standards
- Orchestrator validates both before proceeding

### Deterministic + AI Hybrid

The most effective pattern combines **deterministic tools with AI reasoning**:

> "LLMs should be applied strategically for generating queries from natural language policy descriptions and providing contextual reasoning for complex patterns, while the actual enforcement remains deterministic."
> -- [Tanagram AI](https://tanagram.ai/news/ai-agent-architecture-patterns-for-code-review-automation-the-complete-guide)

**Practical implementation:**
1. Run ESLint/TypeScript first (deterministic, fast)
2. Use AI agent for semantic issues linting can't catch:
   - Stale comments
   - Misleading names
   - Architectural violations
   - Business logic errors

---

## Part 2: Comprehensive vs. Focused Review Trade-offs

### The Noise Problem

> "While comprehensive analysis can be valuable, it also clutters the GitHub timeline and can overwhelm developers, especially on larger changes. You'll need to invest time in configuration to dial down irrelevant feedback."
> -- [Bito AI](https://bito.ai/compare/bitos-ai-code-review-agent-vs-coderabbit/)

### Tiered Review Strategy

A tiered approach balances thoroughness with actionability:

| Review Tier | When to Use | Depth | Speed |
|-------------|-------------|-------|-------|
| **Essential** | Routine changes | Security, error handling, validation | Fast |
| **Standard** | Feature PRs | + DRY, patterns, naming | Medium |
| **Comprehensive** | Critical paths, auth, payments | + Architecture, SOLID, performance | Thorough |

### Specialized vs. General Agents

> "Generic agents are okay agents. Specific agents are game-changers."
> -- [Mobalab Engineering](https://engineering.mobalab.net/2025/08/28/claude-code-subagents-a-developers-guide-to-specialized-ai-assistants/)

**Recommendation:** Use the general `code-reviewer` for most PRs, but delegate to specialized agents (`security-auditor`, `accessibility-reviewer`) when specific concerns arise.

---

## Part 3: React + TypeScript Code Review Checklist

### TypeScript-Specific Code Smells

Recent research identified **6 key code smells specific to React + TypeScript**:

| Code Smell | Severity | Detection Pattern |
|------------|----------|-------------------|
| **Any Type** | High | `any` keyword usage |
| **Non-Null Assertions** | High | `!` operator on possibly-null values |
| **Missing Union Type Abstraction** | Medium | Repeated union types not extracted |
| **Enum Implicit Values** | Low | Enums without explicit values |
| **Overly Flexible Props** | Medium | Props accepting too many types |
| **Multiple Booleans for State** | High | `isLoading`, `isError`, `isSuccess` instead of union |

Source: [ScienceDirect - Detection of code smells in React with TypeScript](https://www.sciencedirect.com/science/article/abs/pii/S0950584925001740)

### React Anti-Patterns Checklist

**Component Structure:**
- [ ] Components under 200-300 lines (create child components if larger)
- [ ] JSX markup under 50 lines
- [ ] Single responsibility per component
- [ ] Logic moved out of render/return into helper functions

**Hooks:**
- [ ] All dependencies included in useEffect/useCallback/useMemo arrays
- [ ] No stale closures (functional updates for state in effects)
- [ ] Custom hooks extracted for reusable logic
- [ ] Event listeners cleaned up in effect cleanup functions
- [ ] Timers unregistered in cleanup effects

**Performance:**
- [ ] No object/array literals in JSX props (causes re-renders)
- [ ] Stable keys on lists (not array index)
- [ ] Expensive components memoized with React.memo
- [ ] Context values memoized to prevent cascade re-renders
- [ ] useCallback for functions passed as props

**Props:**
- [ ] Props destructured in component signature
- [ ] No unused props passed
- [ ] PropTypes or TypeScript interfaces defined
- [ ] No prop drilling beyond 2-3 levels (use context or composition)

Sources: [Pagepro](https://pagepro.co/blog/18-tips-for-a-better-react-code-review-ts-js/), [DEV.to](https://dev.to/padmajothi_athimoolam_23d/react-code-review-essentials-a-detailed-checklist-for-developers-20n2)

### Stale Closure Detection

> "A stale closure captures the initial values of variables and never updates them. The effect captures the initial values of userId, messages, counter, and userName and never updates them, leading to stale closures."
> -- [TkDodo's Blog](https://tkdodo.eu/blog/hooks-dependencies-and-stale-closures)

**Detection patterns:**
```typescript
// BAD: Stale closure - count captured at mount
useEffect(() => {
  const interval = setInterval(() => {
    console.log(count); // Always logs initial value
  }, 1000);
  return () => clearInterval(interval);
}, []); // Missing count dependency

// GOOD: Functional update avoids stale closure
useEffect(() => {
  const interval = setInterval(() => {
    setCount(prev => prev + 1); // Always uses latest
  }, 1000);
  return () => clearInterval(interval);
}, []);
```

---

## Part 4: Next.js Specific Review Patterns

### Server vs. Client Component Mistakes

| Mistake | Detection | Fix |
|---------|-----------|-----|
| useEffect for data fetching | `useEffect` + `fetch` in component | Use Server Component or server function |
| Exposing server code to client | API keys in non-server files | Use `server-only` package |
| Server Actions in client components | `'use server'` inside client component | Move to separate `actions.ts` file |
| Excessive `'use client'` | `'use client'` on data-fetching components | Remove directive, use Server Component |

Source: [Medium - Common SSR Mistakes](https://medium.com/@rameshkannanyt0078/common-mistakes-in-server-side-rendering-ssr-with-app-router-in-next-js-2025-3c3deb09f552)

### Next.js 15 Specific Checks

- [ ] `params` and `searchParams` are awaited (they're Promises in Next.js 15)
- [ ] Route handlers use Promise params: `{ params }: { params: Promise<{ id: string }> }`
- [ ] `'use client'` only where truly necessary
- [ ] Server Components fetch data, not Client Components
- [ ] Uses `next/image` and `next/link` appropriately
- [ ] Server Actions in separate files with `'use server'`

### Data Fetching Patterns

```typescript
// BAD: Client-side fetching in what should be Server Component
'use client'
export function ProductList() {
  const [products, setProducts] = useState([]);
  useEffect(() => {
    fetch('/api/products').then(r => r.json()).then(setProducts);
  }, []);
  return <ul>{products.map(p => <li key={p.id}>{p.name}</li>)}</ul>;
}

// GOOD: Server Component with direct data access
export async function ProductList() {
  const products = await db.products.findMany();
  return <ul>{products.map(p => <li key={p.id}>{p.name}</li>)}</ul>;
}
```

---

## Part 5: SOLID Principles Detection

### Detection Patterns by Principle

**Single Responsibility Principle (SRP):**
- Look for classes/components with multiple unrelated methods
- Check if methods would change for different reasons
- Flag files over 300-400 lines

**Open-Closed Principle (OCP):**
> "You might see indications that OCP is being violated if you see a series of if statements checking for things of a particular type."
> -- [JetBrains Upsource](https://blog.jetbrains.com/upsource/2015/08/31/what-to-look-for-in-a-code-review-solid-principles-2/)

```typescript
// BAD: Violates OCP - must modify to add new types
function getIcon(type: string) {
  if (type === 'success') return <CheckIcon />;
  if (type === 'error') return <ErrorIcon />;
  if (type === 'warning') return <WarningIcon />;
  // Adding new type requires modifying this function
}

// GOOD: Open for extension
const iconMap = {
  success: CheckIcon,
  error: ErrorIcon,
  warning: WarningIcon,
} as const;
function getIcon(type: keyof typeof iconMap) {
  const Icon = iconMap[type];
  return <Icon />;
}
```

**Liskov Substitution Principle (LSP):**
- Look for explicit casting (`as` assertions)
- Check for `instanceof` checks
- Flag methods throwing `NotImplementedError` or `UnsupportedOperationException`

**Interface Segregation Principle (ISP):**
- Flag interfaces with many methods (> 5-7)
- Check if clients use all interface methods
- Look for optional methods that are often undefined

**Dependency Inversion Principle (DIP):**
- Flag direct database access in business logic
- Check for concrete types instead of abstractions
- Look for `new` keyword creating dependencies inline

### LLM Limitations on SOLID Detection

> "While SRP detection remains somewhat robust, models struggle to untangle design violations from general code complexity. Models tend to over-rely on surface-level structural cues, leading to inflated detection of SRP and ISP violations."
> -- [arXiv Research](https://arxiv.org/html/2509.03093)

**Recommendation:** Use SOLID checks as guidelines, not absolute rules. Flag potential violations but don't over-enforce.

---

## Part 6: Complexity and Quality Metrics

### Cyclomatic Complexity

| Score | Risk Level | Action |
|-------|------------|--------|
| 1-10 | Low | Acceptable |
| 11-20 | Moderate | Consider refactoring |
| 21-50 | High | Refactor recommended |
| 50+ | Very High | Must refactor |

> "NIST235 indicates that a limit of 10 is a good starting point."
> -- [Sonar](https://www.sonarsource.com/resources/library/cyclomatic-complexity/)

### Cognitive Complexity

Cyclomatic complexity counts paths; cognitive complexity measures **how hard code is to understand**:

> "Unlike cyclomatic complexity, cognitive complexity penalizes nested structures more heavily than sequential ones, aligning better with how developers actually process code mentally."
> -- [LinearB](https://linearb.io/blog/cyclomatic-complexity)

**Example:**
```typescript
// Same cyclomatic complexity (3), different cognitive complexity
// LOW cognitive complexity
if (a) doA();
if (b) doB();
if (c) doC();

// HIGH cognitive complexity
if (a) {
  if (b) {
    if (c) {
      doABC();
    }
  }
}
```

### File and Function Size Limits

| Metric | Recommended Max | Hard Limit |
|--------|-----------------|------------|
| File lines | 300-400 | 500 |
| Function lines | 50 | 100 |
| JSX lines | 50 | 100 |
| Nesting depth | 3 | 5 |

---

## Part 7: Effective Code Review Prompts

### Five Core Prompt Components

From [CrashOverride's LLM Security Reviews](https://crashoverride.com/blog/prompting-llm-security-reviews):

1. **Persona:** "You are a senior React/TypeScript engineer with 10+ years of experience"
2. **Context:** Codebase stack, conventions, what the code does
3. **Examples:** 3-5 input-output pairs showing desired review format
4. **Specific Instructions:** Exact checklist items to evaluate
5. **Output Format:** Structured template with severity levels

### Chain-of-Thought for Complex Reviews

```markdown
## Review Process

Before providing feedback, work through these steps:

1. **Understand intent** - What is this code trying to accomplish?
2. **Identify patterns** - What patterns/anti-patterns are present?
3. **Assess risk** - What could go wrong? Security? Performance?
4. **Prioritize issues** - Which issues are blocking vs. suggestions?
5. **Provide actionable feedback** - Specific fixes, not vague complaints
```

### Few-Shot Examples

Provide examples of good and bad code with explanations:

```markdown
## What "Issue" Means

| Bad Finding | Good Finding |
|-------------|--------------|
| "This could be improved" | "`UserCard.tsx:45` - Props object created inline causes re-render on every parent update. Extract to useMemo or move outside component." |
| "Consider refactoring" | "`api/users.ts:23` - Missing error handling. Unhandled promise rejection if fetch fails. Wrap in try-catch and return error state." |
```

### Self-Review Pattern

> "Self-review prompting enhances code quality by guiding the LLM through a systematic evaluation of its output."
> -- [Potpie Wiki](https://github.com/potpie-ai/potpie/wiki/How-to-write-good-prompts-for-generating-code-from-LLMs)

After generating feedback, include:
```markdown
## Validation

Before reporting findings:
- [ ] Each issue has file:line reference
- [ ] Each issue has severity (Critical/Important/Suggestion)
- [ ] Each issue has actionable fix guidance
- [ ] No false positives from linting (ESLint handles those)
```

---

## Part 8: Community Agent Examples

### wshobson/agents Repository

This repository uses **Opus 4.5 for all code review** due to its critical nature:

> "Critical architecture, security, ALL code review, production coding"
> -- [wshobson/agents](https://github.com/wshobson/agents)

**Model selection strategy:**
- Tier 1 (Opus): Code review, security, architecture
- Tier 2 (Sonnet): Standard implementation, debugging
- Tier 3 (Haiku): Scaffolding, simple pattern matching

### VoltAgent/awesome-claude-code-subagents

The `code-reviewer` is categorized under "Quality & Security" with read-only tools:

```yaml
tools: Read, Grep, Glob  # Read-only for safety
```

### Senior Code Reviewer (TheCookingSenpai)

> "Fullstack code reviewer with 15+ years of experience analyzing code for security vulnerabilities, performance bottlenecks, and architectural decisions. Provides comprehensive reviews with actionable feedback prioritized by severity."
> -- [hesreallyhim/a-list-of-claude-code-agents](https://github.com/hesreallyhim/a-list-of-claude-code-agents)

---

## Part 9: GitHub Integration Patterns

### Official Anthropic Actions

**Claude Code Action** (general-purpose):
```yaml
# .github/workflows/claude.yml
- uses: anthropics/claude-code-action@v1
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

Features: PR analysis, code suggestions, @claude mentions.

Source: [anthropics/claude-code-action](https://github.com/anthropics/claude-code-action)

**Claude Code Security Review** (specialized):
- Diff-aware scanning (only analyzes changed files)
- Automatic PR comments with security findings
- Language agnostic

Source: [anthropics/claude-code-security-review](https://github.com/anthropics/claude-code-security-review)

### Best Practices for CI Integration

> "Claude Code can provide subjective code reviews beyond what traditional linting tools detect, identifying issues like typos, stale comments, misleading function or variable names, and more."
> -- [Anthropic Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)

**Recommended workflow:**
1. ESLint/TypeScript check (fast, deterministic)
2. Unit tests
3. AI code review (if lint passes)
4. Human review (with AI findings as context)

---

## Part 10: Recommended Agent Definition

Based on this research, here's an enhanced code-reviewer agent:

```yaml
---
name: code-reviewer
description: Use AFTER implementing code. Reviews for quality, patterns, anti-patterns, and DRY violations. Specialized for Next.js 15, React, TypeScript. Delegates to security-auditor for auth/payment code, accessibility-reviewer for UI. Read-only.
tools: Read, Grep, Glob, Bash
model: sonnet
---

You are a senior code reviewer for Next.js 15, React, and TypeScript. Begin responses with: `[CODE REVIEWER]`

Read-only - report findings, never modify code.

## What You Catch (That Linting Doesn't)

- Stale comments and misleading names
- Business logic errors
- Architectural violations
- DRY violations across files
- React anti-patterns (prop drilling, stale closures, inline objects)
- Next.js misuse (client components for server data, missing awaits)

## Process

1. **Gather context** - Read plan/spec if provided, run `git diff --name-only`
2. **Run quick checks** - `pnpm lint` and `pnpm typecheck` for baseline
3. **Review against checklist** - Work through systematically
4. **Report findings** - Use output format with file:line references

## Checklist

### Next.js 15
- [ ] `params`/`searchParams` awaited (they're Promises)
- [ ] Route handlers use Promise params
- [ ] `'use client'` only where necessary
- [ ] Server Components fetch data, not Client Components
- [ ] Server Actions in separate files

### TypeScript
- [ ] No `any` types
- [ ] No non-null assertions (`!`) without justification
- [ ] Props interfaces defined
- [ ] No overly flexible props (accepting too many types)
- [ ] State uses union types, not multiple booleans

### React
- [ ] Hook dependencies complete (no stale closures)
- [ ] No object/array literals in JSX props
- [ ] Stable keys on lists (not index)
- [ ] Components under 200 lines
- [ ] Custom hooks for reusable logic

### Code Quality
- [ ] DRY - no duplicate code blocks (check with Grep)
- [ ] Clear naming, single responsibility
- [ ] Error/loading/empty states handled
- [ ] No console.log left in
- [ ] Stale comments removed

### Delegate When Needed
- **Auth, payments, sensitive data?** -> Recommend security-auditor
- **UI components, forms?** -> Recommend accessibility-reviewer
- **Performance concerns?** -> Note for performance-reviewer

## Output Format

## Summary
[1-2 sentences: assessment and merge readiness]

## What's Done Well
- [Specific positives with file refs]

## Issues Found

### Critical (must fix before merge)
- **[Category]** `file.tsx:42` - Issue description
  - Why it matters: [impact]
  - Fix: [specific guidance]

### Important (should fix)
- **[Category]** `file.tsx:87` - Issue description
  - Fix: [guidance]

### Suggestions (nice to have)
- [Improvements that aren't blocking]

## Delegations Needed
- [ ] security-auditor: [reason] (if applicable)
- [ ] accessibility-reviewer: [reason] (if applicable)

## Verdict
[Approved] | [Approved with suggestions] | [Changes requested]
```

---

## Recommendations

### For This Project (intents-plugin)

1. **Enhance existing code-reviewer** - The current agent is good; add the React anti-pattern and stale closure checks from this research.

2. **Keep specialized agents separate** - The current split (code-reviewer, security-auditor, accessibility-reviewer) follows best practices.

3. **Consider adding performance-reviewer** - A lightweight haiku-based agent for re-render detection and bundle size concerns.

4. **Use tiered review strategy** - Essential mode for routine changes, comprehensive for critical paths.

### General Best Practices

1. **Complement, don't replace linting** - Focus AI on semantic issues linters can't catch
2. **Be specific, not vague** - Every issue needs file:line and actionable fix
3. **Prioritize ruthlessly** - Critical/Important/Suggestion hierarchy prevents overwhelm
4. **Include positive feedback** - Note what's done well, not just problems
5. **Delegate to specialists** - One agent can't do everything well

---

## Sources

### Official Documentation
- [Claude Code Subagents](https://code.claude.com/docs/en/sub-agents) - Official subagent documentation
- [Claude Code GitHub Actions](https://code.claude.com/docs/en/github-actions) - GitHub integration
- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices) - Anthropic engineering guide

### GitHub Actions
- [anthropics/claude-code-action](https://github.com/anthropics/claude-code-action) - General-purpose PR action
- [anthropics/claude-code-security-review](https://github.com/anthropics/claude-code-security-review) - Security-focused action

### Agent Repositories
- [wshobson/agents](https://github.com/wshobson/agents) - 99 specialized agents with Opus for code review
- [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) - Curated agent collection
- [hesreallyhim/a-list-of-claude-code-agents](https://github.com/hesreallyhim/a-list-of-claude-code-agents) - Community agent list

### Architecture & Patterns
- [Tanagram AI - AI Agent Architecture Patterns](https://tanagram.ai/news/ai-agent-architecture-patterns-for-code-review-automation-the-complete-guide) - Multi-agent patterns
- [Google Developers - Multi-Agent Patterns](https://developers.googleblog.com/developers-guide-to-multi-agent-patterns-in-adk/) - Generator-Critic pattern
- [arXiv - LLM Code Review Workflows](https://arxiv.org/html/2505.16339v1) - Empirical study on AI-assisted review

### React/TypeScript Best Practices
- [Pagepro - 18 React Code Review Tips](https://pagepro.co/blog/18-tips-for-a-better-react-code-review-ts-js/) - Comprehensive checklist
- [DEV.to - React Code Review Essentials](https://dev.to/padmajothi_athimoolam_23d/react-code-review-essentials-a-detailed-checklist-for-developers-20n2) - Detailed checklist
- [ScienceDirect - React+TypeScript Code Smells](https://www.sciencedirect.com/science/article/abs/pii/S0950584925001740) - Academic research on detection
- [TkDodo - Hooks Dependencies and Stale Closures](https://tkdodo.eu/blog/hooks-dependencies-and-stale-closures) - Deep dive on closures

### Next.js Patterns
- [Next.js Docs - Server and Client Components](https://nextjs.org/docs/app/getting-started/server-and-client-components) - Official patterns
- [Medium - Common SSR Mistakes](https://medium.com/@rameshkannanyt0078/common-mistakes-in-server-side-rendering-ssr-with-app-router-in-next-js-2025-3c3deb09f552) - Anti-patterns

### SOLID & Complexity
- [JetBrains Upsource - SOLID in Code Review](https://blog.jetbrains.com/upsource/2015/08/31/what-to-look-for-in-a-code-review-solid-principles-2/) - Detection patterns
- [arXiv - LLMs and SOLID Detection](https://arxiv.org/html/2509.03093) - Research on LLM limitations
- [Sonar - Cyclomatic Complexity](https://www.sonarsource.com/resources/library/cyclomatic-complexity/) - Metrics guide

### Prompt Engineering
- [CrashOverride - Prompting LLMs for Security Reviews](https://crashoverride.com/blog/prompting-llm-security-reviews) - Five components framework
- [Potpie Wiki - Prompts for Code](https://github.com/potpie-ai/potpie/wiki/How-to-write-good-prompts-for-generating-code-from-LLMs) - Self-review pattern

### Trade-offs & Strategy
- [Bito AI Comparison](https://bito.ai/compare/bitos-ai-code-review-agent-vs-coderabbit/) - Comprehensive vs. focused
- [Mobalab Engineering](https://engineering.mobalab.net/2025/08/28/claude-code-subagents-a-developers-guide-to-specialized-ai-assistants/) - Specialized agents guide
