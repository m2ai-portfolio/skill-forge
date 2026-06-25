---
name: loop-spec-builder
description: Run a guided one-question-at-a-time interview that converts any recurring burden into a one-page Loop Spec — a structured card defining the loop's trigger, sources, memory, safe actions, human boundary, record, learning mechanism, and wake-up conditions. Use when the user says "/loop-spec-builder", "help me define a loop", "I have a recurring task I want to automate", "turn this into an agent loop", "what would my loop look like", or "I keep doing X manually and want to hand it off".
---

# Loop Spec Builder

Turns a recurring manual burden into a complete, actionable Loop Spec through a structured one-question-at-a-time interview. The output is a one-page card that defines everything a loop needs to run safely without a human in the middle of every cycle.

## Trigger

Use when the user says:
- "/loop-spec-builder", "define a loop", "help me build a loop spec"
- "I have a recurring task I want to automate"
- "turn this into an agent loop", "what would my loop look like"
- "I keep doing X manually and want to hand it off"
- "I want to stop being the integration layer between these tools"

---

## Phase 1: Set the Stage

Tell the user:

> I'm going to interview you one question at a time to map out your loop. Answer as concretely as you can — specific is better than general. When you're done, I'll produce a one-page Loop Spec you can hand to an agent, a team member, or use as a design doc for automation. You can also say "quick" at any point to skip ahead to the minimum viable spec.

Ask: "What's the recurring thing you're doing? Describe it in one or two sentences — what you do, roughly how often, and what triggers you to do it."

---

## Phase 2: One Question at a Time

Ask exactly ONE question at a time. Wait for the answer before asking the next. Do not batch questions. Sequence:

1. **Trigger** — "What's the signal that kicks this off? Is it time-based (e.g., every Monday), event-based (e.g., a new email arrives), or something you notice manually?"

2. **Sources** — "What information do you gather to do this? List the tools, files, inboxes, or systems you check."

3. **Memory** — "What do you need to remember between runs? For example: what you saw last time, decisions you made, open items, thresholds crossed."

4. **Safe Actions** — "What actions can this loop take without you reviewing each one? Be specific — what's safe to automate, and what must stay in your hands?"

5. **Human Boundary** — "Where should the loop stop and hand control back to you? Think about money, relationships, legal exposure, irreversible actions, or weak sources."

6. **Record** — "How will you know the loop ran and what it did? What should it log or report so you can audit it?"

7. **Gets Smarter By** — "How could this loop improve over time? What feedback or signal would make next week's run better than this week's?"

8. **Wakes Up** — "Does completing this loop trigger anything else — another loop, a downstream process, a notification? List any known dependencies."

**Quick escape hatch**: If the user says "quick" or "minimum viable", skip to a compressed version: ask only Trigger, Safe Actions, and Human Boundary, then draft the spec with the rest marked as TBD.

**Smallest version this week**: After the full interview, ask: "What's the smallest version of this loop you could run manually once this week to prove the idea? Walk me through the steps you'd take."

---

## Phase 3: Produce the Loop Spec

Output a structured one-page Loop Spec card:

```markdown
## Loop Spec: [Loop Name]

**TRIGGER**: [what kicks the loop off]
**SOURCES**: [where information comes from]
**MEMORY**: [what persists between runs]
**SAFE ACTIONS**: [what the loop can do autonomously]
**HUMAN BOUNDARY**: [where the loop must stop and hand off]
**RECORD**: [what gets logged / how runs are audited]
**GETS SMARTER BY**: [feedback mechanism for improvement]
**WAKES UP**: [downstream loops or processes this triggers]

---
*Smallest manual version this week*: [one-sentence description of the pilot run]
*Missing information*: [any TBD fields with a note on how to fill them]
```

If any field is empty after the interview, mark it as TBD and explain why it matters before the loop can safely run.

---

## Verification

A complete Loop Spec satisfies these checks:
- [ ] TRIGGER is a specific observable signal, not "when I feel like it"
- [ ] SAFE ACTIONS list is narrow enough that a stranger could follow it without judgment calls
- [ ] HUMAN BOUNDARY names at least one category of action the loop must never take autonomously
- [ ] RECORD describes something verifiable (a file written, a message sent, a count logged) — not "it will report back"
- [ ] Every TBD field is flagged with a consequence: "Without this, the loop cannot run safely because..."

---

## Source

Derived from Nate Jones's "AI Loop Managers" framework and the "Find Your First Loop" prompt kit (natesnewsletter.substack.com, 2026-06-24). The Loop Spec schema (TRIGGER through WAKES UP) is Nate's structured output format, adapted for skill-based delivery.
