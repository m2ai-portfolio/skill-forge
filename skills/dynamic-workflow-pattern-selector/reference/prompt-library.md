# Dynamic Workflow Prompt Library

Companion reference for `dynamic-workflow-pattern-selector`. The SKILL.md answers "which pattern
is this task?" and carries a minimal template per pattern. This file is the long form: one full
prompt per pattern, one per common two-pattern stack, the keyword contract that actually routes
Claude Code into each shape, and the guardrail that breaks each pattern when it is dropped.

Source: 6 Dynamic Workflow Patterns from the Anthropic masterclass, via Mark Kashef,
"Master All 6 Claude Code Dynamic Workflows" (2026-06-03),
https://www.youtube.com/watch?v=g9b9G8dcS8Y

## How to use this file

1. Pick the pattern with the SKILL.md decision table.
2. Copy the template from here, not from memory. The keyword contract lines are load-bearing:
   Claude Code infers the workflow shape from those phrases, so paraphrasing them can silently
   produce a different shape than the one you chose.
3. Fill every `[slot]`. An unfilled slot is the single most common cause of a workflow that runs
   wide and returns nothing usable.
4. Keep the guardrail sentence. It is the line that prevents the failure mode the pattern exists
   to fix.
5. Log the run in the validation log at the bottom.

Token cost per workflow class is not repeated here. See `dynamic-workflow-orchestration`
(Token economics) before running anything at fan-out scale.

**Provenance is marked per template and it is not decoration.** `source example` means the shape
came from a worked example in the masterclass. `composed` means it was assembled from the pattern
rules and has not been run as written. Nothing in this file has a recorded field run yet, so treat
every template as a starting draft and record what actually happened in the validation log.

## Slot conventions

| Slot | Means | Bad fill | Good fill |
|------|-------|----------|-----------|
| `[corpus]` | The bounded set being worked over | "the codebase" | "every file under `src/billing/`" |
| `[item]` | One unit the classifier or generator sees | "stuff" | "one unread email" |
| `[slice unit]` | The axis that splits work into non-overlapping parts | "sections" | "one contract file" |
| `[rubric]` | Written criteria, ideally authored before the run | "quality" | "the 5 checks in `rubric.md`" |
| `[real source]` | The ground truth a skeptic checks against, not the draft | "the document" | "the linked primary source" |
| `[observable condition]` | A condition an outside observer can confirm | "until it's good" | "until a full pass adds no new findings" |
| `[output file]` | Where the result lands | "a summary" | "`findings.md`, one row per finding" |

## Keyword contract

Phrases that route the prompt into each shape. Keep at least the required ones verbatim.

| Pattern | Required phrases | Supporting phrases |
|---------|------------------|--------------------|
| Classify and Act | `spawn a classifier agent`, `routes it to` | `the classifier never acts`, `deduplicate against` |
| Fan Out and Synthesize | `fan out`, `one sub-agent per`, `barrier synthesize step` | `each in its own clean context`, `with the exact source path` |
| Adversarial Verification | `a separate agent that checks it against`, `adversarial` | `devil's advocate`, `return only the claims that failed` |
| Generate and Filter | `generator agent`, `judge agent`, `must be different agents` | `scores every option against` |
| Tournament | `tournament of pairwise comparisons`, `each head-to-head match is its own comparison agent` | `the deterministic loop holds the brackets` |
| Loop Until Done | `keep looping until`, `no fixed pass count` | `do not stop until`, `a fresh agent per attempt` |

---

# Single-pattern templates

## 1. Classify and Act

**Fixes:** wrong-handler contamination. The classifier quarantines before anything acts.
**Provenance:** source example (inbox triage).

**Template**

```
[Context: what this input stream is and why it is heterogeneous.]
Build a workflow that triages [input source] by spawning a classifier agent that reads each
[item] and routes it to a [category-A] handler, a [category-B] handler, or a [category-C] handler.
The classifier only labels and routes, it never acts on the item itself.
Deduplicate every item against [existing tracker] before any handler runs.
Each handler returns [expected output per category], and anything the classifier cannot label
with confidence goes to an [unclassified] bucket for me, not to a default handler.
```

**Worked example**

```
This is my support inbox for the week, roughly 200 messages, mixed quality.
Build a workflow that triages `inbox/2026-08/` by spawning a classifier agent that reads each
message and routes it to a bug handler, a refund handler, or a sales-lead handler.
The classifier only labels and routes, it never replies.
Deduplicate every message against the open tickets in `tickets.csv` before any handler runs.
Each handler returns a one-line summary plus the proposed next action, and anything the
classifier cannot label with confidence goes to an unclassified bucket for me, not to a
default handler.
```

