---
name: role-prompt-kit
description: Four paste-ready starter prompts for Claude, segmented by user role (builder/engineer, team leader, executive, analyst). Each is pre-calibrated for that role's job-to-be-done and paired with a model tier recommendation. Use when onboarding a new user, calibrating a prompt for a specific audience, or building a role-aware wrapper.
---

# Role Prompt Kit

Most users apply the same generic prompt regardless of their role. This kit provides four role-optimized starter prompts that produce systematically better output by matching the prompt's framing to how the role thinks and what they need from an output.

Each prompt ships with a role description, paste-ready text, a model tier recommendation, and the expected output shape.

## When to Invoke

- Onboarding a new user who asks "where do I start with Claude?"
- Choosing a prompt template for a role-specific workflow
- Building a wrapper or UI that needs to segment users by role
- User says "role prompt kit", "starter prompt for [role]", "role-based prompts", "prompt for exec/leader/builder", or "/role-prompt-kit"

---

## Role 1: Builder / Engineer

**Who:** Software engineers, technical PMs, data scientists — people who produce artifacts (code, specs, queries, configs) and need them fast and correct.

**Model tier:** Sonnet (most tasks) / Opus (architecture, novel algorithm design)

**Paste-ready prompt:**
```
You are a senior engineer pairing with me. I need working [code / query / spec / config], not explanations.

Context: [one sentence on the project/stack]
Task: [specific artifact to produce]
Constraints: [language, framework, output format]
Acceptance criteria: [what done looks like — e.g. "runs without errors", "matches this schema"]

Return only the artifact. If something is ambiguous, state the assumption at the top and proceed.
```

**Why it works:** "Pairing" sets collaborative tone without triggering over-explanation. Explicit acceptance criteria convert the task from open-ended to checkable. "Return only the artifact" prevents padding.

---

## Role 2: Team Leader / Manager

**Who:** Engineering leads, product managers, department heads — people who need options, tradeoffs, and decisions framed for review before committing.

**Model tier:** Sonnet (routine decisions) / Opus (high-stakes or novel decisions)

**Paste-ready prompt:**
```
I'm a [role] making a decision about [topic]. I need options, not a single answer.

Context: [2–3 sentences on the situation]
Decision: [what I need to decide]
Constraints: [time, budget, team size, existing systems, etc.]

Format your response as:
1. Option A — [name]: [description], pros, cons, when to choose this
2. Option B — [name]: same
3. Recommendation: [which option you'd choose and why — commit to one]
```

**Why it works:** "Options, not a single answer" prevents the model from over-committing before the leader has reviewed tradeoffs. Requesting an explicit recommendation after listing options gets the analytical work done without removing human judgment.

---

## Role 3: Executive

**Who:** C-suite, VPs, directors — people who need briefing-ready outputs with the decision recommendation upfront and no padding.

**Model tier:** Sonnet (most briefings) / Opus (board-level or investor content)

**Paste-ready prompt:**
```
I'm briefing [audience] on [topic]. Write a decision-ready briefing.

Structure:
- Situation (1 sentence): what's happening
- Recommendation (1 sentence): what I should do
- Options considered (2–3 bullets): what else was evaluated and why it was ruled out
- Risk (1 sentence): what could go wrong with the recommendation
- Ask (1 sentence): what decision or action I need from [audience]

Context: [2–3 sentences of background]
Tone: direct, no hedging, assume a busy reader with 90 seconds
```

**Why it works:** Recommendation-first structure matches how executives actually read documents. Banning hedging forces commitment, which produces cleaner output even when the underlying decision is uncertain.

---

## Role 4: Analyst / Deep Thinker

**Who:** Researchers, strategists, writers, analysts — people who need rigorous reasoning, not a summary.

**Model tier:** Opus (always — this role's tasks require maximum reasoning depth)

**Paste-ready prompt:**
```
I'm exploring [topic / question] and want rigorous reasoning, not a summary.

What I know: [2–3 sentences]
What I'm uncertain about: [the specific gap or tension]
What I want: [analysis / argument / steelman / critique / alternative framing]

Do not hedge. If you're uncertain, say what you'd need to resolve it. If the question is under-specified, name the assumption you're making and proceed.
```

**Why it works:** "Rigorous reasoning, not a summary" signals the level of engagement expected. Asking for uncertainty to be named prevents confident answers to under-constrained questions.

---

## Quick Reference

| Role | Default Tier | When to Upgrade |
|------|-------------|-----------------|
| Builder | Sonnet | Architecture, novel algorithms → Opus |
| Leader | Sonnet | High-stakes, irreversible decisions → Opus |
| Executive | Sonnet | Board / investor content → Opus |
| Analyst | Opus | Always — don't downgrade |

For full model tier routing logic (per task complexity, not per role), see the `model-router` skill.

## Verification

Before deploying a role prompt in a workflow:
- [ ] The prompt names a specific artifact type or output format — not "help me with X"
- [ ] It includes explicit acceptance criteria (builder) or output structure (leader/exec)
- [ ] It has been tested with at least one real task from the target role
- [ ] Model tier is matched to output stakes — not defaulted to Opus for everything

## Source

Nate's Newsletter (natesnewsletter@substack.com), 2026-06-03:
"Model-Routing Guide + Role-Specific Paste-Prompts — a model-routing skill paired with a pack of ready-to-paste prompts segmented by audience role (builder, leader, executive)."
Idea #4 from intake 2026-06-04.
