---
name: agent-first-operating-model
description: Generate a complete agent-first operating model kit — work-object taxonomy, HIL gate definitions, permission manifests, and agent role contracts — so AI runs as managed labor rather than an ad-hoc tool.
---

# Agent-First Operating Model Kit

Produces a complete operating model scaffold for running AI as managed labor: work objects, gate definitions, permission manifests, and agent role contracts. The output is a set of governance primitives a team can actually enforce, not just a philosophy.

## Trigger

Use when someone says "I want to set up an AI team structure", "move from ad-hoc tools to managed AI", "create CLAUDE.md rules for my org", "set up gates and permissions for agents", "need an agent operating model", "how do I manage AI like employees", or "AI spend isn't producing outcomes I can measure".

## Phase 1: Current-State Intake

Gather the minimum context to generate a relevant kit:

1. **Team size** — how many humans, how many AI agents (current or planned)?
2. **Primary domain** — software development, content, research, ops, or mixed?
3. **Existing AI tools** — which models/platforms are in use?
4. **Current pain** — what is broken about how AI is used today? (pick the closest)
   - "We have no visibility into what agents do"
   - "Costs are unpredictable"
   - "Quality is inconsistent"
   - "Humans are bottlenecks on every decision"
   - "We use AI but it doesn't compound over time"
5. **Risk tolerance** — can agents make changes autonomously, or does every action need review?

## Phase 2: Work-Object Taxonomy

Define the types of work the AI system handles. Produce a table:

| Work Object | Description | Owner (human or agent) | Output Contract |
|-------------|-------------|----------------------|-----------------|
| [name] | [what it is] | [who is responsible] | [what done looks like] |

Rules for work objects:
- Each object must have ONE clear owner — no joint ownership
- The output contract must be testable (not "good quality", but "a diff with passing tests" or "a published post with >N words")
- Agents process work objects, not named tasks — this makes pipelines swappable
- 5–10 objects is the right range; more than that means the taxonomy is too granular

Produce 5–10 work objects appropriate to the stated domain.

## Phase 3: Gate Definitions

Gates are decision points where work must pause for human review. Over-gating kills speed; under-gating creates blast-radius risk. Produce a gate inventory:

| Gate Name | Trigger Condition | Reviewer Role | Timeout Behavior | Risk If Skipped |
|-----------|------------------|---------------|------------------|-----------------|
| [name] | [what trips it] | [who reviews] | [what happens if no response in N min] | [the risk] |

Starting set of gates (adapt to domain):
- **Proposal gate** — before any agent takes an irreversible action
- **Cost gate** — before any spend above a defined threshold
- **External-publish gate** — before any content goes public
- **Data-mutation gate** — before write operations on production data
- **Escalation gate** — when an agent would loop more than N times on the same problem

For each gate, specify whether it is a hard block (work stops) or a soft alert (work continues with notification). Default: high-stakes gates are hard blocks; monitoring gates are soft alerts.

## Phase 4: Permission Manifests

Translate the gate definitions into permission primitives. For Claude Code projects, produce a starter `settings.json` permissions block and a CLAUDE.md section:

**settings.json block:**
```json
{
  "permissions": {
    "allow": [
      "Read(*)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(npm test)",
      "Bash(pytest *)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(git push --force *)",
      "Bash(git reset --hard *)"
    ]
  }
}
```

**CLAUDE.md permissions section:**
```markdown
## Agent Permissions

### Autonomous (no gate required)
- Read any file
- Run tests (read-only)
- Create branches
- Draft pull requests

### Requires HIL gate
- Merging to main or default branch
- Deploying to production
- Writing to external APIs or third-party services
- Deleting files or records
- Spending money or triggering billing events
```

Adjust both for the stated risk tolerance from Phase 1. Lower risk tolerance → more items in the gate list; higher tolerance → move items to autonomous.

## Phase 5: Agent Role Contracts

For each distinct agent role needed, produce a role contract. Use a generic naming convention (Coder, Researcher, Publisher, Reviewer, etc.) — not product-specific names.

```markdown
## Role: [Agent Role Name]

**Domain**: [what area this agent owns]
**Work objects**: [which objects from Phase 2 this agent processes]
**Authorized tools**: [what tools/permissions it has]
**Gates it observes**: [which gates apply to it]
**Escalation path**: [who/what it escalates to when stuck]
**Max turns per task**: [turn budget — e.g., 30 turns for coding, 15 for research]
**Success signal**: [how you know the task is done correctly]
```

Draft 2–4 role contracts appropriate to the domain. Cover at least: a doer (takes work objects and produces outputs) and a reviewer (validates outputs against contracts).

## Phase 6: CLAUDE.md Starter Pack

Produce a minimal CLAUDE.md the team can drop into their project root. Include:

1. **Hard rules** — the non-negotiables derived from the gate definitions
2. **Work-object definitions** — brief list from Phase 2
3. **Escalation ladder** — who/what to contact when stuck
4. **Verification loop** — what checks to run before declaring a task done

Keep it to one screen. Long CLAUDE.md files are not read.

## Output Format

Deliver as a single Markdown document with labeled sections:

```markdown
# [Project Name] Agent Operating Model

## Work Objects
[Phase 2 table]

## Gates
[Phase 3 table]

## Permission Manifest
[Phase 4 blocks]

## Role Contracts
[Phase 5 contracts]

## CLAUDE.md Starter
[Phase 6 content]
```

## Verification

The kit is complete when:
- Every work object has a named owner and a testable output contract
- Every irreversible action type has a corresponding gate
- The permission manifest is copy-paste ready (no placeholder values)
- At least one role contract covers the primary agent type for the domain
- The CLAUDE.md starter fits on one screen (~50 lines max)

## Source

Extracted from Nate Kadlac newsletter (2026-06-07) — "Executive Briefing: Uber Burned Its Entire AI Budget Early. The Bill Was Trying to Tell Them Something." Idea 6: Agent-First Operating Model Kit — replacing token-cap governance with work objects, gates, permissions, and agent role contracts that turn AI spend into compounding organizational advantage.
