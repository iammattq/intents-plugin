# Effective Test Practices Beyond Coverage

Research conducted: 2026-01-11
Purpose: Inform redesign of `test-spec` agent to prioritize test quality over coverage metrics

## Problem Statement

Coverage alone is not a good metric. Tests need to cover critical parts of the software with meaningful assertions. The current `test-spec` agent focuses on test quantity and structure but doesn't guide prioritization or quality.

---

## Key Finding: Coverage Measures Execution, Not Validation

Code coverage only measures that code was **executed**, not that it was **correctly validated**. You can achieve 90%+ coverage while still missing critical bugs if tests lack meaningful assertions or skip important edge cases.

Goodhart's law applies: "When a measure becomes a target, it ceases to be a good measure."

**Sources:**
- [Augment Code: Unit Testing Best Practices](https://www.augmentcode.com/guides/unit-testing-best-practices-that-focus-on-quality-over-quantity)
- [Medium: How to Measure Code Coverage for Meaningful Test Quality](https://medium.com/@sancharini.panda/how-to-measure-code-coverage-for-meaningful-test-quality-254c0b4cd9ef)

---

## Framework 1: Risk-Based Testing (RBT)

**Sources:**
- [Testlio: Understanding Risk-Based Testing](https://testlio.com/blog/risk-based-testing/)
- Gartner forecasts 70% of enterprises will adopt "Smart Prioritization Engines" integrating RBT by 2025

**Core Principle:** Prioritize testing based on business impact and failure likelihood.

**Risk Factors:**
- **Business criticality** - Revenue-generating features get higher priority
- **Failure impact** - What breaks if this fails?
- **Historical defect patterns** - Areas that have failed before
- **Code complexity** - Complex code is more likely to have bugs

**Application to test-spec:**
- Tests for payment processing > tests for logging utilities
- Tests for auth boundaries > tests for string formatting
- Tests for core user journeys > tests for admin settings

---

## Framework 2: Mutation Testing

**Sources:**
- [Master Software Testing: Mutation Testing Ultimate Guide](https://mastersoftwaretesting.com/testing-fundamentals/types-of-testing/mutation-testing)
- [LambdaTest: Mutation Testing Concepts](https://www.lambdatest.com/learning-hub/mutation-testing)

**Core Principle:** Mutation testing is the "gold standard" for assessing test quality.

**How it works:**
1. Make small changes ("mutations") to your code
2. Run your tests
3. Check if tests catch the mutations

If a mutation survives (tests still pass), your tests have a gap.

**Risk-based thresholds:**
- Payment/security modules: 95%+ mutation score
- Core business logic: 85%+
- Utilities/helpers: 70%+
- Generated code: Skip

**Tools:**
- Stryker (JavaScript/TypeScript)
- PIT (Java)
- MutPy (Python)

**Application to test-spec:**
- Recommend mutation testing for high-risk components
- Set different quality thresholds based on criticality
- Use mutation scores to validate test effectiveness, not just coverage

---

## Framework 3: Testing Trophy vs Testing Pyramid

### Traditional Testing Pyramid

**Source:** [Devzery: Software Testing Pyramid Guide 2025](https://www.devzery.com/post/software-testing-pyramid-guide-2025)

Classic ratio: **70% unit / 20% integration / 10% E2E**

Economic rationale - cost of finding bugs increases exponentially:
- Bug caught by unit test: $1
- Same bug in integration: $10
- In E2E: $100
- In production: $1,000+

**Best for:** Backend services, libraries, pure business logic, algorithms

### Testing Trophy (Modern Alternative)

**Source:** [Kent C. Dodds: The Testing Trophy](https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications)

```
     E2E (small)
  Integration (large)  <-- Primary focus
    Unit (medium)
   Static (base)
```

**Key principle:** "The more your tests resemble the way your software is used, the more confidence they can give you."

**Rationale for integration focus:**
- Fewer tests needed to identify problems
- Less dependent on implementation details
- Less maintenance as code evolves
- Catch issues unit tests miss (component interactions)

**Best for:** Frontend applications, UI-heavy apps, systems with many component interactions

### Application to test-spec

Don't dogmatically follow one model. Choose based on context:
- Backend API with complex business logic → Pyramid (unit-heavy)
- React component library → Trophy (integration-heavy)
- Microservices → More integration tests to verify service communication

---

## Framework 4: Assertion Quality

**Source:** [Medium: Meaningful Test Quality](https://medium.com/@sancharini.panda/how-to-measure-code-coverage-for-meaningful-test-quality-254c0b4cd9ef)

**Core Problem:** High coverage with few assertions provides false confidence.

A test that executes code but doesn't verify outcomes is useless:

```javascript
// Bad - executes but doesn't verify
test('processes payment', () => {
  processPayment({ amount: 100 });
  // no assertions!
});

// Good - verifies behavior
test('processes payment', () => {
  const result = processPayment({ amount: 100 });
  expect(result.status).toBe('success');
  expect(result.chargedAmount).toBe(100);
  expect(auditLog).toContainEntry({ type: 'payment', amount: 100 });
});
```

**Metrics:**
- **Assertion density** - Number of meaningful assertions per test
- Tests should verify outcomes, not just execute paths

**Application to test-spec:**
- Require explicit expected outcomes for each test case
- Flag test specs that only describe execution without verification
- Emphasize "expects [outcome]" format

---

## Framework 5: Behavior Over Implementation

**Sources:**
- [Microsoft: Unit Testing Best Practices](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-best-practices)
- [Kent C. Dodds: Write tests](https://kentcdodds.com/blog/write-tests)

**Core Principle:** Tests should verify *what* the code does, not *how* it does it.

**Problem with implementation-coupled tests:**
- Break on every refactor
- Don't catch actual bugs
- Create maintenance burden
- Discourage code improvement

**Example:**

```javascript
// Bad - tests implementation
test('uses cache before fetching', () => {
  const spy = jest.spyOn(cache, 'get');
  getUser(1);
  expect(spy).toHaveBeenCalledWith('user:1');
});

// Good - tests behavior
test('returns cached user on second call', () => {
  const user1 = await getUser(1);
  const user2 = await getUser(1);
  expect(user1).toEqual(user2);
  expect(fetchCount).toBe(1); // only fetched once
});
```

**Application to test-spec:**
- Frame test cases around user-observable behavior
- Avoid specifying internal method calls or data structures
- Ask "what should the user/caller see?" not "what should the code do internally?"

---

## Quality Metrics Beyond Coverage

**Source:** [Qodo: Code Quality in 2025](https://www.qodo.ai/blog/code-quality/)

### Recommended Metrics

| Metric | What It Measures | Target |
|--------|------------------|--------|
| Mutation Score | Test effectiveness at catching bugs | 85%+ for critical code |
| Assertion Density | Meaningful verifications per test | 2-5 per test |
| Defect Escape Rate | Bugs reaching production | Trending down |
| Test Flakiness Rate | Inconsistent pass/fail | <1% |
| MTTD | Mean time to detect defects | Trending down |

### Coverage Guidance

Google's internal guidance:
- 60% acceptable
- 75% commendable
- 90% exemplary

**Practical target:** 75-80% coverage paired with high mutation scores

Chasing 100% leads to testing trivial code with diminishing returns.

---

## TDD in 2025: What's Still Valuable

**Sources:**
- [NOP Accelerate: AI-Powered TDD Best Practices 2025](https://www.nopaccelerate.com/test-driven-development-guide-2025/)
- [IBM: Unit Testing Best Practices](https://www.ibm.com/think/insights/unit-testing-best-practices)

### Still Valuable

1. **Red-Green-Refactor cycle** - Write failing test, make it pass, refactor
2. **Tests as design drivers** - Forces thinking about interface before implementation
3. **Immediate feedback** - Know instantly if changes break behavior
4. **Regression prevention** - Bugs fixed with tests don't come back

### What's Evolved

- **TDD + BDD hybrid** - BDD for business requirements, TDD for technical components
- **AI-assisted test generation** - LLMs suggest edge cases humans miss
- **Balance with integration tests** - Pure unit-focused TDD can neglect system interactions

### Defect Reduction

Studies show TDD reduces defect density by 40-90% (IBM, Microsoft research).

---

## Synthesis: Principles for test-spec Agent

### 1. Prioritize by Risk, Not Coverage

```
High Priority (thorough testing):
- Payment processing
- Authentication/authorization
- Core user journeys
- Data validation at boundaries
- Security-sensitive operations

Medium Priority (solid coverage):
- Business logic
- API endpoints
- State management
- Error handling

Low Priority (basic coverage):
- Utilities and helpers
- Configuration
- Logging
- Generated code
```

### 2. Require Meaningful Assertions

Every test case must specify:
- Input/setup
- Action
- **Expected outcome** (the critical part)

Bad: "Test payment processing"
Good: "Test payment processing with valid card - expects success status and charge record"

### 3. Test Behavior, Not Implementation

Frame tests around:
- What the user/caller observes
- What state changes occur
- What outputs are produced

Avoid:
- Internal method call sequences
- Private state inspection
- Implementation-specific mocks

### 4. Adapt Test Type to Context

| Code Type | Primary Test Type |
|-----------|-------------------|
| Pure functions, algorithms | Unit tests |
| API endpoints | Integration tests |
| React components | Integration tests (Testing Library) |
| Database operations | Integration tests |
| Complex UI flows | E2E tests (sparingly) |

### 5. Edge Cases Before Happy Paths

Edge cases catch more real-world bugs:
- Null/undefined inputs
- Empty collections
- Boundary values (0, -1, MAX_INT)
- Invalid formats
- Timeout/failure scenarios
- Concurrent access

### 6. Set Quality Thresholds by Risk

| Component Risk | Coverage Target | Mutation Target |
|----------------|-----------------|-----------------|
| Critical (payments, auth) | 90%+ | 95%+ |
| High (core business) | 80%+ | 85%+ |
| Medium (standard features) | 70%+ | 75%+ |
| Low (utilities) | 60%+ | 70%+ |

---

## Next Steps

Apply these principles to update `agents/test-spec.md`:

1. Replace "YAGNI for Tests" with risk-based prioritization framework
2. Add assertion quality requirements to test case format
3. Add behavior-focused framing guidance
4. Make test type recommendations context-dependent
5. Add mutation testing as quality validation
6. Include quality threshold guidance based on component criticality
