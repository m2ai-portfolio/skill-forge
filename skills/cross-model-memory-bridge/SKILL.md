---
name: cross-model-memory-bridge
description: "Design a portable memory layer that a user or agent can read and write from multiple AI providers (Claude, GPT, Gemini, open-source models) without re-building context each time. Produces a storage schema, read/write policy, and MCP server sketch. Trigger on: 'I want memory that works across models', 'share context between Claude and GPT', 'portable agent memory', 'model-agnostic memory', 'my memory is stuck in one AI', or any request to own context that persists across provider boundaries."
---

# cross-model-memory-bridge — provider-agnostic memory layer

Designs a memory store and access pattern that any AI provider can read and write,
so that knowledge built in one session (or with one model) carries into the next
without manual copy-paste or re-briefing.

## Purpose

AI memory is currently silo'd: context you build with one provider vanishes when
you switch to another. A cross-model bridge treats the memory store as the source
of truth and each AI provider as a stateless reader/writer — the intelligence is
rented, the memory is owned.

## Trigger

Use when the user wants persistent context that survives model switches, provider
outages, or subscription changes. Do NOT use when the user only works with one
provider and has no plans to switch.

Activation phrases:
- "I want memory that works across models"
- "share context between Claude and GPT"
- "portable agent memory"
- "model-agnostic context"
- "I don't want to lose my context if I switch providers"
- "own my AI memory"

## Tools required

- **Read / Write / Bash** — inspect and scaffold local storage files
- **WebFetch** (optional) — check MCP SDK docs if building a server interface

## Phase 1 — Inventory the user's memory needs

Ask the user to describe what they currently brief their AI on repeatedly.
Categorize into four buckets:

| Bucket | Examples |
|--------|---------|
| **Identity** | Role, goals, working style, preferences, project context |
| **Method** | Recurring procedures, decision heuristics, style guides |
| **State** | In-progress work, open decisions, project status |
| **Receipts** | What the agent did, when, and what changed |

For each item the user names: decide if it belongs in a bucket, then note its
update frequency (static / weekly / per-session / per-task).

## Phase 2 — Design the storage schema

Choose a storage format that any text-producing AI can read:

**Recommended: structured markdown files**
- One file per bucket (e.g., `memory/identity.md`, `memory/method.md`)
- YAML frontmatter for machine-readable metadata (last-updated, owner, scope)
- Prose body for human-readable content the AI can cite directly

**Alternative: SQLite with a thin MCP server**
- Good when multiple agents write concurrently or when scoping by project is needed
- Requires an MCP server to expose read/write endpoints to each provider

Produce a file-layout sketch:

```
memory/
  identity.md        # Who the user is, roles, goals — rarely changes
  method.md          # Recurring procedures and heuristics — updated per workflow change
  state/
    <project>.md     # Per-project open decisions and status — updated per session
  receipts/
    YYYY-MM-DD.md    # What changed today — append-only
```

## Phase 3 — Define the read/write policy

For each bucket, specify:

1. **Who may READ** — which agents or humans can load this file into context
2. **Who may WRITE** — which agents or humans can update this file
3. **When to update** — trigger condition (on session end, on task completion, on state change)
4. **Review gate** — does a human approve writes, or is the agent trusted to write directly?

Write-gate guideline: identity and method files require human approval before write;
state and receipt files can be agent-written with append-only semantics (never overwrite,
never delete).

## Phase 4 — MCP server sketch (optional)

If the user needs programmatic access from multiple agents or providers, sketch a
minimal MCP server with four tools:

```
memory_read(bucket, key?)    -> returns file content or filtered section
memory_write(bucket, entry)  -> appends to the appropriate file; never overwrites
memory_search(query)         -> keyword search across all buckets
memory_scope(project)        -> scopes all reads/writes to a named project subfolder
```

The server stores files in a location the user controls (configured via env var,
not hardcoded). Each AI provider connects to the same MCP endpoint — the bridge.

## Phase 5 — Provider loading instructions

Produce a one-paragraph "how to load memory" instruction block for each provider
the user intends to use:

- **Claude Code**: add the MCP server to `.claude/mcp.json`, or paste the identity
  and method files as the first message in a new session.
- **ChatGPT / GPT-4**: paste the relevant file contents in the system prompt or
  as the opening user message. Custom GPTs can use a hosted version of the memory
  server as an Action.
- **Open-source / local models**: pipe the relevant files as a prefix to the prompt.
  The schema's plain-markdown format is intentionally LLM-neutral.

## Verification

Before delivering the design:
- [ ] Each memory bucket has a named owner, read/write policy, and update trigger
- [ ] Storage format is plain text readable by any LLM (no binary, no platform-specific format)
- [ ] Write policy prevents agents from overwriting or deleting existing memory entries
- [ ] MCP server (if included) has a configured, user-owned storage path — no hardcoded paths
- [ ] At least two providers have explicit loading instructions

## Source

Nate's Newsletter, 2026-07-01 — "You can build 80% of your own AI memory by talking to the agent already on your computer"
Pattern: Open Brain — portable cross-model memory layer. Core principle: "rent the intelligence, own the memory."
URL: https://natesnewsletter.substack.com/p/open-stack-ai-memory
Field guide: https://unlock-ai.natebjones.com/guides/open-stack/open-stack-field-guide
