---
name: open-weight-model-routing
description: Route a task between cheap open-weight self-hosted models and frontier proprietary models based on data sensitivity, task complexity, and cost tolerance. Produces a routing decision with rationale and estimated cost delta. Use when evaluating whether a task is safe for a cheap open-weight model vs requires a frontier model, or when designing a cost-tiered agent pipeline.
---

# Open-Weight Model Routing

Determines whether a task should run on a cheap open-weight model (self-hosted or low-cost API) or a frontier proprietary model, based on data sensitivity, reasoning requirements, and cost tolerance.

This is a complement to per-tier routing within a single provider. This skill answers a different question: **should this task use a frontier provider at all, or is a cheap open-weight model appropriate?**

## Trigger

Use when the user says "/open-weight-model-routing", "should I use a cheap model for this", "route to open weights", "can this run on a self-hosted model", "GLM vs Claude for this", "open source vs frontier", "is this task safe for a cheap API", "cost-sensitive model routing", or is designing a pipeline that mixes cheap and frontier inference.

## Phase 1: Task Classification

Classify the incoming task across three dimensions.

### Dimension A: Data Sensitivity

| Level | Description | Examples |
|-------|-------------|---------|
| **Public** | No PII, no proprietary IP, no confidential business data | Summarizing public docs, formatting public content, classifying open datasets |
| **Internal** | Business data not intended for public disclosure, but non-regulated | Internal meeting notes, product roadmaps, code in a private repo |
| **Sensitive** | PII, financial records, health data, credentials, regulated data | Customer PII, financial transactions, medical information, API keys |
| **Restricted** | Data with explicit data-residency or compliance requirements | HIPAA, GDPR-regulated content, defense/government data |

### Dimension B: Reasoning Depth

| Level | Description |
|-------|-------------|
| **Mechanical** | Template filling, formatting, classification with clear rules, data extraction from structured input |
| **Standard** | Code generation, summarization, translation, content rewriting |
| **Complex** | Multi-step reasoning, architecture decisions, nuanced judgment, novel synthesis |

### Dimension C: Error Tolerance

| Level | Description |
|-------|-------------|
| **High** | Draft content, exploration, internal tooling -- mistakes are cheap to fix |
| **Medium** | Output that will be reviewed before use |
| **Low** | Production output, client-facing content, one-shot decisions |

## Phase 2: Routing Decision

Apply this matrix:

| Data Sensitivity | Reasoning | Error Tolerance | Routing |
|-----------------|-----------|-----------------|---------|
| Public | Mechanical | Any | **Open-weight (cheap path)** |
| Public | Standard | High | **Open-weight** |
| Public | Standard | Medium | **Open-weight** (with review pass) |
| Public | Standard | Low | **Frontier** |
| Public | Complex | Any | **Frontier** |
| Internal | Mechanical | High | **Open-weight** |
| Internal | Mechanical | Medium/Low | **Open-weight** (if self-hosted) or **Frontier** (if API) |
| Internal | Standard | Any | **Frontier** preferred; **Open-weight self-hosted** is acceptable |
| Internal | Complex | Any | **Frontier** |
| Sensitive | Any | Any | **Frontier** (or self-hosted open-weight with on-premise deployment only) |
| Restricted | Any | Any | **On-premise self-hosted only** (no external API regardless of tier) |

### Override Rules

- If data residency is a requirement: **never use an external API** regardless of model tier
- If the task involves credentials, tokens, or secrets: **frontier on private infrastructure** or refuse
- If cost is the primary constraint and quality loss is acceptable: **open-weight** with explicit acknowledgment of risk
- If the task is in a pipeline that already sends the data to a frontier model downstream: routing to open-weight upstream provides no privacy benefit

## Phase 3: Cost Comparison

Show the cost difference between the cheap path and the frontier path:

```
Task: [short description]
Data sensitivity: [level]
Reasoning depth: [level]

Routing recommendation: [Open-weight / Frontier]
Rationale: [one line]

Cost comparison (estimated):
  Cheap path (open-weight): ~$X.XX per 1M tokens (or $0.00 if self-hosted)
  Frontier path: ~$X.XX per 1M tokens
  Savings per 1M tokens: $X.XX
  Savings per day at [N] calls of ~[K] tokens: $X.XX/day
```

Do not hardcode specific model pricing. Note that pricing changes frequently and should be verified against the provider's current rate card.

## Phase 4: Pipeline Routing (Optional)

If the user is designing a multi-step pipeline, route each step independently and flag the aggregate cost profile:

```
Pipeline: [name]
Step 1: [task description] -> [Open-weight / Frontier] | Reason: [data sensitivity / reasoning]
Step 2: [task description] -> [Frontier] | Reason: [sensitive data enters at this step]
Step 3: [task description] -> [Open-weight] | Reason: [public output, mechanical formatting]

Pipeline profile:
  Cheap steps: X of N (XX% of volume)
  Frontier steps: Y of N
  Estimated cost reduction vs all-frontier: XX%
  Key risk: [which step is the highest-sensitivity chokepoint]
```

## Phase 5: Deployment Note (Optional)

If the user chooses an open-weight model, suggest the deployment path:

- **Zero-cost self-hosted**: suitable for Restricted or Sensitive data with on-premise infrastructure; eliminates data egress but adds ops burden
- **Low-cost API** (e.g. Z.ai, OpenRouter, DeepInfra with Anthropic-compatible endpoints): suitable for Public/Internal data; eliminates ops burden but data leaves the premises
- **Managed fine-tuned variant**: when the task requires domain-specific quality that base open weights miss

## Verification

A complete routing decision has:
- All three dimensions scored
- A routing recommendation from the matrix (or a documented override with rationale)
- A cost comparison with the cheap path and frontier path
- A note on data egress implications if Sensitive or Restricted data is involved

## Source Attribution

Framework derived from Nate Kadlac newsletter (2026-06-28): "Executive Briefing: Cheap Intelligence Won't Matter If Your Context Is Trapped" -- cost/sensitivity routing between GLM-5.2 open weights and frontier models as a response to the Claude Tag vendor lock-in thesis.
