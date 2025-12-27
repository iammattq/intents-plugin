# Research 004: Checklists and Structured Formats for LLM Instruction Following

**Date:** 2025-12-26

**Status:** Complete

**Related:** Agent definition optimization, command/skill/agent instruction design

## Problem Statement

Do checklists help LLMs better follow instructions compared to other formats (prose, numbered lists, bullet points)? This research investigates:

1. Research on prompt engineering for instruction following
2. Whether checkbox/checklist formats improve compliance vs prose or numbered lists
3. Anthropic-specific guidance on structuring prompts
4. Patterns that prevent LLMs from skipping steps in multi-step workflows

## Constraints

- Findings must be applicable to agent definitions (AGENT.md, SKILL.md, commands)
- Must work within Claude Code's context window limitations
- Should integrate with existing Markdown-based instruction patterns
- Need practical, implementable recommendations

---

## Findings

### Why LLMs Skip Instructions

Research from multiple sources identifies consistent causes:

1. **Attention degradation** - Attention becomes less effective as input gets longer during token-by-token processing. Models focus more on early instructions, with later ones receiving diminished attention.

2. **Training bias** - Models encounter more simple instructions in training data than complex multi-step ones. They prefer simpler patterns that are more common.

3. **Poor structure** - Poorly structured prompts lacking clear separation, bullet points, or numbering make it harder for models to distinguish between steps, increasing the chance of merging or omitting instructions.

4. **Token limits** - Input exceeding maximum tokens causes trailing instructions to be ignored entirely.

5. **Instruction density** - The SIFo benchmark shows all models exhibit monotonic performance decline as instruction sequence length increases. Even top models struggle at step 2+.

