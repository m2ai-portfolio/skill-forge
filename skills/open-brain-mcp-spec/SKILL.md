---
name: open-brain-mcp-spec
description: "Produce an implementation spec for a portable memory MCP server — a personal knowledge store that any MCP-compatible AI agent can read from and write to, regardless of which AI product is running the session. The spec covers the data model, read/write policy, eviction rules, per-host adapter contract, and scoping model. Use when you want memory that follows you across AI tools rather than being locked to one product's session, or when you need multiple agents to share a common context store."
---

# open-brain-mcp-spec

Produces a concrete build spec for a portable memory MCP server you own and control. The server is the single source of truth for context that multiple AI agents — potentially running in different products — can read and write without duplicating or losing state across tool switches.

This skill answers "what exactly do I need to build" rather than "what memory pattern should I use." The output is an implementation-ready spec: data model, tool surface, policy rules, and integration contract. Building the server is the next step after this spec.

## Trigger

Use when the user says "I want to own my AI memory", "build me a memory MCP server", "I want one memory that works across Claude and GPT", "I don't want to start from scratch in every session", "spec out an Open Brain", "portable memory for my agents", "cross-model context store", or "memory that travels with me".

## Phase 1: Scope Interview

Ask one question at a time if not already stated:

1. **What kinds of things need to be remembered?**
   - User preferences and working style
   - Project-specific context (decisions, constraints, active tasks)
   - Reference knowledge (docs, patterns, standards)
   - Conversation continuations (where a session left off)
   - Cross-agent state (what one agent told another)

2. **Which agent hosts need to connect?**
   - Same host, multiple sessions (e.g., Claude Code only)
   - Multiple products (e.g., Claude + a coding agent + a research agent)
   - Human-facing tools too (e.g., a note-taking app or task manager)?

3. **What are your privacy requirements?**
   - Fully local (server runs on your machine, data never leaves)
   - Cloud-hosted but private (encrypted, single-tenant)
   - No constraint

4. **What is the expected memory volume?**
   - Small (< 1,000 entries, a personal knowledge base)
   - Medium (1,000–50,000 entries, team or project portfolio)
   - Large (50,000+, organizational or research corpus)

## Phase 2: Data Model Spec

Every memory entry in the store has these fields:

```
Entry {
  id:          string         // stable UUID; never reused
  content:     string         // the memory text (the thing being remembered)
  scope:       string         // who/what can see this: "global" | "agent:<name>" | "project:<id>" | "user:<id>"
  tags:        string[]       // searchable labels (e.g., ["decision", "auth", "2026-07"])
  source:      string         // what created this: "human" | "agent:<name>" | "import"
  importance:  float 0–1      // 0 = ephemeral, 1 = permanent; drives eviction
  created_at:  ISO 8601
  accessed_at: ISO 8601       // updated on every read
  expires_at:  ISO 8601|null  // null = no expiry; set for session-scoped entries
  embedding:   float[]|null   // vector for semantic search; null if search not enabled
}
```

Adapt the scope field to match the host list from Phase 1:
- Single host, multiple sessions: scope values are `"global"` and `"project:<id>"`
- Multiple AI products: add `"agent:<product-name>"` scopes so each product has a private lane plus a shared `"global"` lane
- Multi-user: add `"user:<id>"` scope and a shared `"team"` scope

## Phase 3: MCP Tool Surface

Expose exactly these tools on the MCP server. No more; a larger surface creates unnecessary permission scope.

```
memory_write(content, scope, tags, importance, expires_at?)
  → writes a new entry; returns entry id
  → if content is near-duplicate of an existing entry (cosine similarity > 0.95), update instead

memory_read(query, scope?, tags?, limit?)
  → semantic search if embeddings enabled; lexical fallback if not
  → filters by scope and tags if provided
  → returns top-limit entries ranked by relevance × importance × recency

memory_update(id, patch)
  → updates content, tags, importance, or expires_at on an existing entry
  → logs the change with a timestamp

memory_delete(id)
  → hard-delete; returns confirmation
  → reserved for explicit human action; agents may not call this without a gate

memory_list(scope?, tags?, limit?)
  → returns entries without semantic search; useful for browsing or export

memory_stats()
  → returns entry count, scope distribution, oldest and newest entries
  → no entry content exposed; safe to call from any host
```

**What agents should NOT be able to do via MCP:**
- Delete entries without a human approval gate
- Change the scope of an entry (scope is set on write; immutable after)
- Read entries outside their own scope without an explicit `global` grant

## Phase 4: Read/Write Policy

Write down the policy rules before building. Each rule becomes an enforcement check in the server:

