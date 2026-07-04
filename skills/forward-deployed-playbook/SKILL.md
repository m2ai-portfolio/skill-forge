---
name: forward-deployed-playbook
description: Generate an implementation-first plan for any AI deployment. Inverts the "pick a model, then figure out the rest" sequence — starts with data access, permissions, audit hooks, and governed action paths before model selection. Use when the user says "forward-deployed playbook", "implementation-first plan", "build room plan", "model selection last", "data first AI plan", "implementation before strategy", "technical-first planning", or wants a client-ready AI deployment brief that leads with what the agent touches, not which model it uses.
---

# Forward-Deployed Playbook

Generate a structured AI deployment plan that leads with implementation reality — what the agent accesses, what it can authorize, how it is audited — and defers model selection until those constraints are defined. Addresses the procurement failure mode Nate Kadlac identifies: most AI deployments start with "which model?" and fail when the agent hits data access walls, undefined audit boundaries, or unauthorized action paths.

## When to Use

- Starting a new client AI engagement and need a scoping brief that survives technical review
- Planning a new agent feature and want to define authority boundaries before architecture
- Reviewing an existing AI deployment plan that starts with model selection
- Producing a "build room" deliverable that finance and technical reviewers can both sign off on

## Inputs

1. **Goal** (required): one sentence — what the agent is supposed to accomplish
2. **Access context** (optional): what systems, databases, or APIs the agent will touch
3. **Audience** (optional): internal tool / client-facing product / enterprise deployment — affects how detailed the permission model section needs to be

If inputs 2 or 3 are missing, ask before proceeding.

## Phase 1: Data Access Inventory

Map what the agent needs to read and write to accomplish the goal. For each data source:

- **Source name**: database, API, file system, SaaS tool
- **Access type**: read-only / read-write / write-only
- **Data sensitivity**: public / internal / confidential / regulated (PII, PCI, HIPAA)
- **Current permission state**: accessible today / requires provisioning / blocked by policy

Output a table. Flag any regulated or write-access sources — these determine where the permission model has hard constraints.

## Phase 2: Permission Model

Define the authorization structure before the agent is written. For each access type identified in Phase 1:

- **Who authorizes the agent?** Named human role or automated policy
- **Scope of authority**: exactly what operations are permitted (not "access to CRM" — "read contact records, create follow-up tasks, no delete")
- **Credential mechanism**: OAuth token / API key / service account / ambient auth — and how it rotates
- **Revocation path**: how a human stops the agent from acting (kill switch, token expiry, role removal)

Flag any access that lacks a named authorizer or a clear revocation path.

## Phase 3: Audit Hooks

Define what must be logged before a single line of agent code is written. For each action class (read, write, external-send, irreversible):

- **What gets logged**: action type, target, parameters, timestamp, triggering user/session
- **Where it goes**: append-only log / audit DB / SIEM
- **Retention**: how long, and who has read access
- **Compliance anchor**: any regulatory requirement this log satisfies (SOC 2, HIPAA, GDPR)

If no audit anchor is identified, note it explicitly. A deployment with write actions and no audit log is not production-ready regardless of model choice.

## Phase 4: Governed Action Paths

Classify every action the agent takes into one of four tiers:

| Tier | Definition | Default gate |
|------|-----------|--------------|
| **Autonomous** | Reversible, read-only or low-blast-radius, bounded cost | No gate — agent acts |
| **Supervised** | Irreversible OR affects shared state OR non-trivial cost | Propose + human approve |
| **Scheduled** | Recurring batch with pre-approved scope | Scheduled approval, anomaly alert |
| **Escalate** | Outside scope, novel situation, or cost spike | Always surface to human |

For each action from the Data Access Inventory, assign a tier and name the gate mechanism (PreToolUse hook, HIL gate, approval webhook, etc.).

## Phase 5: Model Selection

Only now: recommend the model tier. With Phases 1-4 defined, the selection criteria are concrete:

- **Latency budget**: can the task tolerate the p95 latency of a frontier model, or does it need a faster tier?
- **Context window**: does the task require multi-document reasoning, or is it per-record?
- **Tool call volume**: high-frequency tool use favors models with low tool-call overhead
- **Audit requirements**: some regulated environments require model-version pinning and reproducibility
- **Cost ceiling**: given the estimated call volume and the permission model's cost-boundary rules, which model tier fits the budget?

State the recommended model tier and the one or two criteria that drove the choice. If multiple tiers are defensible, say so — don't fabricate precision.

## Output Format

```
## Forward-Deployed Playbook — [Goal Summary]

### Phase 1: Data Access
[Table: Source | Type | Sensitivity | Status]
Flags: [any regulated or write-access sources]

### Phase 2: Permission Model
[Per-source: authorizer, scope, credential, revocation]
Flags: [any missing authorizer or revocation path]

### Phase 3: Audit Hooks
[Per-action-class: what, where, retention, compliance anchor]
Flags: [any write action without an audit log]

### Phase 4: Governed Action Paths
[Table: Action | Tier | Gate mechanism]

### Phase 5: Model Selection
Recommended tier: [name]
Rationale: [1-2 sentences, citing the binding constraint from phases 1-4]

### Implementation Sequence
1. Provision [named access]
2. Implement [named audit hook]
3. Wire [named gate mechanism] to [named action]
4. Deploy model tier [name] with [specific config]
5. [...]
```

## Verification

A good playbook:
- Has a named human authorizer for every write-access source (Phase 2)
- Has an audit log for every Supervised or Escalate action (Phase 3)
- Defers model selection until Phase 5 — any plan that opens with model choice has the sequence inverted
- Produces an Implementation Sequence in which no model config step appears before the audit hook step
- Does not use "TBD" for revocation paths on write-access sources — that is a deployment blocker, not a detail to figure out later

## Source

Extracted from Nate Kadlac newsletter (2026-05-10) — "Executive Briefing: Six announcements in 48 hours just changed how enterprise AI gets bought" — idea #6 (Forward-Deployed Engineering Playbook Generator). Codifies the build-room-first sequencing argument into a standalone planning skill.
