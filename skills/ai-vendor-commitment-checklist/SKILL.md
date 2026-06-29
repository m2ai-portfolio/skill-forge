---
name: ai-vendor-commitment-checklist
description: Walk an executive through the questions to settle before committing to an AI agent vendor or deepening dependence on one. Produces a scored pre-commitment brief with identified gaps and negotiation leverage points. Use before signing a contract, expanding usage, or integrating a vendor's agent product into a core workflow.
---

# AI Vendor Commitment Checklist

Guides an executive or technical lead through seven questions to answer before committing to an AI agent vendor. Surfaces gaps, quantifies lock-in risk, and identifies negotiating leverage before the commitment is made.

This is a pre-commitment diagnostic. It requires no vendor material -- the user answers from their own knowledge of the vendor. If they cannot answer a question, that gap is itself a finding.

Note: this skill is for **pre-commitment evaluation** (before you have received or signed anything). To stress-test a vendor pitch or RFP response you have already received, use a vendor pressure-test skill instead.

## Trigger

Use when the user says "/ai-vendor-commitment-checklist", "questions before choosing an agent vendor", "AI vendor due diligence", "what should I ask an AI vendor before signing", "vendor commitment checklist", "pre-commitment AI audit", "should we commit to this vendor", or is about to sign a contract or expand usage with an agent AI provider.

## Phase 1: Intake

Ask the user:
1. **Which vendor** are you evaluating or already using?
2. **What is the commitment level?** (Pilot / Contract / Expanding usage to production / Core infrastructure)
3. **What is the data type** the agent will handle? (Public / Internal / Sensitive / Regulated)
4. **Who is the audience** for this checklist output? (Technical lead / Exec / Legal / All three)

Use these answers to calibrate which questions deserve the most attention and how to frame the output.

## Phase 2: The Seven Questions

For each question: rate the vendor as CLEAR / VAGUE / UNKNOWN, note what the user knows, and flag the commitment risk.

### Q1: Can you cancel a running agent task?
Does the vendor provide a documented API or UI control to stop an in-flight agent job before it completes?

- **CLEAR**: Stop/cancel endpoint is documented. You have tested it.
- **VAGUE**: The vendor mentions "managed infrastructure" but no specific stop control.
- **UNKNOWN**: You have not asked; the docs do not address it.

Risk if VAGUE/UNKNOWN: A runaway agent with write access cannot be halted without killing the entire service or revoking credentials manually.

### Q2: Is agent data access scoped, not broad?
Does the vendor enforce per-agent data scoping? Can you limit what data one agent can access, independent of other agents or the service account?

- **CLEAR**: Per-agent data scoping is documented and configurable.
- **VAGUE**: Vendor claims "enterprise security" or "RBAC" but does not describe per-agent scope.
- **UNKNOWN**: You do not know whether the agent runs on shared credentials or its own scoped identity.

Risk if VAGUE/UNKNOWN: A compromised or misbehaving agent has access to everything the service account can reach.

### Q3: Does each agent have an independently revocable identity?
Can you revoke one agent's access without disrupting other agents or the broader service?

- **CLEAR**: Each agent runs under its own machine identity (API key, service account, OAuth scope) that can be revoked individually.
- **VAGUE**: Vendor talks about "agent management" but credentials appear shared at the service level.
- **UNKNOWN**: You have not investigated the credential model.

Risk if VAGUE/UNKNOWN: Revoking access to one misbehaving agent takes down all of them, or you cannot revoke at all without canceling the contract.

### Q4: Can you export your context and memory today?
If you downloaded everything the agent knows and has been told today, would you have a complete, portable dataset?

- **CLEAR**: Export API is documented. You have run it. Output is in a standard format (JSON, Markdown, plain text).
- **VAGUE**: Vendor mentions "data portability" but the export path is not tested.
- **UNKNOWN**: You have not asked and there is no documented export.

Risk if VAGUE/UNKNOWN: Switching vendors means rebuilding all accumulated context from scratch. Your investment in configuring the agent is non-transferable.

### Q5: Where are your standing instructions stored?
Are the agent's system prompts, skills, and standing rules in a repo you own, or only inside the vendor's product?

