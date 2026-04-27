---
name: ai-cost-exposure-audit
description: Walk through a three-prompt sequential audit of an organization's exposure to the AI inference cost curve -- inventorying dependencies, running a sensitivity analysis on what happens when subsidized pricing ends, and classifying each workload as on-device-moveable vs structurally cloud-bound. Use when an organization wants to understand its AI spend risk, plan for provider pricing changes, or identify which workloads could be moved on-device for cost or compliance reasons.
---

# AI Cost Exposure Audit

A three-prompt sequential audit that surfaces an organization's structural exposure to AI inference pricing risk. Each prompt builds on the prior output. The result is an exposure scorecard: which AI dependencies are fragile, which workloads could move on-device, and which are structurally cloud-bound regardless of cost.

Complementary to retrospective cost modeling (see `agent-cost-model` in the registry for per-task token economics) — this audit is **prospective**: it asks "what happens to our cost structure if the economics break?" rather than "what are we spending today?"

## When to Invoke

Trigger on: "AI cost exposure", "what happens when AI pricing changes", "inference dependency audit", "on-device vs cloud", "AI spend risk", "subsidized pricing", "cost curve", "lock-in economics", "AI budget sensitivity", "which workloads can move on-device", "compliance-driven local AI".

## Prompt 1 — Dependency Inventory

Ask the user to answer these questions (accept bullet lists, tables, or free text):

1. **Which AI models do you call?** List every model by name and provider (e.g., claude-sonnet-4-6 via Anthropic, gpt-4o via OpenAI, gemini-2-flash via Google).
2. **Where is each model hosted?** Note the hosting layer (provider API, Azure OpenAI, Vertex AI, self-hosted, etc.).
3. **What hardware underlies each?** If known: H100, TPU v5, or unknown.
4. **What does each model do in your workflow?** One sentence per call site (routing, generation, review, etc.).
5. **Approximate volume** — calls per day or per month per model.

Produce an inventory table:

```
| Model | Provider | Hosting Layer | Hardware | Use Case | Daily Volume |
|-------|----------|--------------|----------|----------|-------------|
| ...   | ...      | ...          | ...      | ...      | ...         |
```

Then map each row to three ownership layers:

- **Model layer** — who controls the model weights?
- **Hosting layer** — who controls the compute the model runs on?
- **Hardware layer** — who controls the physical silicon?

For each layer, note: is there a substitute readily available, or is the organization dependent on a single entity?

## Prompt 2 — Sensitivity Analysis

Using the inventory from Prompt 1, run a sensitivity scenario for each dependency:

**Scenario A — Subsidized pricing converges to true unit economics.**
Current frontier model APIs are priced below cost to acquire market share. If pricing moves to full margin:

- Estimate: what would a 5×, 10×, or 20× price increase do to each use case's economics?
- Flag any use case where current economics only hold because pricing is subsidized (i.e., the task would be human-labor-equivalent at true cost).

**Scenario B — Provider deprecates or changes a model.**
- For each model, note: what is the nearest substitute on a different provider?
- How much prompt engineering or integration work would a switch require?
- Is any use case dependent on a specific model capability with no equivalent elsewhere?

**Scenario C — Provider outage or policy change.**
- Does the workflow have a fallback if the primary model is unavailable for 24h?
- Is any workflow blocked entirely by a single provider?

Produce a sensitivity table:

```
| Use Case | 10× Price Impact | Substitute Available | Outage Fallback |
|----------|-----------------|---------------------|----------------|
| ...      | unaffordable / manageable / negligible | yes (easy) / yes (hard) / no | yes / no |
```

Flag any row where the use case becomes **unaffordable at 10× AND has no substitute**. These are critical exposures.

## Prompt 3 — Workload Classification

For each use case in the inventory, classify it into one of three categories:

### Category A — On-Device Moveable
Workloads that could run on local hardware (Mac Mini, Jetson, NPU, or equivalent) within 12 months, given appropriate model size and acceptable quality degradation.

Indicators:
- Does not require frontier-model reasoning (classification, summarization, short generation)
- Latency tolerance > 1 second
- Data residency or compliance requirement already present or anticipated
- Volume is high enough that local inference amortizes hardware cost

For each Category A workload: estimate the model size class needed (3B, 7B, 13B, 70B parameters) and the hardware class required.

### Category B — Provider-Switchable
Workloads that must remain on cloud inference but could move to a different provider with moderate effort.

Indicators:
- Requires cloud scale or a model capability class available from multiple providers
- No deep API surface coupling (only standard completions)
- Prompt works across providers with < 1 day of tuning

For each Category B workload: name the target provider and the estimated switching effort.

### Category C — Structurally Cloud-Bound
Workloads that cannot feasibly move on-device or switch providers in the near term.

Indicators:
- Requires a frontier-model capability with no local equivalent
- Deep API coupling (extended thinking, fine-tune, provider-specific vision, etc.)
- Latency requirement < 500ms at scale that rules out remote round-trip to an alternative

For each Category C workload: document the specific constraint that locks it and the earliest realistic exit date.

## Output — Exposure Scorecard

```markdown
# AI Cost Exposure Audit — {date}

## Summary
- Total AI use cases audited: N
- Category A (on-device moveable): N
- Category B (provider-switchable): N
- Category C (structurally cloud-bound): N
- Critical exposures (unaffordable at 10× AND no substitute): N

## Dependency Inventory
[table from Prompt 1]

## Sensitivity Analysis
[table from Prompt 2]

## Workload Classification

### Category A — On-Device Candidates
[list with model size class and hardware requirement]

### Category B — Provider-Switch Candidates
[list with target provider and effort estimate]

### Category C — Structurally Cloud-Bound
[list with constraint and earliest exit date]

## Top 3 Actions
1. [Highest-leverage action — e.g., "Move [use case] to a 7B local model; eliminates $X/month at projected volume"]
2. [Second action]
3. [Third action]
```

Save to `./ai-cost-exposure-audit-{date}.md` unless the user specifies otherwise.

## Verification

- [ ] All three prompts executed in sequence — do not skip Prompt 2 because the output is uncomfortable
- [ ] Every use case from Prompt 1 appears in Prompt 3 classification — no silent drops
- [ ] Critical exposures (unaffordable at 10× AND no substitute) are named explicitly
- [ ] Category A workloads have a model size class estimate, not just "could move on-device"
- [ ] Category C entries have a specific constraint named, not just "too complex"
- [ ] Output saved to a relative path (`./`) — no hardcoded absolute paths
- [ ] Top 3 actions are concrete (named use case, estimated impact) — not generic advice

## Source

Nate Kadlac — "Executive Briefing: The AI cost curve your strategy is riding just broke + 3 prompts to find your exposure" (Nate's Newsletter, 2026-04-26). The newsletter's core thesis: most AI strategic planning has not priced in the structural cost problem in cloud inference economics. The 3-prompt audit shape is derived from the newsletter's public thesis and section headers; the specific prompt prompts in the paid tier are paywalled.
