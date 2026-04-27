---
name: inference-vendor-lock-in-scorer
description: Scan agent manifests, skill files, and config to score how locked each component is to a specific AI vendor -- checking for hardcoded model names, non-portable API surfaces, missing fallback chains, and key management patterns. Outputs a per-component score and aggregate lock-in rating with a prioritized remediation queue. Use when auditing an agent stack for portability, planning a provider migration, or wanting to quantify "when not if" cutover risk.
---

# Inference Vendor Lock-In Scorer

Audits an agent or skill codebase for AI vendor dependency and produces a scored inventory: each component gets a lock-in score (0 = fully locked, 5 = fully portable), an aggregate stack score, and a remediation queue ordered by migration impact.

Distinct from format portability audits (which check MCP vs proprietary extension formats) — this skill focuses on **model vendor dependency inside manifests and config**: hardcoded model names, API surface portability, fallback chain presence, and key management patterns.

## When to Invoke

Trigger on: "audit my agent for lock-in", "how portable is my skill stack", "what happens if Anthropic changes pricing", "vendor dependency score", "fallback chain audit", "hardcoded model names", "can I switch providers", "lock-in risk", "portability score", "migration risk".

## Phase 1: Inventory the Stack

Ask the user to identify the scope. Collect:

1. **Agent manifests** — `agent.yaml`, `AGENTS.md`, `agent.config.json`, or equivalent
2. **Skill files** — any `SKILL.md`, `skill.py`, or prompt files that invoke a model
3. **Config files** — `settings.json`, `.env`, environment variable definitions, LiteLLM or proxy configs
4. **MCP server configs** — `claude_desktop_config.json` or equivalent
5. **Orchestration code** — Python/TypeScript files that call the Anthropic, OpenAI, or Google SDK directly

For each file, note: which model provider is called, and how.

## Phase 2: Score Each Component

For each component, evaluate five lock-in dimensions:

### Dimension 1 — Model Name Hardcoding (0–1)
- **1 (portable)**: model name is set via environment variable or config constant with a clear override path
- **0 (locked)**: model name is a string literal in the file (e.g., `model="claude-sonnet-4-6"` inline)

### Dimension 2 — API Surface Portability (0–1)
- **1 (portable)**: uses an abstraction layer (LiteLLM, an OpenAI-compatible proxy, or a provider-agnostic SDK)
- **0.5 (partial)**: calls the provider SDK directly but only uses standard completions API (messages, temperature, max_tokens)
- **0 (locked)**: uses provider-specific features without equivalents elsewhere (extended thinking, tool_choice: "any", provider-specific vision API, etc.)

### Dimension 3 — Fallback Chain (0–1)
- **1 (portable)**: an explicit fallback model or provider is configured for failure scenarios
- **0.5 (partial)**: retry logic exists but falls back to the same provider
- **0 (locked)**: no fallback; a provider outage stops the workflow entirely

### Dimension 4 — Key Management (0–1)
- **1 (portable)**: API key is injected via environment variable; no key material in source files
- **0.5 (partial)**: key is in a separate `.env` file committed to the repo, or referenced by a relative path that may not exist in another environment
- **0 (locked)**: key hardcoded in source, or path to key file is machine-specific

### Dimension 5 — Substitutability (0–1)
- **1 (portable)**: another provider with an equivalent model and feature set exists and has been identified
- **0.5 (partial)**: a substitute exists but requires prompt engineering changes
- **0 (locked)**: no known substitute (proprietary feature, unique fine-tune, or exclusive capability)

**Component score** = sum of five dimensions (0–5).

Produce a table:

```
| Component | Model Hardcoding | API Surface | Fallback | Key Mgmt | Substitutability | Score |
|-----------|-----------------|-------------|----------|----------|-----------------|-------|
| skill-X   | 0               | 0.5         | 0        | 1        | 0.5             | 2.0   |
| agent-Y   | 1               | 1           | 1        | 1        | 1               | 5.0   |
| ...        |                 |             |          |          |                 |       |
```

## Phase 3: Aggregate Score and Exposure Rating

Calculate the stack aggregate:

```
aggregate_score = mean(all component scores)
```

Map to exposure rating:

| Score | Rating | Meaning |
|-------|--------|---------|
| 4.0–5.0 | **LOW** | Provider migration is low-risk. A few config changes. |
| 3.0–3.9 | **MODERATE** | Migration requires prompt engineering and config work. 1–3 days. |
| 2.0–2.9 | **HIGH** | Significant rework needed. Provider-specific features must be replaced. |
| 0–1.9 | **CRITICAL** | Stack is deeply coupled to one vendor. Migration is a multi-week project. |

Output the aggregate prominently:

```
Stack Lock-In Score: X.X / 5.0 — [LOW / MODERATE / HIGH / CRITICAL]
Components audited: N
Highest risk: [component name] (score: X.X)
```

## Phase 4: Remediation Queue

List components with score < 3.0, ordered by impact (lowest score first, then by how frequently the component runs):

For each entry, produce:
```
[Component name] — Score: X.X
  Problem: [specific lock-in issue — e.g., "model name hardcoded as string literal on line 14"]
  Fix: [specific change — e.g., "replace with os.environ.get('PRIMARY_MODEL', 'claude-sonnet-4-6')"]
  Effort: [low / medium / high]
  Blocks migration: [yes / no]
```

Mark any finding that blocks a provider migration as `Blocks migration: yes`. Those are the P0 fixes.

## Phase 5: Output Report

```markdown
# Inference Vendor Lock-In Audit — {date}

## Stack Score: X.X / 5.0 — [RATING]

## Component Inventory
[table from Phase 2]

## Remediation Queue (P0 first)
[list from Phase 4]

## Components Already Portable
[components scoring 4.0+, briefly noted]

## Recommended Next Step
[one concrete action — e.g., "Extract all model names to a MODEL_PRIMARY env var. Estimated effort: 2 hours. Unblocks migration for 80% of the stack."]
```

Save to `./lock-in-audit-{date}.md` unless the user specifies otherwise.

## Verification

- [ ] Every component in the stated scope has a row in the inventory table
- [ ] Every dimension scored 0, 0.5, or 1 — no subjective range scores
- [ ] Aggregate score and exposure rating are displayed before the remediation queue
- [ ] Every P0 remediation item has a concrete fix (not just "add fallback")
- [ ] Report saved to a relative path (`./`) — no hardcoded absolute paths
- [ ] Components scoring 4.0+ are acknowledged (don't bury good news)

## Source

Nate Kadlac — "Executive Briefing: The AI cost curve your strategy is riding just broke + 3 prompts to find your exposure" (Nate's Newsletter, 2026-04-26). Idea 9 from the Forge extraction: operationalizes the harness-wars thesis at the artifact level by scoring model vendor dependency across the full skill and agent manifest set.
