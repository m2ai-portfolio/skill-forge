---
name: ai-exit-lever-auditor
description: Audit the six exit levers (export, inspect, revoke, route, keep-local, prove) for each AI tool or service already in your stack. Scores how locked in you are, names the missing lever per tool, and gives one concrete ask per gap. Use when evaluating how hard it would be to leave a connected AI tool, before expanding usage of any AI service, or when the user says "exit test", "how locked in am I", "AI lock-in audit", "can I leave this tool", "portability check".
---

# AI Exit Lever Auditor

For AI tools you are already using, score how locked in you are across six exit levers and identify the single missing lever that matters most. The exit test is not about whether the tool is good -- it is about whether leaving is a data problem.

## When to trigger

- "exit test for [tool]"
- "how locked in am I to [tool]"
- "can I leave [service] without losing my context?"
- "portability audit"
- "AI lock-in audit"
- Before expanding usage of any AI service (upgrading plan, adding team seats, integrating into a core workflow)
- When evaluating a vendor migration or consolidating your AI stack

Do NOT trigger for pre-commitment evaluation (before you have used the tool at all) -- that is a different surface.

## Prerequisites

- At least one AI tool or service the user is currently using
- Optional: access to the tool's settings, data export page, or privacy policy

## The Six Exit Levers

Each lever addresses one way a tool creates switching cost. A tool with all six levers present is easy to leave. A tool missing most of them has captured your context.

| Lever | The question it answers |
|-------|------------------------|
| **EXPORT** | Can you download everything the tool knows, in a format you own? |
| **INSPECT** | Can you see a log of what the tool did -- every action, every access? |
| **REVOKE** | Can you instantly cut the tool's access without disrupting other tools? |
| **ROUTE** | Can you send the same work through a different model or tool without rebuilding the setup? |
| **KEEP-LOCAL** | Are the prompts, rules, and memory that make the tool useful stored somewhere you own? |
| **PROVE** | Can you demonstrate to an auditor what the tool did and did not do? |

## Phase 1: Intake

Ask the user to name the tool(s) to audit. For each tool, ask:

1. **What does this tool have access to?** (files, email, calendar, Slack, code repos, browser, phone)
2. **What do you use it for?** (summarization, drafting, task execution, search, scheduling)
3. **How long have you been using it?** (rough order of magnitude: days / months / years)

If auditing multiple tools, process one at a time. Announce the current tool before starting each audit.

## Phase 2: Six-Lever Audit

For each lever, score: **PRESENT** (lever exists and works) / **PARTIAL** (lever exists but limited or untested) / **MISSING** (no lever, or lever is hidden behind support request).

### Lever 1 — EXPORT

Does the tool let you download your complete context in a portable format?

- **PRESENT**: Data export is available in the product UI or via an API. You have the option to download conversation history, memory, stored files, and configuration in a standard format (JSON, Markdown, CSV, plain text).
- **PARTIAL**: Export exists but is incomplete (some data types excluded), hard to find, or outputs in a proprietary format that requires vendor tools to read.
- **MISSING**: No documented export path. Data is visible in the UI but not downloadable. Export requires contacting support or canceling the account.

Risk of MISSING: If you stop paying, your accumulated context (conversation history, preferences, custom instructions, stored files) may be unrecoverable.

### Lever 2 — INSPECT

Can you audit what the tool actually did?

- **PRESENT**: An activity log or audit trail is available showing which data was accessed, what actions were taken, and when. Log is searchable and covers at least 30 days.
- **PARTIAL**: Some logging exists (e.g., chat history visible but no action log; or logs exist but only for admin-tier accounts).
- **MISSING**: No activity log. You cannot determine what the tool accessed or what it did in a past session without memory of your own session.

Risk of MISSING: You have no way to detect unexpected behavior, verify compliance, or reconstruct what the tool did during an incident.

### Lever 3 — REVOKE

Can you cut the tool's access instantly and independently?

- **PRESENT**: You can revoke this tool's access (OAuth token, API key, connector permission) in one step, without affecting other tools or services. Revocation takes effect immediately.
- **PARTIAL**: Revocation requires multiple steps (e.g., change password to invalidate all sessions), affects other services, or has a delay before taking effect.
- **MISSING**: No revocation path short of canceling the entire account or contacting support. Access cannot be narrowed post-grant.

Risk of MISSING: A misbehaving or compromised tool cannot be isolated without collateral disruption to your other services.

### Lever 4 — ROUTE

Can you run the same workflow through a different model or provider?