- **CLEAR**: All standing instructions are in version-controlled files your team owns. The vendor is just the runner.
- **VAGUE**: Some instructions are in repo; others were configured directly in the vendor's UI.
- **UNKNOWN**: Instructions were set up inside the vendor's product and have never been exported.

Risk if VAGUE/UNKNOWN: No audit trail, no rollback, no diff. If the vendor changes behavior or you lose access, you cannot reproduce the agent's prior configuration.

### Q6: What happens to your data when you stop paying?
Does the vendor's contract specify data deletion timelines, export windows, and what "deleted" means?

- **CLEAR**: Contract specifies: data export window after cancellation (minimum 30 days), deletion timeline and method (e.g. NIST 800-88 wipe), what logs/training derivatives are retained.
- **VAGUE**: Vendor says "we take data privacy seriously" without contractual specifics.
- **UNKNOWN**: You have not read the data processing agreement or it does not address this.

Risk if VAGUE/UNKNOWN: After cancellation, your data may persist in the vendor's infrastructure indefinitely, including in fine-tuning datasets.

### Q7: Can you replicate this workflow on a different model today?
If this vendor raised prices 3x tomorrow, how long would it take to run the same workflow on a different provider?

- **CLEAR**: Instructions are model-agnostic, integrations use standard APIs, context is in a portable format. Switching is a config change measured in hours.
- **VAGUE**: Some parts would transfer, others are tied to vendor-specific behaviors or integrations.
- **UNKNOWN**: You have never evaluated portability; the workflow has only ever run on this vendor.

Risk if VAGUE/UNKNOWN: You have no negotiating leverage. Price increases and terms changes must be accepted or the workflow is disrupted.

## Phase 3: Commitment Score

```
Pre-Commitment Score: X/14 (2 points per CLEAR, 1 per VAGUE, 0 per UNKNOWN)

| Question | Rating | Gap Summary |
|----------|--------|-------------|
| Q1: Cancel running task | CLEAR/VAGUE/UNKNOWN | ... |
| Q2: Per-agent data scoping | ... | ... |
| Q3: Independently revocable identity | ... | ... |
| Q4: Context/memory export | ... | ... |
| Q5: Repo-backed instructions | ... | ... |
| Q6: Post-cancellation data policy | ... | ... |
| Q7: Workflow portability | ... | ... |

Commitment risk: [Low / Moderate / High / Do Not Commit Yet]
```

Thresholds:
- **Low risk (12-14)**: Proceed. You have visibility into what you're buying.
- **Moderate risk (8-11)**: Proceed with negotiation on the VAGUE/UNKNOWN items before signing.
- **High risk (4-7)**: Surface the gaps to legal and technical leadership before any contract expansion.
- **Do Not Commit Yet (0-3)**: Significant unknowns. Ask for documented answers on all UNKNOWN items before further evaluation.

## Phase 4: Negotiation Leverage Points

For each VAGUE or UNKNOWN answer, generate a concrete ask for the vendor:

```
## Before You Sign: Ask for These in Writing

1. [Q#] [Title]: "[Specific contractual or documented ask]"
   Why it matters: [risk in plain language]
   Minimum acceptable: [what CLEAR looks like for this item]

2. ...
```

Keep each ask to one sentence. These should be requests for documented evidence, not reassurances.

## Phase 5: Output

Present the scored checklist and negotiation leverage points, then offer:
- "Want me to draft the vendor questions as a formal due-diligence email?"
- "Want a one-page risk summary for your legal team?"
- "Want to run the context portability audit on your existing setup?"

## Verification

A complete checklist has:
- All 7 questions rated (CLEAR/VAGUE/UNKNOWN)
- A commitment risk tier assigned
- At least one negotiation ask per VAGUE or UNKNOWN answer
- Asks that are concrete and documentable (not "tell us your data policy" -- instead "provide the data processing agreement section specifying export window and deletion timeline")

## Source Attribution

Framework derived from Nate Kadlac newsletter (2026-06-28): "Executive Briefing: Cheap Intelligence Won't Matter If Your Context Is Trapped" -- executive decision framework for evaluating AI agent vendor commitment risk in the context of the Claude Tag / context lock-in thesis.
