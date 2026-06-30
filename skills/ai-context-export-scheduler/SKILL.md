---
name: ai-context-export-scheduler
description: Guide the user through setting up a recurring export of their AI context (conversation history, memories, saved facts, uploaded files) out of each connected AI tool, so that leaving is never a "memory problem." Produces a per-tool export command or script plus a cron/scheduled-task spec with owner, sink, and kill declared. Use when the user says "back up my AI context", "export my AI memory", "schedule context exports", "I want to own my AI history", "context backup cron", or wants to set up a recurring job that keeps local copies of what each tool knows about them.
---

# AI Context Export Scheduler

Own the memory; rent the agent. This skill maps which of your AI tools store context, identifies the export mechanism for each, and produces a scheduled-task spec (with owner/sink/kill) to pull that context locally on a recurring basis.

## When to trigger

- "back up my AI context"
- "export my AI memory on a schedule"
- "set up a context export cron"
- "I want to own copies of what my AI tools know about me"
- After running `ai-lock-in-exit-auditor` and finding the Export lever is Present or Partial for a tool

Do NOT trigger on: one-time manual exports, vetting new tools (use `ai-tool-vetting-test`), or auditing lock-in levels (use `ai-lock-in-exit-auditor`).

## Prerequisites

- User can name at least one AI tool they want to back up
- User has API access or export credentials for that tool (or is willing to set them up)
- A local directory or accessible sink (email, cloud folder) where exports should land

## Phase 1: Inventory connected tools

Ask the user which AI tools they actively use that store context. For each, identify:
1. **Tool name** (e.g., "ChatGPT", "Claude.ai", "Gemini", "GitHub Copilot", "Notion AI")
2. **What it stores** (conversation history / uploaded files / memory / preferences / generated artifacts)
3. **Export mechanism** (API endpoint / UI download / browser script / IMAP/Gmail if email-based)
4. **Credentials needed** (API key / OAuth token / login session)

Use the table below as a reference for common tools. Extend it based on what the user names.

### Common export mechanisms

| Tool | What it stores | Export mechanism | Notes |
|------|---------------|-----------------|-------|
| ChatGPT | Conversations, memory, uploaded files | Settings → Data Controls → Export → ZIP delivered to email | Manual only; no API for personal history |
| Claude.ai | Conversations | Settings → Privacy → Export conversations | Manual ZIP; no memory export API currently |
| Gemini | Conversations, extensions context | Google Takeout (myaccount.google.com/data-and-privacy) | Bundled with Google account data; includes all Gemini chats |
| Notion AI | AI-generated content lives in Notion pages | Notion API (`GET /pages`, `GET /blocks`) or Settings → Export | API preferred for automation; full workspace export via UI |
| GitHub Copilot | No persistent personal context stored | N/A — stateless per session | Skip this tool |
| Perplexity | Conversation threads | No public API; manual export only via browser | Check account settings for any export feature |

If a tool is not in the table, check: (1) the tool's account/privacy settings page, (2) the tool's developer/API docs, (3) whether Google Takeout covers it.

## Phase 2: Prove one export end-to-end

**Before scheduling anything, prove the export works for exactly one tool.** Pick the tool with the most stored context (highest value to protect).

1. Run the export manually using the mechanism identified in Phase 1.
2. Verify the output: open the export file and confirm it contains readable, complete history.
3. Save it to the target sink directory.
4. Note the exact command or steps so they can be scripted.

Only move to Phase 3 after the manual export succeeds and the output is verified.

## Phase 3: Generate the export script

For each tool with a scriptable export mechanism (API or CLI), generate a shell script or short script that:
1. Authenticates (reads credentials from an environment variable or a config file — never hardcoded)
2. Fetches all context since the last export (incremental if the API supports it; full otherwise)
3. Saves output to a timestamped file in the sink directory: `<tool-slug>-export-YYYYMMDD.json` (or `.zip`)
4. Prints a one-line summary: `[tool] exported N items to [path]`

Example structure (adapt to tool's actual API):

```bash
#!/usr/bin/env bash
# Export context from [TOOL_NAME]
# Reads: TOOL_API_KEY (env var)
# Writes: $EXPORT_DIR/[tool-slug]-export-$(date +%Y%m%d).json

set -euo pipefail

: "${TOOL_API_KEY:?Set TOOL_API_KEY in your environment}"
: "${EXPORT_DIR:?Set EXPORT_DIR to the sink directory}"

OUTPUT="$EXPORT_DIR/[tool-slug]-export-$(date +%Y%m%d).json"

curl -s -H "Authorization: Bearer $TOOL_API_KEY" \
  "https://api.[tool].com/v1/export" \
  -o "$OUTPUT"

echo "[TOOL_NAME] exported to $OUTPUT"
```

For tools with no scriptable export (ChatGPT, Claude.ai personal), generate a checklist reminder instead:

```markdown
## Manual export reminder: [Tool Name]

Steps:
1. Go to [Settings URL]
2. Click [Export button path]
3. Wait for email delivery (up to 24h)
4. Download ZIP to $EXPORT_DIR/[tool-slug]-export-$(date +%Y%m%d).zip
5. Verify: open the ZIP and confirm history is present

Frequency: monthly (first Monday of each month)
```

## Phase 4: Scheduled task spec

For scriptable tools, produce a scheduled-task spec with all three guards declared:

```
## Scheduled export: [tool-slug]-context-export

owner: [the user — specify by name or role, e.g. "account holder"]
sink: [absolute path to export directory, or "email to <address>"]
kill: stop after 3 consecutive failures; alert owner via [email/notification/log file]

schedule: monthly on the 1st at 08:00 (or user's preferred cadence)
script: [path to the generated export script]
env:
  TOOL_API_KEY: [env var name, not the value]
  EXPORT_DIR: [configured sink path]
```

For manual-only tools, produce a calendar reminder spec instead:

```
## Calendar reminder: [tool-slug]-manual-export

owner: [the user]
sink: [the sink directory where the download lands]
kill: if reminder is missed 3 months in a row, reconsider whether this tool's context is worth the manual effort

recurrence: monthly, first Monday, 09:00
title: "Export [Tool Name] context backup"
notes: [paste the manual export checklist here]
```

## Phase 5: Report

Present a summary:

```
## Context Export Setup

| Tool | Mechanism | Frequency | Sink | Status |
|------|-----------|-----------|------|--------|
| [Tool] | Automated script | Monthly | [path] | Script generated |
| [Tool] | Manual | Monthly | [path] | Calendar reminder generated |
| [Tool] | Not exportable | N/A | N/A | Flagged for lock-in audit |

**Tools with no export lever**: [list] — consider running `ai-lock-in-exit-auditor` on these.
**First export verified**: [tool name] on [date] — [N] items exported.
```

## Verification

- [ ] At least one export was run manually and verified before any schedule was created
- [ ] Every scheduled task has owner, sink, and kill declared with real values (not placeholders)
- [ ] Credentials are read from environment variables, not hardcoded in scripts
- [ ] Export files land in a gitignored or non-repo location (never in a version-controlled directory)
- [ ] Tools with no export mechanism are explicitly listed rather than silently skipped

## What this skill does NOT do

- Authenticate to third-party services on the user's behalf — credentials must already exist
- Build a unified search index across exported context (that is a separate knowledge-management project)
- Handle tools that require browser-session authentication and have no API (these are manual-only)

## Source Attribution

Technique from Nate's Newsletter (natesnewsletter@substack.com), 2026-06-29:
"Run this 4-question test before you let any AI into your files, your Slack, or your phone."
The "own the memory, rent the agent" framing and context-portability backup pattern.
