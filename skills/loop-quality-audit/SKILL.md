---
name: loop-quality-audit
description: Audit any existing automation, cron job, or agent loop against five quality dimensions — safe actions, human boundary, record, gets-smarter, and what-else-wakes-up — and produce a scored gap report with remediation steps. Use when the user says "/loop-quality-audit", "audit my loop", "is my automation safe", "check my cron", "what's missing from this agent", or "review this loop against quality criteria".
---

# Loop Quality Audit

Takes any existing loop, automation, cron job, or agent workflow and audits it against five quality dimensions that distinguish a well-designed loop from one that runs silently into trouble.

The five questions come from Nate Jones's loop-manager framework. Each maps to a structural failure mode that shows up when automations are missing that dimension.

## Trigger

Use when the user says:
- "/loop-quality-audit", "audit my loop", "quality check my automation"
- "is my cron safe", "what's missing from this agent"
- "review this loop", "five questions audit", "loop quality check"
- "check my automation against quality criteria"
- When reviewing an existing automation before handing it to an agent or scheduling it unattended

---

## Phase 1: Gather the Loop Definition

Ask the user to describe the loop. Accept any of:
- A Loop Spec card (from `/loop-spec-builder`)
- A cron job definition with a plain-language description of what it does
- A workflow / automation spec
- A prose description: "Every morning I have a script that..."

If the description is thin, ask exactly three clarifying questions before proceeding:
1. "What does this loop produce or change when it runs?"
2. "What happens downstream when it finishes?"
3. "Who receives the output or is affected by the action?"

---

## Phase 2: Score Against Five Dimensions

Evaluate the loop against each dimension. Score each **Present / Partial / Missing**:

### Dimension 1 — Safe Actions
**Question**: Are the actions this loop takes autonomously narrow enough that they could be described in a checklist a stranger could follow without judgment calls?

- **Present**: The loop's action set is explicitly defined and bounded. An unexpected input causes the loop to halt and ask, not to improvise.
- **Partial**: Most actions are defined, but at least one action is described as "handle as appropriate" or similar.
- **Missing**: The loop is described in terms of outcomes, not actions. There is no definition of what it does vs. what it refuses to do.

**Failure mode when missing**: The loop takes increasingly creative actions as edge cases pile up, eventually doing something the designer didn't anticipate and can't explain.

### Dimension 2 — Human Boundary
**Question**: Is there a named point where the loop stops and waits for a human, rather than completing the cycle autonomously?

- **Present**: The boundary is explicit (e.g., "draft and send to human for approval before sending externally"). It names at least one category of action that always requires a human.
- **Partial**: A boundary exists but is defined vaguely (e.g., "escalate if unsure") with no specification of what triggers escalation.
- **Missing**: The loop is designed to run to completion in all cases. There is no described handoff point.

**Failure mode when missing**: The loop acts past the boundary the designer assumed was implied — typically at money, legal, relationships, or irreversible actions. The first sign is often a surprised stakeholder.

### Dimension 3 — Record
**Question**: Is there a verifiable trace of each run — something that exists on disk, in a log, or as a message — that would let you audit what the loop did without asking it to tell you?

- **Present**: Each run produces a log entry, file, or timestamped artifact that an observer can inspect independently of the loop itself.
- **Partial**: The loop reports success/failure, but the report is self-generated and contains no independently verifiable artifact.
- **Missing**: There is no described output beyond the primary action. You can only tell the loop ran by its side effects.

**Failure mode when missing**: Silent failures compound. The loop appears to be running fine (no errors) while silently skipping work, and you only find out weeks later when a downstream effect is missing.

### Dimension 4 — Gets Smarter
**Question**: Does the loop have a mechanism to improve between runs — a signal it reads that makes next week's run better than this week's?

- **Present**: There is a named feedback mechanism (e.g., a quality score, a rejection rate, a human rating field, a source freshness check).
- **Partial**: The loop is designed to accept corrections manually, but has no automated improvement signal.
- **Missing**: The loop is stateless across runs. It will produce the same output quality indefinitely, regardless of how many times it runs.

**Failure mode when missing**: The loop reaches a ceiling quickly. Early wins look good; later runs plateau as the static design stops fitting the evolving environment.

### Dimension 5 — What Else Wakes Up
**Question**: Is the loop's effect on downstream processes declared? Does it know when it triggers another loop, and is that documented?

- **Present**: The loop explicitly lists what it triggers, notifies, or writes to — and those dependencies are tested when the loop changes.
- **Partial**: The downstream effects are known informally but not documented or tested.
- **Missing**: The loop's downstream effects are undeclared. Other automations may depend on it without the loop designer knowing.

**Failure mode when missing**: Cascading silent failures. One loop changes behavior (or stops running), and three dependent automations break — none of which have the first loop in their dependency list.

---

## Phase 3: Gap Report

Produce a structured report:

```markdown
## Loop Quality Audit: [Loop Name]

| Dimension         | Score   | Gap |
|-------------------|---------|-----|
| Safe Actions      | [P/Pa/M] | [one-line gap description or "none"] |
| Human Boundary    | [P/Pa/M] | [one-line gap description or "none"] |
| Record            | [P/Pa/M] | [one-line gap description or "none"] |
| Gets Smarter      | [P/Pa/M] | [one-line gap description or "none"] |
| What Else Wakes Up| [P/Pa/M] | [one-line gap description or "none"] |

### Critical Gaps (Missing)
[List each Missing dimension with its failure mode and a specific remediation step]

### Partial Gaps
[List each Partial dimension with what would make it Present]

### Recommendation
[One sentence: is this loop ready to run unattended, should it run attended only, or should it be blocked until gaps are addressed?]
```

**Scoring key**: Present = loop is safe on this dimension. Partial = loop is improvable. Missing = loop has a structural gap that will cause a failure eventually.

---

## Verification

Confirm before presenting:
- [ ] All five dimensions are scored (none skipped)
- [ ] Every Missing dimension has a named failure mode AND a concrete remediation step
- [ ] The recommendation maps to the score: any Missing → cannot run unattended
- [ ] The report is based on what was described, not what a well-designed loop would do

---

## Related Skills

- `/loop-spec-builder` — build a Loop Spec for a new loop before running this audit
- `/classify-loop` — classify which operational loop type an agent is in (code-gen, operational, supervisory, autonomous) before scoping its audit

---

## Source

Derived from Nate Jones's "AI Loop Managers" framework (natesnewsletter.substack.com, 2026-06-24). The five quality dimensions (safe actions, human boundary, record, gets-smarter, what-else-wakes-up) are Nate's framework adapted into an audit rubric. The "Partial" scoring tier and the failure-mode descriptions are original additions.
