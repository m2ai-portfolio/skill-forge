---
name: ship-gate-review
description: Evaluate agent output against a configurable "good enough to ship" rubric before it reaches a downstream consumer (client, user, system, or pipeline stage). Produces a SHIP / REVISE / REJECT decision with annotated evidence per criterion. Use when the user says "is this ready to ship?", "quality gate", "ship/no-ship check", "review before delivery", "does this meet our standards?", or when wiring an output gate into an agent workflow.
---

# Ship-Gate Review

An agent producing output is not the same as that output being ready to ship. Without an explicit review-standards gate, output quality is assessed informally -- usually by the user after the fact, after time and trust have already been spent. This skill encodes "review standards" as a callable gate: given output and optional criteria, it returns a structured SHIP / REVISE / REJECT verdict with evidence, so the standard is consistent across runs and reviewers.

## Trigger

Use when the user says "is this ready to ship?", "ship/no-ship", "quality gate", "review before delivery", "does this meet our standards?", "final check", or "output review." Can also be wired as a post-task step in an agent workflow: "after generating the report, run ship-gate-review before returning it."

## Phase 1: Intake

Accept two inputs:

1. **The output to evaluate** -- any artifact: text, code, report, JSON, plan, email draft, slide deck outline, analysis.
2. **Review criteria** (optional) -- one of:
   - A named workflow type (e.g., "client deliverable", "internal report", "code diff", "marketing copy", "API response")
   - An explicit checklist the user provides
   - Nothing (the skill infers criteria from the output type)

If neither criteria nor workflow type is provided and the output type is ambiguous, ask: "What is this output for, and who is the primary consumer?"

## Phase 2: Criteria Resolution

Map the workflow type to a review-standards rubric. Defaults by output type:

| Output type | Default criteria set |
|-------------|---------------------|
| **Client deliverable** (report, deck, email) | Completeness, Accuracy, Tone, Actionability, No-internal-leakage |
| **Code diff / patch** | Correctness, Test coverage signal, No debug artifacts, Follows stated conventions |
| **Agent task output** (structured data, JSON) | Schema conformance, No hallucinated fields, Completeness, Parseable by downstream |
| **Marketing or content copy** | On-brief, Audience match, No factual errors, CTA clarity |
| **Internal report or analysis** | Claims sourced, No overreach beyond data, Actionable conclusion, Reader-appropriate depth |
| **Plan or spec** | All dependencies stated, No circular dependencies, Scope matches stated goal, Risks named |

If the user provides explicit criteria, use those verbatim and skip defaults.

## Phase 3: Criterion-by-Criterion Evaluation

For each criterion in the resolved set, evaluate the output and assign:

- **PASS** -- criterion is clearly satisfied, with evidence
- **FLAG** -- criterion is partially met or uncertain; the specific gap is named
- **FAIL** -- criterion is not met; the deficiency is named and quoted from the output

Do not aggregate into a vague "overall quality" score. Each criterion is its own finding.

## Phase 4: Verdict

Apply the following decision rule:

| Condition | Verdict |
|-----------|---------|
| All criteria PASS | **SHIP** |
| One or more FLAG, zero FAIL | **REVISE** -- list flagged items; output is close |
| One or more FAIL | **REJECT** -- list failing items; output needs substantive rework |

Override: if any single criterion is critical (marked with `[blocking]` by the user or inferred from context -- e.g., "accuracy" for a client deliverable), a FAIL on that criterion alone yields REJECT regardless of other scores.

## Phase 5: Output

```
## Ship-Gate Review

**Verdict: SHIP / REVISE / REJECT**

| Criterion | Result | Evidence / Gap |
|-----------|--------|---------------|
| [criterion 1] | PASS/FLAG/FAIL | [one line] |
| [criterion 2] | PASS/FLAG/FAIL | [one line] |
...

**Required before shipping:**
- [If REVISE or REJECT: bullet list of specific changes needed, tied to flagged/failed criteria]

**If SHIP:** output meets the stated review standard and is cleared for delivery.
```

If the verdict is SHIP, no further action is required. If REVISE or REJECT, the list of required changes is the agent's next task input.

## Phase 6: Wiring as a Workflow Step

To wire this as a post-generation gate in an agent workflow, append to the agent's task prompt:

```
After generating [output type], run ship-gate-review against it before returning.
Workflow type: [client deliverable / code diff / internal report / etc.]
If the verdict is REVISE or REJECT, apply the required changes and re-evaluate once before returning.
Maximum re-evaluation passes: 2.
```

Cap re-evaluation passes to avoid loops. If two passes still yield REVISE or REJECT, surface the verdict and evidence to the user rather than continuing.

## Verification

A good gate output:
- Does not default to REJECT on all outputs (SHIP should be the common path for acceptable work)
- Names the specific gap in FLAG and FAIL findings -- no generic "quality could be improved"
- Separates blocking from non-blocking criteria when the user has specified blocking ones
- The verdict follows directly from the criterion results; no unexplained overrides

## Source

Extracted from Nate Kadlac newsletter (2026-06-14) -- "Executive Briefing: Your company is about to get cheap intelligence. That is not the same as being able to use it." -- "review standards" as a harness layer: the non-outsourceable asset that turns cheap intelligence into trustworthy organizational work. Generalized into a standalone callable gate skill.
