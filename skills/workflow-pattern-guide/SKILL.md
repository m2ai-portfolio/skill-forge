---
name: workflow-pattern-guide
description: Select the right dynamic workflow pattern for any task from six named shapes: Classify and Act, Fan Out and Synthesize, Adversarial Verification, Generate and Filter, Tournament, and Loop Until Done. Returns a pattern recommendation with a starter prompt and explains how to stack patterns for complex tasks. Trigger: "which workflow pattern", "how should I design this workflow", "workflow pattern guide", "what pattern for this task", "workflow-pattern-guide".
---

# Workflow Pattern Guide

Dynamic workflows decompose work across independent agents, each with its own context window, to avoid the three failure modes of long single-session work: agent laziness (tasks incompletely executed), self-preference bias (a session that can't objectively review its own output), and goal drift (the original objective degrading through compaction and tool-call noise).

There are six shapes a dynamic workflow can take. Each maps to a class of problems. This skill identifies which pattern fits a given task and generates a starter prompt.

## When to Use This Skill

Use when you know you need a dynamic workflow but aren't sure which architecture to reach for. If you already know the pattern, skip this skill and write the workflow prompt directly.

Do NOT use this for single-agent tasks, simple sequential automations, or any task that finishes in under 5 minutes.

## Phase 1: Intake

Ask the user to describe their task in 2–3 sentences:
- What is the input?
- What is the desired output?
- What's the main risk if the output is wrong?

## Phase 2: Pattern Selection

Match the task against the six patterns. Return the best fit and the second-best fit (for stacking guidance in Phase 4).

---

### Pattern 1 — Classify and Act

**Shape**: One classifier agent reads each input item and routes it to the appropriate handler agent.

**Use when**:
- Inputs arrive in a heterogeneous stream and need to be sorted before processing.
- Different input types require fundamentally different handling logic.
- You want to isolate routing decisions from execution decisions.

**Examples**: Inbox triage (bug vs. refund vs. upgrade), document routing, ticket classification before assignment.

**Starter prompt**:
```
Build a workflow that processes each item in [source] by spawning a classifier agent
that reads each item and routes it to one of [handler A / handler B / handler C].
The classifier must quarantine the item before routing — no handler acts until
classification is confirmed. Deduplicate against [existing store] before any
handler executes.
```

---

### Pattern 2 — Fan Out and Synthesize

**Shape**: One task is split into parallel sub-questions. Each sub-question goes to its own agent. A synthesizer merges all responses at the end.

**Use when**:
- The task has multiple independent angles that can be investigated in parallel.
- Each angle requires a clean context window — cross-contamination between branches would degrade quality.
- The final output benefits from citing which branch produced each finding.

**Examples**: Multi-folder due diligence, competitive research across multiple sources, codebase audits spanning multiple modules.

**Starter prompt**:
```
Build a workflow that analyzes [input] by fanning out one sub-agent per [folder /
topic / module], each in its own clean context so content never cross-contaminates.
Have every agent return a structured summary with the exact source path for each
finding. Run a synthesize step after all agents complete that merges their outputs
into one cited [report / document / database], where every claim links back to
the source it came from.
```

---

### Pattern 3 — Adversarial Verification

**Shape**: One agent produces a deliverable. Three independent skeptic agents each try to find flaws using a shared rubric. The deliverable is accepted only if skeptics find no critical issues.

**Use when**:
- Self-preference bias is a concern — the producing agent cannot be trusted to validate its own output.
- The deliverable makes factual or technical claims that need external verification.
- You need to detect hallucinations, logical errors, or overconfident statements before shipping.

**Examples**: Fact-checking a blog post, validating an architecture proposal, reviewing generated code before merging.

**Starter prompt**:
```
Build a workflow to verify [deliverable]. First, have one agent extract each
[claim / component / assumption] into its own item. For every item, spawn a
separate skeptic agent that checks it against [the source material / real test /
spec]. The skeptic must assume the item is wrong and actively look for a refutation.
Return a list of items that failed verification with the exact reason each failed.
Items with no refutation are provisionally accepted.
```

---

### Pattern 4 — Generate and Filter

**Shape**: Multiple generator agents produce many candidate options independently. A judge agent scores all candidates against a rubric. The rubric is written before generation begins.

**Use when**:
- You need volume to find quality — it's easier to filter 500 options to 3 than to generate 3 directly.
- Taste or subjective judgment is required and you want an explicit rubric to guide the filter.
- You want the judge's reasoning to be traceable and consistent across all candidates.

**Examples**: Naming a product, generating video title options, brainstorming campaign angles, generating test cases.

**Starter prompt**:
```
Build a workflow to generate [N] options for [goal]. Use one generator agent to
produce all options independently. Then pass all options to a judge agent that
scores every option against the following criteria: [criterion 1 / criterion 2 /
criterion 3]. The generator and the judge must be different agents. Return the
top [N] options ranked by score with the judge's reasoning for each.
```

---

### Pattern 5 — Tournament

**Shape**: Items are compared pairwise in elimination brackets. Each bracket match is a fresh agent with no knowledge of prior matches. Rounds continue until one winner emerges.

**Use when**:
- You have a large set of candidates that can't all be compared at once without context bloat.
- Ranking quality requires comparative judgment ("which of these two is better and why") rather than absolute scoring.
- Bias from accumulating context across matches would degrade late-round decisions.

**Examples**: Ranking resumes, selecting the best proposal from a large set, tournament-style A/B testing of content variants.

**Starter prompt**:
```
Build a workflow to rank every item in [collection] using a tournament of pairwise
comparisons. Each head-to-head match is its own fresh agent with a clean context
window. The match agent evaluates the two items against [rubric / criteria] and
returns a winner with a one-sentence reason. The loop holds the bracket — only
the running order stays in context. Run rounds until one overall winner emerges.
Optionally: give each round a different evaluation criterion.
```

---

### Pattern 6 — Loop Until Done

**Shape**: A goal-directed loop spawns new agents until a done condition is met. No fixed pass count — the loop continues as long as new findings are being discovered or the condition remains unmet.

**Use when**:
- You don't know in advance how many iterations are needed.
- Success is defined by a state change, not a count (e.g., "find the bug," "no new findings remain").
- The task benefits from continuously incorporating findings from prior iterations into the next hypothesis.

**Examples**: Reproducing a flaky bug, exhaustive pattern-mining across conversation history, hunting for all edge cases in a codebase until no new ones surface.

**Starter prompt**:
```
Build a workflow that [task description]. Keep forming hypotheses and testing each
one in its own isolated agent. Do not specify a fixed number of passes — continue
until [done condition: no new findings / the bug is reproduced and traced /
a full clean pass produces no new results]. Each agent should build on the
findings of prior agents. Return only confirmed results, each with the evidence
that confirms it.
```

---

## Phase 3: Starter Prompt

Based on the pattern selected in Phase 2, generate a customized starter prompt filled in with the user's actual task details. Do not return a generic template — replace every bracketed placeholder with the user's specifics.

## Phase 4: Stacking Guidance

For complex tasks, two or three patterns can be stacked. Common combinations:

| Stack | When to use |
|-------|-------------|
| Fan Out → Adversarial Verify | Research a topic broadly, then check each finding for hallucinations before using |
| Generate and Filter → Tournament | Generate many options, filter to finalists, then rank finalists pairwise |
| Fan Out → Loop Until Done | Fan out for initial coverage, then loop until the union of all findings stops growing |
| Classify and Act → Adversarial Verify | Route inputs to handlers, then verify each handler's output before accepting |

Stacking example prompt (Fan Out → Adversarial Verify → Loop Until Done):
```
Build a workflow that audits every file in [codebase]. Fan out one agent per file.
Have a separate agent adversarially verify each finding against the actual code.
Loop until a full clean pass produces no new confirmed issues.
Return only confirmed issues, each with the file path and exact line number.
```

## Phase 5: Token Budget Warning

Dynamic workflows are expensive. Before running:

- Estimate: ~250,000–300,000 tokens for a small focused team; 1–3M tokens for a full codebase audit.
- Tell the workflow its budget explicitly in the prompt: "Budget: X tokens total."
- Use only when the manual equivalent is at least 2 hours of human work, or when quality from a single agent is demonstrably insufficient.

## Source Attribution

Technique: Six dynamic workflow pattern taxonomy for Claude Code
Source: Mark Kashef YouTube — "Every Claude Code Dynamic Workflow (& When to Use Each)"
URL: https://youtu.be/g9b9G8dcS8Y
Published: 2026-06-03
