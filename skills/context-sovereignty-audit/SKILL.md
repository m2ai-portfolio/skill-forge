---
name: context-sovereignty-audit
description: "Run a scored portability checklist against an agent setup to answer \"do we own our context, or does the vendor?\" — covers memory read/edit/delete access, human-agnostic export, cross-model compatibility, workflow resilience to vendor disruption, and instruction location (repo-backed vs product-private). Use when planning a vendor migration, hardening an agent setup against lock-in, or evaluating whether a team's agent context is truly portable. Trigger phrases: \"context sovereignty audit\", \"portability check for my agent\", \"can I move my agent setup\", \"audit agent memory ownership\", \"sovereignty test\", \"/context-sovereignty-audit\"."
---

# Context Sovereignty Audit

Scores an agent setup on five dimensions that determine whether you own your context or the vendor does.

## When to Use

Trigger when the user says "context sovereignty audit", "portability check for my agent setup", "can we move our agent to a different vendor", "audit agent memory ownership", "is our agent context portable", or "/context-sovereignty-audit".

## Phase 1: Intake

Ask the user to describe their current agent setup. Accept any of:
- A description of which agent platform they use and how memory/instructions are stored
- A list of tools, plugins, memory stores, or standing instructions
- A shared system prompt, agent config file, or CLAUDE.md equivalent

If nothing is provided, ask: "Describe how your agent currently stores memory and standing instructions — which vendor, which format, and where the data physically lives."

## Phase 2: The Five Sovereignty Questions

Evaluate the setup against each question. Assign one of three scores per question:
- **OWNED (2 pts)**: Fully satisfied. A human can do this today without vendor involvement.
- **PARTIAL (1 pt)**: Technically possible but requires effort, export steps, or vendor cooperation.
- **LOCKED (0 pts)**: Not possible without going through the vendor; data is not independently accessible.

### Q1 — Human Read/Edit/Delete Access
Can a human directly read, correct, or delete the agent's stored memory without going through the vendor's UI or API?

- OWNED: Memory files live on disk (markdown files, plain text), editable with any editor.
- PARTIAL: Memory is in a product's storage but exportable via an API export endpoint.
- LOCKED: Memory is inside the product's database with no export path; deletion requires vendor action.

### Q2 — Model-Agnostic Export
Can the memory be exported to a plain, human-readable, model-agnostic format (markdown, JSON, plain text) that a different model could consume tomorrow?

- OWNED: Already stored in open formats. No conversion needed.
- PARTIAL: Exportable but requires a transform step (e.g., proprietary JSON to markdown).
- LOCKED: Stored in a vendor-proprietary or opaque embedding format with no export path.

### Q3 — Cross-Model Compatibility
Could another LLM (a different model family) use this memory store tomorrow without transformation?

- OWNED: Instructions and context are plain prose; any LLM reading the same file would understand them.
- PARTIAL: Mostly plain prose but includes model-specific syntax (tool call formats, plugin schemas) that would need translation.
- LOCKED: Memory is trained into a fine-tune, embedded in a proprietary vector store, or uses undocumented vendor formats.

### Q4 — Vendor Disruption Resilience
Does the workflow survive the vendor being disabled, rate-limited, or having API access revoked?

- OWNED: Instructions, context, and outputs are in local files or version control; the team can continue with a different provider immediately.
- PARTIAL: Some context is recoverable; the team would lose recent state but could rebuild within hours.
- LOCKED: The agent's institutional memory lives exclusively in the vendor's product; a disruption means starting from zero.

### Q5 — Repo-Backed Instructions
Are the key standing instructions and context in version-controlled runbooks rather than product-private memory?

- OWNED: System prompts, agent rules, and standing context all live in a git repo or equivalent version-controlled store.
- PARTIAL: Some instructions are in a repo; some are stored in the product's memory feature.
- LOCKED: All standing instructions live in the vendor's product memory; no version-controlled copy exists.

## Phase 3: Score and Report

Total score range: 0–10.

```
# Context Sovereignty Audit — {date}

## Scores

| Question | Score | Status |
|----------|-------|--------|
| Q1: Human Read/Edit/Delete | X/2 | OWNED / PARTIAL / LOCKED |
| Q2: Model-Agnostic Export  | X/2 | OWNED / PARTIAL / LOCKED |
| Q3: Cross-Model Compatibility | X/2 | OWNED / PARTIAL / LOCKED |
| Q4: Vendor Disruption Resilience | X/2 | OWNED / PARTIAL / LOCKED |
| Q5: Repo-Backed Instructions | X/2 | OWNED / PARTIAL / LOCKED |

**Total: X / 10**

## Verdict

[8–10] SOVEREIGN — your context is genuinely portable. Low migration cost.
[5–7]  PARTIAL — you have a path out, but it has friction. Gaps flagged below.
[0–4]  LOCKED — significant context is owned by the vendor. A migration would be expensive.

## Top Remediation Steps

1. [Highest-impact gap]: [Specific action to move from LOCKED/PARTIAL to OWNED]
2. [Second gap]: [Specific action]
3. [Third gap if applicable]: [Specific action]

## What to Do Next

- For each LOCKED item: decide explicitly whether to accept the lock-in or remediate.
- For each PARTIAL item: assess the cost of the remaining friction and set a deadline.
- Re-run this audit after any vendor change or agent architecture overhaul.
```

## Verification

A good audit:
- Assigns a score to every question — no skipped rows
- Cites a specific evidence point for each score (e.g., "instructions are in a CLAUDE.md tracked in git" earns OWNED on Q5)
- Gives remediation steps that are actionable, not generic ("move standing instructions to a git-tracked file" not "improve portability")

## Source Attribution

Technique derived from Nate Kadlac newsletter (2026-06-28): "Executive Briefing: Cheap Intelligence Won't Matter If Your Context Is Trapped" — portability checklist for agent memory and context sovereignty. Five-question proxy sourced from alphasignalai corroborating analysis; Nate's full seven questions are in the Executive Circle at natesnewsletter.substack.com/p/glm-5-2-context-lock-in.