- **PRESENT**: The tool's instructions, prompts, and standing rules are in a format (markdown, YAML, plain text) that can be loaded into a different model or service. Switching is a configuration change, not a rebuild.
- **PARTIAL**: Some configuration is portable but core logic (system prompts, fine-tuning, vendor-specific integrations) is tied to this vendor.
- **MISSING**: The workflow exists only inside the vendor's product. No instructions have been extracted. Reproducing the same behavior on a different tool would require starting over.

Risk of MISSING: Price increases, model changes, or vendor outages force you to rebuild, not just switch.

### Lever 5 — KEEP-LOCAL

Is the intelligence that makes this tool useful stored somewhere you own?

- **PRESENT**: All standing instructions, custom prompts, memory, and context are in files you own (version-controlled repo, local files, or a portable format). The vendor is the runner, not the keeper.
- **PARTIAL**: Some configuration is in files you own, but key parts (memory, fine-tuning, saved conversations used to seed behavior) live only in the vendor's product.
- **MISSING**: The system prompt, trained preferences, and context are all inside the vendor's product. There are no files you own that reproduce the tool's behavior.

Risk of MISSING: If the vendor changes the product, loses data, or shuts down, you lose the accumulated configuration investment.

### Lever 6 — PROVE

Can you demonstrate to an external party what this tool did and did not do?

- **PRESENT**: Audit-grade records exist: timestamped logs of actions, data accessed, and decisions made. These can be exported and presented to legal, security, or compliance reviewers.
- **PARTIAL**: Some records exist (e.g., chat history) but they lack the metadata (timestamps, data access scope, action receipts) needed for a formal audit.
- **MISSING**: No audit-grade records. You could not reconstruct tool behavior for a compliance review, legal hold, or incident investigation.

Risk of MISSING: In a regulated environment, using a tool without provable records may itself be a compliance violation.

## Phase 3: Lock-In Scorecard

Produce a scorecard table for each tool:

```
## [Tool Name] — Exit Lever Scorecard

| Lever         | Status   | Gap Summary                          |
|---------------|----------|--------------------------------------|
| EXPORT        | PRESENT / PARTIAL / MISSING | [one line]  |
| INSPECT       | PRESENT / PARTIAL / MISSING | [one line]  |
| REVOKE        | PRESENT / PARTIAL / MISSING | [one line]  |
| ROUTE         | PRESENT / PARTIAL / MISSING | [one line]  |
| KEEP-LOCAL    | PRESENT / PARTIAL / MISSING | [one line]  |
| PROVE         | PRESENT / PARTIAL / MISSING | [one line]  |

Lock-In Score: X/6 levers PRESENT (Y PARTIAL, Z MISSING)
Exit difficulty: Easy / Moderate / Hard / Trapped
```

Exit difficulty rubric:
- **Easy (5-6 PRESENT)**: Leaving is a config change. Use freely.
- **Moderate (3-4 PRESENT)**: Leaving costs effort but not data. Review annually.
- **Hard (1-2 PRESENT)**: Leaving means losing significant context. Limit scope of integration. Start building KEEP-LOCAL structure now.
- **Trapped (0 PRESENT)**: You cannot leave without losing everything. Freeze expansion until at least 3 levers are established.

## Phase 4: Critical Missing Lever

Name the single missing lever that matters most for this tool, given its access scope:

- If the tool has WRITE access to production data: REVOKE is most critical (inability to cut access quickly is highest blast-radius risk).
- If the tool holds accumulated context (memory, preferences, long history): KEEP-LOCAL is most critical.
- If the tool is used in a regulated domain: PROVE is most critical.
- Otherwise: EXPORT is the default most critical missing lever.

## Phase 5: One Ask per Gap

For each MISSING lever, provide a concrete ask the user can make to the vendor or take as a self-help action:

```
Lever: [LEVER NAME]
Ask: "[Specific, documentable request -- one sentence]"
Self-help alternative: "[What the user can do unilaterally if the vendor cannot provide this]"
```

Keep each ask to one action. Prefer asks for documented evidence, not vendor reassurances.

## Verification

A complete audit has:
- All 6 levers scored (PRESENT/PARTIAL/MISSING) with explicit evidence, not assumption
- An exit difficulty tier assigned
- The critical missing lever named with its specific risk called out
- One ask per MISSING lever that is concrete and actionable

## Source Attribution

Framework derived from Nate's Newsletter (natesnewsletter@substack.com), 2026-06-29:
"Run this 4-question test before you let any AI into your files, your Slack, or your phone."
Exit levers operationalize the six portability demands discussed in the article's "exit test" section.
