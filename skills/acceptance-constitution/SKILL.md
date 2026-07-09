---
name: acceptance-constitution
description: "Author a testable acceptance constitution for any build: 10-14 criteria phrased as executable checks, then score every output round against them automatically. Use when the user says \"acceptance constitution\", \"testable criteria\", \"done-right spec\", \"quality constitution\", \"write the acceptance criteria\", \"what does done look like\", \"create a scoring rubric\", \"define done-right before we build\", or before starting any build where success criteria have not been written as runnable checks."
---

# Acceptance Constitution

Ad-hoc review asks "does this look right?" A constitution asks "does this pass 14 specific
checks?" The difference is authority: a constitution authored before the build becomes the
ground truth for every round of output, makes review mechanical rather than subjective, and
prevents the most common drift -- where "done" shifts to match whatever the team actually
produced. This skill authors the constitution once and scores every output against it automatically.

## Trigger

Use when the user says "acceptance constitution", "testable criteria", "done-right spec",
"quality constitution", "write the acceptance criteria", "what does done look like",
"create a scoring rubric", "define done-right before we build", or when starting a build
where the success criteria are currently informal or implicit.

---

## Phase 1: Scope the Build

Before writing any criteria, establish three things:

1. **What is being built?** (One sentence: the artifact type and its primary purpose.)

2. **Who receives it?** (The consumer: a user, a downstream agent, a file, a database, an API.)

3. **What failure modes would cause this build to be redone?** (Ask the user to name 2-3 specific
   outcomes that would trigger rejection. These become the seed for the constitution's criteria.)

If the user cannot name at least one concrete failure mode, the scope is not clear enough to
author a constitution. Surface this and clarify before proceeding.

---

## Phase 2: Author the Constitution

Produce 10-14 criteria. Each criterion must satisfy all four of these properties:

**1. Phrased as a positive assertion, not a vague quality:**
- Good: "Every route returns a response in under 2 seconds on a cold start."
- Not acceptable: "The application should be performant."

**2. Has a named check method:**
Each criterion includes one of three check types:
- `SHELL`: a shell command that exits 0 on pass (e.g., `axe-core --exit` or `wc -l < report.txt`)
- `FILE`: a file or directory that must exist and be non-empty
- `LLM`: a single yes/no question an LLM checks against the artifact (use only for criteria that
  cannot be expressed as a shell command or file check)

**3. Falsifiable -- a single counter-example would fail it:**
A criterion that cannot be falsified is not a criterion; it is a wish.

**4. Scoped to this build, not to all possible builds:**
Each criterion names the specific artifact, route, file, or behavior it covers.

Format each criterion as:

```
[N]. [Criterion text]
     Check: [SHELL / FILE / LLM]
     Command or question: [exact command, file path, or yes/no question]
     Failure example: [one concrete case where this criterion would fire]
```

After drafting, review the set for:
- **Coverage gaps**: list any failure mode named in Phase 1 that no criterion covers. Add criteria
  until all named failure modes are covered.
- **Overlap**: if two criteria would always pass or fail together, merge them into one.
- **Ceiling**: if the set exceeds 14 criteria, cut the weakest (criteria whose failure is already
  implied by another criterion).

---

## Phase 3: Scoring Pass

After each build round (each time new output is produced), run the constitution against the output.

For each criterion:
1. Run the check (shell command, file check, or LLM question).
2. Record: **PASS** or **FAIL**.
3. If FAIL: record one sentence of evidence (the exact error, the missing file, or the LLM answer).

Produce the score report:

```
## Constitution Score -- Round [N]
Artifact: [name or path]
Date: [YYYY-MM-DD]

Score: [N_pass] / [total] passing

| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | [text] | PASS | -- |
| 2 | [text] | FAIL | [one sentence] |
...

Blockers (must fix before next round):
- [criterion N]: [evidence]

Recommended priority order:
1. [the criterion whose fix unblocks the most other criteria]
2. ...
```

Do not proceed to the next build round while any FAIL is present, unless the user explicitly
decides to defer it (and records the deferral in the score report).

---

## Phase 4: Constitution Maintenance

A constitution can be wrong. When a criterion fires on output that appears correct, run the
appeals process (see `check-appeals-gate` if available) before treating the criterion as
authoritative. If the criterion is confirmed wrong, update it in the constitution and log the
correction:

```
## Constitution Amendment -- [YYYY-MM-DD]
Criterion [N] before: [old text]
Criterion [N] after: [new text]
Reason: [one sentence -- what the criterion got wrong and why]
```

The amendment log is part of the constitution document. It prevents the same incorrect criterion
from being re-introduced and accumulates evidence about which domains are hardest to specify.

---

## Verification

- [ ] Scope established: artifact type, consumer, and at least one named failure mode
- [ ] Every criterion is phrased as a positive assertion (not a vague quality)
- [ ] Every criterion names its check method (SHELL / FILE / LLM)
- [ ] Every criterion has one concrete failure example
- [ ] All failure modes named in Phase 1 are covered by at least one criterion
- [ ] Set is 10-14 criteria (trim or add to stay in range)
- [ ] Scoring pass produces a PASS/FAIL verdict for every criterion, not "approximately"
- [ ] Any FAIL has one sentence of evidence before next round begins

---

## Source

Extracted from Nate Kadlac newsletter (2026-07-08), idea #5 -- "The Constitution Institution":
"Define 'done-right' as 10-14 testable criteria, each phrased so a check can verify it, then
measure every round against it automatically. 'The prompt is a standard plus a way to check it.'
The Elsa build used a 14-point accessibility constitution and finished at 171/171 verbatim content
needles, axe-core 0 violations across every route in both themes, WCAG AAA body contrast."
Source URL: https://natesnewsletter.substack.com/p/trust-ai-agents
