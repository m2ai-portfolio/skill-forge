---
name: agent-first-operating-model-kit
description: Scaffold an agent-first operating model for a project or organization — defining work objects, HIL gates, permission manifests, and agent role contracts that replace ad-hoc token caps with a managed-labor framework. Use when the user says "agent operating model", "manage AI as labor", "define agent permissions", "agent governance scaffold", "work objects", or wants to move from informal AI use to a structured autonomous agent system.
---

# Agent-First Operating Model Kit

Transforms informal AI usage into a managed-labor system. Instead of controlling agents by adjusting token limits or seat licenses, this kit produces the governance artifacts that let you run agents like a workforce: defined roles, bounded permissions, explicit human approval points, and feedback loops that turn usage into compounding advantage.

Addresses the "invisible labor" failure mode: organizations can see token spend but cannot connect it to outcomes because there is no system for managing the work — only for purchasing the capability.

## When to Use

- You have multiple agents running and no consistent model for what each one owns or is allowed to do autonomously
- Token spend is growing but you cannot attribute it to business outcomes
- You are onboarding a new agent and want to define its scope before it runs unsupervised
- You want to replace ad-hoc "stop when something feels wrong" instincts with explicit, auditable gates

## Prerequisites

- At least one agent is running or planned (Claude Code, scheduled tasks, or A2A workers)
- You can describe the kinds of work the agent does in plain English
- You have 30-60 minutes for the initial scaffolding session

## Phases

### Phase 1 — Inventory Work Objects

A work object is a discrete, attributable unit of AI work: a commit, a report, a drafted email, a code review, a support ticket resolution. Work objects make invisible labor legible.

For each agent (or agent role) in scope:

1. List the 3-5 most common tasks the agent performs.
2. For each task, define:
   - **Output**: what artifact does it produce? (file, message, PR, row in a table)
   - **Scope**: which parts of the system does it touch?
   - **Attribution**: how would you know the agent did this vs a human?

Produce a `work-objects.md` table:

```markdown
| Work Object | Agent | Output | Scope | Attribution Signal |
|-------------|-------|--------|-------|-------------------|
| Draft PR description | coding-agent | PR body text | GitHub PR | authored-by tag |
| Weekly summary report | research-agent | Markdown doc | ./reports/ | file timestamp + agent ID |
```

### Phase 2 — Map HIL Gates

A gate is a point where the agent must pause and surface its work for human review before proceeding. Gates are not failure states — they are load-bearing approval checkpoints.

For each work object, answer:

- **Is this reversible?** (Can the action be undone in < 5 minutes? → low gate pressure)
- **Is this visible to others?** (Will an external party see this before you can review it? → gate required)
- **Does this touch a shared resource?** (Database, production config, external API → gate required)

Gate levels:
- **G0 — No gate**: fully autonomous, logged only
- **G1 — Soft gate**: agent surfaces a summary; human can veto within N minutes; proceeds if no response
- **G2 — Hard gate**: agent halts; explicit approval required before proceeding
- **G3 — Pre-approval gate**: human defines the work object before agent starts; agent executes within the defined scope only

Produce a `gates.md` file listing each work object and its gate level with rationale.

### Phase 3 — Write Permission Manifests

A permission manifest defines what the agent is allowed to do autonomously, what it must ask about, and what is categorically off-limits.

Template for each agent role:

```markdown
## Agent Role: <name>

### Autonomous (G0/G1)
- [ ] Read any file in the project root
- [ ] Run read-only CLI commands (git log, grep, ls)
- [ ] Write draft files to ./output/ or ./tmp/

### Requires Approval (G2)
- [ ] Commit to any branch
- [ ] Send messages to external services (email, Slack, API calls)
- [ ] Modify shared configuration files

### Prohibited
- [ ] Push to main/master directly
- [ ] Delete files or branches
- [ ] Access credentials or secrets files
- [ ] Execute commands with --force or destructive flags
```

Produce a `permissions/<agent-role>.md` for each role. Wire these into the agent's CLAUDE.md or system prompt as hard rules using imperative language ("NEVER", "ALWAYS", "MUST").

### Phase 4 — Draft Agent Role Contracts

A role contract is the single source of truth for what an agent owns, what it is accountable for, and how it hands off to other agents or humans.

Contract template:

```markdown
## Role Contract: <agent-name>

**Owns**: <what domain or function>
**Does not own**: <explicit exclusions>
**Inputs**: <what triggers this agent — a message, a schedule, a file in a queue>
**Outputs**: <what it produces and where it puts it>
**Escalates to human when**: <list of conditions>
**Handoff protocol**: <how it signals completion and to whom>
**Success metric**: <how you know this agent is working>
```

Produce a `contracts/<agent-name>.md` for each active agent.

### Phase 5 — Wire and Verify

1. Copy the permission manifest rules into the agent's CLAUDE.md (or equivalent system prompt file).
2. Add gate enforcement: for G2 gates, ensure the agent's workflow includes a `AskUserQuestion` or equivalent pause before the gated action.
3. Run a smoke test: trigger the agent on a low-stakes work object and confirm it halts at the first G2 gate before proceeding.
4. Produce a summary `operating-model-index.md` listing all roles, their contracts, and gate map.

## Output Artifacts

```
operating-model/
  work-objects.md        # inventory of all work types by agent
  gates.md               # gate level for each work object with rationale
  permissions/
    <agent-role>.md      # per-role permission manifest
  contracts/
    <agent-name>.md      # per-agent role contract
  operating-model-index.md  # master index linking all artifacts
```

Place these under a `./operating-model/` directory in the project root, or wherever the user's agent configurations live. Do not assume a specific vault or config path.

## Verification

- [ ] Every active agent has a role contract
- [ ] Every G2 gate has an explicit enforcement mechanism (not just documentation)
- [ ] No permission manifest contains "allowed to do anything" or equivalent open-ended grants
- [ ] The smoke test confirmed at least one gate halt before proceeding

## Source Attribution

Concept extracted from Nate's Newsletter, 2026-06-07: *"Executive Briefing: Uber Burned Its Entire AI Budget Early. The Bill Was Trying to Tell Them Something."* — specifically Part 4 (replacing the token cap with an operating model built on work objects, gates, permissions, and training) and the core thesis that invisible agent labor requires a managed-labor framework, not just spend limits.