**Guardrail:** name the unclassified bucket explicitly. Without it, low-confidence items get
swept into whichever handler is listed first, which is exactly the contamination the pattern
was chosen to prevent.

---

## 2. Fan Out and Synthesize

**Fixes:** agent laziness (15 tasks, 7 done) and goal drift, by giving each slice its own context
window and its own completion criteria.
**Provenance:** source example (data room / due diligence).

**Template**

```
[Context: what the corpus is and why it matters.]
Build a workflow that [goal] across [corpus] by fanning out one sub-agent per [slice unit],
each in its own clean context so [data class] never cross-contaminates between slices.
Every agent returns [structured output format] with the exact source path and line or page for
each finding, and an explicit "nothing found" if its slice is clean.
Then run a barrier synthesize step that waits for all of them to finish and merges their output
into [output file], where every claim links back to the file it came from.
Flag any [slice unit] an agent could not read rather than dropping it.
```

**Worked example**

```
This is the data room for a company we are acquiring, about 40 contracts.
Build a workflow that finds deal risk across `dataroom/contracts/` by fanning out one sub-agent
per contract file, each in its own clean context so terms from one contract never bleed into
another.
Every agent returns a table of findings (clause type, risk, severity) with the exact file path
and page for each, and an explicit "nothing found" if its contract is clean.
Then run a barrier synthesize step that waits for all of them to finish and merges their output
into `deal-risks.md`, grouped by risk type, where every claim links back to the contract it came
from. Flag any contract an agent could not read rather than dropping it.
```

**Guardrail:** require the explicit "nothing found" return. A silent agent and a clean slice look
identical in the merged output, and that is how a skipped slice gets reported as verified.

---

## 3. Adversarial Verification

**Fixes:** self-preference bias. A fresh skeptic per claim cannot be flattered by having written
the claim.
**Provenance:** source example (fact-checking a produced document).

**Template**

```
Use a workflow to verify [document or output] before I ship it.
Have one agent extract each [claim type] into its own item, with the sentence it came from.
Then for every claim, spin off a separate agent that checks it against [real source], not against
the document itself, and scores it against [rubric].
Return only the claims that failed, the exact reason each failed, the source that contradicts it,
and where the error most likely originated.
Do not rewrite anything. Report only.
```

**Worked example**

```
Use a workflow to verify `draft-post.md` before I publish it.
Have one agent extract each factual claim and each cited statistic into its own item, with the
sentence it came from.
Then for every claim, spin off a separate agent that checks it against the linked primary source,
not against the draft itself, and scores it against the 4 checks in `fact-rubric.md`.
Return only the claims that failed, the exact reason each failed, the source that contradicts it,
and where the error most likely originated (bad source, misread source, or invented).
Do not rewrite anything. Report only.
```

**Guardrail:** write the rubric before the run and point at it by path. A skeptic asked to invent
its own success criteria will invent criteria the draft already meets.

---

## 4. Generate and Filter

**Fixes:** self-preference bias in taste work. Overproduce with one agent, score with a different
one.
**Provenance:** source example (naming and title generation).

**Template**

```
Use a workflow to brainstorm [N] [option type] for [topic, audience, and constraint] with
generator agents, then hand the full set to a judge agent that scores every option against
[rubric], with a numeric score per criterion.
The generator that brainstorms and the judge that scores must be different agents, and the judge
must not see which generator produced which option.
Return the top [K] with their scores and the reason each ranked where it did, plus the highest
scoring option that I am most likely to reject and why.
```

**Worked example**

```
Use a workflow to brainstorm 200 YouTube titles for a video about dynamic workflow patterns,
aimed at working developers, no clickbait and no colons, with generator agents, then hand the
full set to a judge agent that scores every title against `title-rubric.md` (clarity, specificity,
curiosity gap, honesty), with a numeric score per criterion.
The generator that brainstorms and the judge that scores must be different agents, and the judge
must not see which generator produced which title.
Return the top 5 with their scores and the reason each ranked where it did, plus the highest
scoring title I am most likely to reject and why.
```

**Guardrail:** the different-agents sentence is the pattern. Drop it and the workflow degrades
into one agent grading its own homework, which is the failure this pattern exists to remove.
Going from 1,000 to 3 works, going from 10 to 3 does not, so keep N large.

---

## 5. Tournament

**Fixes:** ranking bias from accumulated context. Every match is a fresh window that sees two
candidates and nothing else.
**Provenance:** source example (resume screening).

**Template**

