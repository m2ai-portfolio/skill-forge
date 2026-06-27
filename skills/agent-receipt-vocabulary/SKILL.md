---
name: agent-receipt-vocabulary
description: "Reference skill for the 11-label agent status grammar (AGENT CLAIMED, BLOCKED, UNBLOCKED, HUMAN HOLD, HUMAN ANSWERED, RESUMED, DONE, FAILED, APPLIED, FOLLOW-UP, STATUS). Use when designing or auditing agent output to ensure status updates are inspectable, cross-harness compatible, and carry enough context for a human or downstream agent to resume without re-reading the full run. Trigger when: writing an agent prompt that should emit receipts, reviewing agent output for traceability gaps, or asking 'what should my agent say when it finishes / gets blocked / hands off'."
---

# agent-receipt-vocabulary — 11-label status grammar for agent handoffs

A shared status vocabulary ensures that one agent's output is the next agent's claimable
input — with enough context to resume, audit, or escalate without human copy-paste.

## Purpose

Most agent loops leave no inspectable trace. The agent runs, something happens, and the
only record is the final output (if it arrived). When a run is handed off to a second
harness, or picked up after a session restart, the receiving agent has to re-read the
entire prior conversation to understand where work stands. The receipt vocabulary closes
this gap: a small set of labeled status events that any loop can emit so that any
downstream reader — human or agent — knows exactly what to do next.

## The 11 labels

| Label | When to emit | Minimum payload |
|-------|-------------|-----------------|
| `AGENT CLAIMED` | Task accepted; agent is beginning work | task id, timestamp |
| `BLOCKED` | Cannot continue without external input | what blocks it, one specific question (not a list) |
| `UNBLOCKED` | A prior BLOCKED resolved; ready to resume | what resolved it |
| `HUMAN HOLD` | Needs approval before a destructive or irreversible action | what action, why flagged |
| `HUMAN ANSWERED` | Human responded to a HUMAN HOLD | the decision |
| `RESUMED` | Restarting after BLOCKED or HUMAN HOLD resolved | what it will do next |
| `DONE` | Task complete | what changed, where it landed, what was checked, what needs review |
| `FAILED` | Could not complete; will not retry without intervention | reason, last state, what a human or next agent should do |
| `APPLIED` | A result has been applied (merged, deployed, written) | what, where |
| `FOLLOW-UP` | Task done but spawned a new task | what the new task is, who owns it |
| `STATUS` | Heartbeat or progress update mid-run | current step, percent complete if knowable |

## Emit patterns

### Minimal CLAIMED
```
AGENT CLAIMED — task: read-inbox-2026-06-26 — started 2026-06-26T14:00:00Z
```

### BLOCKED with one question
```
AGENT BLOCKED — task: draft-reply-to-alice
Blocker: sender's preferred tone is unknown.
Question: Should I use formal or casual tone in replies to Alice? (reply here to unblock)
```

### DONE with evidence
```
AGENT DONE — task: draft-reply-to-alice
What changed: reply drafted
Where: ./drafts/reply-alice-2026-06-26.md
Checked: grammar pass, no sensitive data in body
Needs review: human should approve before send
```

### FAILED with handoff context
```
AGENT FAILED — task: deploy-preview
Reason: upload step exited 1
Last state: compiled OK, upload failed at 14:23:00Z
Next step: fix upload credentials, then re-run from deploy step
```

### FOLLOW-UP spawning a new task
```
AGENT DONE — task: extract-action-items
What changed: 3 action items extracted from meeting notes
Where: ./action-items-2026-06-26.md
Needs review: assignees are guesses — confirm before distributing
FOLLOW-UP: task: send-action-items — owner: [human] — ready when review complete
```

## Integration checklist

When designing a new agent loop, confirm:

- [ ] Does the prompt instruct the agent to emit CLAIMED on start?
- [ ] Does BLOCKED include exactly one question (not a list)?
- [ ] Does DONE specify where the artifact landed (path, URL, or store key)?
- [ ] Does FAILED include enough context for the next agent to resume?
- [ ] Is every status event landing somewhere a human or downstream agent will read?

## Subset guidance

Not every loop needs all 11 labels. At minimum, every task loop should emit:
- `AGENT CLAIMED` — I started
- `DONE` or `FAILED` — I finished (and how)
- `BLOCKED` — I need help

Add `HUMAN HOLD` for any action with side effects (send, deploy, delete, billing).
Add `FOLLOW-UP` when a task is complete but spawns dependent work.
Add `STATUS` only for long-running tasks where silence would be alarming.

## Source

Nate's Newsletter, 2026-06-26 — "AI Agent Handoffs / Open Engine"
Pattern: receipt vocabulary as a minimum language of trust for cross-harness agent coordination.
URL: https://natesnewsletter.substack.com/p/ai-agent-handoffs
