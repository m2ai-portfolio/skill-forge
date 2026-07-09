---
name: check-appeals-gate
description: Run an appeals arbitration when a verification check fails a worker -- determines whether the failure is "worker wrong" or "check wrong", and corrects the check if the gate itself is broken. Use when the user says "the check is wrong", "appeals gate", "false failure", "check arbitration", "the gate keeps failing", "bad rule", "fix the verification", "my check rejected good work", or after a CI gate fires on output you believe is actually correct.
---

# Check Appeals Gate

Verification gates are not infallible. When a check fails a worker, the correct response is
not always "fix the worker" -- sometimes the check is wrong. Without an appeals path, a broken
gate calcifies: workers route around it, teams add exceptions, and the verification layer loses
its authority. This skill runs a structured arbitration to distinguish "worker got it wrong" from
"check is wrong," and produces a corrected check when the gate was the problem.

## Trigger

Use when:
- A verification check has failed a worker's output and the output appears correct on manual review
- A check has fired the same false-positive pattern across multiple runs
- You want to correct a check rule without guessing -- you want evidence
- A self-healing loop has retried the same failure 2+ times with no improvement

---

## Phase 1: Collect the Evidence

Gather three artifacts:

1. **The failing check** -- the exact shell command, assertion, or LLM-scored criterion that fired.
   Include the exit code, stdout, and stderr from the failure.

2. **The worker output** -- the full artifact the check was evaluating. Do not summarize it;
   the arbitration reads the actual output.

3. **The original specification** -- what the check was intended to enforce. If no written spec
   exists, ask: "What property was this check trying to guarantee?"

If any of the three is missing, surface the gap before proceeding. Arbitrating without the actual
output or the check's intent produces a verdict that cannot be trusted.

---

## Phase 2: Classify the Failure Mode

Given the three artifacts, determine which of four failure modes applies:

| Mode | Description | Verdict |
|------|-------------|---------|
| **Worker wrong, check right** | The output genuinely violates the criterion the check enforces | SUSTAINED |
| **Check wrong: false floor** | The check enforces a floor (minimum length, count, presence) that is set too high for legitimate outputs | OVERTURNED -- lower the floor |
| **Check wrong: wrong criterion** | The check enforces a criterion that does not match the stated specification | OVERTURNED -- replace the criterion |
| **Check wrong: ambiguous scope** | The check fires on a case the original spec did not intend to cover | OVERTURNED -- narrow the scope |

State the mode explicitly. If the failure does not fit any of the four, describe the actual mode
before proceeding.

---

## Phase 3: Produce the Verdict

**If SUSTAINED:**

Return the failure output to the worker with the failure evidence injected as context:

```
APPEALS VERDICT: SUSTAINED
The check fired correctly. The output violates [criterion].
Evidence: [exact excerpt from output that failed the check]
Required: [what the output must contain or satisfy for this check to pass]
```

The worker retries with this context. The check does not change.

**If OVERTURNED:**

Produce a corrected check with all three components:

1. **Corrected check** -- the revised shell command, assertion, or scoring criterion. Must be
   runnable or directly substitutable for the old check.

2. **Rationale** -- one sentence: why the old check was wrong, citing the specific case that
   exposed the flaw. This becomes the incident record so the fix is not re-litigated.

3. **Regression test** -- one case that the old check would have rejected but the new check
   correctly accepts, and one case the new check should still reject. The corrected check must
   pass both.

```
APPEALS VERDICT: OVERTURNED
Mode: [failure mode]
Rationale: [one sentence, citing the specific case]

Old check:
[exact old check]

Corrected check:
[exact replacement]

Regression:
  ACCEPT case: [description] -- new check exits 0, old check exits 1
  REJECT case: [description] -- both checks exit 1
```

---

## Phase 4: Log the Correction

Append the verdict to the project's check log. If no check log exists, create one at the path
the user specifies. Format:

```
## [YYYY-MM-DD] Check Correction
Check: [name or short description]
Verdict: SUSTAINED | OVERTURNED
Mode: [failure mode, if overturned]
Corrected check: [new check, if overturned]
Rationale: [one sentence]
```

The log prevents the same bad check from being re-introduced and accumulates a record of which
checks have required correction -- a signal that a domain's verification strategy may need broader review.

---

## Verification

- [ ] All three evidence artifacts collected before arbitration starts
- [ ] Failure mode identified from the four-mode taxonomy (or named explicitly if novel)
- [ ] Verdict is exactly SUSTAINED or OVERTURNED -- no "it depends" verdicts
- [ ] If SUSTAINED: failure evidence and required fix returned to the worker
- [ ] If OVERTURNED: corrected check is directly substitutable (not a description of a check)
- [ ] If OVERTURNED: both regression cases are specified and verified against the new check
- [ ] Correction logged with rationale

---

## Source

Extracted from Nate Kadlac newsletter (2026-07-08), idea #6 -- "The Appeals Process Institution":
"When a check fails a worker, sometimes the check is wrong. Build a post-mortem that can
overturn a bad check, or the verification layer calcifies into gameable bureaucracy." The Elsa
build corrected 3 of its own checks via this mechanism, including an 800-character floor that
wrongly rejected legitimately short news posts.
Source URL: https://natesnewsletter.substack.com/p/trust-ai-agents
