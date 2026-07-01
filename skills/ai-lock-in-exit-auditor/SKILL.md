---
name: ai-lock-in-exit-auditor
description: Score any AI tool across 6 exit levers (export, inspect, revoke, route, keep-local, prove) to quantify how stuck you would be if you tried to leave. Names the missing lever per tool and ranks tools from most to least trapped. Use when the user says "exit test", "lock-in audit", "how stuck am I", "can I leave [tool]", "portability check", "what happens if I stop using [tool]", or wants to evaluate AI vendor dependency before or after connecting a new service.
---

# AI Lock-In Exit Auditor

Before you hand a tool your context, answer one question: "If I needed to leave tomorrow, what would I lose?" This skill scores any AI tool across 6 exit levers and tells you exactly which lever is missing.

## When to trigger

- "exit test on [tool]"
- "how locked in am I to [tool]?"
- "can I leave [tool] without losing my context?"
- "portability check for [AI service]"
- "what's my exit lever for [tool]?"
- When a user is evaluating whether to deepen commitment to a tool (paid plan, data migration, workflow integration)

Do NOT trigger on: general tool recommendations, capability comparisons, or vetting for security risk (use `ai-tool-vetting-test` for that).

## Prerequisites

- Tool name(s) provided by the user
- Optional: the tool's privacy policy, data export page, or account settings open

## The 6 Exit Levers

A tool is "portable" only if all 6 levers exist. Each missing lever is a concrete switching cost.

| # | Lever | The question it answers |
|---|-------|------------------------|
| 1 | **Export** | Can you get your data out, in a usable format, without contacting support? |
| 2 | **Inspect** | Can you see exactly what the tool knows about you right now? |
| 3 | **Revoke** | Can you delete your stored context and revoke all access in one step? |
| 4 | **Route** | Can you redirect your data or workflow to a different provider without starting over? |
| 5 | **Keep-local** | Can you run a local/self-hosted version that breaks the vendor dependency? |
| 6 | **Prove** | Can you audit what happened — produce a log that proves what the tool accessed and did? |

## Phase 1: Lever Assessment

For each lever, score: **Present** (lever exists and works) / **Partial** (lever exists but is incomplete, gated, or manual) / **Absent** (lever does not exist).

### Lever 1 — Export
- Is there a "Download my data" or "Export" button in account settings?
- What format does it export? (machine-readable like JSON/CSV = good; PDF/screenshot = partial)
- Does it export everything: conversations, memories, uploaded files, saved prompts, preferences?
- Is the export available without contacting support or waiting days?

**Score absent if**: export requires a support request, takes >24h, or produces an unusable format.
**Score present if**: self-serve export, machine-readable format, covers all stored context, available within minutes.

### Lever 2 — Inspect
- Is there a "What you've shared" or "My data" view in the product?
- Can you see the full list of: conversations, uploaded files, inferred preferences, connected accounts?
- Is stored memory (if any) visible and editable in the UI?

**Score absent if**: no inspection surface exists — you cannot see what the tool holds without running an export.
**Score present if**: a real-time view of all stored context is available in-product, with no export required.

### Lever 3 — Revoke
- Is there a "Delete all my data" option?
- Does revocation cover: conversation history, uploaded files, inferred user model, third-party access tokens?
- Does it complete immediately, or is it a "submitted for deletion within 30 days" flow?
- Can you revoke individual connected app permissions (email, calendar, Slack) without deleting the whole account?

**Score absent if**: deletion requires account closure, is not granular, or takes more than 7 days.
**Score present if**: per-category deletion is available, completes within 24h, and connected app tokens can be individually revoked.

### Lever 4 — Route
- Can you connect this tool to a different underlying model (e.g., swap GPT-5 for Fable 5)?
- Can you point your workflow at a competing tool without manual re-entry of context?
- Does the tool support API access so a migration script could pull your data and push it elsewhere?
- Is the tool model-agnostic or model-locked?

**Score absent if**: the tool is vertically integrated with one vendor's model and provides no API for programmatic export or routing.
**Score present if**: model selection is configurable or an API exists that enables programmatic migration.

### Lever 5 — Keep-local
- Does an open-source version, local install, or self-hosted option exist?
- Can you run the same capability without a vendor account (e.g., a local LLM + your own data)?
- Is the tool's configuration (system prompts, workflows, skills) stored in plain files you own?

**Score absent if**: the tool is cloud-only with no open-source equivalent and no way to run it without the vendor's infrastructure.
**Score present if**: a local or self-hosted option exists, or your configuration is stored in portable files that work with any compatible runtime.

### Lever 6 — Prove
- Is there an activity log that records what the tool accessed and what actions it took?
- Can you generate a compliance report or audit trail on demand?
- Does the vendor publish a data processing agreement (DPA) or sub-processor list?
- Can you prove to a third party (employer, regulator) what data was shared with this tool?

**Score absent if**: no activity log exists and the vendor cannot produce a data-access audit report.
**Score present if**: a timestamped audit log of all data access and actions is available in-product or via API.

## Phase 2: Scoring

Calculate a lock-in score:
- **Present** = 1 point, **Partial** = 0.5 points, **Absent** = 0 points
- Maximum = 6 points

Classify:
- **5-6**: Low lock-in — safe to deepen commitment
- **3-4**: Moderate lock-in — acceptable with a documented exit plan
- **1-2**: High lock-in — vendor dependency is real; plan a mitigation before going deeper
- **0**: Critical lock-in — do not increase dependency; begin migration planning now

## Phase 3: Report

```
## [Tool Name] — Exit Audit

| Lever     | Score   | Missing piece (if Partial or Absent) |
|-----------|---------|--------------------------------------|
| Export    | Present / Partial / Absent | [what's missing] |
| Inspect   | Present / Partial / Absent | [what's missing] |
| Revoke    | Present / Partial / Absent | [what's missing] |
| Route     | Present / Partial / Absent | [what's missing] |
| Keep-local| Present / Partial / Absent | [what's missing] |
| Prove     | Present / Partial / Absent | [what's missing] |

**Lock-in score**: X/6
**Classification**: Low / Moderate / High / Critical

**Missing levers** (highest switching cost):
1. [most critical missing lever and why it's expensive]
2. [second most critical]

**Exit plan summary**: [one sentence: what you'd lose and what it would take to leave cleanly]
```

## Phase 4: Multi-tool ranking

If multiple tools are audited, rank from most locked-in (lowest score) to most portable (highest score). For each, name the single most expensive missing lever.

## Phase 5: Recommended action

For the highest-lock-in tool, recommend exactly one of:
- **Negotiate**: ask the vendor to add the missing lever (data export, audit log) as a condition of a paid plan upgrade
- **Limit**: stop growing context in this tool (no new files, no new memories) until the lever exists
- **Parallel-run**: start building a portable duplicate of your workflow in a more portable alternative
- **Exit now**: if lock-in score is 0 and the tool has access to sensitive data, begin migration immediately

## Verification

- [ ] Every lever scored with explicit evidence or documented uncertainty
- [ ] "Partial" is never used as a default — it requires a specific known gap
- [ ] Missing-lever description is concrete enough to take to vendor support as a feature request
- [ ] Action recommendation is one of the four above (not a vague "consider alternatives")

## Source Attribution

Technique from Nate's Newsletter (natesnewsletter@substack.com), 2026-06-29:
"Run this 4-question test before you let any AI into your files, your Slack, or your phone."
Exit lever framework: the "six exit levers" section of the same issue.
