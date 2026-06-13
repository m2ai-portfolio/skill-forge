---
name: meeting-synthesis
description: Process a meeting transcript into a fixed-format structured summary with decisions (attributed), action items (owner + deadline), open questions, and a hard said-vs-inferred separator. Consistent output every time.
---

# Meeting Synthesis

Takes a meeting transcript and produces a structured summary in a fixed format. Every decision is attributed, every action item has an owner and deadline if stated, and a hard line separates what was explicitly said from what was inferred. Designed for immediate team distribution.

## Trigger

Use when the user says "synthesize this meeting", "summarize the transcript", "extract the decisions", "write up the meeting notes", "turn this call into action items", or when receiving transcript output from a transcription step.

## Phase 1: Input

Accept the transcript in any of these forms:
1. **Pasted text** — raw or timestamped transcript in the chat
2. **File path** — a `.md`, `.txt`, or `.vtt` file
3. **Chained from a transcription step** — `transcript.md` from a prior transcription pass

Ask if not provided:
- "Paste the transcript or give me the file path."
- "How long was the meeting and who attended? (optional — helps with attribution)"

## Phase 2: Extract Structure

Identify and extract four categories:

### Decisions

Statements that commit the group to a course of action, a priority, or a conclusion. Each decision must have an owner (who made or owns it) if attributable.

Signal phrases: "We agreed that...", "The decision is...", "Going forward we will...", "[Name] confirmed that...", "We're not doing..."

### Action Items

Specific tasks with an assignee. Extract: the task, the owner, and the deadline if mentioned. If no deadline was stated, mark as `(no deadline stated)`. Do not infer owners — only attribute what was explicitly said.

Signal phrases: "[Name] will...", "Action:", "By [date], [person] needs to...", "Can you [name]..."

### Open Questions

Issues explicitly left unresolved or deferred. Include who raised it if attributable.

Signal phrases: "We still need to figure out...", "TBD:", "Who's responsible for...", "That's unclear", "Let's come back to..."

### Inferred (flagged separately)

Conclusions or implications that are reasonable to infer but were not stated explicitly. These are always clearly labeled to prevent misattribution. Err on the side of putting something here rather than in Decisions.

## Phase 3: Format the Output

Produce the structured summary in this fixed format:

```markdown
# Meeting Summary — {date or topic}

**Attendees:** {names if known, or "unknown"}
**Duration:** {length if known, or "unknown"}

---

## Decisions

| Decision | Owner |
|----------|-------|
| {decision text} | {owner or "group"} |

---

## Action Items

| Task | Owner | Deadline |
|------|-------|----------|
| {task} | {owner} | {deadline or "none stated"} |

---

## Open Questions

- {question} *(raised by {name} if known)*

---

## Inferred (not explicitly stated)

> These items were not said directly but follow reasonably from the conversation.
> Verify before acting on them.

- {inferred conclusion or implied next step}

---

*Synthesized from transcript — {word count} words input, {N} decisions, {N} actions, {N} open questions.*
```

If there are no items in a section (e.g., no open questions), keep the section heading and write "(none)" — do not omit the section. Consistent structure matters more than brevity.

## Phase 4: Deliver

Output the formatted summary inline. Offer to:
- Save it to a file: `./meeting-{date}-summary.md` (or the path the user specifies)
- Send it as a draft if email or messaging tools are available in the session

## Calibration Notes

- **Attribution is sacred.** Do not move an inferred item into Decisions because it "seems obvious." The said-vs-inferred line exists precisely for this.
- **No fake owners.** If the transcript doesn't name who owns an action, write "unassigned" — do not guess from context.
- **Short meetings (under 20 min)** often have no formal decisions — that is expected; do not inflate.

## What This Does NOT Do

- Does not transcribe audio — use a transcription skill first if you have a recording.
- Does not guarantee correctness of attributed decisions — review the Inferred section carefully.
- Does not produce formal meeting minutes in legal or compliance formats.
- Does not send the summary — it produces the document; delivery is the user's step.

## Source

Extracted from Nate Kadlac newsletter (2026-06-12): "Grab my Ultimate Guide to Codex and catch up to the 1 in 1,600 people using it every week." Idea 7: "Fixed format: decisions+who, actions+owners, open questions, said-vs-inferred line." Category: Research and Thinking Skills.