```
Use a workflow to rank every [item] in [corpus] for [goal] by running a tournament of pairwise
comparisons against [rubric], where each head-to-head match is its own comparison agent that sees
only the two candidates, and the deterministic loop holds the brackets so only the running order
stays in context.
[Round 1: criteria A. Round 2: criteria B. Final round: criteria C.]
Return the final ranking plus the match log: who beat whom, in which round, and the one-line
reason.
Note any match the agent called too close to separate rather than forcing a winner.
```

**Worked example**

```
Use a workflow to rank every resume in `applicants/` for the senior backend role by running a
tournament of pairwise comparisons against `hiring-rubric.md`, where each head-to-head match is
its own comparison agent that sees only the two resumes, and the deterministic loop holds the
brackets so only the running order stays in context.
Round 1: hard requirements only. Round 2: depth of relevant experience. Final round: fit with the
team's current gaps.
Return the final ranking plus the match log: who beat whom, in which round, and the one-line
reason. Note any match the agent called too close to separate rather than forcing a winner.
```

**Guardrail:** ask for the match log. Without the audit trail the tournament costs bracket-many
agent calls and returns a bare ordering you cannot defend, which a single ranking pass would have
produced for less.

---

## 6. Loop Until Done

**Fixes:** the fixed-count habit. The exit is a condition, not a number, so the work ends when the
outcome is reached rather than when the budget of passes runs out.
**Provenance:** source example (flaky test hunt).

**Template**

```
Build a workflow that [task], forming a theory each pass and adversarially testing it in its own
isolated work tree, with no fixed pass count and a fresh agent per attempt.
Keep looping until [observable condition].
After each pass, append what was tried and what it ruled out to [output file] so later passes do
not repeat earlier ones.
Stop and report if [failure condition, for example: three consecutive passes rule nothing new out].
/goal Do not stop until [observable condition].
```

**Worked example**

```
Build a workflow that finds why `test_checkout_retry` fails roughly 1 run in 50, forming a theory
each pass and adversarially testing it in its own isolated work tree, with no fixed pass count and
a fresh agent per attempt.
Keep looping until a run reproduces the failure with a captured stack trace and a named root cause.
After each pass, append the theory tried and what it ruled out to `flaky-log.md` so later passes do
not repeat earlier ones.
Stop and report if three consecutive passes rule nothing new out.
/goal Do not stop until the failure is reproduced with a captured stack trace.
```

**Guardrail:** always pair the exit condition with a stall condition. A loop with only a success
exit and no "nothing new is being learned" exit is an open-ended token burn, which is the No Orphan
Loops failure in workflow form.

---

# Two-pattern stack templates

Stacks compose in one prompt. You do not wire them by hand: including both keyword sets in the
right order is what produces the stacked shape.

## A. Fan Out then Adversarial Verification

**Use when:** you need broad coverage and you do not trust the findings, which is most audits and
most research.
**Order rule:** fan out first. There is nothing to verify until content exists.
**Provenance:** source example (the audit stack in SKILL.md), extended with the failure report.

```
Build a workflow that audits every [slice unit] under [corpus], fanning out one agent per
[slice unit] in its own clean context, each returning findings with the exact file and line.
Then, for every finding, spin off a separate agent that tries to refute it against the actual
[real source], not against the first agent's report.
Return only the confirmed findings, each with the file and line, plus a separate list of findings
that were refuted and why, so I can see what the first pass got wrong.
```

## B. Classify and Act then Fan Out and Synthesize

**Use when:** the corpus is mixed and only one category deserves the expensive deep pass.
**Order rule:** classify first, so fan-out spend goes only where it pays.
**Provenance:** composed.

```
Build a workflow that first spawns a classifier agent that reads each [item] in [corpus] and
labels it [category-A], [category-B], or [irrelevant], acting on nothing.
Then fan out one sub-agent per [category-A] item, each in its own clean context, to [deep analysis
goal], and have every agent return [structured output] with its source path.
Run a barrier synthesize step that merges only the [category-A] results into [output file], and
report the counts per category so I can see what was skipped and confirm the filter was right.
```

## C. Generate and Filter then Tournament

**Use when:** the option space is huge and you need an ordered top list, not just a shortlist.
**Order rule:** filter before the bracket. Pairwise comparison over the raw pool costs far more
agents than it is worth.
**Provenance:** composed from the SKILL.md stacking rule.

```
Use a workflow to brainstorm [N] [option type] for [topic] with generator agents, then hand them
all to a judge agent, different from the generators, that scores every option against [rubric] and
keeps the top [K].
Then run a tournament of pairwise comparisons over those [K], where each head-to-head match is its
own comparison agent judged on [final criterion] and the deterministic loop holds the brackets.
Return the final ordered [K] with the match log and the score each carried out of the filter stage.
```

