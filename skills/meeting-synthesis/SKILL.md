---
name: meeting-synthesis
description: Converts a raw meeting transcript or notes into a fixed-format artifact with decisions + owners, actions + owners, open questions, and an explicit said-vs-inferred boundary.
---

# Meeting Synthesis

Produces a standard meeting artifact from any raw input: transcript, notes, voice memo summary, or a brief verbal description. The fixed format ensures every reader gets the same four things: what was decided, what was assigned, what is still open, and which claims came directly from the meeting vs. what you inferred.

## Trigger

Use when the user says "synthesize this meeting", "write up that call", "meeting notes from [topic]", "clean up these notes", "what did we decide", or pastes a raw transcript and asks for a summary.

## Phase 1: Ingest

Accept input in any form:
- Pasted raw transcript (timestamped or plain)
- Bullet-point notes
- Voice memo transcript
- Verbal description: "We had a 30-min call with X about Y, we decided Z, A is on the hook for B"

If the input is a file path, read the file. If it is a URL to a recording transcript service, fetch it.

Ask one clarifying question only if the meeting participants are completely absent from the input: "Who were the participants and their roles?" If participants can be inferred, skip the question.

## Phase 2: Extract

Scan the input for four categories. Be strict about the said-vs-inferred line: something is "said" only if it appears verbatim or near-verbatim in the source. Everything else is "inferred."

### Decisions
- What was agreed, resolved, or confirmed
- Who made or ratified each decision (if stated)
- If a decision was provisional or conditional, note that explicitly

### Actions
- Each next step with a single owner
- Deadline if stated; "no deadline set" if absent
- If an action has no owner, mark it `[OWNER UNASSIGNED]` -- do not assign one by inference

### Open Questions
- Items explicitly tabled, deferred, or flagged as unresolved
- Questions raised but not answered
- Topics that generated disagreement without resolution

### Said vs. Inferred
- **Said:** appeared in the source, attributed to a specific speaker or agreed by the group
- **Inferred:** your reading of implication, tone, or context -- label these clearly

## Phase 3: Format

Produce the artifact in this exact structure:

```markdown
# [Topic] — Meeting Notes
**Date:** [date if known, else "not stated"]
**Participants:** [names/roles if known]
**Duration:** [if stated]

## Decisions
- [Decision] — Owner: [name or "not stated"]
- [Decision] — Owner: [name or "not stated"]

## Actions
| Action | Owner | Deadline |
|--------|-------|----------|
| [task] | [name] | [date or "none set"] |
| [task] | [OWNER UNASSIGNED] | [date or "none set"] |

## Open Questions
- [Question or tabled item]
- [Question or tabled item]

## Said vs. Inferred
**Said (direct from source):**
- [verbatim or near-verbatim claim, speaker if known]

**Inferred (my reading):**
- [implication or interpretation — mark clearly as inferred]
```

Do not pad sections. If there are no open questions, say "None identified." If there are no inferred items, say "None -- all claims traceable to source."

## Phase 4: Deliver

Output the formatted artifact. Then add a one-line meta note:

> _Synthesis confidence: High / Medium / Low — [reason if Medium or Low, e.g., "transcript was incomplete" or "several speakers unidentified"]_

If the user wants to save the artifact, write it to a path they specify -- default to `./meeting-notes-[YYYY-MM-DD].md` if they say "save it" without specifying a location.

## Notes

- The said-vs-inferred boundary is the core value of this skill. A meeting note that conflates direct statements with your interpretation is worse than no note, because it creates false attribution.
- `[OWNER UNASSIGNED]` is intentional -- surfacing ownership gaps is more useful than silently filling them in.
- This skill is appropriate for client-facing delivery. Keep language neutral; avoid editorializing about participants.

## Source

Extracted from Nate Kadlac newsletter (2026-06-12), idea 7 — Meeting Synthesis: "Fixed format: decisions+who, actions+owners, open questions, said-vs-inferred line."
