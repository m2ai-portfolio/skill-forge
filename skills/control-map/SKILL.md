---
name: control-map
description: Walk an agent workflow through all 7 control-layer rows (runtime, governed data, identity/principal, action authorization, payment authority, observability, kill switch) and report which row fails first with a concrete remediation. Use when asked "is this agent safe to ship", "audit my agent workflow", "control layer review", "which control row does my agent fail", or "/control-map".
---

# Control-Map Assessment

Evaluates an agent workflow against the 7-row control-layer framework. Identifies which row fails first and what must be fixed before production.

## When to Invoke

Trigger on: "is this agent safe to ship", "audit my agent workflow", "control layer review", "fill in my control map", "what row does my agent fail", "agent infrastructure review", "/control-map".

## Inputs

Ask the user (skip any already answered):

1. **Workflow description** — what the agent does, what data it reads, what actions it takes, what external systems it calls
2. **Deployment target** — local dev, cloud (provider), or distributed/multi-region
3. **Sensitive data involved** — PII, financial records, health data, credentials, or none
4. **Human-in-the-loop** — is a human in the approval path for any action, or is the agent fully autonomous?
5. **Payment or spend authority** — can the agent initiate any financial transaction, charge a card, or commit spend?

## The 7-Row Control Map

Walk the workflow through each row in order. Report the first row that has no answer as the **blocking gap**. Continue through all rows to produce the full map.

### Row 1 — Runtime

*Can you pause or cancel the agent mid-run?*

Questions to answer:
- What process or service hosts the agent at runtime? (Lambda, container, cron, long-running process?)
- Is there a pause/cancel API, a TTY signal path, or a timeout that terminates the run?
- If the run hangs or loops, what stops it?

Pass condition: A concrete stop mechanism exists and has been tested at least once.

### Row 2 — Governed Data

*Does the agent only see data it is authorized to see?*

Questions to answer:
- What data sources does the agent query? (databases, APIs, file systems, vector stores)
- Are row-level or attribute-level policies enforced at the data layer, or only in the agent prompt?
- Can the agent exfiltrate data outside its declared scope?

Pass condition: Data access is enforced at the storage layer, not just by prompt instruction.

### Row 3 — Identity / Principal

*Does the agent have a stable, revocable identity that records what it acts as?*

Questions to answer:
- What credential does the agent present to external systems? (API key, service account, OAuth token)
- Is this credential scoped to least-privilege?
- Can you revoke it without redeploying the agent?
- Is there an audit trail of what the agent acted as?

Pass condition: Credential is scoped, revocable, and appears in audit logs.

### Row 4 — Action Authorization

*Is there a boundary on what the agent can do?*

Questions to answer:
- Does the agent have write access to any external system? (databases, APIs, file systems, queues)
- Is every write action gated by an explicit allow-list, or does the agent decide at runtime?
- Can the agent grant itself new permissions?

Pass condition: Writes are gated by an explicit allow-list defined outside the agent's own context.

### Row 5 — Payment Authority

*If the agent can spend money, is there a cap it cannot exceed?*

Questions to answer:
- Can the agent initiate any financial transaction, issue an API call that incurs cost, or trigger a billing event?
- Is there a spend cap enforced at the payment layer (not just in the prompt)?
- Who authorized the spend cap, and how is it adjusted?

Pass condition: If no spend authority → row passes automatically. If spend authority → a hard cap exists at the payment layer and has been tested.

### Row 6 — Observability

*Can you answer "what did the agent do and why" after the fact?*

Questions to answer:
- Are the agent's tool calls, inputs, and outputs logged?
- Are logs queryable (not just tailed in real time)?
- Is there a cost-per-run metric visible somewhere?
- Can you reconstruct a specific run's decision chain?

Pass condition: Logs exist, are queryable, and include enough context to reconstruct decisions.

### Row 7 — Kill Switch

*Can you stop the agent across all 5 layers simultaneously?*

The kill switch must work at all 5 layers — stopping only at the runtime layer leaves the other 4 active:

| Layer | Kill Action |
|---|---|
| 1. Runtime | Cancel/pause the running process or job |
| 2. Credential | Revoke the identity credential |
| 3. Gateway | Block tool-call routing (deny-list the agent's client ID) |
| 4. Payment | Freeze or revoke payment instrument or spend cap |
| 5. Workflow | Interrupt the orchestration graph (if an orchestrator is present) |

Pass condition: Each layer has a named person and a named mechanism. "I would email the team" is not a mechanism.

## Output Format

```
CONTROL MAP — [Agent / Workflow Name]
Assessed: [date]

| Row | Name | Status | Gap / Note |
|-----|------|--------|------------|
| 1 | Runtime | PASS / FAIL / PARTIAL | [detail] |
| 2 | Governed Data | PASS / FAIL / PARTIAL | [detail] |
| 3 | Identity | PASS / FAIL / PARTIAL | [detail] |
| 4 | Action Authorization | PASS / FAIL / PARTIAL | [detail] |
| 5 | Payment Authority | PASS / FAIL / N/A | [detail] |
| 6 | Observability | PASS / FAIL / PARTIAL | [detail] |
| 7 | Kill Switch | PASS / FAIL / PARTIAL | [detail] |

BLOCKING GAP: Row [N] — [name]
REMEDIATION: [concrete next action, not a suggestion]

SHIP VERDICT: READY / NOT READY — [one-sentence reason]
```

## Verification

A complete assessment:
- Answers all 7 rows, not just the obvious ones
- Does not accept "yes we have logging" — asks where and whether it is queryable
- Does not accept "we can always restart it" as a kill switch — requires all 5 layers
- Produces a SHIP VERDICT with a concrete READY or NOT READY decision

## Source Attribution

Technique derived from Nate's Newsletter (2026-05-20): "Seven questions decide whether your AI agent ships. Most teams can answer two." — the Control-Map Fill-In idea (#1), grounded in the 7-row control-layer framework for agent infrastructure readiness.
