---
name: session-history-model-onboarding
description: Mine your personal Claude Code session history (JSONL files) with a dynamic multi-agent workflow to generate a tailored adoption report for a new model release — what changed for YOUR patterns, not a generic summary. Trigger: "new model dropped", "how should I change my workflow for [model]", "personalized model onboarding", "mine my sessions for [model]".
---

# Session History Model Onboarding

Uses Claude Code's dynamic workflow system to fan out agents over your JSONL session history, identify your actual usage patterns, and generate a personalized guide for adopting a new model — calibrated to how you actually work, not to generic documentation.

## When to Use

Trigger when:
- A new model version releases and you want adoption guidance beyond generic docs
- You suspect your prompting patterns or scaffolding need to change for the new model
- You want a short video or report tailored to your real workflows, not a YouTube summary
- You plan to run this type of analysis repeatedly and want to save it as a reusable workflow

Do NOT use for:
- API compatibility checks before migration — use `model-migration-preflight` for that
- Cost projections for a model switch — use `agent-cost-model` for that
- General dynamic workflow questions — use `dynamic-workflow-orchestration` for general patterns

## Phase 1: Locate Session History

Claude Code stores every session as a JSONL file. Find the path:

```bash
# Default location on macOS
ls ~/.claude/projects/

# Default location on Linux
ls ~/.config/claude/projects/

# Or ask Claude Code directly:
# "Where are my JSONL session files stored?"
```

Each file is a conversation replay: alternating assistant/user turns with all tool calls. These are token-heavy but contain your actual prompting patterns, tools used, and success/failure signals.

Confirm the path exists and note the approximate count before proceeding. If there are < 10 sessions, the analysis will be thin — acknowledge this to the user.

## Phase 2: Build the Workflow Prompt

Use the following template. The word "workflow" is the trigger phrase that activates Claude Code's multi-agent mode.

```
I would like you to build a workflow that analyzes all JSONL files in [SESSION_PATH]
and generates a personalized adoption guide for [NEW_MODEL_NAME].

Step 1 — Data analysis:
  For each JSONL file, extract:
  - Token usage patterns (input/output ratios)
  - Most-used tools and MCP servers
  - Recurring prompt structures and phrasing styles
  - Session lengths and turn counts
  - Any explicit failures or retries visible in the history

Step 2 — Model comparison:
  Use the claude-guide sub-agent to retrieve the official release notes and
  capability changes for [NEW_MODEL_NAME] vs the previous version.
  Cross-reference with the patterns from Step 1.

Step 3 — Synthesis:
  Produce a personalized report with:
  a) Executive summary: top 3-5 changes that affect MY workflows
  b) Usage profile analysis: which patterns transfer cleanly vs. need adjustment
  c) Prompting pattern updates: specific rewrites for flagged prompts
  d) Tool and skill recommendations: what to add, remove, or reconfigure
  e) New capability opportunities: dynamic workflow patterns worth trying with this model

Output the report as an HTML page saved to [OUTPUT_PATH or ./model-onboarding-report.html].
```

Customize [SESSION_PATH], [NEW_MODEL_NAME], and [OUTPUT_PATH] before running.

## Phase 3: Invoke and Monitor

Run the prompt in Claude Code. You will see:
1. A workflow specification phase — review agent roles and scope before approving
2. Batch progress: agents fan out over JSONL files, then a synthesis layer
3. Final output: the HTML report (or markdown if HTML is not requested)

Typical agent count: 10–40, depending on session history volume.
Typical token cost: 500K–2M tokens for a full history scan.

If the agent count or scope looks wrong before execution, cancel and narrow the prompt (e.g., limit to sessions from the past 90 days, or filter by project folder).

## Phase 4: Save as a Reusable Skill

Once the workflow runs successfully, ask Claude Code to save it as a reusable skill:

> "Create a skill called model-migration from this workflow so I can run it again
> for future model releases with a single command."

Claude Code will package the workflow specification into a SKILL.md under `~/.claude/skills/model-migration/`. The next time a new model drops, invoke it with the model name as an argument instead of rebuilding the prompt from scratch.

## Optional: Generate a Video Summary

If you want a 1–2 minute video walkthrough of the report, pass the HTML output to Hyperframes:

> "Take the HTML report at [OUTPUT_PATH] and use Hyperframes to generate a
> 2-minute explainer video at 2x speed covering every section."

This requires Hyperframes to be configured in your environment.

## Verification

A successful run produces:
- An HTML or markdown report that references specific session patterns (not generic advice)
- Prompting rewrites that mention phrases actually found in your history
- A section that distinguishes "no change needed" from "change required" items
- Tool/skill recommendations grounded in tools you actually used

If the report reads like generic model documentation with no personal references, the JSONL scan likely failed or found no parseable data — check the session file path and format.

## Source Attribution

Technique: Personalized Model Adoption via Session History Analysis
Source: Mark Kashef YouTube
URL: https://www.youtube.com/watch?v=9_ExDZFlaNc
Published: 2026-06-01
Title: "3 AMAZING Claude Code Dynamic Workflows (Opus 4.8)"
