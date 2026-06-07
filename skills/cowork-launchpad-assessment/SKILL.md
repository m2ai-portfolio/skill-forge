---
name: cowork-launchpad-assessment
description: Conducts a Discovery Sprint assessment for a prospective Claude Cowork client — takes their current tool stack and vertical, outputs a capability audit plus 3 prioritized workflow recommendations with effort and ROI estimates. Use when the user says "assess a client for Cowork", "run a discovery sprint", "what should this client automate first", or before a Cowork sales call.
---

# Claude Cowork Launchpad Assessment

Produces the Discovery Sprint deliverable: a client-ready capability audit and 3-workflow recommendation, priced as a $1,500 fixed engagement. This skill makes that deliverable repeatable in 15 minutes instead of a bespoke half-day.

## Phase 1: Client Intake

Collect via one message or from a pre-call notes doc:

```
1. Business type and vertical (e.g., Nashville real estate brokerage, HVAC company, boutique law firm)
2. Team size (headcount, roles — especially who will use Cowork)
3. Current tool stack — list every SaaS tool they use (CRM, comms, accounting, project mgmt, etc.)
4. Biggest time sink right now — "what eats the most hours per week?"
5. Do they have a Claude Max subscription? (Cowork requires it)
6. Is this Windows, Mac, or both? (Cowork is desktop-app only)
7. Any data security constraints? (Highly regulated = flag AWS Bedrock option)
8. Budget signal — are they expecting a one-time setup or ongoing service?
```

If the user is running this during a live call, the 8 fields above can be typed as shorthand. The skill will expand them.

## Phase 2: Connector Availability Check

Map their tool stack against Cowork's 38+ available MCP connectors. Output a table:

| Tool | Connector Status | Notes |
|------|-----------------|-------|
| {tool} | ✅ Native MCP / ⚠️ Computer Use workaround / ❌ Not available | {note} |

Known native connectors (as of Q1 2026): Gmail, Google Calendar, Google Drive, Slack, HubSpot, Salesforce, Jira, Linear, Notion, Figma, Snowflake, BigQuery, Databricks, Excel/M365, SharePoint, Amplitude, Intercom, Harvey, LegalZoom, DocuSign, WordPress, Canva, Similarweb, Apollo, Clay, ZoomInfo, Outreach, FactSet, MSCI, Fireflies, GitHub.

Computer Use coverage: any web UI (GoHighLevel, Follow Up Boss, QuickBooks desktop, legacy portals).

## Phase 3: Workflow Recommendation Engine

Score all applicable workflows from the standard catalog against this client using:

- **Time saved per week** (from the ROI framing table)
- **Setup complexity** (S/M/L — connector availability is the main driver)
- **Sales demo potential** (will this workflow wow them in a live demo?)

Output the top 3 as the recommendation. For each:

```markdown
## Workflow {N}: {Name}

**Problem it solves:** {one sentence — use the client's own language from intake Q4 if possible}
**What Claude will do:** {process description, 2–3 steps}
**Trigger:** {manual / scheduled daily / file-event}
**Connectors needed:** {list}
**Estimated time saved:** {X hr/week}
**Setup complexity:** {S / M / L} — {brief reason}
**Timeline to live:** {X days after kickoff}

**ROI framing for this client:**
> "{Quote-ready sales sentence specific to their vertical and tools}"
```

## Phase 4: Package Recommendation

Based on budget signal (intake Q8) and team size, recommend one of:

| Signal | Recommendation |
|--------|---------------|
| One-time / trying it out | Discovery Sprint → Launchpad upsell path |
| Wants ongoing help | Launchpad + Managed Service retainer ($3,500/mo) |
| Multiple users / team | Team Launchpad + department plugin |
| Regulated industry flag | Launchpad + Private Bedrock add-on |

## Phase 5: Discovery Sprint Deliverable Output

Format the final output as a client-presentable document:

```markdown
# Claude Cowork Discovery Sprint
## {Client Name} — {Date}

### Capability Summary
{2 sentences: what they have, what's possible}

### Connector Map
{table from Phase 2}

### Top 3 Workflow Recommendations
{3 workflows from Phase 3, formatted as above}

### Recommended Package
{Package from Phase 4 + pricing reference}

### Next Step
{Specific ask — "schedule a 90-min Launchpad kickoff" or "sign the SOW and we start Monday"}
```

## Source

Intake: `cowork-2026-06-07.md` — Derived from Freelance Market Intelligence Report (Section 2: Cowork Onboarding is #2 most in-demand, $65–$160/hr; near-zero supply) and Deep Dive (Section 9: Discovery Sprint offer at $1,500, Sections 7–10: ROI framing and workflow catalog). The assessment skill is the engine behind the repeatable Discovery Sprint offer.
