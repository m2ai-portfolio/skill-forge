---
name: ai-tool-vetting-test
description: Run a structured 4-question vetting test against any AI tool to produce a per-tool exposure scorecard (strong/partial/weak) across four dimensions — what it can SEE, DO, REMEMBER, and how you CHECK it. Outputs a ranked exposure list and a single highest-value move for the week. Use when the user says "vet this AI tool", "is this tool safe to use", "4-question test", "see/do/remember/check", "what can this AI access", or wants to assess a new app/connector/model before granting it access to their files, accounts, or communication.
---

# AI Tool Vetting Test

Run Nate's 4-question test against any AI tool before you hand it access to your context. Produces a per-tool scorecard (strong / partial / weak) across SEE / DO / REMEMBER / CHECK, a ranked exposure list, and one highest-value move for this week.

## When to trigger

- "vet this tool before I connect it"
- "4-question test on [tool]"
- "see/do/remember/check for [tool]"
- "what can [tool] actually see?"
- "is [Slack app / phone AI / coding agent / browser extension] safe?"
- When a user is about to grant a new AI connector, integration, or assistant access to their data

Do NOT trigger on: general "what AI tool should I use?" questions or model comparison — those are different surfaces.

## Prerequisites

- Tool name or description provided by the user
- Optional: the tool's permission/data-access settings page open or screenshotted

## Phase 1: Identify the tool

Ask the user to name the tool and describe the access it has requested or currently has:
- What accounts/services does it connect to? (email, calendar, files, Slack, phone, code repos)
- What actions can it perform? (read only, write, send, execute, browse, purchase)
- Did it ask for login access, file system access, or background access?

If the user provides a URL to the tool's permission page or privacy policy, read it to pre-fill answers.

## Phase 2: The 4-Question Test

Evaluate the tool on each dimension. Score each: **Strong** (clear, auditable, limited) / **Partial** (possible but undocumented or opt-in) / **Weak** (absent, opaque, or unlimited).

### Question 1 — What can it SEE?
Map every data surface the tool has read access to:
- Files and documents (local disk, cloud storage, shared drives)
- Communication (email inbox, sent mail, calendar events, chat history)
- Code repositories and project workspaces
- Browser history, open tabs, or screen content
- Contacts, phone calls, SMS (mobile integrations)

**Score weak if**: access scope is undefined, consent was buried in a EULA, or the tool requests "full account access" with no granular control.
**Score strong if**: the tool lists exactly which data types it reads, scoped to a specific folder/label/repo, with no ambient monitoring.

### Question 2 — What can it DO?
Map every write or side-effecting action the tool can take without a separate confirmation:
- Send messages, emails, or calendar invites on your behalf
- Modify or delete files
- Execute code or terminal commands
- Make purchases or API calls that cost money
- Post publicly or share content externally
- Grant access to third parties

**Score weak if**: the tool can take irreversible actions (send, delete, execute, purchase) without an explicit per-action confirmation gate.
**Score strong if**: write actions require a human-in-the-loop approval step, and the tool has no ambient action authority.

### Question 3 — What does it REMEMBER?
Determine what context the tool retains across sessions and where it is stored:
- Does it save conversation history? Where? For how long?
- Does it build a user model or preferences file that persists?
- Does it store uploaded files, pasted content, or inferred facts?
- Is stored context used to train the vendor's models? (check privacy policy)
- Is there a way to delete stored context on demand?

**Score weak if**: memory is opaque, persists indefinitely, is used for model training without opt-out, or cannot be deleted.
**Score strong if**: memory is ephemeral or explicitly opt-in, retention period is stated, data is not used for training, and deletion is one click.

### Question 4 — How do you CHECK it?
Assess your ability to audit what the tool has done and is currently doing:
- Is there an activity log or audit trail?
- Can you see all sessions, actions taken, and data accessed in a dashboard?
- Does the tool send you notifications when it acts on your behalf?
- Can you revoke access instantly if behavior is unexpected?
- Is there a way to inspect the stored context it holds?

