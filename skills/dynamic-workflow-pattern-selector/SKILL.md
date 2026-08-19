---
name: dynamic-workflow-pattern-selector
description: 'Given a task, select the right one of Claude Code''s 6 dynamic workflow patterns (classify-and-act, fan-out-and-synthesize, adversarial-verification, generate-and-filter, tournament, loop-until-done) and produce a ready-to-run prompt. Trigger phrases: "which workflow pattern", "how should I structure this workflow", "what pattern for", "should I fan out or loop", "help me pick a workflow pattern", "stack workflow patterns".'
---

# Dynamic Workflow Pattern Selector

A decision guide for Claude Code's 6 named dynamic workflow patterns from the Anthropic masterclass. Given a task description, maps it to the right pattern (or stack of patterns), explains why, and produces a ready-to-run prompt. Complements `dynamic-workflow-orchestration`, which covers invocation mechanics; this skill covers pattern selection and prompt construction.

**Prompt library:** `reference/prompt-library.md` in this skill folder holds the long-form version of every template below, plus one template per common two-pattern stack, the keyword contract that routes a prompt into each shape, the guardrail sentence per pattern, and the anti-stacks. Select the pattern here, then copy the prompt from there rather than paraphrasing the short template. Record runs in its validation log.

## Trigger

Use when:
- You know you want a dynamic workflow but don't know which shape it should take
- A task seems to fit multiple patterns and you need to resolve the ambiguity
- You want to stack patterns and need help sequencing them
- You're writing a workflow prompt and want a structural review before running it

Do NOT use for:
- Deciding whether to use a workflow at all — use `workflow-fit-scorer` for that
- General dynamic workflow invocation help — use `dynamic-workflow-orchestration` for that
- Tasks under 5 minutes that don't need multi-agent coordination

## The 6 Patterns

### 1. Classify and Act

**What it does:** A lightweight classifier agent reads the input and routes it to the correct specialist agent based on category. The classifier never acts; it only routes.

**Mental model:** Receptionist at the front door. Quarantine before action.

**When to use:**
- Input is heterogeneous and different categories need different handlers
- You want to prevent the wrong agent from touching the wrong input
- Examples: inbox triage (bug / refund / lead / spam), support ticket routing, document type dispatch

**Prompt keyword:** `spawn a classifier agent that reads each [item] and routes it to a [handler]`

**Prompt template:**
```
Build a workflow that triages [input source] by spawning a classifier agent that reads
each [item] and routes it to a [category-A], [category-B], [category-C] handler,
deduplicating against [existing tracker] before any handler acts.
```

---

### 2. Fan Out and Synthesize

**What it does:** Breaks the task into mutually exclusive slices, assigns one agent per slice (each with its own clean context window so data never cross-contaminates), then runs a barrier synthesis step that waits for all agents and merges their outputs into one result with citations.

**Mental model:** Parallel research team, each member owns one lens, then one editor assembles the final report.

**When to use:**
- Work can be cleanly divided into independent, non-overlapping slices
- Each slice is large enough to justify its own context window
- Examples: deep research (one agent per angle), due diligence (one agent per folder), codebase audit (one agent per module)

**Prompt keywords:** `fan out`, `one sub-agent per [X]`, `each in its own clean context`, `barrier synthesize step`

**Prompt template:**
```
Build a workflow that does [goal] on [corpus] by fanning out one sub-agent per [slice unit],
each in its own clean context (so [data] never cross-contaminate), and have every agent return
a structured [output format] with the exact source path for each finding.
Then run a barrier synthesize step that waits for all of them to finish and merges their
outputs into one [output file] where every claim links back to the file it came from.
```

---

### 3. Adversarial Verification

**What it does:** Runs a series of devil's-advocate agents that check a prior output against a rubric or checklist. Each skeptic agent checks one specific claim or component independently, preventing the self-preference bias of a single-session auto-review.

**Mental model:** Red team. Three skeptics audit the work you already produced.

**When to use:**
- The output was produced by Claude and you don't trust self-review
- Fact accuracy is critical (blog posts, technical docs, legal claims)
- You want per-claim pass/fail verdicts with traceable sources, not a general "looks good"
- Best applied AFTER fan-out-and-synthesize as a second pass on the merged findings

**Prompt keywords:** `separate agent that checks it against the real source`, `adversarial`, `devil's advocate`, `verify each claim`

**Pro tip:** Write the rubric before running the workflow. The rubric is the pseudo-plan; agents push against it rather than generating their own success criteria.

**Prompt template:**
```
Use a workflow to verify [document/output] before I ship it.
Have one agent extract each [claim/finding] into its own item.
Then for every [claim], spin off a separate agent that checks it against [real source].
Return only the claims that failed, the exact reason each failed, and where the source
of the error likely came from.
```

---

### 4. Generate and Filter

**What it does:** Spins up a swarm of generator agents to overproduce ideas, names, options, or candidates, then passes the full set to one or more judge agents that score everything against a rubric. The final output is a short, high-quality shortlist.

**Mental model:** 1,000 ideas → filter to 3. Going from 1,000 to 3 is easier than going from 10 to 3.

**When to use:**
- Taste or judgment is required (naming, copy, strategy selection)
- Volume of options is more valuable than quality of any single option
- Examples: product names, video titles, cold email openers, brand positioning angles

