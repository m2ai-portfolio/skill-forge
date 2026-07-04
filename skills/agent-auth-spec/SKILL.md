---
name: agent-auth-spec
description: Generate a finance- and legal-accepted authorization specification for an autonomous agent -- covering scope of authority, dollar caps, evidence trail, revocation path, and escalation matrix. Use when the user says "auth spec", "agent authorization spec", "finance sign-off for agent", "legal agent auth", "authorization scope document", or needs to produce a document that tells a finance or legal team exactly what an agent is allowed to do before it touches money.
---

# Agent Authorization Spec Generator

Produce a structured authorization specification for an autonomous agent that finance and legal teams will actually sign off on. The output is a document (not a code review) designed to make the scope of agent authority visible, bounded, and revocable.

The core problem this addresses: authorization is not the same as payment. An agent that can "buy things" without an explicit authorization scope document is operating on implied authority -- which is the failure mode that causes payment products to be scaled back after launch.

## When to Use

- Before an agent product goes to legal or finance for approval
- When scoping a new agent feature that will initiate or proxy transactions
- When a finance team asks "what exactly can this agent do with our money?"
- As a pre-requisite before connecting an agent to a live payment rail

## Inputs

1. Agent description: what the agent does, in plain language
2. Transaction context: what kinds of purchases or authorizations the agent will make
3. Human principal: whose authority the agent is acting under
4. Optional: target market or regulatory geography (affects compliance section)

## Phase 1: Scope Elicitation

If the user has not provided the above inputs, ask for them in sequence:

1. "What does this agent do?" (free text)
2. "What types of transactions will it initiate? Give examples with approximate dollar amounts."
3. "Who is the human whose authority the agent is acting under?"
4. "What country or regulatory context does this operate in? (or: global/unknown)"

Do not proceed to Phase 2 until you have answers to 1-3.

## Phase 2: Draft the Authorization Specification

Produce a document with the following sections:

---

### AGENT AUTHORIZATION SPECIFICATION

**Agent Name**: [from input or "unnamed agent"]
**Version**: 1.0
**Date**: [today]
**Prepared by**: [user or "draft"]
**Status**: DRAFT -- not yet approved

---

#### 1. Agent Identity

State who or what the agent is:
- Legal/technical identity of the agent (software system operated by [builder])
- Human principal whose authority is delegated: [name / role / organization]
- Authorization delegation mechanism (API key, OAuth token, signed credential, etc.)

---

#### 2. Scope of Authority

State explicitly what the agent IS and IS NOT authorized to do:

**Authorized actions** (be specific):
- May initiate purchases of [category] up to $[cap] per transaction
- May initiate purchases up to $[cap] per [day/week/month]
- May purchase from [approved merchant categories or specific merchants]

**Explicitly out of scope** (required -- omitting this is a red flag):
- May NOT initiate refunds without human approval
- May NOT transfer funds between accounts
- May NOT increase its own authorization limits
- [add specifics from input]

---

#### 3. Dollar Caps and Limits

| Limit type         | Value       | Rationale                        |
|--------------------|-------------|----------------------------------|
| Per-transaction cap | $[amount]  | [brief justification]            |
| Daily cap           | $[amount]  | [brief justification]            |
| Monthly cap         | $[amount]  | [brief justification]            |
| Escalation threshold | $[amount] | Requires human approval above this |

If the user has not specified limits, recommend conservative defaults and flag them as placeholders requiring approval.

---

#### 4. Evidence Trail

State what evidence the agent must persist for each authorized action:

- Timestamp of authorization request
- Identity of requesting party (agent ID + human principal)
- Scope of authorization granted
- Transaction ID (once settlement occurs)
- Any scope limitations or conditions applied at time of authorization

Evidence must be queryable for a minimum of [12 months / 7 years for financial records -- flag if regulatory context is unknown].

Specify storage location and access controls.

---

#### 5. Revocation Path

State exactly how to revoke the agent's authorization:

**Immediate revocation** (takes effect within [SLA]):
- Step 1: [e.g., rotate the API key at [provider]]
- Step 2: [e.g., disable the agent service via [mechanism]]
- Step 3: [e.g., notify [payment network] of revocation]

**Graceful revocation** (allows in-flight transactions to complete):
- [describe process]

**Who can revoke**: [role/team -- be specific, not just "an admin"]

---

#### 6. Escalation Matrix

| Scenario                                  | Escalation action                        | Notified party           |
|-------------------------------------------|------------------------------------------|--------------------------|
| Transaction exceeds per-transaction cap   | Block and notify human principal         | [role]                   |
| Cumulative spend exceeds monthly cap      | Suspend and require re-authorization     | [role]                   |
| Suspected fraud signal received           | Suspend pending review                   | [role] + security team   |
| Agent identity verification fails        | Hard stop, alert immediately             | [role] + engineering     |
| Refund requested by human customer        | Pause agent, human handles refund        | [role]                   |

---

#### 7. Compliance Notes

[Fill based on regulatory geography input, or mark as "TBD -- regulatory review required"]

Common items to address:
- PCI-DSS scope: does the agent store, process, or transmit cardholder data?
- PSD2 / open banking requirements (if EU)
- AML/KYC: does the agent identity need to be registered?
- Record retention requirements

---

#### 8. Approval Signatures

| Role                  | Name | Signature | Date |
|-----------------------|------|-----------|------|
| Builder (technical)   |      |           |      |
| Finance approver      |      |           |      |
| Legal approver        |      |           |      |
| Human principal       |      |           |      |

---

## Phase 3: Review Flags

After generating the spec, flag any sections where the user's input was insufficient to produce a concrete answer:

```
REVIEW FLAGS
============
[Section N] -- PLACEHOLDER: [what is missing and who needs to provide it]
[Section N] -- ASSUMPTION: [what was assumed and why]
```

A spec with more than 3 placeholders is not ready for legal/finance review -- surface this explicitly.

## Verification

- [ ] All 8 sections present -- no section omitted
- [ ] Dollar caps are specific values, not "reasonable" or "appropriate"
- [ ] Revocation path names specific roles, not generic "admins"
- [ ] Escalation matrix covers at least 5 scenarios
- [ ] Review flags surfaced for any section requiring additional input

## Source Attribution

Framework from Nate's Newsletter, 2026-05-12: "Agentic Commerce Is A Protocol War. Here's Who's Fighting."
Named as the second prompt template for agentic-commerce product teams.
