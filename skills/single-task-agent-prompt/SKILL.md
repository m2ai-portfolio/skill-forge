---
name: single-task-agent-prompt
description: "Generate a self-contained single-task execution contract for any agent: claim one task, do scoped work only, block with one question if stuck, leave a structured receipt and stop. Use when writing a new agent prompt, designing a scheduled loop that should process exactly one item per invocation, or hardening an existing agent prompt to prevent scope creep and silent failure. Trigger on: 'write me an agent prompt that processes one task at a time', 'how should my agent know when to stop', 'make my loop process one item then stop', 'I need an agent that claims a task and leaves a receipt', or any agent prompt design request where the unit of work is a single claimable task."
---

# single-task-agent-prompt — one task, one receipt, stop

A structured prompt template that gives an agent a complete execution contract for a
single task: how to claim it, what scope is allowed, when to ask for help, and how to
leave an auditable receipt when done.

## Purpose

Two failure modes ruin most agent loops:

1. **Scope creep** — the agent processes multiple tasks per run, corrupting state or
   racing other agents that share the same queue.
2. **Silent completion** — the agent finishes without emitting a receipt, leaving no
   trace for audit, resume, or hand-off to the next run.

This skill produces a prompt that prevents both. The result is a self-contained execution
contract the agent can follow without any follow-up instructions.

## Phase 1 — Gather the task shape

Ask (if not already stated):
1. Where does the agent find the task? (a directory of markdown files, a database table,
   an issue tracker, a message queue — one source)
2. What type of work does it do? (one sentence)
3. Where does the output land? (a file path, an API update, a status write-back)
4. What actions must never happen without explicit human approval?

Keep it to one short exchange. If any answer is unclear, ask that one question — do not
keep probing.

## Phase 2 — Generate the execution contract

Produce a prompt block using this template. Fill the bracketed placeholders with
answers from Phase 1:

```
## Agent execution contract

**Your job:** [one-sentence description of the task type]

**Step 1 — Find and claim one task**
Read [task source]. Find the oldest item with status [todo/unclaimed/your term].
Move it to [working/claimed/your term].
Emit: `AGENT CLAIMED — task: [id] — started [ISO timestamp]`

If no tasks are available:
Emit: `STATUS — queue empty` and stop. Do not invent work.

**Step 2 — Do scoped work only**
Complete exactly the work described in the claimed task. Do not process any other
item from the queue. Do not read, write, or modify anything outside of:
[scope boundary: named files, directories, or systems the task involves]

**Step 3 — Ask one question if blocked, then stop**
If you cannot complete the task without information you do not have:
1. Emit `AGENT BLOCKED — task: [id]`
2. Follow immediately with exactly ONE specific question. Not a list.
3. Update the task status to [blocked/pending-input/your term].
4. Stop. Do not guess. Do not continue past the blocker.

**Step 4 — Leave a receipt and stop**
When the task is done, emit:
  AGENT DONE — task: [id]
  What changed: [one line]
  Where: [file path, URL, or store key where the output landed]
  Checked: [what you verified before declaring done]
  Needs review: [what a human should inspect before treating this as shipped]

Update the task status to [done/complete/your term]. Stop.
Do not claim another task. The scheduler handles the next invocation.

**Never do these without explicit human approval:**
- Send, publish, deliver, or post to any external party
- Delete or overwrite source data
- Deploy to a live environment
- Modify credentials, billing, or access control
[add any task-specific constraints here]
```

## Phase 3 — Adapt for the target queue type

| Queue type | Adaptation notes |
|------------|-----------------|
| File directory | Replace `[task source]` with the dir path; `[working]` with `status: doing` in frontmatter |
| Relational database | Replace with the SELECT and UPDATE queries; include WHERE status = 'todo' ORDER BY created ASC LIMIT 1 |
| Issue tracker | Replace with the issue status transitions; note any API rate limits |
| Message queue | Add a visibility-timeout note — release the message if BLOCKED, do not acknowledge until DONE |
| Cron invocation | Note that the agent exits cleanly after emitting the receipt; the cron handles retries |

## Verification

Before finalizing the generated prompt, confirm:
- [ ] Exactly one task source named
- [ ] Scope boundary is explicit (what is and is not in scope)
- [ ] BLOCKED path asks one question, not multiple
- [ ] DONE receipt names where the output landed
- [ ] "Never without approval" list includes at least: send, publish, deploy, delete, credentials
- [ ] Prompt ends with a stop instruction

## Rules

- The prompt must be self-contained. The agent receiving it needs no follow-up context.
- BLOCKED asks exactly one question. Multiple questions mean the task itself needs
  decomposition before dispatch — surface that to the user rather than patching the prompt.
- The receipt is mandatory even for simple tasks. A task with no receipt is undocumented.

## Source

Nate's Newsletter, 2026-06-26 — "AI Agent Handoffs / Open Engine"
Pattern: 30-minute single-task execution contract for agent loops.
URL: https://natesnewsletter.substack.com/p/ai-agent-handoffs
