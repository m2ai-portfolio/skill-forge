---
name: action-classifier
description: Classify any agent action into one of 5 risk buckets (read-only, reversible-write, irreversible-write, external-send, cross-system) and route it to the correct approval gate. Use when building a judge layer, asking "classify this action", "what risk bucket is this?", "action risk taxonomy", "how dangerous is this tool call", or when setting up routing for a multi-gate approval architecture. Produces a classification decision with routing gate and rationale.
---

# Action Classifier

Before a judge can evaluate a tool call and before a proposals gate can route it, the action needs a risk classification. This skill classifies any agent action into one of 5 buckets that determine which gate it goes to.

The buckets are mutually exclusive and exhaustive for the actions a Claude-based agent typically takes. Every tool call fits exactly one bucket. If it seems to fit two, assign the higher-risk one.

## When to Use

- Setting up a judge layer and needing a routing taxonomy
- Auditing which of an agent's tool calls require human review vs. can auto-execute
- Designing a multi-gate architecture where different action types go to different evaluators
- Classifying a specific planned action before executing it

## Inputs

- A description of the planned action OR a tool call signature (name + input)
- Optional: list of all tool calls the agent has access to (for bulk classification)

## Phase 1: Classify the Action

Apply the 5-bucket taxonomy. Assign the FIRST bucket whose criteria are met (listed highest-risk first -- stop at the first match):

---

### Bucket 5: cross-system
**Definition**: The action spans multiple external systems, modifies shared infrastructure, or triggers a cascade that affects other agents, services, or users beyond the immediate target.

Criteria (any one is sufficient):
- Writes to a database, queue, or API that other agents or users read from
- Modifies infrastructure (deploy config, firewall rules, service routing)
- Triggers an automated downstream action in a different system
- Creates, deletes, or modifies a resource that another service depends on

Examples: updating a shared database record, modifying a deployment config, publishing to a message queue, changing a permission that affects multiple users.

Default gate: **QUEUE** (do not execute without specialist review)

---

### Bucket 4: external-send
**Definition**: The action sends a message, notification, or data to a person or external system outside the agent's local environment.

Criteria (any one is sufficient):
- Sends an email, chat message, SMS, or webhook
- Posts to a social platform, ticketing system, or external API with side effects
- Shares a document or link with an external recipient
- Triggers a notification to a person who did not request it in this session

Examples: sending an email, posting a Slack message, creating a GitHub issue, triggering an n8n webhook that sends a notification.

Default gate: **ASK** (get explicit approval before sending)

---

### Bucket 3: irreversible-write
**Definition**: The action modifies or deletes state that cannot be restored to its prior state without a backup or significant effort.

Criteria (any one is sufficient):
- Deletes a file, record, or resource without a recovery path
- Overwrites data without preserving the previous version
- Runs a migration or schema change with no rollback
- Truncates or clears a dataset

Examples: `rm -rf`, `DROP TABLE`, overwriting a file without backup, running a destructive migration, clearing a cache that took significant compute to build.

Default gate: **ASK** (surface the action and require confirmation before executing)

---

### Bucket 2: reversible-write
**Definition**: The action modifies local or owned state in a way that can be undone in under 5 minutes by the user without data loss.

Criteria (all must be true):
- Does not send anything to an external person or system
- Modifies only local files, local database, or owned resources
- A straightforward undo path exists (git revert, delete the created file, restore from a draft)

Examples: editing a local file, creating a draft (not sent), inserting a record into a local development database, creating a branch, staging a git commit.

Default gate: **ACT** with audit log (proceed, log the action)

---

### Bucket 1: read-only
**Definition**: The action reads, queries, or inspects state without modifying anything.

Criteria (all must be true):
- Produces no side effects
- Does not modify any file, database record, or external resource
- Cannot trigger downstream state changes

Examples: reading a file, running a SELECT query, fetching an API response, listing directory contents, checking git status.

Default gate: **ACT** (proceed without logging)

---

## Phase 2: Produce the Classification

Output a structured classification:

```
Action Classification
=====================
Action: [tool name or description]
Input summary: [key parameters in one line]

Bucket: [1-5] -- [bucket name]
Default gate: [ACT / ACT with audit log / ASK / QUEUE]
Rationale: [one sentence explaining which criterion matched]

Escalation condition: [if any, describe what would push this to a higher-risk bucket]
```

If classifying a list of tool calls, produce one row per tool in a table:

```
Tool                  Bucket              Default Gate
----                  ------              ------------
read_file             read-only           ACT
edit_file             reversible-write    ACT (audit)
delete_record         irreversible-write  ASK
send_email            external-send       ASK
update_shared_config  cross-system        QUEUE
```

## Phase 3: Gate Routing Summary

After classifying all actions, produce a gate routing summary:

```
Gate Routing Summary
====================
ACT (no log):        [tools] -- [count]
ACT (audit log):     [tools] -- [count]
ASK:                 [tools] -- [count]
QUEUE:               [tools] -- [count]
```

This summary is the input to a proposals pattern or judge layer -- each gate bucket maps to a different approval flow.

## Escalation Rules

Apply these after initial classification. If any rule matches, escalate one bucket level:

1. **Unattended execution**: agent is running autonomously (scheduled, background, no active user session) -- escalate all ASK to QUEUE, all reversible-write to irreversible-write
2. **High-frequency**: action will be called more than 10 times per session -- escalate reversible-write to irreversible-write (cumulative risk)
3. **Ambiguous target**: the target field is dynamic or user-supplied at runtime -- escalate one level (read-only stays read-only; all others go up)
4. **Cross-agent call**: the action is an A2A call to another agent -- classify as cross-system regardless of the underlying action

## Verification Checklist

- [ ] Every action assigned to exactly one bucket (no ties, no "both 3 and 4")
- [ ] Higher-risk bucket wins when ambiguous -- do not underclassify
- [ ] Escalation rules checked after initial classification
- [ ] Gate routing summary produced when classifying more than one action
- [ ] cross-system bucket used for any action that touches shared state, even if it looks like a simple write

## Source Attribution

Framework derived from Nate's Newsletter (natesnewsletter@substack.com), 2026-05-11:
"You gave your AI agent real tools. Here's the 4-part control layer it's missing + the Judge Layer implementation guide"
https://natesnewsletter.substack.com/p/agent-judge-layer-production-control

Core concept: Part 1 of the 4-part control layer -- action classification is the routing input to the judge system. Without classification, a single general-purpose gate evaluates every tool call identically, which either over-gates safe actions (breaking flow) or under-gates dangerous ones (missing the Lindy-class failure mode).
