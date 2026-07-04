---
name: responsibility-audit
description: Audit a product or agent specification against the 8 agentic-commerce responsibility layers (Identity, Authorization, Fraud, Payment credentials, Settlement, Refunds, Liability, CRM). Produces a per-layer gap report with a named owner (builder / merchant / operator / payments network) and a coverage status (owned / partial / missing / unclear) for each layer. Use when the user says "responsibility audit", "commerce layers", "agent commerce audit", "agentic trust audit", "who owns which layer", or wants to know if an agent product has thought through all commercial responsibility domains before it touches real money.
---

# Responsibility-Layer Audit

Audit any agent product, service spec, or technical design against the 8 commercial-responsibility layers that define whether an agent can safely handle real transactions. Most products that reach production have only addressed two or three layers -- this skill surfaces the gaps before they become incidents.

## When to Use

- Before an agent product accepts live payment authorizations
- When handing off an agent design to legal or finance for sign-off
- When reviewing a vendor product that will hold authorization on your behalf
- After a payment-related incident to identify which layer was under-built

## Inputs

1. A product or agent description (paste a spec, README, architecture doc, or use-case summary)
2. Optional: a named role context (are you the builder, merchant, operator, or payments network?)

## Phase 1: Parse the Spec

Read the provided spec and extract:
- What the agent does (scope of autonomous action)
- Whether the agent holds or requests payment credentials
- Whether the agent initiates or proxies transactions
- Who the human accountable party is (if stated)

If the spec is silent on any of these, note it as "unknown" -- silence is a finding.

## Phase 2: Score Each of the 8 Layers

For each layer, assign:
- **Status**: `owned` / `partial` / `missing` / `unclear`
- **Named owner**: `builder` / `merchant` / `operator` / `payments network` / `unassigned`
- **Evidence**: the specific sentence or section in the spec that supports the status, or "no evidence found"
- **Gap**: a one-line description of what is missing or ambiguous

### Layer 1: Identity
Does the spec define how the agent authenticates itself to counterparties? Is the agent's identity federated to a human owner, an independent legal entity, or per-task ephemeral credentials?

Questions to answer:
- Can a merchant or payment network verify who the agent is?
- Is there a revocation path if the agent identity is compromised?
- Is the agent identity stable across transactions (persistent) or per-session?

### Layer 2: Authorization
Does the spec define the scope of what the agent is authorized to do -- including dollar caps, category restrictions, and time limits?

Questions to answer:
- Is there an explicit authorization scope document (not just "the agent can buy things")?
- Does authorization require a human signature or can the agent self-authorize?
- Is there an escalation path when a transaction exceeds the authorized scope?

### Layer 3: Fraud
Does the spec address how fraud signals are generated and consumed for agent traffic?

Questions to answer:
- Agent traffic looks like fraud by default (clean headers, perfect retries, no jitter). Is this accounted for?
- Is there a mechanism to distinguish known-good agent callers from bad actors?
- Who is responsible for absorbing fraud losses -- builder, merchant, or payments network?

### Layer 4: Payment Credentials
Does the spec address how payment credentials (cards, wallet keys, stablecoin addresses) are stored, rotated, and protected?

Questions to answer:
- Are credentials scoped to the minimum required authorization scope?
- Is there a credential rotation policy?
- Are credentials stored in an HSM or equivalent, or are they in application memory?

### Layer 5: Settlement
Does the spec define how and when funds actually move -- and what happens when settlement fails?

Questions to answer:
- Is settlement synchronous (blocks the agent flow) or asynchronous (agent continues before funds confirm)?
- What is the retry policy for failed settlement?
- Who holds funds in escrow during the settlement window?

### Layer 6: Refunds
Does the spec define a refund path for agent-initiated purchases that the human did not intend or disputes?

Questions to answer:
- Can the agent initiate a refund, or must a human do it?
- Is there an audit trail sufficient to support a refund dispute?
- What is the SLA for refund processing?

### Layer 7: Liability
Does the spec assign liability for each failure mode -- unauthorized purchase, double charge, agent malfunction, merchant repudiation, chargeback?

Questions to answer:
- For each failure mode, is there a named liable party?
- Is liability assignment consistent with the agent's authorization scope?
- Does the spec reference any contractual or regulatory obligation?

### Layer 8: CRM
Does the spec address how agent "customers" are tracked, preferenced, and managed over time?

Questions to answer:
- Is the agent treated as a first-class customer entity (with preferences, history, lifecycle stage)?
- When the agent acts on behalf of a human, are those actions attributed back to the human in any CRM system?
- Is there a mechanism to notify the human customer of agent actions taken on their behalf?

## Phase 3: Coverage Summary

Produce a table:

```
RESPONSIBILITY-LAYER AUDIT
==========================
Product: <name or "unnamed spec">
Date: <today>

| Layer               | Status  | Owner       | Key Gap (if any)             |
|---------------------|---------|-------------|------------------------------|
| 1. Identity         | missing | unassigned  | No agent identity defined    |
| 2. Authorization    | partial | builder     | No dollar cap specified      |
| 3. Fraud            | missing | unassigned  | Agent traffic not addressed  |
| 4. Payment creds    | owned   | builder     |                              |
| 5. Settlement       | unclear | unassigned  | Sync vs async not specified  |
| 6. Refunds          | missing | unassigned  | No refund path described     |
| 7. Liability        | missing | unassigned  | No failure-mode assignment   |
| 8. CRM              | missing | unassigned  | Agent not a tracked entity   |

Layers fully owned: X / 8
Layers with gaps:   Y / 8
```

## Phase 4: Priority Recommendations

For each layer with status `missing` or `unclear`, generate one concrete recommendation:

```
[Layer N: <name>] -- Priority: HIGH / MED / LOW
Gap: <one sentence>
Recommendation: <specific action to close the gap>
Minimum viable version: <the smallest thing that moves this from missing to partial>
```

Sort by priority: Identity and Authorization first (highest blast radius), CRM last.

## Verification

- [ ] All 8 layers scored -- no layer silently skipped
- [ ] Every `owned` status has cited evidence from the spec
- [ ] Every `missing` status has at least one concrete recommendation
- [ ] No layer assigned to "unassigned" without a recommendation to assign it

## Source Attribution

Framework from Nate's Newsletter, 2026-05-12: "Agentic Commerce Is A Protocol War. Here's Who's Fighting."
8-layer commercial-responsibility decomposition for agent products.
