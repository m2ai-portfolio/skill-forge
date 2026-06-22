---
name: agent-owner-card
description: >
  Auto-draft an Agent Owner's Card from an existing agent's manifest, system prompt, logs, and config. Populates every field it can infer (name, purpose, data sources, tools, blast radius, last-reviewed date) and surfaces ownership questions only a human can answer. Use when you say "owner card", "draft ownership card", "agent owner", "who owns this agent", or want to make an agent visible and accountable before promoting it to production.
---

# Agent Owner's Card

Generate an Agent Owner's Card for any autonomous agent. The card makes an agent visible and
accountable: one page that captures what the agent does, what it touches, and who is responsible
for it. Populates every field it can read from config and logs; hands the ownership questions
only a human can answer back to the user for review.

Concept sourced from Nate's *AI Executive Briefing: "Your team is running agents nobody owns."*
The failure mode: ownerless agents keep emitting confident output while value silently drains
(stale context, drifted instructions, dead review loops) because nobody's name is on the door.

## When to Use

- Before promoting an agent from sandbox to shared/production use
- When onboarding a collaborator and they ask "what is this agent allowed to do?"
- During periodic governance review of a fleet of running agents
- When an agent's output starts to feel off and you want to establish a review baseline
- Any time you hear "nobody knows who owns this agent"

## Inputs

- Agent manifest or config file (e.g. `agent.yaml`, `agent.config.json`, `AGENT.md`)
- System prompt or CLAUDE.md that governs the agent's behavior
- Optional: recent logs or session output for the agent (used to infer blast radius)
- Optional: agent name or project path (defaults to cwd)

## Phases

### Phase 1 — Gather

Read every available artifact:

1. Config file: parse `name`, `description`, `tier`, `tools`, `mcpServers`, `maxTurns`, any
   explicit capability declarations.
2. System prompt / AGENT.md: extract stated purpose, scope restrictions, output targets, and
   any mention of escalation or review.
3. Logs (if available): identify data sources accessed, external services called, files written
   outside the project root, and any errors or escalations.

If an artifact is missing, note it as unverified; do not fabricate.

### Phase 2 — Populate the card (auto-filled fields)

Fill every field the artifacts confirm. Use `[UNVERIFIED — not found in artifacts]` for gaps.

```
AGENT OWNER'S CARD
==================
Agent name:          <from config.name>
Purpose:             <one sentence from description or system prompt>
Last reviewed:       <date from last git commit touching the config, else UNVERIFIED>

DATA SOURCES
  Reads:             <files, DBs, APIs the agent is configured to access>
  Writes:            <files, DBs, services it is configured to modify>
  External calls:    <MCP servers, API endpoints>

TOOLS
  Allowed tools:     <tool list from config>
  Blocked tools:     <explicit denies, if any>

BLAST RADIUS
  Max footprint:     <inferred from tools + write targets>
  Shared state:      <yes/no — does it write to resources other agents or humans depend on?>

BEHAVIOR BOUNDS
  Max turns/budget:  <from config>
  Escalation path:   <from system prompt, else UNVERIFIED>
  Review window:     <declared, else UNVERIFIED>

OWNERSHIP (→ HUMAN TO COMPLETE)
  Owner name:        ___________________________
  Owner role:        ___________________________
  Backup owner:      ___________________________
  Review cadence:    ___________________________
  Last reviewed by:  ___________________________
  Next review date:  ___________________________
  Escalation contact: __________________________
  Kill condition:    ___________________________
```

### Phase 3 — Surface ownership questions

After printing the card, present a numbered list of ownership questions the human must answer:

1. Who is the single named owner of this agent — not a team, one person?
2. What is the review cadence, and when was the last review?
3. Who is the backup owner when the primary is unavailable?
4. What is the kill condition — the specific state that means "stop this agent immediately"?
5. Does shared state it writes have any other consumers? Are those consumers aware?
6. If this agent drifts (wrong output, wrong scope), how will its owner know within 24 hours?

Remind the user: ownership questions the card cannot answer are exactly where agents fail silently.

### Phase 4 — Optional: register the card

If the user confirms ownership fields, offer to write the completed card to:

- `./OWNER.md` alongside the agent config
- A central registry path if one exists in the project

Do NOT write to any external or hardcoded path. Prompt the user for the output location if
registering.

## Verification

- Every auto-filled field must cite which artifact it came from (config, system prompt, logs).
- Any field left `UNVERIFIED` is a finding, not a gap to paper over.
- Ownership section must remain blank until the human fills it — never fabricate an owner.

## Source Attribution

Concept from Nate's Newsletter, 2026-06-21: *"Executive Briefing: Your team is running agents
nobody owns. The one-page card and two prompts that fix it."*
`https://natesnewsletter.substack.com/p/ai-agent-ownership`
Original card schema and verbatim prompts are paywalled (Executive Circle tier). This skill
implements M2AI's own schema informed by the section descriptions, not a copy of Nate's.
