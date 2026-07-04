---
name: grounded-draft
description: Draft a memo, brief, or proposal grounded exclusively in a curated source set — every factual claim carries an inline source ID, inferences are labeled, and unsupported claims are flagged rather than smoothed over.
---

# Grounded Draft

Produces AI-assisted written artifacts (memos, briefs, proposals, reports) where every assertion is traceable to a specific source in the project room. Combats the AI-slop failure mode where polished output rests on phantom or hallucinated citations.

## Trigger

Use when the user says "draft from my sources", "write a memo from the project room", "grounded draft", "citation-backed draft", "draft with sources", or hands you a set of documents and asks for a deliverable that must be factually grounded.

## Phase 1: Source Intake

Ask the user to provide:
1. **The source set** — file uploads, pasted text, or an inventory CSV from a project room
2. **The artifact type** — memo, brief, proposal, executive summary, report section, etc.
3. **The authority hierarchy** — which source wins when sources conflict (e.g., "current plan beats transcript beats old deck"). If the user doesn't specify, default to: most-recent-dated > longest > background
4. **The target audience and length** — who reads this and how long should it be?

If source set is absent, stop and ask. Do not draft from memory or inference alone.

Label each source `[SRC-1]`, `[SRC-2]`, etc. in the order provided. Confirm the list with the user before drafting.

## Phase 2: Authority Resolution

Before drafting, scan for conflicts:
- Find any fact, number, or decision that appears in more than one source with different values
- Apply the authority hierarchy to resolve each conflict
- Output a short conflict log:
  ```
  CONFLICT: Revenue figure
    SRC-2 says $4M (dated 2024-Q3 deck)
    SRC-1 says $5M (dated 2025-plan — AUTHORITATIVE)
    Resolved: $5M per authority hierarchy
  ```
- If a conflict cannot be resolved by hierarchy (e.g., same date, different data), flag it as a `[CONFLICT — REVIEW]` item in the draft and do not guess.

## Phase 3: Draft

Write the artifact following these citation rules:

| Case | Markup |
|------|--------|
| Fact directly supported by a source | `claim [SRC-N]` |
| Inference drawn from one or more sources | `claim [INFERENCE from SRC-N]` |
| Claim the room cannot support | `[UNSUPPORTED — source needed]` |
| Conflicting sources, unresolved | `[CONFLICT — REVIEW: SRC-N vs SRC-M]` |

Rules:
- Every factual sentence must carry at least one source tag
- Narrative transitions and structural language (e.g., "This memo outlines...") do not need tags
- Inferences must name the source(s) they are drawn from
- Do not smooth over gaps — flag them explicitly
- Do not fabricate plausible-sounding specifics (dates, numbers, names) without a source tag

## Phase 4: Unsupported-Claim Threshold Check

After drafting, count the `[UNSUPPORTED]` flags. If the count exceeds 3 (or a user-specified threshold):
- Do not deliver the draft silently
- Surface the list of unsupported claims and ask: "These claims can't be backed by your sources. Should I (a) remove them, (b) rephrase as open questions, or (c) proceed and flag for manual follow-up?"

## Phase 5: Output

Deliver:
1. **The artifact** — with inline citation markup
2. **Source legend** — `[SRC-N]: <source name or description>` for each source used
3. **Conflict log** — if any conflicts were found (even resolved ones)
4. **Unsupported list** — enumerated, with suggested resolution for each

## Verification

A good grounded draft:
- Has zero uncited factual assertions (every factual claim has a source tag)
- Has a source legend that maps every tag to a real provided source
- Does not hallucinate specifics (numbers, names, dates) without a source
- Flags rather than fills every gap
- The conflict log is present if any two sources disagreed, even if resolved

## Source

Extracted from Nate's Newsletter 2026-05-22 — "AI: Organize Files Before Writing" — idea #6: Grounded Draft from Clean Room.
