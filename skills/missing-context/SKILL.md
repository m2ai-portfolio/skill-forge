---
name: missing-context
description: Scan a project room's inventory and working brief to produce three actionable gap lists — explicitly missing inputs, ambiguous references, and dangerous unsupported claims. Outputs a human-action queue, never a guess.
---

# Missing-Context List Generator

Attacks the AI-slop failure mode before it happens: surfaces what the source set cannot support so the human (not the model) decides how to fill the gaps. Produces three distinct lists — each with a different urgency level — rather than a single undifferentiated "things are missing" warning.

## Trigger

Use when the user says "what am I missing", "check my sources for gaps", "missing context audit", "what can't the AI answer from these files", "run the gap check", or presents an inventory + working brief and asks whether the room is draft-ready.

## Phase 1: Intake

Ask the user to provide:
1. **Source inventory** — the list of source files (names, dates, types) in the project room, ideally with brief per-source summaries. An inventory CSV from `/project-room-init` works directly.
2. **Working brief** — the document describing what the final artifact must accomplish: key questions to answer, claims to support, decisions to recommend, or sections to populate.

If either is absent, stop and ask. Do not run the gap analysis on a single input alone — both inventory and brief are required.

## Phase 2: Cross-Reference

For each key claim, question, or decision in the working brief:
- Search the inventory for a source that directly addresses it
- If found: mark it as COVERED with the source ID
- If partially found: mark PARTIAL with the source ID and the gap
- If absent: mark MISSING

Do not invent bridging assumptions. Do not rephrase the brief to make gaps disappear.

## Phase 3: Output — Three Lists

### List A — Explicitly Missing Inputs
Items the brief requires but no source addresses at all.

```
MISSING: Q3 revenue actuals
  → Brief requires: "current-quarter revenue for the financial section"
  → No source in inventory contains Q3 actuals
  → Human action: obtain Q3 actuals from finance team
```

### List B — Ambiguous References
Items the brief or sources reference that cannot be resolved from the room.

```
AMBIGUOUS: "the prior agreement" (brief §2)
  → Brief says: "per the prior agreement, the vendor will..."
  → No document titled "agreement" or "contract" is in the inventory
  → Human action: locate the agreement and add it to the room, or clarify the reference
```

### List C — Dangerous Gaps
Claims in the brief that depend on a source the room does not contain. These are the highest-risk items — they would cause the draft to silently fabricate.

```
DANGEROUS: Revenue growth claim
  → Brief: "we grew 40% YoY"
  → Room has last year's actuals (SRC-3) but no this-year actuals
  → A draft would invent or extrapolate this number
  → Human action: provide this-year actuals before drafting
```

All three lists must be present in the output, even if empty. An empty list is `[NONE — room is complete for this category]`.

## Phase 4: Priority Queue

After the three lists, produce a consolidated action queue sorted by impact:

```
## Human Action Queue

HIGH (blocks drafting):
1. [Dangerous gap item]
2. [Explicitly missing item on a critical claim]

MEDIUM (produces partial draft):
3. [Explicitly missing item on a secondary claim]

LOW (polish only):
4. [Ambiguous reference that can be footnoted]
```

## Phase 5: Room-Readiness Verdict

Close with a single verdict:

- **DRAFT-READY** — no HIGH items; proceed to drafting
- **CONDITIONALLY READY** — only MEDIUM/LOW items; can draft with flags, human must review gaps before finalizing
- **NOT READY** — at least one HIGH item; do not draft until resolved

## Verification

A good missing-context run:
- Produces all three lists (A, B, C) even if some are empty
- Contains no invented gap-fillers — gaps are stated, not papered over
- The action queue is ordered by impact (HIGH before LOW)
- The verdict matches the contents of the lists (DRAFT-READY only if no HIGH items)
- Every item in the queue maps back to a specific list entry

## Source

Extracted from Nate's Newsletter 2026-05-22 — "AI: Organize Files Before Writing" — idea #5: Missing-Context List Generator.