## D. Loop Until Done wrapping Fan Out and Synthesize

**Use when:** one sweep is not trusted to be exhaustive and you want passes until a clean one.
**Order rule:** the loop is the outermost wrapper. A loop nested inside each slice has no global
exit and will not converge.
**Provenance:** source example (the audit-until-clean stack in SKILL.md).

```
Build a workflow that sweeps [corpus] for [target], fanning out one agent per [slice unit] each
pass, merging results in a barrier synthesize step into [output file].
Then loop the whole sweep with no fixed pass count, each pass seeded with what previous passes
already found so it looks for what they missed.
Keep looping until a full pass adds nothing new to [output file].
Stop and report if two consecutive passes add nothing and the coverage list still shows unread
[slice unit].
/goal Do not stop until a full clean pass finds nothing new.
```

## E. Loop Until Done wrapping Adversarial Verification

**Use when:** you are fixing what the red team finds and need the fixes re-verified, not just the
original draft.
**Order rule:** re-extract claims every pass. Verifying a stale claim list after an edit is how a
newly introduced error ships.
**Provenance:** composed.

```
Build a workflow that verifies and repairs [document] with no fixed pass count.
Each pass: one agent re-extracts every [claim type] from the current version of the document, then
a separate agent per claim checks it against [real source] and reports pass or fail with the reason.
Apply only the fixes for failed claims, changing nothing else, and record each fix in [output file].
Keep looping until a full verification pass returns zero failed claims.
Stop and report if the same claim fails three passes in a row.
```

## F. Generate and Filter then Adversarial Verification

**Use when:** the shortlist makes factual or legal claims, so taste scoring is not enough.
**Order rule:** verify only the survivors. Fact-checking all N generated options is the expensive
mistake this order avoids.
**Provenance:** composed.

```
Use a workflow to brainstorm [N] [option type] for [topic] with generator agents, then hand them
to a judge agent, different from the generators, that scores against [rubric] and keeps the top [K].
Then, for each of the [K] survivors, spin off a separate agent that checks every factual claim it
makes against [real source] and returns pass or fail per claim.
Return only survivors that pass every check, with their scores, and list separately any option that
scored well but failed verification so I can see what taste alone would have shipped.
```

---

# Anti-stacks

Combinations that look reasonable and reliably waste a run.

| Anti-stack | Why it fails | Do instead |
|------------|--------------|------------|
| Adversarial Verification before Fan Out | Nothing exists to verify, so skeptics invent scope | Fan out, then verify (stack A) |
| Tournament over the raw pool | Bracket cost scales with the pool, most matches are between two weak candidates | Filter to a shortlist first (stack C) |
| Generator also judging | Self-preference bias, the exact failure Generate and Filter removes | Different agents, stated in the prompt |
| Loop nested inside each fan-out slice | Each slice loops on its own with no global exit condition | Loop outermost (stack D) |
| Classify and Act after a handler already acted | Quarantine after contact is not quarantine | Classifier routes, never acts |
| "Run it 10 times" labelled Loop Until Done | A count is not a condition, it stops early or burns late | "Keep looping until [observable condition]" plus a stall exit |
| Fan Out over a corpus with overlapping slices | Duplicate findings inflate the merged result and look like corroboration | Make slices mutually exclusive, one agent per unit |

---

# Extending this library

Add a template when a pattern is used against a real task and the prompt survives contact. Keep
the same block shape: fixes, provenance, template, worked example, guardrail. Update the keyword
contract if a new phrase proves load-bearing, and record the run below.

A template's provenance moves from `composed` to `validated` only after a recorded run in this
log, with the outcome written down. Do not promote a template because it reads well.

## Validation log

| Template | Provenance | Last run | Outcome |
|----------|------------|----------|---------|
| 1. Classify and Act | source example | not yet run | |
| 2. Fan Out and Synthesize | source example | not yet run | |
| 3. Adversarial Verification | source example | not yet run | |
| 4. Generate and Filter | source example | not yet run | |
| 5. Tournament | source example | not yet run | |
| 6. Loop Until Done | source example | not yet run | |
| A. Fan Out then Adversarial | source example | not yet run | |
| B. Classify then Fan Out | composed | not yet run | |
| C. Generate and Filter then Tournament | composed | not yet run | |
| D. Loop wrapping Fan Out | source example | not yet run | |
| E. Loop wrapping Adversarial | composed | not yet run | |
| F. Generate and Filter then Adversarial | composed | not yet run | |
