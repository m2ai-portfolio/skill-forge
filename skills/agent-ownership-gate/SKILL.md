---
name: agent-ownership-gate
description: >
  One-sentence triage gate: has this agent crossed from tool into owned-work? Evaluates three criteria — reads real files, drafts real messages, changes shared state — and names the most-likely accountable owner if so. Use before shipping any new agent or automation, or when you say "does this need an owner", "ownership test", "agent ownership gate", "tool or agent", or "does this need a human on the hook".
---

# Agent Ownership Gate

A fast creation-time gate that decides whether a new agent or automation requires a named human
owner before it ships. Runs three diagnostic checks and returns one of two verdicts:
**TOOL** (low-stakes, no ownership required) or **OWNED-WORK** (must name an owner, or do not ship).

Concept from Nate's *AI Agent Ownership* briefing: the moment an agent starts reading real files,
drafting real messages, or changing things others depend on, it stops being a tool and becomes
work that needs exactly one accountable human. Ownerless agents fail silently — confident, polished
output while value drains.

## When to Use

- Before deploying any new agent, scheduled task, or automation
- As a pre-creation check alongside the tool/skill/subagent triage decision
- When onboarding a client or team member who asks "do we need governance for this?"
- Any time you're about to wire an agent into a production pipeline and haven't named an owner

## Inputs

- Agent description (a sentence or a system prompt)
- Optional: existing config or tool list
- Optional: intent ("this agent will do X")

## The Three Checks

Run all three. A YES on any one check triggers OWNED-WORK verdict.

### Check 1 — Real files

> Does this agent read from or write to files that others depend on?

Criteria for YES:
- Reads files outside a sandboxed temp directory (config files, database files, shared repos, vault notes)
- Writes files that persist beyond the session (logs, reports, database rows, code changes)
- Modifies or deletes files created by another person or process

### Check 2 — Real messages

> Does this agent draft or send communications on behalf of a human?

Criteria for YES:
- Drafts emails, Slack messages, reports, or any external-facing text
- Posts to external services (GitHub PRs, social media, ticketing systems, APIs)
- Generates content others will read and act on without re-drafting from scratch

### Check 3 — Shared state

> Does this agent change resources that other agents, humans, or systems depend on?

Criteria for YES:
- Writes to a shared database, queue, or key-value store
- Updates configuration files used by downstream processes
- Creates or modifies scheduled tasks, cron entries, or hooks
- Any output that another automated system reads as input

## Output

```
AGENT OWNERSHIP GATE
====================
Agent: <name or description>

Check 1 — Real files:    YES / NO
Check 2 — Real messages: YES / NO
Check 3 — Shared state:  YES / NO

VERDICT: TOOL / OWNED-WORK

[If OWNED-WORK:]
Most-likely accountable owner: <role or person inferred from context>
Reasoning: <one sentence>

REQUIRED before shipping:
- Name one human owner (not a team, not "the AI team")
- Declare a review cadence
- Define a kill condition
- Run /agent-owner-card to draft the full ownership record
```

## Owner inference logic

If the verdict is OWNED-WORK, infer the most-likely owner from available context:

- If a specific person initiated the agent or is in the session: that person
- If the agent's outputs feed a specific team or product: the DRI for that product
- If unclear: flag "UNRESOLVED — owner must be named before shipping"

Never name a committee, team, or "the AI team" as the owner. The diagnostic value of this check
is forcing single-human accountability, not assigning it to a group.

## Verification

- Run this check before creating the config, not after. The gate is only useful pre-ship.
- If all three checks are NO and you are uncertain, prefer OWNED-WORK over TOOL. False-negative
  (shipping an unowned agent) costs more than a false-positive (adding ownership to a simple tool).

## Source Attribution

Concept from Nate's Newsletter, 2026-06-21: *"Executive Briefing: Your team is running agents
nobody owns. The one-page card and two prompts that fix it."*
`https://natesnewsletter.substack.com/p/ai-agent-ownership`
