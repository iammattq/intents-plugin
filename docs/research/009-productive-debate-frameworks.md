# Productive Debate Frameworks for AI Agent Refinement

Research conducted: 2026-01-02
Purpose: Inform redesign of `feature-refine` agent to balance constructive tension with convergence

## Problem Statement

The current `feature-refine` agent leans too adversarial—it finds problems but doesn't collaborate toward solutions. We need frameworks that:

1. Encourage genuine pushback on weak ideas
2. Steel-man ideas before stress-testing them
3. Converge on the best solution (not stalemate)
4. Remove human-time assumptions irrelevant to AI agent orchestration

---

## Framework 1: Disagree and Commit

**Sources:**
- [Wikipedia: Disagree and commit](https://en.wikipedia.org/wiki/Disagree_and_commit)
- [Inc: Amazon and Intel Use This Principle](https://www.inc.com/debbie-madden/amazon-intel-use-this-1-principle-to-make-quick-effective-group-decisions.html)
- [Tomasz Tunguz: Disagree and Commit](https://tomtunguz.com/disagree-and-commit/)

**Origins:** Created in the 1980s, popularized by Intel's Andy Grove and later Amazon. Scott McNealy's version: "Agree and commit, disagree and commit, or get out of the way."

**Core Principle:** Vigorous debate *during* decision-making, full commitment *after*. The decision phase welcomes disagreement; the execution phase demands unity.

**Key Insights:**
- "Failure to capitalize on a new idea often has far less to do with the quality of the idea than with the indecision and waffling that accompany it"
- Debate must be backed by facts, not opinions
- Once decided, even dissenters commit wholly
- Execution speed is the primary advantage this unlocks

**Application to feature-refine:**
- The debate phase should be genuinely adversarial
- But there must be a clear convergence point where debate ends
- Post-convergence, the recommendation is wholehearted (not hedged)

---

## Framework 2: Steel Manning

**Sources:**
- [The Mind Collection: Steelmanning](https://themindcollection.com/steelmanning-how-to-discover-the-truth-by-helping-your-opponent/)
- [Constant Renewal: The Steel Man Technique](https://constantrenewal.com/steel-man)
- [Ali Abdaal: The Steelman Argument](https://aliabdaal.com/newsletter/the-steelman-argument/)

**Origins:** Popularized by the Rationalist Movement (Bay Area programmers, AI researchers). Conor Friedersdorf introduced it to mainstream via The Atlantic in 2017.

**Core Principle:** Present the *strongest possible version* of an argument before critiquing it. The opposite of straw-manning.

**Daniel Dennett's Rules:**
1. Re-express the other position so clearly they say, "Thanks, I wish I'd thought of putting it that way"
2. List any points of agreement
3. Mention anything you learned from them
4. *Only then* are you permitted to critique

**Formal Debate Rule:** You cannot counter-argue until you've summarized their position *to their satisfaction*.

**Benefits:**
- Forces genuine understanding before critique
- Builds empathy and reduces defensiveness
- If your counter-argument survives against their *best* case, it's robust
- Transforms adversaries into "interlocutors—partners in truth-seeking"

**Application to feature-refine:**
- Advocate role must articulate the strongest version first
- Critic cannot attack until the idea has been properly steel-manned
- This prevents dismissing good ideas due to weak initial framing

---

## Framework 3: Dialectical Synthesis (Thesis-Antithesis-Synthesis)

**Sources:**
- [Stanford Encyclopedia: Hegel's Dialectics](https://plato.stanford.edu/entries/hegel-dialectics/)
- [PolSci Institute: Hegel's Dialectical Method](https://polsci.institute/western-political-thought/hegel-dialectical-method-thesis-antithesis-synthesis/)
- [Sparkco: Dialectical Reasoning](https://sparkco.ai/blog/dialectical-reasoning-thesis-antithesis-synthesis)

**Origins:** Attributed to Hegel (though he didn't use this exact language—it was formalized by Heinrich Moritz Chalybäus). Fichte influenced the concept.

**Core Principle:**
- Thesis: An initial position
- Antithesis: A counter-position that contradicts or negates the thesis
- Synthesis: A resolution that incorporates the merits of both, creating something qualitatively better

The synthesis then becomes the new thesis, potentially generating its own antithesis.

**Key Insight:** "Contradiction and conflict are not obstacles to progress but its very mechanism."

**Practical Workflow:**
- Thesis Artifact: Initial hypothesis with assumptions and evidence
- Antithesis Artifact: Counterargument matrix with contradictions and supporting data
- Synthesis Artifact: Integrated resolution with validation metrics

**Application to feature-refine:**
- The goal is not "thesis wins" or "antithesis wins"
- The goal is a *synthesis* that's better than either original position
- Each debate round should move toward synthesis, not just accumulate objections

---

## Framework 4: Red-Blue Team Intervention

**Sources:**
- [Neurofied: Red-Blue Team Intervention](https://neurofied.com/red-blue-team-intervention/)
- [Wikipedia: Red team](https://en.wikipedia.org/wiki/Red_team)
- [Medium: Red Team vs Blue Team Exercises](https://cyberw1ng.medium.com/red-team-vs-blue-team-designing-collaborative-exercises-ffe54a72e9cf)

**Origins:** Cold War military exercises (Red = Soviet, Blue = USA). Robert McNamara used it for contractor decisions. Now common in cybersecurity and organizational decision-making.

**Structure:**
1. **Preparation**: Each team develops arguments independently
2. **Blue Team Presentation**: 5 minutes to argue FOR the statement
3. **Red Team Presentation**: 5 minutes to argue AGAINST
4. **Open Dialogue**: 15 minutes for constructive back-and-forth
5. **Hats Off**: 5 minutes to integrate insights as a unified group

**Critical Insight:** "The goal of this exercise is not to win the debate or outwit your opponents with mind-bending arguments. The goal for both the red and blue team is the same: coming up with strong arguments and later on, finding an optimal solution together."

**Purple Team Evolution:** In cybersecurity, "purple teams" emerged where red and blue collaborate in real-time rather than sequentially—accelerating learning by eliminating the "report-and-remediate" cycle.

**Application to feature-refine:**
- Explicit "hats off" phase where roles dissolve into collaborative synthesis
- Minimum rounds required (prevents rubber-stamping)
- Maximum rounds capped (prevents endless debate)
- Both roles share the same goal: best solution

---

## Synthesis: Design Principles for feature-refine

Based on this research, the redesigned agent should follow these principles:

### 1. Steel Man First (Mandatory)

Before any criticism, the idea must be articulated in its strongest form. The Advocate's job is to make the idea as compelling as possible—even improving on the original framing.

### 2. Minimum 2 Rounds, Maximum 5

- Minimum ensures genuine batting around (no rubber-stamping)
- Maximum prevents diminishing returns
- Early exit allowed only on clear convergence or fundamental blocker

### 3. Each Round Must Advance

Not "here's another problem" but "here's a concern AND a potential resolution." Rounds should move toward synthesis, not just accumulate objections.

### 4. Synthesis Focus

The goal is a *better* solution—not declaring a winner. The final recommendation may differ from both the original idea and the critiques.

### 5. Convergence Criteria

Stop when you've found a solution that addresses core concerns. Don't exhaust every possible objection—that's infinite.

### 6. Agent-Relevant Constraints Only

Remove human-time assumptions:
- ❌ "Will we regret this in 6 months?" (human memory/context)
- ❌ "Maintenance burden" (assumes human ongoing cost)
- ✅ "Is this reversible if we learn something new?"
- ✅ "Does complexity here propagate elsewhere?"
- ✅ "Is this correct and complete?"

### 7. Same Goal, Different Roles

Both Advocate and Critic share the objective: find the best solution. They're not adversaries—they're partners using different lenses.

---

## Next Steps

Apply these principles to rewrite `intents-plugin/agents/feature-refine/AGENT.md`:

1. Reframe from "adversarial debate" to "collaborative refinement through structured tension"
2. Make steel-manning explicit and required
3. Add minimum round requirement
4. Replace human-time constraints with agent-relevant criteria
5. Add explicit synthesis/convergence phase
6. Emphasize shared goal throughout