**Prompt keywords:** `generator agent`, `judge agent`, `scores every option against`, `the generator and judge must be different agents`

**Key rule:** Always make the generator and the judge different agents. Never have the agent that generated the ideas also score them.

**Prompt template:**
```
Use a workflow to brainstorm [N] [option type] for [topic] with one generator agent,
then hand them all to a judge agent that scores every option against [criteria].
The generator that brainstorms and the judge that scores must be different agents.
Return only the top [N] options with their scores and the reason each ranked where it did.
```

---

### 5. Tournament

**What it does:** Takes a large candidate pool and runs pairwise head-to-head comparisons in rounds, like a bracket tournament. Each comparison is its own fresh-context agent. The winner advances to the next round. Continues until one candidate remains. Each round can use a different rubric.

**Mental model:** March Madness bracket. Pair comparison eliminates context window bloat and forces explicit tradeoff reasoning.

**When to use:**
- The candidate pool is too large to rank in one session (50+ items)
- Ranking quality matters more than speed
- You need an auditable decision trail (who beat whom and why)
- Examples: resume screening, feature prioritization, vendor selection, design variant selection

**Key advantage:** Each comparison has a fresh context window — no accumulated bias from prior comparisons. The orchestrating loop holds the bracket state; each agent only sees one match.

**Prompt keywords:** `pairwise comparisons`, `tournament`, `each head-to-head match is its own comparison agent`, `deterministic loop holds the brackets`

**Prompt template:**
```
Use a workflow to rank every [item] for [goal] by running a tournament of pairwise
comparisons against [rubric], where each head-to-head match is its own comparison agent,
and the deterministic loop holds the brackets so only the running order stays in context.
[Round 1: criteria A. Round 2: criteria B. Final: criteria C.]
```

---

### 6. Loop Until Done

**What it does:** Spins up new agents in a loop without a fixed iteration count, continuing until a specific observable outcome is reached. The loop terminates on the condition, not on a count.

**Mental model:** `/goal` — keep going until clean. The loop is the exit condition, not the input.

**When to use:**
- You can't predict how many passes the task needs
- The task requires repeated attempts to reproduce or trigger a condition (flaky bugs, edge cases)
- Examples: hunting a flaky test that fails 1 in 50 runs, exhaustively mining session history, finding all optimizations in a codebase until a clean pass returns nothing new

**Key rule:** Never say "do this 10 times." Always say "do this until [observable condition]." Each attempt spawns a new agent with a fresh context window.

**Prompt keywords:** `no fixed pass count`, `keep going until`, `loop until`, `don't stop until`

**Prompt template:**
```
Build a workflow that [task description], forming theories and adversarially testing each
one in its own isolated work tree, with no fixed pass count.
Keep looping until [specific observable condition — e.g., "a full clean pass finds no new issues"].
[Optional: /goal Do not stop until [condition].]
```

---

## Pattern Selection Decision Table

| Situation | Pattern |
|-----------|---------|
| Heterogeneous inputs needing different handlers | Classify and Act |
| Large corpus that can be sliced independently | Fan Out and Synthesize |
| Need to audit/validate output you don't trust | Adversarial Verification |
| Need high-quality shortlist from a large option space | Generate and Filter |
| Large candidate pool needing fair ranking with audit trail | Tournament |
| Unknown iteration count, terminate on condition | Loop Until Done |

## Stacking Patterns

Patterns compose. A realistic complex task might be:

1. **Fan Out** over the codebase to extract all findings (parallel analysis)
2. **Adversarial Verification** of the merged findings (red team pass)
3. **Loop Until Done** continuing until the adversarial pass returns nothing new

Single prompt for this stack:
```
Build a workflow that audits every file under [codebase], fans out one agent per file,
has a separate agent try to refute each finding against the code (adversarial verify),
and loops until a clean pass turns up with no new issues.
Return only the confirmed issues, each with the file and the exact line.
/goal Do not stop until a full clean pass finds no new issues.
```

**Stacking rules:**
- Fan Out always precedes Adversarial Verification (you need content before you can verify it)
- Generate and Filter can have Tournament applied to the filtered shortlist for final ranking
- Loop Until Done is typically the outermost wrapper when used in a stack
- You don't need to design the stack by hand: include the right keywords in one prompt and Claude Code will infer the pattern

## When NOT to Use Any Workflow

- Single-file changes or button styling tasks: one agent suffices
- Tasks that finish in under 5 minutes with a standard prompt
- As models improve (4.8, 4.9, 5.x), more work will be in-context — reserve workflows for genuine multi-layer complexity

## Sharing Workflows

Workflows save as `.js` files. A shareable workflow package is a folder containing:
- `SKILL.md` (the skill definition)
- `[workflow-name].js` (the saved workflow)
- Any supporting markdown (rubric files, etc.)

To save a running workflow: `/workflows` to view running workflows, then save the current one.

## Source Attribution

Technique: 6 Dynamic Workflow Patterns from the Anthropic Masterclass
Source: Mark Kashef YouTube
URL: https://www.youtube.com/watch?v=g9b9G8dcS8Y
Published: 2026-06-03
Title: "Master All 6 Claude Code Dynamic Workflows"
