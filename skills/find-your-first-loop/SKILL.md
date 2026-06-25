---
name: find-your-first-loop
description: Convert a recurring burden — the kind of repeating work that lives scattered across apps and inside your head — into a one-page Loop Spec an agent could carry. Conducts a one-question-at-a-time interview (or a quick-version pass if you're in a hurry). Outputs a structured LOOP SPEC with trigger, sources, memory, safe actions, human boundary, record, learning, and the "wakes up" hinge into a loop-of-loops. Use when you say "find my first loop", "help me spec an automation", "I keep doing X by hand", "what should I automate first", "/find-your-first-loop", or when you want to turn a recurring frustration into a concrete, buildable spec.
---

# Find Your First Loop

Turns a recurring burden into a one-page Loop Spec ready for an agent to carry. The skill does not build the loop — it names it precisely enough that building becomes straightforward.

A "loop" is a recurring responsibility with a trigger, sources it checks, memory it carries from last time, safe actions it can take, a boundary where it stops and asks you, and a record that makes the next pass smarter. Most people already run a dozen loops by hand. This skill surfaces one and specifies it.

## Trigger

Use when the user says "/find-your-first-loop", "find my first loop", "help me spec a loop", "what should I automate first", "I keep doing X by hand", "turn this into a loop", "help me think through an automation", or when a recurring frustration needs to become a buildable specification.

## Prerequisites

No prerequisites. This is the entry point — the user needs only a nagging recurring task, not any existing automation.

## Phase 1: Set the Frame

Open by explaining what a loop is in two or three sentences: a recurring responsibility with a trigger, sources it checks, memory it carries from last time, safe actions it can take, a boundary where it stops and asks you, and a record that makes the next pass smarter.

Then offer the quick-version escape hatch:

> If you're in a hurry, paste a description of your recurring burden and type "quick" — I'll skip the interview and fill the Loop Spec myself, clearly labeling every assumption so you can correct it.

Otherwise proceed to Phase 2.

## Phase 2: One-Question Interview (max 6 questions)

Interview the user ONE QUESTION AT A TIME. Never batch questions. Wait for each answer before asking the next. Cap at roughly six questions. Walk this spine in order:

**Q1.** What is one recurring thing you keep asking AI to help with, or keep doing by hand, that comes back again and again? (If they name several, ask them to list all — you will help pick the best candidate.)

**Q2.** What kicks it off? What is the trigger that tells you "this is happening again"?

**Q3.** Which places, apps, or documents do you keep checking when you do it? (email, calendar, a portal, a thread, a spreadsheet, etc.)

**Q4.** What do you carry in your head from last time — the context, the state, the "I already know this" — that you would lose if someone else did it cold?

**Q5 (the five quality questions — ask as one focused step or split if needed):**
- What could this safely do on its own?
- What should it always stop and ask you about?
- What record should it leave so there is a trail?
- How should it get smarter next time?
- And — most importantly — what OTHER recurring job in your life or work should know if something here changes?

## Phase 3: Candidate Ranking (when multiple loops surfaced in Q1)

If the user named several candidate burdens in Q1, before producing the spec, rank them and recommend ONE to build first. Use this bar: pick the one that is tedious enough to matter but safe enough to inspect — the most "loop-able" one (clear trigger, stable sources, mostly boring actions), NOT the highest-stakes one. Explain the pick in two or three sentences, then build the spec for that candidate only.

## Phase 4: Force Specificity

Before finalizing, review every answer. If any answer is vague ("I check a few things"), ask for the actual apps, the actual person, the actual document. Do not produce the spec until every field has a concrete, actionable answer.

## Phase 5: Output — Loop Spec

Produce a one-page LOOP SPEC with these labeled fields, each filled from the user's own answers:

```
LOOP NAME — a plain, specific name (e.g., "School Trip Prep Loop", "Weekly Sales Follow-up Loop").

TRIGGER — what starts it (a calendar event, an incoming email, a weekly schedule, a file landing).

SOURCES — the specific places it checks (name the actual apps, folders, URLs, or documents).

MEMORY — what it should remember from last time so the next pass does not start from zero.

SAFE ACTIONS — what it can do on its own without asking (drafting, formatting, summarizing, fetching).

HUMAN BOUNDARY — what it must stop and ask you before doing (drafts, not sends; suggests, not buys;
                  anything touching money, relationships, external messages, or hard-to-undo actions
                  defaults to "draft and ask").

RECORD — what trail it leaves (a log file, a summary note, a dated entry in a shared doc).

GETS SMARTER BY — how each run improves the next (updates a preferences list, extends a contacts
                   note, corrects a pattern from feedback).

WAKES UP — which other recurring job should be notified if something here changes (this is the hinge
            into a loop-of-loops — even a placeholder ("nothing yet") is a valid answer).
```

End with a section titled **SMALLEST VERSION YOU COULD RUN THIS WEEK**: strip the loop down to the one trigger, one source, and one safe action that would deliver real relief on a single run. The user should be able to start tiny rather than building the whole thing at once.

## Guardrails

- Only use information the user gives. Do not infer details about their life, family, job, or tools.
- Do not fabricate example sources, names, or events. If a detail is needed to fill a field, ask for it.
- When making assumptions in quick-version mode, label every assumption explicitly.
- Keep the human boundary honest: if an action touches money, a relationship, an external message, or anything hard to undo, default it to "draft and ask," not "do automatically."
- Stop at the spec. Do not write build instructions, code, or automation configuration. This skill names the loop; it does not build it. Hand building downstream.

## Source

Nate Jones newsletter (2026-06-24): "The Five Questions That Turn a Messy Task Into an AI Loop." Prompt 1 recovered verbatim from https://promptkit.natebjones.com/20260609_998_promptkit_1.
