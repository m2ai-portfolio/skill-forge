---
name: framework-to-mcp
description: Package a written decision framework, briefing methodology, or scoring rubric as a thin MCP server so any MCP-compatible agent can call it as a structured tool. Produces a server scaffold (TypeScript or Python), a tool definition matching the framework's phases, and a README for distribution. Use when the user says "package this as an MCP server", "framework to MCP", "turn my framework into a callable tool", "MCP-wrap this checklist", or "/framework-to-mcp".
---

# Framework to MCP

Turns a written decision framework (a checklist, rubric, scoring tool, or briefing methodology) into a standalone MCP server — callable by any MCP-compatible agent.

## When to Use

Trigger when the user says "package this as an MCP server", "framework to MCP", "turn my framework into a tool any agent can call", "MCP-wrap this checklist", "distribute my framework as an MCP tool", or "/framework-to-mcp".

## Phase 1: Intake

Accept the framework to package. This can be:
- A skill file (SKILL.md) to convert to an MCP-callable tool
- A written checklist, rubric, or methodology pasted as text
- A description of a multi-phase decision process

Ask the user three questions (skip any already answered):

1. "What is the framework called?" — becomes the MCP server name and tool name.
2. "What does a caller need to provide as input?" — becomes the tool's input schema.
3. "What does a successful output look like?" — becomes the tool's output contract.

## Phase 2: Framework Analysis

Read the framework and extract its structure:

| Element | What to capture |
|---------|----------------|
| **Phases** | Ordered steps the framework walks through |
| **Required inputs** | What the caller must provide (text, URL, file path, config) |
| **Scoring / classification outputs** | Scores, verdicts, tiers, or recommendations the framework produces |
| **Optional enrichments** | Web fetches, file reads, or external lookups the framework may invoke |

Document a tool contract before writing any code:

```
Tool name: {framework-name}
Input:  {field: type — description}
Output: {field: type — description}
Side effects: [none | file write | web fetch]
```

Present the contract to the user and confirm before proceeding.

## Phase 3: MCP Server Scaffold

Generate a minimal MCP server in the user's preferred language (ask: TypeScript or Python; default TypeScript).

### TypeScript scaffold structure

```
{framework-name}-mcp/
├── package.json        # @modelcontextprotocol/sdk dependency
├── tsconfig.json       # NodeNext, strict
├── src/
│   └── index.ts        # server + tool definition + handler in one file
└── README.md
```

**`src/index.ts` pattern:**

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const server = new Server(
  { name: "{framework-name}", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "{tool-name}",
      description: "{one-line description from Phase 2 contract}",
      inputSchema: {
        type: "object",
        properties: {
          // paste input schema from Phase 2 here
        },
        required: [
          /* required field names */
        ],
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name !== "{tool-name}") {
    throw new Error(`Unknown tool: ${request.params.name}`);
  }

  const input = request.params.arguments as Record<string, unknown>;

  // Phase 1 of the framework
  // Phase 2 of the framework
  // ...
  const result = await runFramework(input);

  return {
    content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
  };
});

async function runFramework(
  input: Record<string, unknown>
): Promise<Record<string, unknown>> {
  // Replace with framework implementation matching the phases from Phase 2
  throw new Error("Not implemented");
}

const transport = new StdioServerTransport();
await server.connect(transport);
```

**`package.json` minimum:**

```json
{
  "name": "{framework-name}-mcp",
  "version": "1.0.0",
  "type": "module",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0"
  }
}
```

### Python scaffold (if requested)

Use FastMCP for the shortest path:

```
{framework-name}-mcp/
├── pyproject.toml      # mcp[cli] dependency
├── src/
│   └── server.py
└── README.md
```

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("{framework-name}")

@mcp.tool()
def {tool_name}(
    # inputs from Phase 2 contract, typed
) -> dict:
    """{One-line description from Phase 2 contract}."""
    # Phase 1 of the framework
    # Phase 2 of the framework
    return {}  # output contract from Phase 2

if __name__ == "__main__":
    mcp.run()
```

## Phase 4: README for Distribution

Generate a README at the repo root:

```markdown
# {Framework Name} MCP Server

{One-sentence description: what the framework does and what a caller gets back.}

## Tool: `{tool-name}`

### Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| ...   | ...  | yes/no   | ...         |

### Output

| Field | Type | Description |
|-------|------|-------------|
| ...   | ...  | ...         |

## Install

\`\`\`bash
npm install && npm run build
\`\`\`

## Register in Claude Desktop or Claude Code

\`\`\`json
{
  "mcpServers": {
    "{framework-name}": {
      "command": "node",
      "args": ["/absolute/path/to/{framework-name}-mcp/dist/index.js"]
    }
  }
}
\`\`\`
```

## Phase 5: Distribution Checklist

Before sharing or publishing, verify each item:

- [ ] Server starts without errors: `node dist/index.js` (TypeScript) or `python src/server.py` (Python)
- [ ] Tool appears when connected to an MCP client (check `list_tools` response)
- [ ] Calling with missing required fields returns a clear error, not a crash
- [ ] No hardcoded paths, API keys, or user-specific values in the server code
- [ ] README covers install and register steps end-to-end — a stranger should be able to use it without asking
- [ ] If the framework is gated/paid: API key check happens at the handler level before any framework logic runs

## Verification

A good output from this skill:
- Produces a scaffold the user can `npm install && npm run build` (or `pip install` equivalent) immediately
- Maps the framework's phases 1:1 to commented sections in the handler function
- Tool contract from Phase 2 is reflected exactly in the `inputSchema` and the return type

## Source Attribution

Pattern derived from Nate Kadlac newsletter (2026-06-28): "Executive Briefing: Cheap Intelligence Won't Matter If Your Context Is Trapped" — the "paid carrot" pattern of packaging a written decision framework as a distributable MCP server, turning a methodology into a callable tool any agent can invoke.