```
WRITE POLICY:
  Any agent may write to:   global scope, its own agent:<name> scope, any project scope it is granted
  No agent may write to:    another agent's private scope, user:<id> scopes owned by a different user

READ POLICY:
  Any agent may read:       global scope, its own agent:<name> scope, granted project scopes
  No agent may read:        another agent's private scope without explicit grant
  Embedding search:         same scope restrictions apply; similarity score does not bypass scope

DELETE POLICY:
  Agents may soft-expire entries (set expires_at) via memory_update
  Hard delete (memory_delete) requires: human approval gate OR the same source that created the entry

DUPLICATE POLICY:
  On write, check for near-duplicate in the same scope (threshold: 0.95 cosine similarity)
  If found: update existing entry, extend accessed_at, preserve original importance
  Reason: prevents the store from filling with minor rephrasing of the same fact
```

## Phase 5: Eviction Rules

Define how the store stays bounded as it grows:

```
EVICTION TRIGGER:
  When entry count exceeds [capacity_limit], run eviction before the next write

EVICTION ORDER (lowest-score-first):
  eviction_score = importance × recency_decay × (1 / age_days)
  recency_decay  = 1.0 if accessed in last 7 days, 0.5 if 8–30 days, 0.1 if >30 days

PROTECTED FROM EVICTION:
  importance = 1.0 (pinned entries)
  expires_at = null AND importance > 0.8 (high-importance, no expiry)
  created_at within last 24h (new entries are never immediately evicted)

TTL (time-based expiry):
  Entries with expires_at set are removed at next access after expiry
  A daily background sweep removes all expired entries
```

Set `capacity_limit` based on Phase 1 volume:
- Small: 5,000 entries
- Medium: 100,000 entries
- Large: no hard cap; use eviction score only

## Phase 6: Per-Host Adapter Contract

Each AI product that connects to the memory MCP server acts as a host. Define the contract:

```
HOST REGISTRATION:
  Each host has: name (string), scope_grants (list of scopes it may read/write), api_key (secret)
  The server validates api_key on every tool call

INITIALIZATION (on session start, any host):
  Call memory_read("session context", scope=["global", "agent:<this-host>"], limit=20)
  Inject top results into the session's context window
  This is the "waking up" step that makes memory portable

COMMIT (on session end or at checkpoints):
  Call memory_write for any new decisions, preferences, or facts surfaced this session
  Tag with current date, project, and relevance signal
  Set importance based on how load-bearing the fact is (1.0 = "always need this", 0.3 = "nice to have")

CONFLICT RESOLUTION:
  If two hosts write conflicting entries (same topic, different content):
  Server accepts both, tags the newer one "conflict:pending"
  Next human-present session resolves via memory_list(tags=["conflict:pending"])
```

## Phase 7: Spec Output

```
OPEN BRAIN MCP SPEC

Data model: [Entry schema with scope values for this user's host list]
MCP tools:  memory_write / memory_read / memory_update / memory_delete / memory_list / memory_stats
Policy:
  Write:  [scope rules]
  Read:   [scope rules]
  Delete: [human gate rule]
  Dedup:  [cosine threshold]
Eviction:
  Capacity: [N entries]
  Score:    importance × recency_decay × (1 / age_days)
  Protected: [pinned entries, recent entries]
Hosts:
  [host name] → scopes: [global, agent:<name>, project:<ids>]
  ...
Storage: [SQLite file at ./ | PostgreSQL at <url> | filesystem JSON]
Embedding: [enabled via <provider> | disabled, lexical search only]
```

## Implementation notes (not part of the spec, guide only)

A minimal implementation in TypeScript with the `@modelcontextprotocol/sdk` package:
- SQLite via `better-sqlite3` for the entry store (local, zero-config)
- `better-sqlite3-fts5` extension or a separate vector library for semantic search
- One `server.ts` entry point that registers the 6 MCP tools and handles authentication
- One `store.ts` module for all DB operations

Do not build the embedding layer until lexical search is working and deployed. Optimize for correctness first; add semantic search as a separate phase.

## Verification

The spec is complete when:
- Every host in the Phase 1 list has a named scope and a read/write grant
- The eviction policy will keep the store within the capacity limit indefinitely
- The duplicate policy prevents near-identical entries from accumulating
- The delete gate is named (who approves hard deletes)
- The initialization and commit steps are defined for each host

## Source

Nate Jones newsletter 2026-07-01: "You can build 80% of your own AI memory by talking to the agent already on your computer." Ideas #1 (Open Brain — portable cross-model memory MCP) and #8 (cross-model memory bridge — one shared memory across multiple AI hosts). Linked field guide: `https://unlock-ai.natebjones.com/guides/open-stack/open-stack-field-guide`
