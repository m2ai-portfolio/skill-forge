---
name: agent-context-sovereignty-audit
description: Run a portability checklist against a team's agent setup to determine whether they own their AI context or whether it is trapped in a vendor's private memory. Outputs a scored sovereignty report with remediation priorities. Use when the user asks about AI vendor lock-in for context and memory, wants to assess portability of their agent setup, or is planning a vendor migration.
---

# Agent Context Sovereignty Audit

Runs a structured checklist against a team's agent setup to score how much of their context, memory, and workflow is truly portable vs trapped behind a vendor's private memory layer.

## Trigger

Use when the user says "/agent-context-sovereignty-audit", "sovereignty audit", "context portability check", "is my agent setup portable", "can I switch AI vendors", "audit our agent memory lock-in", "how portable is our agent context", "do we own our AI memory", or is planning a vendor migration and wants to assess what moves with them.

## Phase 1: Intake

Collect the following from the user (or infer from context):

1. **Agent runtime** -- which AI platform(s) the team uses for agents (e.g. Claude, GPT, Gemini, Slack-integrated agents)
2. **Memory/context stores** -- where agent context lives: product-private memory, external vector DBs, markdown runbooks, ticket trackers, shared docs
3. **Workflow definitions** -- where the standing instructions and skills live: product-private (inside the vendor's UI), repo-backed files, MCP server configs
4. **Integration surface** -- which tools/channels the agent is connected to (Slack, email, calendar, code repos) and whether those connections are per-vendor or standard APIs

If the user cannot answer items 2-4, that itself is a signal scored in Phase 2.

Announce scope:
```
Auditing agent context sovereignty for: {runtime}
Memory stores: {stores or "unknown"}
Workflow definitions: {locations or "unknown"}
```

## Phase 2: Sovereignty Checklist

Score each question YES / PARTIAL / NO. Provide a brief rationale for each.

### Q1: Human Readability
**Can a human read, correct, or delete the agent's stored memory without going through the vendor's UI or API?**
- YES: Memory lives in files, databases, or standard formats a human can open directly.
- PARTIAL: Memory is accessible via vendor export but requires a download step.
- NO: Memory exists only inside the vendor's private storage with no export path.

Failure cost: Cannot audit what the agent knows. Cannot correct hallucinated memory. Cannot onboard a new team member to review agent behavior.

### Q2: Format Portability
**Can the context be exported into a human-agnostic format (Markdown, JSON, plain text) that any model can consume?**
- YES: Context is already in open format (markdown runbooks, structured JSON, plain text docs).
- PARTIAL: Export is possible but requires a vendor-specific script or API call.
- NO: Context only exists in a proprietary format or is embedded in the vendor's model.

Failure cost: Switching vendors requires rebuilding all accumulated context from scratch.

### Q3: Model Independence
**Can a different model use the same context and instructions without re-authoring them?**
- YES: Standing instructions are plain text or Markdown; any model can read them.
- PARTIAL: Instructions rely on vendor-specific syntax (e.g. system prompt conventions, plugin invocations) that need light adaptation.
- NO: Instructions are so deeply tied to one model's behavior that they would not transfer.

Failure cost: The team's accumulated prompt engineering and tuning cannot transfer to a new vendor.

### Q4: Vendor-Disable Survivability
**If the vendor disabled or capped the account today, could the team continue operating within 48 hours using a different provider?**
- YES: Instructions in repo, memory in portable store, integrations via standard APIs. A swap is a config change.
- PARTIAL: Most things are portable but one or two key integrations are vendor-specific.
- NO: The team would lose significant functionality and context. Recovery is weeks, not hours.

Failure cost: Outage = full stop. Pricing change = no negotiating leverage. Vendor sunset = data loss.

### Q5: Repo-Backed Instructions
**Are the agent's key instructions (system prompts, skills, standing rules) committed to a version-controlled repo the team owns?**
- YES: All standing instructions are in a repo; the vendor's UI is just the runner.
- PARTIAL: Some instructions are in repo, others were typed directly into the vendor's product and not exported.
- NO: All instructions live inside the vendor's product memory.

Failure cost: No audit trail. No rollback. No diff. Cannot reproduce agent behavior after a system reset.

## Phase 3: Scoring

Assign points per answer:
- YES = 2
- PARTIAL = 1
- NO = 0

Total possible: 10

```
Sovereignty Score: X/10

| Question | Score | Rationale |
|----------|-------|-----------|
| Q1: Human Readability  | X/2 | ... |
| Q2: Format Portability | X/2 | ... |
| Q3: Model Independence | X/2 | ... |
| Q4: Vendor-Disable Survival | X/2 | ... |
| Q5: Repo-Backed Instructions | X/2 | ... |

Tier: [Sovereign / Partially Sovereign / Captured]
```

Tier thresholds:
- **Sovereign (9-10)**: Context is fully portable. Vendor is interchangeable.
- **Partially Sovereign (5-8)**: Meaningful lock-in exists. Migration is painful but possible.
- **Captured (0-4)**: Context is trapped. Switching vendors means starting over.

## Phase 4: Remediation Queue

For each NO or PARTIAL answer, generate one remediation item. Order by impact (highest switching-cost risk first).

Format:
```
## Remediation Priorities

1. [Q#] [Issue title]
   Risk: [what happens if this stays unfixed]
   Fix: [concrete action, e.g. "Export system prompts to /docs/agent-instructions/ in the team repo"]
   Effort: [hours / days / sprint]

2. ...
```

Keep each fix to one concrete action. Do not prescribe specific vendor tools unless the user has identified them -- keep the fix advice model-agnostic.

## Phase 5: Output

Present the sovereignty report, then offer:
- "Want me to draft a migration plan from Captured to Sovereign?"
- "Want a one-page exec summary of the lock-in risk?"
- "Want me to export the checklist as a decision template for future vendor evaluations?"

## Verification

A complete audit has:
- All 5 questions scored with rationale (not left blank)
- A tier assignment
- At least one remediation item per NO/PARTIAL answer
- Fixes that are model-agnostic (no hardcoded vendor assumptions)

## Source Attribution

Framework derived from Nate Kadlac newsletter (2026-06-28): "Executive Briefing: Cheap Intelligence Won't Matter If Your Context Is Trapped" -- 5-question sovereignty test from corroborating public source (alphasignalai.substack.com, "The Real Claude Tag Question Is Context Lock-In"). Nate's full 7-question framework is behind the Executive Circle paywall; this skill uses the 5 confirmed questions from the free-tier coverage.
