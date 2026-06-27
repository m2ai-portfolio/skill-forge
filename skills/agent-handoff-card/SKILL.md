---
name: agent-handoff-card
description: "Generate a seven-part structured task card that can move work from one AI harness (or human) to another without losing context: Requester, Desired outcome, Sources, Acceptance criteria, Boundaries, Blocker rule, Receipt placeholder. Use when a task needs to cross a harness boundary (between different AI tools, different sessions, or human-to-agent handoffs) and the receiving party must be able to claim and complete it without asking follow-up questions. Trigger on: 'I need to hand this off to another agent', 'help me write a task card', 'format this for another AI to pick up', 'I want to package this work so someone else can run it', or any handoff where context must travel with the task."
---

# agent-handoff-card — seven-part cross-harness task record

A structured task card that packages work so that any agent or human — on any harness —
can claim and complete it without the original requester being present. The seven fields
are the minimum that make a task claimable: who asked, what success looks like, where the
source material lives, when it's done, what is off-limits, what blocks it, and where the
receipt lands.

## Purpose

When a task passes between agents or across sessions, context leaks at every seam:
- The source material that prompted the request is not attached.
- The acceptance criteria are implicit ("looks right to me").
- The requester's undocumented assumptions become the next agent's silent constraints.

The seven-part card makes these explicit before handoff, so the receiving party can run
the task without re-interviewing the requester.

## Phase 1 — Elicit the seven fields

Ask only what isn't already clear. If the user has provided most fields in their message,
fill in what you can and ask for the gaps in a single exchange.

1. **Requester** — Who is handing this off? (Name or role. Used for escalation and
   follow-up routing.)
2. **Desired outcome** — One sentence: what is the end state when this task is complete?
   Must be specific enough that an outside observer could verify it.
3. **Sources** — What input material does the agent need? List each item: document,
   file path, URL, database query, previous task output. If the source is ambiguous,
   name it explicitly rather than saying "the relevant files."
4. **Acceptance criteria** — What observable conditions define "done"? At least two.
   Prefer artifact-first criteria ("file X exists at path Y with field Z populated") over
   quality criteria ("looks complete").
5. **Boundaries** — What must the agent NOT do without explicit approval? Examples:
   send or publish to external parties, delete or overwrite source data, modify
   credentials or billing, take any action outside the named sources. Anything not
   listed here is implicitly in scope — be thorough.
6. **Blocker rule** — If the agent gets stuck, what is the single question it should ask?
   Frame it now, before dispatch. This forces the requester to pre-think the most likely
   failure mode. If you can't name a likely blocker, write "ask one specific question and
   stop — do not guess."
7. **Receipt** — Where should the agent leave its completion record? (A file path,
   a status update in a tracker, a message thread, a specific sink.) Also: who reviews
   the receipt before the task is considered shipped?

## Phase 2 — Generate the card

Produce the completed card in this format:

```markdown
## Task Card — [short task name]

**Requester:** [name or role]
**Created:** [date]

### Desired outcome
[One sentence. Observable end state.]

### Sources
- [Source 1 — type and location]
- [Source 2 — type and location]
(Add more as needed. Name each one. Do not use "the relevant files.")

### Acceptance criteria
- [ ] [Criterion 1 — artifact-first if possible]
- [ ] [Criterion 2]
(Minimum two. An outside observer must be able to verify each one.)

### Boundaries (must not do without approval)
- [Boundary 1]
- [Boundary 2]
(At minimum: no send/publish/deploy/delete/credential changes without approval.)

### Blocker rule
If you cannot proceed: [one specific question, or "ask one specific question and stop"].
Do not guess. Do not continue past the blocker.

### Receipt
Leave a completion record at: [path, URL, or tracker reference]
Format: DONE/FAILED with what changed, where it landed, what was checked, what needs review.
Reviewed by: [human name or role] before this task is considered shipped.
```

## Phase 3 — Delivery notes

- **Same harness, different session**: attach the card as the opening context of the
  new session. The receiving agent should emit `AGENT CLAIMED` on start.
- **Different harness** (e.g., Claude to a different tool): paste the card as the
  task description. Omit any harness-specific syntax — the card is vendor-neutral.
- **Human-to-agent**: the card IS the task prompt. The agent needs no additional briefing.
- **Agent-to-human**: use the card as a review checklist — the acceptance criteria become
  the review gates.

## Verification

Before handing off:
- [ ] Desired outcome is one sentence and observer-verifiable
- [ ] All sources are named explicitly (no "the relevant files")
- [ ] At least two acceptance criteria, both artifact-first where possible
- [ ] Boundaries list includes at minimum: send, publish, deploy, delete, credentials
- [ ] Blocker rule names one specific question (or the generic fallback)
- [ ] Receipt location is a real sink, not "somewhere"

## Rules

- The card must be self-contained. The receiver must be able to start without asking
  any follow-up questions.
- If the user cannot name a specific blocker question, that is a signal the task is
  not well enough defined for dispatch — help them sharpen it before generating the card.
- Acceptance criteria are not a style guide. "Well-written" is not a criterion. An
  artifact existing at a specific path IS a criterion.

## Source

Nate's Newsletter, 2026-06-26 — "AI Agent Handoffs / Open Engine"
Pattern: seven-part task record for cross-harness agent coordination.
URL: https://natesnewsletter.substack.com/p/ai-agent-handoffs
