---
name: loop-of-loops-mapper
description: For users already running 2 or more agent loops — interview for ripple effects between loops, apply a strict safety filter, and produce a connection map plus the single safest loop-of-loops to start. Use when the user says "/loop-of-loops-mapper", "my loops interact", "how do my agents relate", "map my loop dependencies", "find the safest loop to connect first", or "I want my loops to talk to each other".
---

# Loop-of-Loops Mapper

Takes a set of existing loops and finds the hidden connections between them — where one loop's output is another loop's trigger or input. Outputs a connection map and a recommended first loop-of-loops with an explicit blast-radius statement.

The hard constraint: some connections are too risky to automate. This skill applies a safety filter before any recommendation, refusing candidates that involve money, legal decisions, or unreviewed external messages.

## Prerequisites

- The user has at least 2 running loops (automated, semi-automated, or manually executed on a schedule)
- Each loop should be describable in one sentence (if not, run `/loop-spec-builder` first to define them)

## Trigger

Use when the user says:
- "/loop-of-loops-mapper", "map my loops", "how do my loops connect"
- "my loops interact", "loop dependencies", "find loop connections"
- "I want my loops to talk to each other", "safest loop to connect"
- "build a meta-loop", "find my loop-of-loops"

---

## Phase 1: Inventory Existing Loops

Ask the user to list their current loops. For each loop, collect:

1. **Name** — a short label (e.g., "Weekly digest", "New lead handler", "Inbox triage")
2. **Trigger** — what starts it
3. **Output** — what it produces or changes
4. **Frequency** — how often it runs

If the user has a Loop Spec (from `/loop-spec-builder`), accept it directly. If not, ask for the four fields above, one loop at a time.

Continue until all loops are listed. Ask "Is there another one?" after each entry.

---

## Phase 2: Connection Mapping

For each pair of loops, ask:

> "When [Loop A] finishes, does [Loop B] need to know about it? Could [Loop A]'s output trigger [Loop B], or does [Loop A] depend on [Loop B] having already run?"

Map the connections as a directed graph:

```
[Loop A] → outputs to → [Loop B]
[Loop B] → wakes up → [Loop C]
[Loop C] → depends on → [Loop A]
```

Surface these connection types:
- **Feed**: one loop's output is another's input
- **Wake**: one loop finishing is another's trigger
- **Depends on**: one loop needs another to have run first
- **Conflicts with**: two loops would act on the same resource simultaneously

---

## Phase 3: Safety Filter

Before recommending any connection, evaluate each candidate against the safety filter. **Refuse** any connection that involves:

- **Money** — the connection would trigger spending, invoicing, payments, or financial commitments without human review
- **Legal exposure** — contracts, compliance actions, terms changes, or regulated communications
- **Unreviewed external messages** — emails, posts, or messages sent to real people outside the system without a human drafting/approval step
- **Irreversible high-blast-radius actions** — deleting data, removing access, canceling subscriptions

For each refused candidate, state the refusal reason explicitly:
> "Loop A → Loop B is excluded: this connection would send an unreviewed message to a client. A human must review before any external communication."

---

## Phase 4: Recommend the First Loop-of-Loops

From the safe candidates, recommend ONE connection to start — the one with:
- The narrowest blast radius (fewest downstream effects if something goes wrong)
- The most observable record (easiest to audit)
- The clearest human boundary (the handoff point is unambiguous)

Output:

```markdown
## Recommended First Loop-of-Loops

**Connection**: [Loop A] → [Loop B]
**How it works**: When [Loop A] produces [output], it signals [Loop B] to start with [input].
**Blast radius**: If this connection misfires, [specific consequence] — recoverable by [specific recovery action].
**Human boundary**: The combined loop pauses at [specific point] and waits for [specific human action] before proceeding.
**Record**: Both loops log to [location]; the connection event is logged as [entry format].

---
## Full Connection Map

[Loop diagram from Phase 2]

---
## Excluded Connections (Safety Filter)

[List of refused connections with reasons]
```

---

## Verification

Before presenting the recommendation, confirm:
- [ ] The recommended connection has a blast-radius statement that names a specific recovery action
- [ ] The human boundary is at a named decision point, not "when something feels wrong"
- [ ] Every excluded connection has an explicit refusal reason
- [ ] The connection map shows all loops, not just the recommended pair

---

## Source

Derived from Nate Jones's "AI Loop Managers" framework and the "Find Your Loop-of-Loops" prompt kit (natesnewsletter.substack.com, 2026-06-24). The safety filter (money/legal/unreviewed-external-message refusal) and the blast-radius output format follow Nate's guardrails verbatim.
