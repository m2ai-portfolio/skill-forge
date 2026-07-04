---
name: mcp-blast-radius-tagger
description: Add blast-radius metadata to MCP tool manifests so hooks and permission systems can reason about tool impact without pattern-matching on tool names. Outputs an annotated manifest plus a lint hook that fails on untagged tools. Use when the user says "tag MCP tools", "blast radius metadata", "mcp blast radius", "annotate tool impact", "MCP permission tiers", or wants to classify their MCP tools by reversibility before wiring permission gates.
---

# MCP Blast-Radius Tagger

Stamp every MCP tool in a server's manifest with a `blast_radius` field that declares its impact tier. Downstream hooks, permission systems, and approval gates consume this tag — they stop pattern-matching on tool names (fragile) and start reading declared intent (durable).

## Source

Nate's Newsletter, 2026-05-16: Tibo interview — "Blast-radius permissioning scopes agent actions by reversibility, not identity. The tool-side version is a metadata convention every MCP tool manifest declares."

## When to Use

- Setting up a new MCP server and want permission gates from day one
- Adding a PreToolUse hook that should be tier-aware
- Auditing an existing MCP server before connecting it to an autonomous agent
- Building a settings.json policy that maps blast-radius tiers to approval requirements

## Tier Definitions

```
read        — queries only, no side effects (list, get, search, describe)
staging     — writes to a non-production target (test DB, draft, local file)
prod        — writes to a production target (deployed service, live DB, published artifact)
delete      — removes data or resources permanently (even in staging)
external    — sends data outside the system (email, webhook, API POST to a third party)
```

Rules:
- A tool is tagged at its **highest possible impact**, not its typical impact
- `delete` always outranks `prod` — deletion is its own tier regardless of environment
- `external` outranks `prod` for the same reason — external sends may be irreversible even if no local data changes
- When uncertain, tag up (assign the higher tier)

## Phase 1: Inventory the Server

Read the target MCP server's tool definitions. For each tool, extract:
- `name` — the tool identifier
- `description` — what it claims to do
- `inputSchema` — what parameters it accepts (look for destructive patterns: `delete`, `remove`, `send`, `publish`, `deploy`)

If the server is TypeScript (`src/index.ts` with `server.tool()` calls) or Python (`@mcp.tool()` decorators), read those definitions directly.

## Phase 2: Classify Each Tool

For each tool, assign a tier using this decision tree:

```
Does it send data to an external system (email, webhook, API)?
  → external

Does it permanently delete or destroy data/resources?
  → delete

Does it write to a production environment?
  → prod

Does it write to a non-production target?
  → staging

Otherwise (reads, queries, describes)?
  → read
```

Produce a classification table:

| Tool Name | Description (one line) | Assigned Tier | Rationale |
|-----------|------------------------|---------------|-----------|
| ...       | ...                     | ...           | ...       |

Flag any tool where the tier is ambiguous — present it to the user before proceeding.

## Phase 3: Annotate the Manifest

Add `blast_radius` to each tool definition. For TypeScript MCP servers using `@modelcontextprotocol/sdk`:

```typescript
server.tool(
  "send_email",
  {
    blast_radius: "external",  // added
    description: "Send an email to the specified recipient",
    // ... rest of schema
  },
  async (params) => { ... }
);
```

For Python MCP servers:

```python
@mcp.tool(
    name="delete_record",
    description="Permanently delete a database record",
    blast_radius="delete",  # added
)
async def delete_record(id: str) -> str:
    ...
```

If the server uses a static JSON manifest (`manifest.json` or `.mcp/tools.json`), add the field to each tool object:

```json
{
  "name": "create_deployment",
  "blast_radius": "prod",
  "description": "Deploy a service to production"
}
```

## Phase 4: Write the Lint Hook

Generate a PreToolUse hook that checks for the `blast_radius` field and enforces approval requirements by tier:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "mcp__*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/mcp-blast-radius-check.py"
          }
        ]
      }
    ]
  }
}
```

Hook logic (`mcp-blast-radius-check.py`):

```python
import json, sys

APPROVAL_REQUIRED = {"prod", "delete", "external"}

data = json.load(sys.stdin)
tool_name = data.get("tool_name", "")
tool_input = data.get("tool_input", {})

# Look up blast_radius from the tool's metadata
# (The hook receives the tool schema from the MCP server via the harness)
blast_radius = data.get("tool_schema", {}).get("blast_radius", "untagged")

if blast_radius == "untagged":
    print(f"WARN: {tool_name} has no blast_radius tag — treating as prod", file=sys.stderr)
    blast_radius = "prod"

if blast_radius in APPROVAL_REQUIRED:
    print(json.dumps({
        "decision": "block",
        "reason": f"{tool_name} has blast_radius={blast_radius}. Requires explicit approval."
    }))
    sys.exit(0)

print(json.dumps({"decision": "allow"}))
```

## Phase 5: Update settings.json

Add a policy block to `settings.json` that declares the tier-to-approval mapping so the policy is readable without opening the hook code:

```json
{
  "blastRadiusPolicy": {
    "read": "allow",
    "staging": "allow",
    "prod": "require_approval",
    "delete": "require_approval",
    "external": "require_approval"
  }
}
```

## Verification

- Every tool in the server has a `blast_radius` field
- No tool is tagged below its actual impact tier
- Lint hook correctly blocks an `external` or `delete` tool call in a test run
- `read` tool calls pass through without prompting
- `blastRadiusPolicy` block exists in `settings.json`

## Output Files

- Annotated MCP server source (in-place edit)
- `~/.claude/hooks/mcp-blast-radius-check.py` (lint hook)
- Policy block added to `settings.json`
- Classification table written to `docs/mcp-blast-radius-map.md` for reference