**Score weak if**: there is no activity log, no audit trail, and no way to know what the tool did last session.
**Score strong if**: a full audit log is available, access can be revoked immediately, and you receive proactive notifications for material actions.

## Phase 3: Scorecard

Present a scorecard table:

```
## [Tool Name] — Vetting Scorecard

| Dimension | Score | Key Finding |
|-----------|-------|-------------|
| SEE       | Strong / Partial / Weak | [one-line summary] |
| DO        | Strong / Partial / Weak | [one-line summary] |
| REMEMBER  | Strong / Partial / Weak | [one-line summary] |
| CHECK     | Strong / Partial / Weak | [one-line summary] |

**Overall exposure level**: Low / Medium / High / Critical
**Rationale**: [one sentence tying the four scores together]
```

Exposure level rubric:
- **Low**: 4 Strong scores — grant access with standard monitoring
- **Medium**: 1-2 Weak scores — grant limited access, review monthly
- **High**: 3 Weak scores — pilot only, review weekly, consider alternatives
- **Critical**: 4 Weak scores or any Weak on DO with irreversible actions — do not connect until vendor addresses gaps

## Phase 4: Ranked Exposure List

If the user has multiple tools to vet (or has already run this test on prior tools), rank them by overall exposure level from highest to lowest. Present as a numbered list with the overall level and the single weakest dimension per tool.

## Phase 5: One Highest-Value Move This Week

Based on the tool with the highest exposure level, recommend exactly one concrete action the user can take this week to reduce risk:
- Narrow scope (switch from "full access" to a specific folder/label)
- Enable audit logs if the option exists
- Add a confirmation gate to a specific action class
- Delete stored context and set a reminder to review in 30 days
- Switch to a scoped alternative tool that scores better on the weakest dimension

## Verification

- [ ] All 4 dimensions scored with explicit evidence, not assumption
- [ ] Score is not "Partial" by default — "Partial" must mean a specific known limitation, not uncertainty
- [ ] At least one key finding per dimension is concrete (not "unclear")
- [ ] One highest-value move is specific and actionable in under 30 minutes

## Multi-tool path

If the user wants to vet multiple tools in one session:
1. Vet each tool individually (Phases 1-3) in sequence.
2. After all tools are scored, combine into a ranked exposure list (Phase 4).
3. Give one highest-value move for the week targeting the highest-exposure tool (Phase 5).
4. Do not try to run all 4 questions for all tools simultaneously — the scorecard quality degrades.

## Prompt Kit (verbatim, for cross-platform use)

The following prompt can be copied directly into any AI assistant (ChatGPT, Gemini, etc.) for a self-assessment path when the AI does not have tool introspection access:

```
<role>You are a privacy-first AI tool auditor helping me understand what I've let into my digital life.</role>

<context>I use several AI tools that have access to my accounts, files, and communications. I want to understand my exposure level before I add more.</context>

<instructions>
Walk me through the 4-question vetting test for each AI tool I name:
1. What can it SEE? (data access scope)
2. What can it DO? (write/action authority)
3. What does it REMEMBER? (data retention and training)
4. How do I CHECK it? (audit trail and revoke)

For each question, score the tool: Strong / Partial / Weak.
After scoring, give me an overall exposure level: Low / Medium / High / Critical.
Then rank all my tools from highest to lowest exposure.
End with ONE concrete thing I can do this week to reduce my highest exposure.
</instructions>

<output>A scorecard table per tool, a ranked list, and one action item. Under 500 words total. Phone-readable.</output>

<guardrails>Do not make assumptions — if you don't know the answer for a tool, score it Partial and tell me exactly what to look up.</guardrails>
```

## Source Attribution

Technique from Nate's Newsletter (natesnewsletter@substack.com), 2026-06-29:
"Run this 4-question test before you let any AI into your files, your Slack, or your phone."
Prompt Kit fetched verbatim from: https://promptkit.natebjones.com/api/assets/20260627_899_promptkit/markdown
