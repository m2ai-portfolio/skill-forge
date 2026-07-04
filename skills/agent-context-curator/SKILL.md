---
name: agent-context-curator
description: Define and initialize a Curator agent role whose only job is owning a shared team-layer memory corpus — pruning stale entries, reconciling contradictions, surfacing what's been forgotten, and routing new context to the right layer. Produces an agent manifest, a scheduled task definition, and an initial audit of the existing memory corpus. Use when the user says "curator agent", "memory curator", "librarian agent", "team memory owner", "who owns the context", "prune stale memories", or wants a dedicated agent role for maintaining shared context across a multi-agent team.
---

# Agent Context Curator

Initialize a Curator agent role for a multi-agent team. The Curator owns the team-layer memory corpus: it prunes entries that have expired or been superseded, reconciles contradictions between memory files, surfaces context that is likely forgotten but still load-bearing, and routes new context to the correct layer (personal / team / org).

## Source

Nate's Newsletter, 2026-05-16: Tibo interview — "The ops leader's job is not to BE the second pair of eyes; it is to DESIGN the second pair of eyes as a system. For memory, the equivalent is a named Curator role: someone whose incentive is to own the corpus, not just add to it."

## When to Use

- Running a multi-agent team where each agent has read access to a shared memory directory
- MEMORY.md index is approaching its line ceiling and entries are becoming stale
- Multiple agents are writing to the same memory corpus without reconciliation
- Weekly/monthly maintenance cost of reviewing memory manually is too high

## Memory Layer Model

The Curator operates over three named layers:

| Layer | Owner | Scope | Examples |
|-------|-------|-------|---------|
| **Personal** | Individual operator | One person's working style, preferences, personal history | taste profiles, individual feedback memories, per-project notes |
| **Team** | Curator agent | Shared context for the current working group | decisions made together, agreed conventions, shared incident lessons |
| **Org** | Curator agent + human lead | Durable institutional knowledge | constitutional docs, architectural principles, escalation policies |

The Curator writes to team and org layers. It reads all three but never modifies personal-layer files.

## Phase 1: Inventory Existing Corpus

Read the memory directory (default: `memory/` in the agent config root, or `.claude/projects/<project>/memory/`).

For each memory file, extract:
- `name` — the slug from frontmatter
- `type` — user / feedback / project / reference
- `last_modified` — file mtime
- `body_length` — rough token estimate
- `link_count` — how many `[[name]]` references exist in the body

Classify each entry:
- **Active** — referenced by at least one other memory, or modified in the last 30 days
- **Stale** — unmodified for >60 days AND zero incoming references
- **Orphan** — has `[[references]]` to files that do not exist
- **Contradicted** — contains a claim that conflicts with a more recent memory file

Output a triage table before making any changes.

## Phase 2: Pruning Pass

For each **stale** entry:
1. Read the full body and determine if the information is still valid (ask the operator if uncertain)
2. If superseded by a newer memory: archive it to `memory/archive/<name>.md` with a header note `archived: <date>, superseded_by: <newer-name>`
3. If still valid but rarely accessed: add a `decay: low_priority` frontmatter flag; do not delete

For each **orphan** entry:
1. Replace broken `[[references]]` with plain text equivalents if the linked memory was deleted
2. Add a `# Orphaned References` section at the bottom listing what was removed and why

For each **contradicted** entry:
1. Flag both files with a `# CONFLICT` comment block
2. Do NOT auto-resolve — surface the conflict for operator review

## Phase 3: Reconciliation Pass

Scan for semantic overlaps across all team-layer memories:

```
For each pair of memory files in team/ or org/ layer:
  - If body_similarity > threshold (approximate): flag as potential duplicate
  - Present both to operator: "These cover the same topic. Merge, keep both, or archive one?"
```

Merge procedure: concatenate bodies, reconcile contradictions, update MEMORY.md index entry, archive the merged-away file.

## Phase 4: Routing Pass

Check the intake queue (default: `memory/intake/` — a directory where agents drop raw context without classifying it):

For each intake file:
1. Read the body
2. Classify layer: personal / team / org
3. Classify type: user / feedback / project / reference
4. Write to the correct layer directory with proper frontmatter
5. Add to MEMORY.md index
6. Delete from intake/

If no intake directory exists, create it and document it as the drop point for unclassified context.

## Phase 5: Generate Agent Manifest

Produce the Curator agent manifest:

```yaml
# agent.yaml
name: curator
display_name: Context Curator
description: Owns and maintains the team-layer memory corpus. Prunes stale entries, reconciles contradictions, routes new context to the correct layer.
schedule:
  type: cron
  expression: "0 8 * * 0"   # weekly, Sunday 8am
  max_turns: 40
skills:
  - agent-context-curator
memory_access:
  read: [personal, team, org, intake]
  write: [team, org, archive, intake]
  deny_write: [personal]
escalation_triggers:
  - type: contradiction
    action: surface_to_operator
  - type: stale_count
    threshold: 20
    action: surface_to_operator
```

## Phase 6: Scheduled Task Definition

Generate a cron task definition for the Curator's weekly run:

```json
{
  "name": "curator-weekly",
  "schedule": "0 8 * * 0",
  "prompt": "Run the agent-context-curator skill. Inventory the memory corpus at memory/, triage stale and orphaned entries, reconcile contradictions, and route any files in memory/intake/. Surface a summary of changes made and any unresolved contradictions for operator review.",
  "agent": "curator",
  "max_turns": 40,
  "output": "memory/curator-log-<date>.md"
}
```

## Verification

- Curator manifest exists at `agents/curator/agent.yaml`
- `memory/intake/` directory exists and is documented
- Triage table was produced before any mutations
- No personal-layer files were modified
- Contradictions were flagged, not auto-resolved
- MEMORY.md index reflects all changes

## Output

- `agents/curator/agent.yaml` — agent manifest
- `agents/curator/AGENT.md` — system prompt (brief: role + access policy + escalation triggers)
- `tasks/curator-weekly.json` — scheduled task definition
- `memory/intake/` — intake directory (created if missing)
- `memory/curator-log-<date>.md` — audit log of this run
