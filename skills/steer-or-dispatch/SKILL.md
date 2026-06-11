---
name: steer-or-dispatch
description: Score any knowledge-work task on three axes — reversibility, ambiguity, and verification cost — and return a clear routing recommendation: supervise this task live (steer) or hand it off to an autonomous agent with proof-of-completion requirements (dispatch). Use when deciding whether to run a task interactively or delegate it, or when sizing work for automation. Returns a recommendation, a one-line rationale, and minimum proof-of-completion requirements if dispatching.
---

# steer-or-dispatch — Task routing classifier

**DO NOT** default every task to dispatch because it feels more automated. **DO NOT** default every task to steer because it feels safer. The whole point of this classifier is to make the distinction explicit so you can apply the right level of supervision.

## Purpose

Two failure modes recur when working with autonomous agents: over-steering (watching tasks that run fine unsupervised, burning your attention) and over-dispatching (handing off tasks that require real-time judgment, then discovering the mess later). This skill draws the line before the work starts, not after.

The core insight: the cost of verification varies enormously by task. Some tasks are cheap to verify after the fact (run a test suite, check a file exists). Others are expensive or impossible to reverse if wrong (sent email, deleted data, made a billing decision). Steering is the right default when verification cost is high and ambiguity is unresolved.

## Input

A task description — one sentence to a paragraph. Can be free text, a goal statement, a mission, or a user story. No special format required.

## Step 1 — Score on three axes

For each axis, assign a score of 0 (low) or 1 (high):

### Axis 1: Reversibility (0 = reversible, 1 = hard to reverse)

Hard-to-reverse signals (score 1 if any apply):
- Sends an external message (email, Slack, notification, social post)
- Modifies production data or live configuration
- Deletes files, records, or resources
- Makes a billing, payment, or contract action
- Deploys to a live environment

Reversible signals (score 0 if all apply):
- Operates on draft state, local files, or a feature branch
- Creates or modifies artifacts the human can review before publishing
- Can be undone with a rollback, revert, or delete

### Axis 2: Ambiguity (0 = clear, 1 = ambiguous)

Ambiguous signals (score 1 if any apply):
- The success criteria are not measurable or are subject to judgment
- The task requires knowing context that isn't in the description
- There are multiple plausible interpretations of what "done" means
- The task depends on information that may or may not exist

Clear signals (score 0 if all apply):
- Success criteria can be stated as observable outcomes (file exists, test passes, value captured)
- The task description is self-contained — no missing context
- "Done" has only one reasonable interpretation

### Axis 3: Verification Cost (0 = cheap to verify, 1 = expensive or impossible to verify)

Expensive/impossible signals (score 1 if any apply):
- You cannot check the output without domain expertise or subjective judgment
- The task's effects accumulate silently (e.g., rate limit usage, downstream side effects)
- Correct output looks identical to plausible-but-wrong output
- Verification requires running something downstream that has its own side effects

Cheap signals (score 0 if all apply):
- You can verify mechanically: file exists, test passes, command exit code, count matches
- A second agent can verify without additional context
- Verification is faster than re-doing the task

## Step 2 — Route

Sum the three scores (0–3):

| Score | Route | Rationale |
|-------|-------|-----------|
| 0 | **DISPATCH** | Low risk, clear, cheap to verify — ideal for autonomous execution |
| 1 | **DISPATCH with elevated proof** | One risk dimension elevated — require stronger proof-of-completion |
| 2 | **STEER** | Two risk dimensions elevated — supervise to catch issues in real time |
| 3 | **STEER** | All three dimensions elevated — do not dispatch |

**Override rule**: If the task touches auth, money, production data deletion, or external communication, force **STEER** regardless of total score. These categories carry tail risk that the axes don't fully capture.

## Step 3 — Output

Produce exactly this structure (plain text, no preamble):

```
ROUTE: [STEER | DISPATCH]
RATIONALE: [One sentence. Which axes scored 1 and why.]
PROOF REQUIRED (dispatch only):
  - [Concrete, observable proof item 1]
  - [Concrete, observable proof item 2]
  - [Concrete, observable proof item 3 if needed]
ESCALATION CONDITION (dispatch only): [When the agent should stop and ask rather than proceed]
```

For STEER outputs, omit the PROOF REQUIRED and ESCALATION CONDITION lines.

Do not include a preamble, a scoring table, or axis explanations in the output. The user asked for a routing decision, not an explanation of how you arrived at it. If they want to see the scoring, they can ask.

## When the task is composite

If the input contains multiple tasks (e.g., "Search Gmail, write a report, then send it"), classify each component separately and return the overall route as the most restrictive individual route. A single high-risk sub-task makes the whole sequence STEER.

## Proof-of-completion requirements

When the route is DISPATCH, the proof requirements must be:

- **Observable by a third party** — not "the agent reports success," but "the file exists at path X" or "the test suite passed with output Y"
- **Mechanical to check** — automatable, not requiring subjective review
- **Specific to this task** — not generic boilerplate ("task completed successfully" is not proof)

Weak proof (do not emit these):
- "Confirm the task was completed"
- "Review the output"
- "Agent reported no errors"

Strong proof examples:
- "File `report-2026-06-11.md` exists and contains section headers matching the brief"
- "All tests in `tests/` pass with exit code 0"
- "API call returned HTTP 200 and response body contains field `id`"
- "Git diff shows exactly the two files specified in the task as modified, with no other changes"

## Relationship to adjacent skills

If routing to DISPATCH, a structured delegation brief (see `dispatch-handoff-brief`) is the natural next step — it wraps the proof requirements into a complete handoff document the agent can receive.

## Source

Derived from Nate's Newsletter, 2026-06-10 — "Claude vs. Codex isn't about code. It's about whether you steer or dispatch." Steer-or-dispatch framing and the verification-cost axis as the primary dispatch gate.
