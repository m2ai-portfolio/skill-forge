---
name: five-questions-loop-audit
description: Score an existing automation, cron job, scheduled task, or recurring agent against five quality questions — safe actions, human boundary, record, gets-smarter, and what-else-wakes-up — and produce a gap report with recommended fixes. Use when you say "/five-questions-loop-audit", "audit this automation", "score this loop", "is this cron well-designed", "check this agent for loop quality", or when you want to know which quality dimensions a running loop is missing before it silently fails.
---

# Five-Questions Loop Audit

Takes an existing automation, cron, scheduled task, or recurring agent and scores it against five quality dimensions. Produces a scorecard that surfaces missing guardrails before silent failures accumulate.

The five questions come from a single reframe: apps digitized individual tasks but left the wiring between them — remembering, checking, following up, noticing cross-effects — to humans. A well-designed loop closes that gap without creating new oversight burdens. The five questions are the diagnostic for whether it does.

## Trigger

Use when the user says "/five-questions-loop-audit", "audit this loop", "score this automation", "check this cron", "is this agent well-designed", "what dimensions is my loop missing", or when reviewing a scheduled task or recurring workflow for quality gaps.

## Prerequisites

The user must provide a description of an existing loop, automation, cron, or recurring agent. The description should include at minimum: what it does, how it is triggered, and what it produces.

## Phase 1: Collect the Loop Definition

Ask the user to describe the loop. Collect:

1. **Name / purpose:** What does this loop do? One sentence.
2. **Trigger:** What starts a run? (schedule, event, file arrival, message, manual invoke)
3. **Sources:** What does it read or check? (APIs, files, email, databases, calendars)
4. **Actions:** What does it actually do on each run? (generates, sends, writes, transforms, notifies)
5. **Output / sink:** Where does the result go? (file, notification, dashboard, another system)
6. **Any known guardrails:** Is there anything it is already prevented from doing?

If the user pastes a cron definition, a task spec, or a YAML/JSON config, parse it to fill these fields rather than asking.

## Phase 2: Score Against the Five Questions

For each question, assess PASS / PARTIAL / FAIL based on the loop definition. A dimension is PASS only if it is explicitly present — do not assume it is handled if it is not stated.

### Q1 — Safe Actions: What can this safely do on its own?

PASS: The loop definition explicitly lists actions it takes autonomously AND those actions are reversible or low-stakes (draft vs. send, read vs. write, suggest vs. execute).
PARTIAL: Some actions are safe but others are ambiguous or unstated.
FAIL: The loop takes irreversible or high-stakes actions without a stated human gate, or no action boundaries are defined at all.

### Q2 — Human Boundary: What must it always stop and ask about?

PASS: The loop has explicit stop conditions — named triggers that pause execution and request human approval before proceeding.
PARTIAL: There is an implied boundary but it is not stated or enforced mechanically.
FAIL: No human boundary is defined. The loop runs to completion regardless of what it encounters.

### Q3 — Record: What trail does it leave?

PASS: Every run produces a persistent record (log file, timestamped note, audit entry) that an observer could inspect after the fact.
PARTIAL: Some runs leave a record but it is ephemeral, incomplete, or inconsistently written.
FAIL: No record mechanism is defined. The loop runs and leaves no trace.

### Q4 — Gets Smarter: How does each run improve the next?

PASS: The loop explicitly reads from or writes to a memory artifact (preferences file, corrections log, notes) so later runs benefit from earlier ones.
PARTIAL: There is a vague or manual mechanism for improvement but it is not built into the loop itself.
FAIL: Every run starts from zero. The loop does not accumulate knowledge between passes.

### Q5 — Wakes Up: What other recurring job should know if something here changes?

PASS: The loop either notifies downstream loops/agents/humans when a significant change is detected, OR explicitly documents that it has no downstream dependencies ("nothing wakes up").
PARTIAL: Downstream dependencies exist but are implicit or undocumented.
FAIL: No consideration of cross-loop effects. The loop fires, produces output, and that is where its responsibility ends — no signal to anything downstream.

## Phase 3: Produce the Scorecard

```
FIVE-QUESTIONS LOOP AUDIT
Loop: [name]
Date: [date]

Q1 Safe Actions:      [PASS / PARTIAL / FAIL]
Q2 Human Boundary:    [PASS / PARTIAL / FAIL]
Q3 Record:            [PASS / PARTIAL / FAIL]
Q4 Gets Smarter:      [PASS / PARTIAL / FAIL]
Q5 Wakes Up:          [PASS / PARTIAL / FAIL]

Overall: [X/5 PASS, Y/5 PARTIAL, Z/5 FAIL]
```

For each PARTIAL or FAIL, provide:
- **Gap:** What is missing or insufficient.
- **Risk:** What goes wrong when this dimension is absent (silent accumulation, unrecoverable action, no audit trail, loop never improves, cascade blindness).
- **Fix:** A concrete, actionable recommendation (add a log file, define a stop condition, write a corrections note, emit an event when condition X occurs).

## Phase 4: Priority Order

After the scorecard, rank the PARTIAL/FAIL dimensions by urgency:

1. **Q2 (Human Boundary) failures** — most urgent. An unguarded loop acting on irreversible things is the highest-risk gap.
2. **Q3 (Record) failures** — second. No trail means no recovery path and no learning surface.
3. **Q1 (Safe Actions) failures** — third. Undefined action boundaries lead to unintended side effects.
4. **Q5 (Wakes Up) failures** — fourth. Cross-loop blindness causes cascading surprises at scale.
5. **Q4 (Gets Smarter) failures** — fifth. Important for long-running loops; less urgent for new ones.

## Notes

- A FAIL on Q2 (Human Boundary) does not mean the loop is wrong — it means the loop assumes human review happens outside its own boundary. Confirm this is true before flagging it as a gap.
- Q5 is the most commonly skipped dimension. "Nothing wakes up" is a valid answer and should be stated explicitly, not left implicit.
- This audit scores the loop as specified, not as imagined. If a guardrail is "assumed to be there," that is a PARTIAL, not a PASS.
- For loops that combine multiple agents or stages, audit each stage independently if they have different action classes.

## Source

Nate Jones newsletter (2026-06-24): "The Five Questions That Turn a Messy Task Into an AI Loop." The five quality dimensions (safe actions, human boundary, record, gets-smarter, wakes-up) are the spine of Nate's loop architecture framework.
