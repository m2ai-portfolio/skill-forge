---
name: morning-briefing-agent
description: Generates a deployable Claude Cowork "morning briefing" scheduled task spec — aggregates Gmail, Google Calendar, and Slack activity from the prior period and delivers a structured one-pager briefing on a daily schedule. Use when the user says "set up my morning briefing", "build the daily briefing agent", "configure 7am briefing", or when onboarding a client who wants the #1 Cowork workflow. Also runs as a direct briefing when invoked manually.
---

# Morning Briefing Agent

Two modes:

1. **Setup mode** — generates a ready-to-deploy Claude Cowork scheduled task configuration for a client's workspace.
2. **Direct mode** — runs the briefing now using available MCP connectors (Gmail, Google Calendar, Slack).

Detect mode from context: if the user says "set up" or "configure", run Setup mode. If connectors are available and the user says "run" or invokes without context, run Direct mode.

---

## Direct Mode

When invoked directly with Gmail, Google Calendar, and Slack MCP tools available:

### Step 1: Gather overnight activity

Pull in parallel:

**Gmail** (last 18 hours):
- Threads where `is:unread` and `to:me` — categorize as: Action Needed / FYI / Newsletter / Junk
- Identify top 3 threads requiring a response today

**Google Calendar** (today + tomorrow):
- All events for today: title, time, attendees, prep needed
- First event tomorrow (to flag evening prep)

**Slack** (last 18 hours, if available):
- Unread DMs
- Mentions (`@me`) in channels
- Any message from a list of VIP senders (if defined in `working-preferences.md`)

### Step 2: Assemble the one-pager

```markdown
# Morning Briefing — {Day}, {Date}

## Your Day
{Today's events in time order, one line each with any prep note}

## Email Priority (top 3)
1. **{Sender}** — {Subject} — {one-line action needed}
2. **{Sender}** — {Subject} — {one-line action needed}
3. **{Sender}** — {Subject} — {one-line action needed}
*({N} more unread — {N-action-needed} need replies, {N-fyi} FYI, {N-newsletter} newsletters)*

## Slack
{Unread DMs: list with sender and topic}
{Mentions: list with channel and context}

## Heads Up for Tomorrow
{First event + any prep note}

## One Nudge
{One optional insight — a pattern in the email, a scheduling conflict, a follow-up that's overdue}
```

Deliver this in under 300 words. No filler. No "here's your briefing!" preamble.

---

## Setup Mode

When the user wants to configure this as a recurring Cowork scheduled task:

### Step 1: Intake

Collect:
1. Delivery time (default: 7:00am)
2. Days (default: Monday–Friday)
3. Output format: (a) display in Cowork, (b) email to self via Gmail, (c) Slack DM to self, (d) write to file
4. Should it include Slack? (requires Slack MCP)
5. VIP senders — any names/domains whose messages always surface regardless of read status?
6. Calendar: include only work calendar, or all calendars?

### Step 2: Generate the Cowork Scheduled Task Spec

Output a spec the user pastes into Cowork's task scheduler:

```markdown
## Cowork Scheduled Task: Morning Briefing

**Name:** Morning Briefing
**Schedule:** {days} at {time}
**Trigger type:** Time-based

**Task prompt:**
---
Pull my morning briefing. Do these steps in parallel:

1. Gmail: Find all unread emails from the last 18 hours addressed to me. Categorize each as: Action Needed, FYI, Newsletter, or Junk. Identify the top 3 that need a response today.

2. Google Calendar: List all events on my calendar today, in time order. Note any that need prep. Also show my first event tomorrow.

3. Slack (if connected): List any unread DMs and any @mentions since yesterday.

Then produce a single one-page briefing:
- My schedule for today (time order, one line per event)
- Top 3 email priorities with the action I need to take
- Slack summary (DMs + mentions)
- One heads-up for tomorrow
- One optional nudge if there's a pattern worth flagging

Keep it under 300 words. No preamble.

{Output instruction from intake Q3}
---

**Connectors required:** Gmail MCP, Google Calendar MCP{, Slack MCP if enabled}
**Estimated run time:** 2–4 minutes
**Memory:** Write `last-briefing-summary.md` to `~/Claude-Workspace/context/` after each run for continuity.
```

### Step 3: Activation Instructions

```
To activate in Claude Cowork:
1. Open Cowork → Scheduled Tasks → + New Task
2. Paste the task prompt above
3. Set schedule to {days} at {time}
4. Enable connectors: Gmail ✓  Google Calendar ✓  {Slack ✓ if enabled}
5. Save → the briefing will arrive automatically starting tomorrow morning.

To test now: open a Cowork session and type /morning-briefing or paste the task prompt manually.
```

---

## Variations

### Monday Extended Briefing

On Mondays, add:
- Weekend Slack summary (last 48h instead of 18h)
- Weekly priorities from a project tracker (Notion/Linear/Jira if connected)
- Top 3 goals for the week (read from `working-preferences.md` if present)

### Executive Briefing for Clients

When building this for a client, refer to `cowork-context-file-builder` first — the briefing uses `working-preferences.md` to know their autonomy level and VIP senders.

---

## Source

Intake: `cowork-2026-06-07.md` — Derived from Claude Cowork Complete Deep Dive (Section 2.7: Morning Briefing workflow; Section 5: Flagship Pipeline shape) and Freelance Market Intelligence Report (daily briefings listed as the #1 most-requested Cowork automation). The #1 demo workflow that closes Launchpad sales.
