---
name: three-layer-memory-scaffold
description: Scaffold a three-layer memory architecture for agent fleets — personal layer (individual operator), team layer (the squad), org layer (shared institutional knowledge). Each layer gets its own directory, curator role, and portability policy. Use when the user says "three layer memory", "memory layers", "org memory scaffold", "team memory structure", "agent fleet memory", "memory governance", "split my memory by owner", or wants to organize agent memory beyond a single flat file.
---

# Three-Layer Memory Scaffold

Initialize a structured memory architecture that separates concerns by ownership: what belongs to the individual operator, what belongs to the team, and what belongs to the whole organization. Each layer has a named curator role and an explicit portability policy so agents and humans know what memory they can read, write, export, and take with them.

## Source

Nate B. Jones — "Exclusive Interview: Tibo on Codex and the Five Leadership Chairs" (2026-05-16). The chief-of-staff chair: split agent memory into three named layers with distinct ownership; each layer gets a curator and a portability policy.

## Trigger

Use when:
- A solo operator wants to prepare for team growth (add team and org layers now, even if only personal is active)
- A team already shares memory but has no governance about what belongs where
- An agent fleet has a single shared memory file that is becoming unwieldy
- The user wants explicit rules for which agent can read which layer

## Prerequisites

- A project root (defaults to cwd)
- A decision about whether all three layers are needed now, or just two (personal + team or personal + org)

## Phase 1: Scope Interview

Ask the user:
1. **How many people or agents share this memory system?** (1 / 2-5 / 6+)
2. **Do you have memory that is personal and should not be shared?** (yes / no)
3. **Do you have memory that the whole org should know but individuals should not own?** (yes / no)
4. **What is the primary risk you want to prevent?** Examples: "agent reads personal notes it shouldn't", "new team member doesn't have institutional context", "someone leaves and takes knowledge with them"

Based on answers, recommend layers to activate (all three, or a subset). Confirm before scaffolding.

## Phase 2: Directory Structure

Create the following structure at the path the user specifies (default: `./memory/`):

```
memory/
  personal/
    README.md          # who owns this, what belongs here, portability policy
    index.md           # memory index (same format as MEMORY.md if applicable)
    [memory files...]
  team/
    README.md
    index.md
    [memory files...]
  org/
    README.md
    index.md
    [memory files...]
  GOVERNANCE.md        # curator roles, portability policies, escalation rules
```

If the user is migrating from an existing flat memory file, offer to classify existing entries into the appropriate layer.

## Phase 3: Layer README Files

Write a `README.md` for each active layer using this template:

### Personal Layer README

```markdown
# Personal Memory Layer

## What belongs here
- Individual preferences, working style, tool shortcuts
- Personal project context that others don't need
- Notes from 1:1s or personal retrospectives
- Anything that would feel odd for a colleague to read

## What does NOT belong here
- Decisions the team needs to act on → put in team/
- Institutional knowledge that should survive your departure → put in org/
- Shared project state → put in team/

## Curator role
The individual operator. You own this layer; no one else reads it by default.

## Portability policy
Fully portable. This is yours. Export and take it with you when you leave.
Suggested export: `cp -r memory/personal/ ~/personal-context-backup/`

## Agent access
By default, only agents explicitly granted personal-layer access can read this.
To grant: add `personal_memory: true` to the agent's config.
```

### Team Layer README

```markdown
# Team Memory Layer

## What belongs here
- Shared project context and decision history
- Team conventions and working agreements
- Retrospective findings the whole team acts on
- Onboarding context for new team members

## What does NOT belong here
- Personal preferences → put in personal/
- Org-wide standards that predate this team → put in org/

## Curator role
[Assign a named role, e.g., "Engineering lead" or "Weekly curator rotation"]
The curator reviews this layer monthly: prunes stale entries, reconciles
contradictions, and promotes org-level insights to org/.

## Portability policy
Team memory stays with the team, not the individual.
When a team member leaves, they do not take team/ with them.
Export for archival: create a dated snapshot at `memory/archives/team-YYYY-MM.md`.

## Agent access
All agents with project access can read team/ by default.
Write access requires curator approval or an automated PR flow.
```

