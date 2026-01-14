# Brainstorm Skill: Best Practices Analysis

This document analyzes the `feature-brainstorm` skill against established best practices for early-stage ideation and brainstorming facilitation.

## Executive Summary

**Overall Assessment: Strong alignment with best practices, with a few gaps to address.**

The skill correctly positions the LLM as a Socratic thought partner rather than a suggestion engine. It appropriately sits in the "second diamond" (solution space) of the Double Diamond framework. The YAGNI/simplicity bias and devil's advocate elements are well-implemented.

### Key Strengths
- Socratic questioning structure with progressive depth
- Explicit anti-patterns (vague signals table)
- Clear convergence signals
- Strong YAGNI/simplicity principles
- Handoff structure with summary template

### Gaps to Address
1. **Missing divergent phase**: Jumps to challenging too quickly
2. **Problem validation underweighted**: Should spend more time on "is this the right problem?"
3. **No explicit defer-judgment phase**: Violates core brainstorming rule
4. **LLM agreeableness not addressed**: No prompts forcing genuine pushback
5. **Missing "do nothing" option framing**

---

## Detailed Analysis

### 1. Double Diamond Positioning ✅

**Best Practice**: The Double Diamond framework (British Design Council, 2005) has four phases: Discover, Define, Develop, Deliver. The first diamond is "problem space" (understanding the problem), the second is "solution space" (ideating solutions).

**Current Skill**: Correctly states "The user is in the second diamond of the double diamond - they have a problem and are exploring solutions."

**Assessment**: ✅ Correctly positioned. However, the skill should verify the problem is well-defined before diving into solutions—many users think they're in the second diamond when they haven't finished the first.

