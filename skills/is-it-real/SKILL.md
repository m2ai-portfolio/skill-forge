---
name: is-it-real
description: Adversarial audit of a completed agent task for "completion theater" — the gap between an agent that looks done and an agent that actually did the work. Given a task description and the agent's claimed output, apply five independent checks to surface fabricated completions, unfounded assumptions, and silent failures. Use after receiving autonomous agent output before acting on it, or as a post-dispatch gate in any pipeline that hands work to an unsupervised agent.
---

# is-it-real — Completion theater audit

**DO NOT** give the agent the benefit of the doubt. **DO NOT** accept "the output looks reasonable" as a pass. The job is adversarial: find the gap between claimed and actual.

## Purpose

Agents produce polished-looking output even when the underlying work didn't happen, happened incorrectly, or happened on the wrong thing. This pattern — "completion theater" — is distinct from hallucination. The agent may believe it succeeded. The output may be internally coherent. The claim may be technically true in a narrow sense. But the actual goal was not met.

Five failure modes recur:
1. **Fabricated artifacts** — files, records, or outputs the agent claims exist but don't
2. **Missing process evidence** — tests ran, commands executed, APIs called — but no proof
3. **Unresolved ambiguity passed as fact** — the agent made an assumption where a decision was needed, and didn't say so
4. **Stated-vs-observed gap** — the agent's narrative doesn't match the observable state
5. **No-op completion** — the agent did something, but not the thing that was asked

## Inputs

- **Task description**: what the agent was supposed to do (original goal/spec/brief)
- **Agent output**: the agent's response, completion message, or output artifact

If either is missing, ask for it before proceeding. Do not audit a completion without knowing the original task.

## Phase 1 — Inventory claims

Extract every verifiable claim from the agent's output. A verifiable claim is any statement that asserts:
- Something exists (a file, a record, a result)
- Something happened (a command ran, an API was called, a test passed)
- Something was decided or assumed (a value was used, a branch was taken)

List them as a numbered inventory. Do not evaluate yet — just inventory.

Example:
```
1. "Created report.md with three sections"
2. "All tests passed"
3. "Used the first matching record"
4. "API returned 200"
```

## Phase 2 — Apply five checks

For each claim in the inventory, assign a status: **VERIFIED**, **UNVERIFIED**, **SUSPICIOUS**, or **FAILED**.

### Check 1 — Artifact existence
For every artifact the agent claims to have created or modified: does it exist, at the stated path, with the stated content? If you have file access, check directly. If you don't, flag as UNVERIFIED and surface to the reviewer.

Failure signal: "I created X" but X doesn't exist, or exists with different content than claimed.

### Check 2 — Process evidence
For every action the agent claims to have taken (ran a command, called an API, executed a test): is there verbatim output, logs, or observable evidence? Narrative descriptions of what should have happened don't count.

Failure signal: "Tests passed" with no test output. "API returned 200" with no response body. "Ran linter with no errors" with no linter output.

### Check 3 — Assumption surfacing
Did the agent encounter a decision point where multiple interpretations were valid? Did it explicitly state which interpretation it used? An agent that silently picks an interpretation without surfacing the ambiguity is producing completion theater at the decision layer.

Failure signal: "Used the primary account" when multiple accounts existed and none was specified. "Defaulted to English" when language was unspecified and it mattered. Any "I assumed X" buried in the middle of a long output without a visible flag.

### Check 4 — Stated-vs-observed gap
Does the agent's narrative description of what it did match the observable state? Read the claimed sequence of actions. Does the sequence produce the claimed end state? Are there logical steps that would have had to happen but aren't mentioned?

Failure signal: "Migrated all records" but the record count is unchanged. "Sent the email" but no sent-mail evidence. "Merged the branch" but the branch still exists unmerged.

### Check 5 — Goal alignment
Did the agent complete the task that was actually asked, or a superficially similar task? This is the hardest check — it requires holding the original intent against the completed work.

Failure signal: "Created a summary" when the task was "extract the key decisions, not a summary." "Updated the config" for a different service than the one specified. "Fixed the failing test" by deleting it.

## Phase 3 — Render verdict

Produce a structured verdict:

```
VERDICT: [PASS | PASS_WITH_CAVEATS | FAIL]

CHECKS:
  Artifact existence:    [VERIFIED | UNVERIFIED | SUSPICIOUS | FAILED]
  Process evidence:      [VERIFIED | UNVERIFIED | SUSPICIOUS | FAILED]
  Assumption surfacing:  [VERIFIED | UNVERIFIED | SUSPICIOUS | FAILED]
  Stated-vs-observed:    [VERIFIED | UNVERIFIED | SUSPICIOUS | FAILED]
  Goal alignment:        [VERIFIED | UNVERIFIED | SUSPICIOUS | FAILED]

FINDINGS:
  [One line per SUSPICIOUS or FAILED check explaining the specific gap found]

RECOMMENDED ACTION:
  [ACCEPT | VERIFY_BEFORE_ACTING | RE-RUN | ESCALATE_TO_HUMAN]
```

Verdict rules:
- **PASS**: all five checks are VERIFIED or UNVERIFIED with no suspicious signals
- **PASS_WITH_CAVEATS**: at least one UNVERIFIED check, but no SUSPICIOUS or FAILED findings — safe to accept if the unverified items are independently checked
- **FAIL**: any SUSPICIOUS or FAILED finding

Recommended action rules:
- PASS → ACCEPT
- PASS_WITH_CAVEATS → VERIFY_BEFORE_ACTING (surface the specific unverified items)
- FAIL (single minor finding) → RE-RUN with a revised spec that closes the gap
- FAIL (goal alignment or multiple failures) → ESCALATE_TO_HUMAN

## Phase 4 — Closing the gap (optional, on request)

If the verdict is FAIL or PASS_WITH_CAVEATS, produce a revised task spec that addresses the specific gaps found. The revised spec should:
- Make previously ambiguous decisions explicit
- Add proof-of-completion requirements for every FAILED or UNVERIFIED check
- Name the specific failure mode so the next agent run has a forcing function

Do not produce a revised spec unless asked — the verdict is the primary output.

## Calibration note

This audit is adversarial by design. The prior is "completion theater until proven otherwise." If you find yourself accepting claims at face value because "it's probably fine" — that's the gap this skill exists to close. The point is not to block good work; it's to make the verification step explicit and mechanically reproducible rather than implicit and skipped.

## Source

Derived from Nate's Newsletter, 2026-06-10 — "Claude vs. Codex isn't about code. It's about whether you steer or dispatch." "Is it real?" audit framing and the completion-theater pattern as the core verification problem in autonomous agent workflows.