### Org Layer README

```markdown
# Org Layer

## What belongs here
- Standards and rules that apply across all teams and projects
- Institutional knowledge that must survive team turnover
- Historical decisions with org-wide impact
- The org's constitutional document (if one exists)

## What does NOT belong here
- Team-specific conventions → put in team/
- Personal context → put in personal/

## Curator role
[Assign to a senior role or a dedicated "librarian" agent]
The org curator reviews quarterly: identifies gaps, retires outdated entries,
and ensures new standards are captured within 30 days of adoption.

## Portability policy
Org memory is institutional property. It does not travel with individuals.
It MUST be backed up to at least one durable external store (git, shared drive).
Export cadence: weekly automated snapshot recommended.

## Agent access
All agents can read org/ by default. No agent may write to org/ without
curator approval — org memory is the most stable layer and should change slowly.
```

## Phase 4: GOVERNANCE.md

Write a `GOVERNANCE.md` at the root of the memory directory:

```markdown
# Memory Governance

## Layer summary

| Layer | Owner | Curator | Agent read | Agent write | Portability |
|-------|-------|---------|------------|-------------|-------------|
| personal/ | Individual | Self | Explicit grant only | Self only | Fully portable |
| team/ | Team | [Role] | Default yes | Curator-approved | Stays with team |
| org/ | Organization | [Role] | Default yes | Curator-approved | Institutional property |

## Escalation rules

- An agent that wants to write to team/ or org/ must: create a PR or open a task for curator review. Never write directly.
- A rule that should apply across all teams belongs in org/, not in the project's team/ layer.
- If an entry could belong to either team/ or org/, default to team/. Promote to org/ only when the curator confirms it has cross-team value.

## Curator cadence

| Layer | Review frequency | Review task |
|-------|-----------------|-------------|
| personal/ | As needed | Prune stale entries, merge duplicates |
| team/ | Monthly | Reconcile contradictions, promote to org/ |
| org/ | Quarterly | Retire outdated entries, confirm backup integrity |

## Migration

When migrating from a flat memory file:
1. Read each entry.
2. Assign it to personal/, team/, or org/ using the "what belongs here" criteria above.
3. Move the file — do not copy. One source of truth per entry.
4. Update the MEMORY.md index if one exists at the project root.
```

## Phase 5: Agent Wiring

Offer three wiring options:

### Option A: CLAUDE.md pointer
Add to the project CLAUDE.md:
```markdown
## Memory layers
- Personal context: `./memory/personal/index.md`
- Team context: `./memory/team/index.md`
- Org standards: `./memory/org/index.md`
- Governance: `./memory/GOVERNANCE.md`
```

### Option B: Per-agent config
In each agent's config file, set memory paths explicitly:
```json
{
  "memory": {
    "read": ["./memory/team/index.md", "./memory/org/index.md"],
    "write": []
  }
}
```

### Option C: SessionStart hook
Write a hook that injects the appropriate layers based on which agent is starting:
```python
# Reads agent identity from env, injects correct layers
agent = os.environ.get("AGENT_NAME", "default")
layers = AGENT_LAYER_MAP.get(agent, ["team", "org"])
# ... inject layer summaries into session context
```

## Verification

- [ ] All active layers have a directory, README.md, and index.md
- [ ] GOVERNANCE.md is present with curator roles filled in (not left as `[Role]`)
- [ ] Every existing memory entry has been assigned to exactly one layer (if migrating)
- [ ] Agent wiring option chosen and implemented
- [ ] No hardcoded paths — all references use the root the user specified or `./memory/`
- [ ] org/ layer is backed up to at least one external store (git or equivalent)

## Output

Scaffold written to the path the user specifies (default: `./memory/`).
If migrating from a flat file, the original file is renamed to `memory/archives/pre-migration-YYYY-MM-DD.md` — not deleted.
