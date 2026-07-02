---
name: agent-loop-receipt-designer
description: "Design the receipt trail, approval gate, and escalation policy for any agent loop — what events the agent emits, where receipts land, which steps require human sign-off before continuing, and how the loop escalates or halts on failure. Use when standing up a new agent loop that must be auditable, when retrofitting observability onto an existing loop, or when any step should block on human approval rather than auto-continue."
---

# agent-loop-receipt-designer

Produces a concrete receipt trail and approval gate design for a specific agent loop. The output is an implementation-ready spec, not general advice — it names the exact events, the exact sink, the exact gate trigger, and the exact escalation rule for the loop you describe.

The receipt trail answers "what happened and when." The approval gate answers "what the agent may not do without a human saying yes." Together they make a loop auditable and stoppable without having to read the entire run transcript.

## Trigger

Use when the user says "design a receipt trail for my agent", "how do I add an approval gate to this loop", "my agent runs silently and I can't tell what it did", "I want to know when my agent needs human sign-off", "add observability to this loop", "the agent should ask before sending", "make this loop auditable", or "Open Engine design for my workflow."

## Phase 1: Loop Description

Ask the user to describe the loop in one paragraph:
- What triggers the loop (a cron, an event, a human command)?
- What is the loop's primary action (send an email, file a ticket, update a record, call an API, write a file)?
- Who or what consumes the output (a human, a downstream system, another agent)?
- What does "done" look like (observable outcome)?
- What does "blocked" look like (the loop can't proceed without help)?

If the user provides an existing loop prompt or code, extract these from it directly.

## Phase 2: Event Inventory

Map the loop to a set of receipt events. Each event has:
- **Label** — a scannable status word in ALL CAPS (e.g., `CLAIMED`, `DONE`, `BLOCKED`, `HUMAN HOLD`)
- **Trigger condition** — the state change or outcome that fires this event
- **Payload** — the minimum data the receipt must carry to be useful to a downstream reader

### Standard event set (adapt for this loop)

| Label | When to emit | Minimum payload |
|---|---|---|
| `CLAIMED` | Loop starts processing an item | item ID, loop name, timestamp |
| `DRAFT READY` | Agent has produced output but not acted | item ID, draft content or path, confidence |
| `HUMAN HOLD` | Loop must pause for human approval | item ID, what needs approval, where to respond |
| `HUMAN ANSWERED` | Human responded to a HUMAN HOLD | item ID, decision (approved/rejected/modified), modifier |
| `RESUMED` | Loop continues after HUMAN ANSWERED | item ID |
| `DONE` | Loop completed the primary action successfully | item ID, action taken, observable proof (URL, file path, ticket ID) |
| `FAILED` | Loop could not complete after retries | item ID, error description, attempts count, next step |
| `BLOCKED` | Dependency unmet; loop cannot proceed | item ID, which dependency, escalation target |
| `APPLIED` | Output confirmed applied downstream | item ID, confirmed-by (system or human) |

Add or drop events based on the loop. A simple one-step loop may only need `CLAIMED`, `DONE`, and `FAILED`. A multi-step loop with side effects needs `DRAFT READY` + `HUMAN HOLD` + `HUMAN ANSWERED`.

## Phase 3: Approval Gate Design

For each action in the loop, classify it:

| Gate type | When to use | Agent behavior |
|---|---|---|
| **Auto** | Action is reversible, low blast radius, explicitly scoped | Agent proceeds without asking |
| **Ask-first** | Action is hard to reverse, involves external systems, or affects real users | Agent emits `DRAFT READY`, emits `HUMAN HOLD`, waits for `HUMAN ANSWERED` before acting |
| **Never** | Action is outside the loop's mandate entirely | Agent must emit `BLOCKED` and escalate; it may not take this action |

For each action in the user's loop, produce a gate classification and the rule that drives it. Example:

```
ACTION: Send email to client
  Gate:    Ask-first
  Rule:    Draft is complete → emit DRAFT READY with draft body
           Wait for human to respond with APPROVED or MODIFIED
           If APPROVED: send and emit DONE
           If MODIFIED: apply edits, re-present draft (one loop only), then send
           If no response in [N] hours: emit BLOCKED, escalate to [owner]
```

## Phase 4: Sink Design

The sink is where receipts land so a human or downstream system can read them without opening the agent's run transcript.

Choose one:

| Sink type | Best for | Format |
|---|---|---|
| **Append file** | Local loops, single user, auditability over visibility | One JSON object per line: `{"label": "DONE", "item": "...", "ts": "...", ...}` |
| **Structured log** | Existing logging infra, multi-instance loops | Standard log line with label as a field |
| **Task tracker entry** | Work that has a ticket/card (Linear, GitHub Issues, Notion) | Update the status field + append a comment with the receipt payload |
| **Webhook / callback URL** | Real-time notification, alerting | POST the receipt JSON to the URL |
| **Reply in thread** | Async human approval flows (email, chat) | Emit receipts as replies in the same thread where work was requested |

Recommend the sink that matches the loop's operating context. If the loop already has an existing notification channel, use it.

## Phase 5: Escalation Policy

Define what happens when the loop cannot complete:

```
ESCALATION POLICY for [loop name]:

If FAILED after [N] attempts:
  → emit BLOCKED with error description
  → notify [owner] via [sink]
  → do NOT retry until [owner] responds

If HUMAN HOLD unanswered after [T] hours:
  → re-notify [owner] via [sink]
  → if still unanswered after [T×2] hours: emit BLOCKED, halt loop

If dependency missing (BLOCKED):
  → emit BLOCKED with which dependency
  → notify [owner] once, do not repeat every run
  → resume only when [owner] signals dependency is resolved
```

Fill in `N` (retry count), `T` (timeout), and `owner` (a specific human or role, never left blank).

## Phase 6: Receipt Spec Output

Produce the complete spec in this format:

```
RECEIPT TRAIL SPEC — [loop name]

EVENTS:
  [Label]: [trigger] → [payload fields]
  ...

APPROVAL GATES:
  [action]: [Auto | Ask-first | Never]
    Rule: [one sentence]
  ...

SINK: [type] at [location / channel]
  Format: [JSON object | log line | tracker comment | ...]

ESCALATION:
  After [N] failures: [action]
  HUMAN HOLD timeout: [T] hours → [action]
  BLOCKED: notify [owner] via [sink], halt until resolved

KILL CONDITION:
  Loop halts permanently if: [condition that means the loop is no longer needed]
  Cleanup: [what to do with in-flight items when halted]
```

## Verification

The spec is complete when:
- Every action in the loop has a gate classification (Auto / Ask-first / Never)
- Every `HUMAN HOLD` has a timeout and a named escalation target
- The sink is a specific location, not "somewhere" or "a log"
- `FAILED` and `BLOCKED` both have a next step that does not involve the loop retrying indefinitely
- There is a KILL CONDITION so the loop can end cleanly

## Source

Nate Jones newsletter 2026-07-01: "You can build 80% of your own AI memory by talking to the agent already on your computer." Idea #3: Open Engine — task/status/approval/receipt/handoff layer. The five-part loop (Memory, Method, Boundary, Receipt, Judgment) maps to this skill's receipt trail + gate + escalation design.
