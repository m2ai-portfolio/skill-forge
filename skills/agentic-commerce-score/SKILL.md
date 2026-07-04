---
name: agentic-commerce-score
description: Score an agent product 0–100 across the 8 commercial-responsibility layers (Identity 15pts, Authorization 20pts, Fraud 15pts, Payment Credentials 10pts, Settlement 10pts, Refunds 10pts, Liability 15pts, CRM 5pts). Outputs a weighted score, per-layer heatmap, and a ranked TODO list. Use when the user says "commerce score", "agentic commerce score", "commerce readiness", "agent commerce audit", "score my agent for commerce", "payment readiness", or wants a quantitative readiness rating before shipping an agent that handles real money.
---

# Agentic Commerce Readiness Score

Produce a weighted 0–100 score across the 8 commercial-responsibility layers for any agent product. Identifies the highest-leverage gaps and ranks them by risk-adjusted improvement opportunity.

## When to Use

- Before shipping an agent that initiates purchases, bookings, or financial commitments
- After a responsibility-audit to get a quantitative score for the qualitative gaps found
- When comparing two design options for an agent product on commercial readiness
- As a recurring health check as the product evolves

## Inputs

1. A product or agent description (spec, README, architecture doc, or use-case summary)
2. Optional: a completed responsibility-audit output (if already run, use it rather than re-scoring from scratch)

## Phase 1: Score Each Layer

For each layer, assign a score using the rubric below. Rubric scale: 0 / 5 / 10 (out of the layer's max weight).

- **0**: Not addressed — no mention, no design, no coverage
- **5**: Partial — some thought given, but gaps exist that would cause issues in production
- **10**: Fully owned — defined, documented, assigned to a named owner, has a revocation or failure path

Multiply by the layer weight to get the weighted contribution:

| Layer | Max Weight | Rubric 0/5/10 | Score Formula |
|-------|-----------|---------------|---------------|
| 1. Identity | 15 | 0/7.5/15 | raw_score × 1.5 |
| 2. Authorization | 20 | 0/10/20 | raw_score × 2.0 |
| 3. Fraud | 15 | 0/7.5/15 | raw_score × 1.5 |
| 4. Payment Credentials | 10 | 0/5/10 | raw_score × 1.0 |
| 5. Settlement | 10 | 0/5/10 | raw_score × 1.0 |
| 6. Refunds | 10 | 0/5/10 | raw_score × 1.0 |
| 7. Liability | 15 | 0/7.5/15 | raw_score × 1.5 |
| 8. CRM | 5 | 0/2.5/5 | raw_score × 0.5 |

**Total max: 100**

For each layer, document:
- The raw score (0/5/10) and the reasoning (one sentence)
- The weighted contribution
- Any disqualifying condition (a zero on Identity or Authorization is a launch blocker regardless of total score)

## Phase 2: Calculate Total and Classify

```
Total Score = sum of all weighted contributions (0–100)

Classification:
- 0–25:  Not Commerce-Ready — do not ship with real money
- 26–50: Pre-Production — suitable for alpha/testing with capped test funds
- 51–74: Nearly Ready — fix priority gaps before launch; soft-launch with hard caps acceptable
- 75–89: Commerce-Ready — minor gaps acceptable at launch; track and close post-launch
- 90–100: Best-Practice — all layers owned, minimal residual risk
```

**Hard blockers regardless of total score:**
- Identity = 0: cannot establish counterparty trust
- Authorization = 0: undefined scope is undefined liability

If either hard blocker applies, the product must not handle real transactions even if the total score is above 50.

## Phase 3: Per-Layer Heatmap

Output the heatmap in a format that renders well in Markdown:

```
AGENTIC COMMERCE READINESS SCORE
=================================
Product: <name>          Score: XX/100 (<classification>)
Date: <today>

Layer                  | Score   | Max | Pct  | Status
-----------------------|---------|-----|------|--------
Identity               |  7.5    |  15 |  50% | ⚠ Partial
Authorization          | 20.0    |  20 | 100% | ✓ Owned
Fraud                  |  0.0    |  15 |   0% | ✗ Missing
Payment Credentials    | 10.0    |  10 | 100% | ✓ Owned
Settlement             |  5.0    |  10 |  50% | ⚠ Partial
Refunds                |  0.0    |  10 |   0% | ✗ Missing
Liability              |  7.5    |  15 |  50% | ⚠ Partial
CRM                    |  0.0    |   5 |   0% | ✗ Missing
-----------------------|---------|-----|------|--------
TOTAL                  | 50.0    | 100 |  50% | Pre-Production
```

Legend: ✓ Owned (≥ 75%) | ⚠ Partial (25–74%) | ✗ Missing (< 25%)

## Phase 4: Ranked TODO List

Generate a ranked improvement list sorted by: (1) hard blockers first, (2) highest weight-adjusted improvement opportunity, (3) layers currently at 0 before layers at partial.

For each item:

```
### [Priority N] [Layer Name] — +X.X points available

Current state: [one-line description of what exists today]
Gap: [what is missing]
Minimum viable improvement: [smallest change that moves the score from 0→partial or partial→owned]
Effort estimate: [half-day / 1 day / 2 days / 1 week]
Owner candidate: [builder / merchant / operator / payments network]
```

Cap the list at 5 items — more than 5 creates diffusion, not focus.

## Verification

- [ ] All 8 layers scored with explicit reasoning — no layer estimated or skipped
- [ ] Total is the arithmetic sum of weighted contributions (spot-check at least 2 layers)
- [ ] Classification matches the total score band
- [ ] Hard blocker check runs before classification is reported
- [ ] TODO list has no more than 5 items and each has a concrete minimum viable improvement

## Source Attribution

Scoring weights and layer definitions from the 8-layer commercial-responsibility framework.
Via Nate's Newsletter (2026-05-12): "Agentic Commerce Is A Protocol War. Here's Who's Fighting."
https://natesnewsletter.substack.com/p/agentic-commerce-protocol-war
