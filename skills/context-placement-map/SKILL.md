---
name: context-placement-map
description: Map which work surfaces (phone/voice assistant, team chat, code repository, email, documents, calendar, browser) have AI intelligence placed in them versus which are still "intelligence trapped outside the work." Identifies placement gaps and ranks them by leverage. Use when auditing your AI stack for coverage gaps, deciding where to introduce AI next, or when the user says "where should I add AI", "context placement", "AI placement map", "where is AI missing in my workflow".
---

# Context Placement Map

Placement beats raw model quality. A good-enough model with access to where your work actually happens outperforms a better model that can only see what you paste into it. This skill maps where your intelligence is placed versus trapped, then finds the highest-leverage gap to close.

## When to trigger

- "map my AI placements"
- "where am I missing AI in my workflow?"
- "context placement audit"
- "where should I add AI next?"
- "which of my surfaces have AI on them?"
- When deciding where to focus AI investment across a team or personal stack
- When a new AI tool is available and the user wants to know if it fills a real gap

Do NOT trigger for: evaluation of a specific tool's quality, vendor selection, or security/permission audits (those have dedicated skills).

## The Seven Standard Surfaces

A surface is any place where your work actually happens -- where you communicate, create, or execute. AI placed on a surface means an AI tool can see the work there and act on it without you copying content out of the surface first.

| Surface | Examples |
|---------|----------|
| **Voice / Phone** | Siri, Google Assistant, phone call AI, meeting transcription apps |
| **Team Chat** | Slack AI, Microsoft Copilot in Teams, Discord bots |
| **Code Repository** | GitHub Copilot, Claude Code, Codex, Cursor, AI code review |
| **Email** | Gmail AI, Outlook Copilot, AI email triage or drafting connected to your inbox |
| **Documents** | Notion AI, Google Docs AI, Word Copilot, AI in your writing tool |
| **Calendar** | AI scheduling assistants, meeting prep AI connected to your calendar |
| **Browser** | Perplexity, Arc AI, browser extension AI with page context |

Add additional surfaces if the user's workflow involves surfaces not listed (e.g., customer support platform, data warehouse, design tool).

## Placement Status Definitions

For each surface, assign one of three statuses:

- **PLACED WITH CONTEXT**: An AI tool is connected to this surface AND can see the live content there (reads your actual emails, documents, or chat threads -- not just what you paste in).
- **PLACED WITHOUT CONTEXT**: An AI tool exists for this surface type, but it operates on copied/pasted content rather than live surface data. You are the copy-paste bridge.
- **NOT PLACED**: No AI tool connected. You work on this surface without AI assistance.

The key distinction is context access: a ChatGPT tab open next to your email is NOT email-placed AI. An AI that reads your inbox is.

## Phase 1: Surface Inventory

Ask the user to walk through each surface. For each:

1. Is there an AI tool you use for work on this surface?
2. If yes -- does the tool directly access the live content on this surface, or do you copy/paste into it?
3. If yes with context -- does it work well enough that you reach for it first, or do you skip it often?

If the user is uncertain about a surface, default to NOT PLACED rather than PLACED -- uncertainty means the placement is not working even if technically configured.

## Phase 2: Placement Map

Produce a placement map table:

```
## Context Placement Map — [Date]

| Surface      | Status                    | Tool (if placed)     | Context Quality |
|--------------|---------------------------|----------------------|-----------------|
| Voice/Phone  | PLACED WITH CONTEXT / PLACED WITHOUT CONTEXT / NOT PLACED | [tool name or —] | [Strong / Weak / —] |
| Team Chat    | ...                       | ...                  | ...             |
| Code Repo    | ...                       | ...                  | ...             |
| Email        | ...                       | ...                  | ...             |
| Documents    | ...                       | ...                  | ...             |
| Calendar     | ...                       | ...                  | ...             |
| Browser      | ...                       | ...                  | ...             |

Summary:
  PLACED WITH CONTEXT: N surfaces
  PLACED WITHOUT CONTEXT: N surfaces
  NOT PLACED: N surfaces
```

Context quality for placed surfaces:
- **Strong**: You reach for it first. It reduces the time or effort on this surface meaningfully.
- **Weak**: Technically placed, but you often skip it, work around it, or find it slower than manual.

## Phase 3: Placement Gap Analysis

Rank surfaces without strong placement by leverage. Use these signals to prioritize:

**High-leverage gap signals:**
- Surface handles high-volume or repetitive work (email, team chat)
- Surface is where decisions get made or documented (documents, calendar)
- Surface is where you spend the most hours per week
- Surface has well-established AI tooling available (code repos have the densest options)

**Lower-leverage gap signals:**
- Surface is low-volume or infrequent
- Surface is already largely automated (calendar may be low-volume if meetings are few)
- Surface involves external parties who would need to adopt the same tool

Score each NOT PLACED and PLACED WITHOUT CONTEXT surface on leverage: **High / Medium / Low**.

## Phase 4: Highest-Leverage Placement Gap

Name one surface as the highest-leverage gap:

```
Highest-leverage gap: [Surface name]
Current status: [NOT PLACED / PLACED WITHOUT CONTEXT]
Why high leverage: [one sentence -- volume, decision weight, or time spent]
Placement option: [name one tool or approach that would move this to PLACED WITH CONTEXT]
What changes: [one sentence -- what you could stop doing manually if this gap were closed]
```

## Phase 5: One Move This Week

Based on the highest-leverage gap, give one concrete action:

- If NOT PLACED: name the tool to evaluate, the setup step to try first, and what to look for in a one-week trial
- If PLACED WITHOUT CONTEXT: name the specific integration or connector needed to upgrade from copy-paste to live context access

Keep the move to something completable in under two hours. Pilot on one surface before expanding.

## Verification

A complete placement map has:
- All seven standard surfaces addressed (plus any user-specific surfaces named)
- Status assigned to each surface with the copy-paste distinction applied correctly
- At least one surface ranked High on leverage
- One specific move named for the highest-leverage gap

## Source Attribution

Framework derived from Nate's Newsletter (natesnewsletter@substack.com), 2026-06-29:
"Run this 4-question test before you let any AI into your files, your Slack, or your phone."
Central thesis: the AI race has shifted from model quality to context placement -- whoever puts
intelligence closest to where work happens wins.
