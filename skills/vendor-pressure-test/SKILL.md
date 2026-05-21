---
name: vendor-pressure-test
description: Run a vendor pitch deck, RFP response, or internal proposal through the 7-row agent control-layer lens. Identifies which rows are answered, which are dodged, and what each dodge costs in production. Use when asked "pressure-test this vendor", "what is this pitch dodging", "evaluate this agent infrastructure proposal", "vendor control review", "/vendor-pressure-test".
---

# Vendor Pitch Pressure-Test

Applies the 7-row agent control-layer framework as a skeptic lens to vendor pitches, RFP responses, and internal proposals. Separates answers from dodges and prices each dodge in production risk.

## When to Invoke

Trigger on: "pressure-test this vendor", "what is this proposal dodging", "vendor control review", "evaluate this agent pitch", "RFP pressure test", "is this vendor pitch real", "/vendor-pressure-test".

## Inputs

Ask the user (skip any already answered):

1. **The artifact** — paste the pitch deck text, RFP response, proposal, or product page URL
2. **Procurement context** — what problem is this vendor claiming to solve? (runtime, data, identity, payments, observability, or "full-stack agent platform")
3. **Claimed rows** — which of the 7 control rows does the vendor claim to own? (let them state it before you probe)
4. **Deal stage** — early evaluation, shortlist, or contract-ready? (calibrates how hard to push)

## The 7-Row Pressure Test

For each row, apply three lenses: **What did they say? What did they dodge? What does the dodge cost?**

### Row 1 — Runtime

*Did they explain how the agent is paused, cancelled, or timed out mid-run?*

Red flags:
- "Reliable, scalable infrastructure" with no mention of pause/cancel API
- Timeout described only in terms of cost optimization, not safety
- No SLA on run termination latency

Dodge price: Runaway agent, stuck job, or infinite-loop LLM call that bills until someone notices.

### Row 2 — Governed Data

*Did they explain how data access is enforced at the storage layer?*

Red flags:
- "LLM-enforced" data access (prompt instruction, not policy)
- "We support RBAC" without specifying whether it applies to the agent credential or the human user credential
- Vague references to "data governance" without row-level or attribute-level specifics

Dodge price: Agent reads data it was "told" not to read. Prompt injection overrides the instruction.

### Row 3 — Identity / Principal

*Did they explain what credential the agent presents, how it is scoped, and how it is revoked?*

Red flags:
- "Secure by design" with no mention of credential scope
- Shared credentials across agents in the same tenant
- Revocation described as "contact support" or "redeploy the stack"

Dodge price: Compromised credential affects all agents in the tenant. Revocation takes hours or days.

### Row 4 — Action Authorization

*Did they describe an allow-list or policy layer that gates what the agent can write or call?*

Red flags:
- "Guardrails" that are LLM-evaluated, not policy-enforced
- "Customizable permissions" described only via UI toggle, not machine-readable policy
- No mention of who defines the allow-list and how it is audited

Dodge price: Agent calls APIs or writes data outside its intended scope. Discovered after the fact.

### Row 5 — Payment Authority

*If the vendor touches payments, did they describe spend caps enforced at the payment layer?*

Red flags:
- "Budget-aware agents" that read a budget from a config file (agent-controlled)
- No mention of a payment-layer freeze mechanism
- Spend cap described as a prompt constraint ("tell the agent its budget")

Dodge price: Agent exceeds budget. No hard stop. Discovered on the invoice.

If the vendor does not touch payments, note "Row 5: N/A — vendor does not own payment layer."

### Row 6 — Observability

*Did they describe logs that are queryable after the fact and include decision context?*

Red flags:
- "Full visibility" with screenshots of a dashboard but no mention of log retention or query API
- Logs described as real-time only (tail) with no historical query capability
- No cost-per-run metric visible in the demo
- "Trace" described but no mention of whether it captures tool-call inputs and outputs

Dodge price: Post-incident investigation is impossible. Cannot answer "what did the agent do at 2am."

### Row 7 — Kill Switch

*Did they describe a coordinated stop across all 5 kill layers?*

Red flags:
- "Just stop the container" (runtime-only kill, credential stays live)
- "Revoke the API key" (identity kill, but runtime and payment stay live)
- No mention of payment freeze
- "Kill switch" section in the pitch that describes a single-layer stop as complete

Dodge price: Stopping the runtime does not stop the credential from being used by a compromised copy. Stopping the credential does not freeze a payment in flight.

## Output Format

```
VENDOR PRESSURE TEST — [Vendor / Proposal Name]
Assessed: [date]
Context: [what they claim to solve]

| Row | Name | Their Claim | Dodge? | Dodge Price |
|-----|------|-------------|--------|-------------|
| 1 | Runtime | [quote or paraphrase] | YES / NO / PARTIAL | [risk if dodged] |
| 2 | Governed Data | … | … | … |
| 3 | Identity | … | … | … |
| 4 | Action Authorization | … | … | … |
| 5 | Payment Authority | … | … | … |
| 6 | Observability | … | … | … |
| 7 | Kill Switch | … | … | … |

ROWS ANSWERED: [N/7]
ROWS DODGED: [N] — [names]
HIGHEST-COST DODGE: Row [N] — [name] — [one-sentence risk]

PROCUREMENT VERDICT: PROCEED / PROCEED WITH CONDITIONS / REJECT
CONDITIONS (if any): [numbered list of must-answer questions before signing]
```

## Verification

A complete pressure test:
- Distinguishes LLM-enforced controls from policy-enforced controls for every row
- Does not accept "enterprise-grade" or "secure by design" as a row answer
- Produces a PROCUREMENT VERDICT with named conditions, not a vague "due diligence recommended"
- Is specific enough to be sent back to the vendor as a list of required clarifications

## Source Attribution

Technique derived from Nate's Newsletter (2026-05-20): "Seven questions decide whether your AI agent ships. Most teams can answer two." — the Vendor-Pitch Pressure-Test idea (#2), applying the 7-row control-layer as a skeptic lens to vendor claims.