**Source**: [Double Diamond Design Process – UXPin](https://www.uxpin.com/studio/blog/double-diamond-design-process/)

---

### 2. Divergent vs. Convergent Thinking ⚠️

**Best Practice**: Effective ideation separates divergent thinking (generating many ideas without judgment) from convergent thinking (evaluating and narrowing). These phases must be kept distinct—mixing them "neutralizes the benefits of each."

> "If they take place simultaneously, or at the inappropriate time, they will quickly become an obstacle to success. Like matter and antimatter, one will neutralize the benefits of the other." — [Lucidspark](https://lucid.co/blog/convergent-vs-divergent-thinking)

The most important rule of brainstorming is **defer judgment**—avoid critiquing ideas early in the process.

**Current Skill**: The skill is heavily weighted toward convergent/critical thinking from the start:
- "Challenge vagueness"
- "Be direct: 'I'm not sure we need this. Convince me.'"
- The "Challenging (Not Blocking)" section appears early

This risks shutting down divergent exploration before it happens.

**Assessment**: ⚠️ **Gap identified.** The skill needs an explicit divergent phase before introducing challenges.

**Recommendation**: Add a "Divergent Phase" before the current "Core Loop":

```markdown
## Divergent Phase (First 2-3 Exchanges)

Before challenging, EXPAND the idea space:
- "What else have you considered?"
- "If there were no constraints, what would you build?"
- "What's the wildest version of this?"
- "What adjacent problems might this solve?"

Do NOT critique during this phase. Defer judgment.
Only after 2-3 rounds of expansion, shift to probing and challenging.
```

**Sources**:
- [7 Simple Rules of Brainstorming - IDEO U](https://www.ideou.com/blogs/inspiration/7-simple-rules-of-brainstorming)
- [Convergent vs. Divergent Thinking - Lucidspark](https://lucid.co/blog/convergent-vs-divergent-thinking)

---

### 3. Socratic Questioning ✅

**Best Practice**: Socratic questioning uses open-ended, probing questions to help people discover answers themselves rather than being given solutions. Key categories include:
- Clarifying questions
- Questions that probe assumptions
- Questions seeking evidence/reasons
- Questions about implications

> "Coaches make every question count, avoiding vague or general questions." — [Institute of Coaching](https://instituteofcoaching.org/resources/how-use-socratic-questioning-coaching)

**Current Skill**: Strong implementation with progressive depth:
- Early: "What's the actual pain here?" / "What happens if you do nothing?"
- Middle: "Walk me through how this would work." / "What's the hard part?"
- Late: "What could go wrong?" / "What are you assuming that might not be true?"

**Assessment**: ✅ Well-aligned with Socratic methodology.

**Minor Enhancement**: Add questions that probe evidence:
- "How do you know this is true?"
- "What data supports this?"
- "Have you seen this pattern elsewhere?"

**Sources**:
- [Socratic Questioning - Positive Psychology](https://positivepsychology.com/socratic-questioning/)
- [Institute of Coaching](https://instituteofcoaching.org/resources/how-use-socratic-questioning-coaching)

---

### 4. Devil's Advocate / Critical Challenge ⚠️

**Best Practice**: Devil's advocacy deliberately adopts contrary positions to challenge assumptions and uncover blind spots. However, **timing matters critically**:

> "In the early stages of a problem-solving process, we need to refrain from devil's advocacy. If someone immediately begins to poke holes or point out flaws in initial suggestions, others will become reticent to speak up." — [Killer Innovations](https://killerinnovations.com/the-devils-advocate-is-it-good-for-innovation/)

**Current Skill**: Devil's advocate patterns are present but introduced too early:
- "Challenge vagueness" appears in the opening sections
- "Be direct: 'I'm not sure we need this. Convince me.'" could shut down ideation

**Assessment**: ⚠️ **Timing issue.** The challenging should be explicitly gated to AFTER the divergent phase.

**Recommendation**: Restructure to make timing explicit:

```markdown
## When to Challenge

ONLY after:
1. The user has shared their full initial idea
2. You've explored 2-3 alternative approaches together
3. You've asked "What else?" at least twice

THEN shift to challenging mode.
```

**Sources**:
- [Devil's Advocate - Killer Innovations](https://killerinnovations.com/the-devils-advocate-is-it-good-for-innovation/)
- [The Behavioral Scientist](https://www.thebehavioralscientist.com/glossary/devils-advocacy)

---

### 5. Problem Validation (Jobs to Be Done) ⚠️

**Best Practice**: Before ideating solutions, validate that you're solving the right problem. The "Jobs to Be Done" framework asks: What job is the user hiring this solution to do?

> "It's common to see startups that have jumped to the solution without really understanding the problem." — [Nagarro](https://www.nagarro.com/en/blog/problems-first-please-an-approach-to-ideation)

Key questions:
- "What job are you trying to get done?"
- "What's the current workaround?"
- "What's the cost of the status quo?"

**Current Skill**: Has some problem-probing questions but they're mixed with solution questions:
- "What's the actual pain here?" ✅
- "What happens if you do nothing?" ✅
- But missing: "What's the underlying job you're trying to accomplish?"

**Assessment**: ⚠️ Could be stronger on problem validation before solution exploration.

**Recommendation**: Add a "Problem Validation" checkpoint:

```markdown
## Problem Checkpoint (Before Solution Exploration)

Before exploring solutions, confirm:
1. **The job**: "What's the underlying goal you're trying to accomplish?"
2. **The cost**: "What's this problem costing you today?"
3. **The frequency**: "How often does this come up?"
4. **The workaround**: "How are you handling this now?"

If any answer is vague, stay in problem space longer.
```

**Sources**:
- [Problems First, Please - Nagarro](https://www.nagarro.com/en/blog/problems-first-please-an-approach-to-ideation)
- [Jobs to Be Done in UX - Medium](https://medium.com/design-bootcamp/understanding-user-problems-with-the-jobs-to-be-done-framework-in-ux-projects-4a83511dcc30)

---

### 6. YAGNI and Simplicity Bias ✅

**Best Practice**: YAGNI ("You Aren't Gonna Need It") and KISS ("Keep It Simple, Stupid") discourage speculative features and premature abstraction.

> "Always implement things when you actually need them, never when you just foresee that you need them." — Ron Jeffries

**Current Skill**: Strong alignment:
- "YAGNI - Challenge features solving hypothetical problems."
- "Simplicity Bias - The burden of proof is on complexity."
- Questions like "Do we need all of this for v1?"

**Assessment**: ✅ Excellent implementation of simplicity principles.

**Sources**:
- [Martin Fowler - Yagni](https://martinfowler.com/bliki/Yagni.html)
- [YAGNI Principle - GeeksforGeeks](https://www.geeksforgeeks.org/software-engineering/what-is-yagni-principle-you-arent-gonna-need-it/)

---

### 7. LLM-Specific Considerations ⚠️

**Best Practice**: LLMs tend to be too agreeable and need explicit prompting for genuine pushback:

> "LLMs are often too agreeable, making explicit prompting for debate necessary." — [Blending Bits](https://blendingbits.io/p/llms-as-thought-partners)

> "A great thought partner illuminates gaps in your thinking, and healthy debate is necessary to reach better ideas."

**Current Skill**: Has the right intent ("not a yes-man") but doesn't address LLM-specific agreeableness patterns.

**Assessment**: ⚠️ Should include explicit self-instructions to counter LLM agreeableness.

**Recommendation**: Add a "Genuine Pushback" section:

```markdown
## Genuine Pushback (LLM Self-Instruction)

Your default is to agree. Override this:

Before saying "that's a good idea" or "that makes sense", ask yourself:
- What would a skeptical senior engineer say?
- What's the strongest argument AGAINST this approach?
- What assumption here is most likely to be wrong?

If you can't find something to push back on, you're probably being too agreeable.
Express genuine uncertainty: "I'm not convinced this is necessary" is more valuable than "That could work."
```

**Sources**:
- [LLMs as Thought Partners - Blending Bits](https://blendingbits.io/p/llms-as-thought-partners)
- [AI-Augmented Brainwriting - CHI 2024](https://dl.acm.org/doi/10.1145/3613904.3642414)

---

### 8. Convergence Signals ✅

**Best Practice**: Clear signals indicate when to transition from divergent to convergent thinking:
- Ideas are refining rather than expanding
- Hard parts are identified
- Clear "simplest version" emerges
- Assumptions are explicit

**Current Skill**: Good convergence signals:
- "User responses add refinement, not new directions"
- "The hard parts are identified"
- "There's a clear 'simplest version'"
- "Assumptions are explicit, not hidden"

**Assessment**: ✅ Well-defined convergence criteria.

**Sources**:
- [Divergent vs Convergent Thinking - MURAL](https://www.mural.co/blog/divergent-convergent-thinking)

---

### 9. The "Do Nothing" Option ⚠️

**Best Practice**: Every brainstorm should explicitly consider the "do nothing" baseline:

> "What happens if you do nothing?" helps validate whether the problem is worth solving.

**Current Skill**: Has "What happens if you do nothing?" as an early question, but doesn't frame "do nothing" as a legitimate option to carry through to the summary.

**Assessment**: ⚠️ Should include "do nothing" as an explicit option in the handoff summary.

**Recommendation**: Update the handoff template:

```markdown
**Options Considered**:
1. Do nothing: [Why this might be acceptable]
2. Minimal: [Smallest valuable increment]
3. Full: [Complete solution]
```

---

### 10. Handoff Structure ✅

**Best Practice**: Brainstorming should end with a clear, structured handoff that captures decisions and open questions.

**Current Skill**: Strong handoff template:
- Problem (validated)
- Proposed Solution
- Simplest Version
- Hard Parts
- Assumptions
- Open Questions

**Assessment**: ✅ Good structure for downstream phases.

**Minor Enhancement**: Add "Rejected Alternatives" to capture why other paths weren't taken.

---

## Summary of Recommendations

### High Priority

1. **Add Divergent Phase**: Insert an explicit "expansion" phase before challenging. Defer judgment for the first 2-3 exchanges.

2. **Gate the Challenges**: Move devil's advocate patterns to AFTER divergent exploration. Make timing explicit in the skill.

3. **Add Problem Validation Checkpoint**: Before solution ideation, verify the problem is validated using JTBD-style questions.

4. **Counter LLM Agreeableness**: Add explicit self-instructions for genuine pushback. LLMs default to agreeing; the skill needs to override this.

### Medium Priority

5. **Include "Do Nothing" in Options**: Carry the "do nothing" baseline through to the handoff summary as a legitimate option.

6. **Add Evidence-Probing Questions**: "How do you know?" and "What data supports this?" strengthen the Socratic questioning.

### Low Priority

7. **Add "Rejected Alternatives" to Handoff**: Document why other paths weren't taken for future reference.

---

## Proposed Restructured Outline

```
# Feature Brainstorm

## Start Here
(existing opening questions)

## Phase 1: Problem Validation (NEW)
- Verify we're solving the right problem
- JTBD-style questions
- Checkpoint: Is this problem worth solving?

## Phase 2: Divergent Exploration (NEW)
- Expand the idea space
- Defer judgment
- "What else?" questions
- 2-3 exchanges minimum

## Phase 3: Probing and Challenging (existing Core Loop)
- Now introduce Socratic probing
- Challenge vagueness
- YAGNI lens

## Convergence Signals
(existing content)

## Handoff
- Include "do nothing" option
- Add rejected alternatives
```

---

## References

- [Double Diamond Design Process – UXPin](https://www.uxpin.com/studio/blog/double-diamond-design-process/)
- [7 Simple Rules of Brainstorming - IDEO U](https://www.ideou.com/blogs/inspiration/7-simple-rules-of-brainstorming)
- [Convergent vs. Divergent Thinking - Lucidspark](https://lucid.co/blog/convergent-vs-divergent-thinking)
- [Socratic Questioning - Positive Psychology](https://positivepsychology.com/socratic-questioning/)
- [Devil's Advocate - Killer Innovations](https://killerinnovations.com/the-devils-advocate-is-it-good-for-innovation/)
- [Problems First, Please - Nagarro](https://www.nagarro.com/en/blog/problems-first-please-an-approach-to-ideation)
- [Martin Fowler - Yagni](https://martinfowler.com/bliki/Yagni.html)
- [LLMs as Thought Partners - Blending Bits](https://blendingbits.io/p/llms-as-thought-partners)
- [AI-Augmented Brainwriting - CHI 2024](https://dl.acm.org/doi/10.1145/3613904.3642414)