**Source:** [Why Large Language Models Skip Instructions](https://www.unite.ai/why-large-language-models-skip-instructions-and-how-to-address-the-issue/)

---

### Format Comparison: What Actually Works

#### XML Tags (Most Effective for Claude)

XML tags provide the strongest structural cues for Claude models specifically:

> "Structured prompts using descriptive XML tags can increase LLM accuracy, reduce ambiguity, and improve reasoning by providing clear semantic context."

> "Claude performs exceptionally well with XML, treating tags simply as explicit delimiters... Many models, like Anthropic's Claude, have been trained on prompts incorporating XML-style tags."

**Effectiveness:** Up to 40% improvement in response quality reported.

**Best for:** Complex instructions, multi-section prompts, separating context from instructions.

**Example:**
```xml
<process>
1. Read the plan file
2. Validate prerequisites
3. Execute implementation
</process>

<constraints>
- Never modify tests
- Always run linter before committing
</constraints>
```

**Source:** [AI Brand Scan - XML Tags Guide](https://aibrandscan.com/blog/improve-llm-prompts-with-descriptive-xml-tags-seo-guide/)

#### Numbered Lists vs Bullet Points

Research suggests **short sentences on new lines** may outperform both:

> "Short, focused sentences separated by new lines tends to work best. I haven't found other formats like paragraphs, bullet points, or numbered lists to work as well."

However, for sequential multi-step processes, **numbered lists with explicit separation** help models recognize distinct tasks. The key is explicit labeling that signals "these are separate steps."

**Source:** [Eugene Yan - Prompting Fundamentals](https://eugeneyan.com/writing/prompting/)

#### Checklists (Markdown Checkboxes)

Checklists have a specific, valuable use case: **working scratchpads for iterative tasks**.

From Anthropic's Claude Code best practices:

> "For large tasks with multiple steps or requiring exhaustive solutions... improve performance by having Claude use a Markdown file as a checklist and working scratchpad. For example, to fix a large number of lint issues: Tell Claude to run the lint command and write all resulting errors (with filenames and line numbers) to a Markdown checklist, then instruct Claude to address each issue one by one, fixing and verifying before checking it off and moving to the next."

**Key insight:** Checklists work best as **dynamic tracking artifacts** rather than static instruction formats. Claude checks items off as it completes them, creating a verification loop.

**Source:** [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)

#### Prose vs Structured Formats

Prose is consistently the **worst** format for multi-step instructions. The InFoBench research shows that decomposing complex instructions into discrete sub-questions significantly improves evaluation reliability:

> "Breaking complex instructions into simpler criteria significantly enhances evaluation reliability... Pairwise Kappa Agreement of 0.532 compared to Direct Scoring's 0.284."

**Source:** [InFoBench Paper](https://arxiv.org/html/2401.03601v1)

---

### Anthropic-Specific Guidance

#### Claude 4.x Best Practices

From official Anthropic documentation:

1. **Be explicit** - "Claude 4.x models respond well to clear, explicit instructions. Being specific about your desired output can help enhance results."

2. **Provide context/motivation** - "Providing context or motivation behind your instructions, such as explaining to Claude why such behavior is important, can help Claude 4.x models better understand your goals."

3. **Use examples** - "Include 3-5 diverse, relevant examples to show Claude exactly what you want. More examples = better performance."

4. **Match prompt style to output** - "The formatting style used in your prompt may influence Claude's response style."

5. **Tell what to do, not what not to do** - Instead of "Do not use markdown," try "Your response should be composed of smoothly flowing prose paragraphs."

6. **Use XML format indicators** - "Write the prose sections of your response in `<smoothly_flowing_prose_paragraphs>` tags."

**Source:** [Claude 4 Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-4-best-practices)

#### Instruction Capacity

There is a practical limit to how many instructions can be followed:

> "Frontier thinking LLMs can follow ~150-200 instructions with reasonable consistency, and Claude Code's system prompt already contains ~50 instructions, leaving limited capacity for your own."

**Implication:** Keep agent definitions concise. Prioritize universally applicable guidance.

**Source:** [HumanLayer - Writing a Good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md)

---

### Patterns That Prevent Skipping Steps

#### 1. Task Decomposition (Most Effective)

Break multi-step prompts into smaller, focused segments. This is the single most effective technique:

> "Long or multi-step prompts should be divided into smaller, more focused segments. Providing one or two instructions at a time allows the model to maintain better attention."

**Implementation:** Use prompt chaining or multi-agent orchestration where each agent handles a focused task.

#### 2. Chain-of-Thought Prompting

Guide models to reason through each step before acting:

> "Chain-of-thought prompting helps reduce ambiguity in multi-step tasks."

**Example:**
```
First, identify the affected files.
Then, analyze the impact on each file.
Finally, propose the minimal change set.
```

#### 3. Explicit Completion Reminders

Add direct statements requiring all steps:

> "Answer every task completely. Do not skip any instruction."

**Example from Claude 4 docs:**
```
Continue working systematically until you have completed this task.
```

#### 4. Verification Loops

The most robust pattern for complex workflows:

1. Execute step
2. Verify step completion
3. Check off / confirm
4. Move to next step

From Anthropic's guidance on checklists:
> "Address each issue one by one, fixing and verifying before checking it off and moving to the next."

#### 5. Structured Output Requirements

Requiring specific output structure forces attention to each component:

> "Specifying the format (like JSON, bullet points, or tables) and limiting the output's length or structure helps steer the model toward responses that are consistent, parseable, and ready for downstream use."

**Source:** [Multi-Step LLM Chains Best Practices](https://www.deepchecks.com/orchestrating-multi-step-llm-chains-best-practices/)

---

### Research Benchmarks: Hard Data

#### SIFo Benchmark (2024)

Sequential Instruction Following benchmark results:

| Task Type | GPT-4 Accuracy | Llama3-70B |
|-----------|----------------|------------|
| Text Modification | 42.5% | 18.0% |
| Question Answering | 37.5% | 39.0% |
| Mathematics | 91.5% | 87.0% |
| Security Rules | 77.0% | 72.5% |

**Key finding:** "All models show a monotonic decline in performance as the position of an instruction in a sequence increases."

**Source:** [SIFo Benchmark](https://arxiv.org/html/2406.19999v1)

#### InFoBench (2024)

Decomposed instruction following rates:

| Model | Easy Set | Hard Set | Overall |
|-------|----------|----------|---------|
| GPT-4-1106 | 90.1% | 89.1% | 89.4% |
| GPT-3.5-turbo | 90.4% | 85.1% | 86.7% |
| Claude-2.1 | 82.9% | 87.9% | 86.4% |

**Key finding:** "Even the proprietary GPT-4 model fails to meet at least one constraint on over 21% of instructions."

**Hardest constraint types:** Number constraints and Linguistic constraints show lowest compliance.

**Source:** [InFoBench](https://arxiv.org/html/2401.03601v1)

---

## Recommendation

### Format Hierarchy for Agent Definitions

**Best to Worst for Instruction Following:**

1. **XML tags with numbered steps inside** - Best for Claude, provides clear structure
2. **Short sentences on separate lines** - Simple, effective, low overhead
3. **Numbered lists** - Good for sequential processes
4. **Bullet points** - Good for non-sequential requirements
5. **Markdown checklists** - Best as working artifacts, not static instructions
6. **Prose paragraphs** - Worst; avoid for multi-step instructions

### Recommended Pattern for Agent/Skill Definitions

```markdown
---
name: agent-name
description: Use WHEN [trigger]. Does [what]. [Domain] specialized.
---

You are a [role]. [Brief context].

<core_principles>
- Principle 1
- Principle 2
</core_principles>

<process>
1. **Step 1** - [Action]
   Verify: [How to confirm completion]

2. **Step 2** - [Action]
   Verify: [How to confirm completion]

3. **Step 3** - [Action]
   Verify: [How to confirm completion]
</process>

<output_format>
[Structured template]
</output_format>

<constraints>
Complete all steps. Do not skip any step.
</constraints>
```

### When to Use Checklists

Use markdown checklists (`- [ ]`) specifically for:

1. **Dynamic tracking** - Agent writes errors/tasks to file, checks off as completed
2. **Review workflows** - Agent works through checklist, marks items as verified
3. **Multi-item processing** - Processing a list of files/errors/issues one by one

Do NOT use checklists for:
- Static instructions in agent definitions
- Process steps (use numbered lists instead)
- Requirements (use bullet points or XML sections)

---

## Implementation Notes

### For This Codebase (intents-plugin)

1. **Agent definitions** - Use XML tags for major sections (`<process>`, `<output_format>`, `<constraints>`)

2. **Review agents** - Use dynamic checklists as working artifacts:
   ```markdown
   ## Process
   1. Run validation command
   2. Write results to checklist file
   3. Work through checklist, verifying and checking off each item
   ```

3. **Multi-step commands** - Include explicit completion requirement:
   ```markdown
   Complete all phases. Do not skip any phase.
   ```

4. **Keep it concise** - Stay under 150 instructions total per context. Use progressive disclosure (reference external files for details).

5. **Verification loops** - For critical workflows, require explicit verification at each step:
   ```markdown
   1. Execute step
   2. Confirm step succeeded
   3. Only then proceed to next step
   ```

---

## Sources

### Primary Sources (Directly Fetched)

- [Claude 4 Best Practices - Anthropic](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-4-best-practices) - Official Claude 4.x prompt engineering guidance
- [Claude Code Best Practices - Anthropic](https://www.anthropic.com/engineering/claude-code-best-practices) - Agentic coding patterns, checklist usage
- [Why Large Language Models Skip Instructions - Unite.AI](https://www.unite.ai/why-large-language-models-skip-instructions-and-how-to-address-the-issue/) - Research on instruction skipping causes and solutions
- [SIFo Benchmark - ACL 2024](https://arxiv.org/html/2406.19999v1) - Sequential instruction following research with hard data
- [InFoBench - ACL 2024](https://arxiv.org/html/2401.03601v1) - Instruction following evaluation with decomposition methodology
- [Writing a Good CLAUDE.md - HumanLayer](https://www.humanlayer.dev/blog/writing-a-good-claude-md) - Practical CLAUDE.md formatting guidance
- [XML Tags for LLM Prompts - AI Brand Scan](https://aibrandscan.com/blog/improve-llm-prompts-with-descriptive-xml-tags-seo-guide/) - XML tag effectiveness research
- [Prompting Fundamentals - Eugene Yan](https://eugeneyan.com/writing/prompting/) - Format comparison and best practices

### Secondary Sources (Search Results)

- [Multi-Step LLM Chains Best Practices - Deepchecks](https://www.deepchecks.com/orchestrating-multi-step-llm-chains-best-practices/) - Orchestration patterns
- [Prompt Chaining Guide - Prompting Guide](https://www.promptingguide.ai/techniques/prompt_chaining) - Task decomposition techniques
- [Self-Verification - Learn Prompting](https://learnprompting.org/docs/advanced/self_criticism/self_verification) - Verification loop patterns
- [Chain of Verification - Analytics Vidhya](https://www.analyticsvidhya.com/blog/2023/12/chain-of-verification-implementation-using-langchain-expression-language-and-llm/) - CoVe implementation
- [MIT Press Survey on Instruction Following](https://direct.mit.edu/coli/article/50/3/1053/121669/Large-Language-Model-Instruction-Following-A) - Comprehensive research survey
- [Apple Research - Internal Instruction Following](https://machinelearning.apple.com/research/follow-instructions) - LLM internal state analysis

---

## Summary

Checklists are valuable but not as static instruction formats. They work best as **dynamic working artifacts** where Claude checks items off as it completes them. For instruction definitions themselves:

1. Use **XML tags** for major sections (most effective for Claude)
2. Use **numbered lists** for sequential processes
3. Use **short sentences on separate lines** for simple requirements
4. **Decompose** complex tasks into smaller focused steps
5. Include **explicit completion requirements** ("Complete all steps")
6. Add **verification checkpoints** for critical workflows

The research consistently shows that structure, decomposition, and explicit step separation improve instruction following more than any specific format choice.
