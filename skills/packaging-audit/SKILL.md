---
name: packaging-audit
description: Scans recent Claude Code session history or a user-provided list of prompts/tasks and identifies which workflows recur often enough to package as skills or plugins. Returns a ranked list of candidates with effort estimates and recommended abstraction level (prompt / skill / plugin). Use when the user says "/packaging-audit", "what should become reusable", "what should I package", "audit my workflows", "what's worth building", "scan my sessions for patterns", or wants to identify the next skill to build.
---

# Packaging Audit

Answers the question: "Of everything I do repeatedly with AI, what's worth packaging?"

Scans session history or a provided task list, clusters recurring patterns, scores each against the packaging signal dimensions, and returns a prioritized build queue. Complements skill-audit (which identifies *stale* skills) by identifying *missing* skills — the workflows you keep re-explaining that should be formalized.

## Trigger

Use when the user says "/packaging-audit", "what should I package", "what's worth a skill", "audit my prompts", "scan my sessions for patterns", "what am I repeating", or "what should I build next."

## Phase 1: Data Source

Ask which source to use, or infer from context:

**Option A — Session history scan** (automatic)
Read Claude Code session transcripts from the default session log directory. Extract all distinct task types, prompts, and instructions observed across the last N sessions (default: 30 sessions or 14 days, whichever is smaller).

**Option B — User-provided list**
The user pastes or points to a list of recurring tasks, prompts, saved instructions, or a prompt library file. Read that file or list directly.

**Option C — Hybrid**
Combine session scan with a provided list.

Ask: "Should I scan your recent sessions automatically, or do you have a list of recurring tasks to audit?"

## Phase 2: Cluster and Identify Recurring Patterns

For each distinct task type found:

1. **Label it** — one-line description of what the task does.
2. **Count recurrences** — how many times does this pattern appear in the source?
3. **Note current form** — is it a bare prompt, a saved instruction, part of a CLAUDE.md rule, already a skill, or ad-hoc each time?
4. **Identify the friction** — what context or re-explanation does the user provide each time this runs?

Deduplicate: if two task types are >80% similar, merge them into one entry.

Discard: one-off tasks that appear once and show no recurrence pattern.

## Phase 3: Score Each Candidate

For each candidate that appears 2+ times, score against 4 packaging signals:

| Signal | Score 1 | Score 0.5 | Score 0 |
|--------|---------|-----------|---------|
| **Recurrence** | 5+ times in window | 2–4 times | Once |
| **Re-explanation tax** | User re-explains context each time (>3 sentences) | Occasional context refresh | Runs clean without context |
| **Tool surface** | Touches 2+ tools or APIs | 1 tool | No tool calls |
| **Generalizability** | Others could use this without modification | Needs light customization | Highly personal / one-off |

**Total score per candidate: 0–4**

## Phase 4: Recommend Abstraction Level

Apply the following mapping per candidate:

| Score | Packaging recommendation |
|-------|-------------------------|
| 3.5–4.0 | **Build a skill** — formalize with phases, verification, trigger patterns |
| 2.0–3.0 | **Save as a prompt template** — lightweight, no skill overhead |
| 0–1.5 | **Leave as-is** — re-explanation tax is low; packaging cost exceeds benefit |

For candidates scoring 3.5–4.0, optionally note if any dimension (tool surface + generalizability both = 1) suggests a **plugin** instead of a skill.

## Phase 5: Report

```
=================================================================
PACKAGING AUDIT REPORT
=================================================================
Source:      {session history / provided list / hybrid}
Window:      {date range or session count}
Audited:     {total task types found}
Discarded:   {one-off tasks removed}
Candidates:  {count scored 2+}

--- BUILD QUEUE (sorted by score, descending) ---

#{rank}. {task label}
   Recurrences:    {count}
   Re-explain tax: {score} ({evidence})
   Tool surface:   {score} ({evidence})
   Generalizability: {score} ({evidence})
   Total:          {score}/4
   Recommendation: {BUILD SKILL | SAVE PROMPT TEMPLATE | LEAVE AS-IS}
   Suggested name: {kebab-case-name}
   Effort:         {weekend / multi-sprint}

...

--- ALREADY PACKAGED (for awareness) ---
{list any candidates that are already skills or CLAUDE.md rules}

--- NEXT STEP ---
{If top candidate is BUILD SKILL}: Use a skill-creator tool to scaffold
"{suggested name}" from this description: {one paragraph from the audit}.
=================================================================
```

## What This Does NOT Do

- Does not build the skill — it identifies candidates and hands off to skill-creator.
- Does not access session data it isn't given permission to read.
- Does not score technical feasibility — only packaging signal strength.
- Does not replace the decision-ladder skill for borderline prompt/skill/plugin calls.

## Source

Extracted from Nate B. Jones newsletter (2026-05-09):
"OpenAI made Codex smart enough that the bottleneck moved. Most people haven't noticed where it went."
https://natesnewsletter.substack.com/p/codex-plugins-bottleneck-moved

Nate's thesis: the bottleneck has moved from model quality to workflow packaging. This skill operationalizes the audit step — scanning what you already do before deciding what to build.
