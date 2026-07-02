---
name: frontier-open-model-router
description: "Classify a task on the frontier-vs-open model axis and recommend whether to use a proprietary frontier model (Claude, GPT, Gemini) or an open-weight model (Llama, Mistral, Qwen, DeepSeek, Phi). Produces a routing decision with rationale across five dimensions: data sensitivity, reasoning complexity, latency, cost envelope, and output quality bar. Use when choosing between hosted AI services and self-hosted or provider-hosted open models, or when building a system that needs to route work across a mixed fleet."
---

# frontier-open-model-router

Classifies a task along the frontier-vs-open model axis and returns a routing decision with rationale. This is a different decision than tier routing within a single provider (Opus vs Sonnet vs Haiku) — it answers the prior question: does this task need a frontier model at all, or can an open-weight model handle it at lower cost and without sending data to an external API?

## Trigger

Use when the user says "should I use Claude or a local model for this", "frontier vs open", "can I run this on Llama", "is this a GPT-4 task or can I use something cheaper", "I need to route tasks between frontier and open models", "which tasks need an API", "data can't leave my infra", or any question about model selection at the provider/weight level rather than the tier level.

## The two model classes

**Frontier models** — proprietary hosted APIs:
- Examples: Claude (Anthropic), GPT-4o (OpenAI), Gemini Pro (Google), Grok (xAI)
- Characteristics: highest reasoning ceiling, large context windows, latest training, external API call (data leaves your infra), per-token cost, rate-limited

**Open-weight models** — self-hosted or third-party hosted:
- Examples: Llama 3.x (Meta), Mistral / Mixtral, Qwen (Alibaba), DeepSeek, Phi-4 (Microsoft), Gemma (Google)
- Characteristics: deployable on your own infra, data stays local, lower per-token cost at volume, lower (but narrowing) reasoning ceiling, smaller typical context windows

## Phase 1: Five-Dimension Classification

Ask about each dimension if not stated. Score each 1 (open-weight fine) to 5 (frontier required):

### D1 — Data Sensitivity
Does the task involve data that must not leave your infrastructure?
- 1: Public info, generated content, no PII or proprietary data
- 3: Internal business data, acceptable under a DPA / BAA
- 5: PII, PHI, trade secrets, regulated data, or contractual prohibition on external APIs

**Score 5 → frontier API is blocked; must route to self-hosted open-weight.**

### D2 — Reasoning Complexity
How much multi-step inference, planning, or domain reasoning does the task require?
- 1: Formatting, template fill, simple classification, extraction from clear structure
- 3: Standard code generation, bug fixing, summarization with judgment, multi-turn Q&A
- 5: Complex planning, cross-document synthesis, adversarial reasoning, novel research, long dependency chains

**Score 1–2 → open-weight models handle this reliably at lower cost.**

### D3 — Latency
What is the acceptable time-to-first-token for this task?
- 1: Async batch, minutes acceptable
- 3: Interactive, sub-5s acceptable
- 5: Real-time (<500ms), streaming critical, or embedded in a user-facing product with SLA

**Score 5 → self-hosted open-weight on GPU can beat frontier API latency; evaluate both.**

### D4 — Cost Envelope
What is the volume and cost sensitivity?
- 1: One-off or low-volume task; cost immaterial
- 3: Regular usage; cost is a consideration but not blocking
- 5: High-volume pipeline, millions of tokens/day, or cost is a hard budget constraint

**Score 4–5 → open-weight is likely the right default unless reasoning complexity is also high.**

### D5 — Output Quality Bar
Does the quality difference between frontier and open-weight models differentiate the end product?
- 1: Quality is "good enough" from either class; users won't notice the difference
- 3: Quality matters; open-weight models produce acceptable but noticeably lower quality
- 5: Output quality is the product; frontier-class reasoning is required to meet the bar

**Score 5 → frontier model; the quality delta is load-bearing.**

## Phase 2: Routing Decision

| Frontier score (D2 + D5) | Privacy constraint (D1) | Cost pressure (D4) | Recommendation |
|---|---|---|---|
| ≤4, D1=5 | Blocked from external API | Any | **Open-weight required** (self-hosted) |
| ≤4, D1<5 | None | ≥4 | **Open-weight preferred** (cost) |
| ≤4, D1<5 | None | <4 | **Open-weight candidate** (benchmark first) |
| 5–10, D1=5 | Blocked from external API | Any | **Open-weight required** — note quality risk |
| 5–10, D1<5 | None | Any | **Frontier recommended** — verify no open model meets bar |
| Mixed | D1<5, D4≥4, D2≥4 | Both high | **Hybrid**: open-weight for high-volume / low-complexity subtasks, frontier for synthesis and judgment |

### Output format

```
ROUTING DECISION: [FRONTIER | OPEN-WEIGHT | HYBRID]

Scores:
  D1 Sensitivity:   [1-5] — [reason]
  D2 Complexity:    [1-5] — [reason]
  D3 Latency:       [1-5] — [reason]
  D4 Cost:          [1-5] — [reason]
  D5 Quality bar:   [1-5] — [reason]

Recommendation:
  Primary model class: [FRONTIER | OPEN-WEIGHT | HYBRID]
  Suggested candidates: [list 1-3 specific models with why]
  Key rationale: [1-2 sentences]
  Risk to watch: [the dimension most likely to flip this decision]

If HYBRID:
  Frontier for: [which subtasks]
  Open-weight for: [which subtasks]
  Handoff point: [where the split happens]
```

## Phase 3: Model Suggestions

Provide 1–3 specific model candidates per class:

**Frontier candidates** (match to task type):
- Long-context reasoning: Claude Sonnet/Opus, GPT-4o
- Code generation: Claude Sonnet, GPT-4o, Gemini Pro
- Structured extraction: any frontier at Sonnet/Sonnet-equivalent tier

**Open-weight candidates** (match to task type and infra):
- General reasoning, medium complexity: Llama 3.3 70B, Qwen 2.5 72B, Mistral Large
- Low-complexity, high-volume: Llama 3.2 8B/11B, Phi-4, Mistral 7B
- Code-focused: DeepSeek Coder, Qwen 2.5 Coder
- Privacy-critical, on-device: Phi-4, Llama 3.2 3B

**Note on self-hosting vs third-party open hosting**: if D1=5 (data must not leave infra), self-hosting is required. Third-party hosted open models (via OpenRouter, Together AI, etc.) still send data externally.

## Verification

The routing decision is correct if:
- D1=5 never routes to an external frontier API
- D2+D5 ≤ 4 does not default to frontier without a cost or quality justification
- Hybrid splits are explained at the task boundary, not at the model level
- Suggested models exist and are actively maintained (verify before wiring into production)

## Source

Nate Jones newsletter, 2026-07-01: "You can build 80% of your own AI memory by talking to the agent already on your computer." Idea #10: model-picker / router for the week's work (frontier-vs-open routing angle, distinct from tier routing within a provider).
