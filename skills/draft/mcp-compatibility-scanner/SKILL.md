---
name: mcp-compatibility-scanner
description: Scans an MCP server implementation for protocol compliance, capability declarations, security posture, and platform readiness. Catches issues before deployment or distribution.
---

# MCP Compatibility Scanner

Static analysis skill for MCP server codebases. Checks protocol compliance, tool/resource declarations, error handling patterns, transport compatibility, and readiness for OS-level integration (iOS, Android, desktop). Designed for use before shipping any MCP server from M2AI's pipeline.

## Trigger

Use when the user says "scan this MCP server", "check MCP compliance", "is this server ready to ship", "MCP audit", or when an MCP server project has been built or modified and needs pre-deployment review.

Also use proactively after building or modifying any MCP server project.

## Phase 1: Discovery

Locate the MCP server codebase. Accept:
- A project path (e.g., `projects/perceptor/mcp-server`)
- Current working directory if it contains an MCP server

Identify:
- **Language:** TypeScript (look for `@modelcontextprotocol/sdk`) or Python (look for `mcp` SDK imports)
- **Transport:** stdio, SSE, HTTP
- **Entry point:** main server file
- **Tool count:** number of registered tools
- **Resource count:** number of registered resources

## Phase 2: Protocol Compliance

Check each area and rate PASS / WARN / FAIL:

### 2a. Tool Declarations
- [ ] Every tool has a `name` and `description`
- [ ] Descriptions are clear enough for an LLM to select the right tool
- [ ] Input schemas use JSON Schema with required fields marked
- [ ] No tool names conflict with common built-in tool names

### 2b. Resource Declarations (if applicable)
- [ ] Resources have URI templates that follow RFC 6570
- [ ] Resources have `mimeType` declared
- [ ] Resource descriptions explain what content is returned

### 2c. Error Handling
- [ ] Tools return structured errors, not raw exception strings
- [ ] Server handles malformed input gracefully (doesn't crash)
- [ ] Timeout behavior is defined for long-running operations
- [ ] No silent error swallowing (catch blocks that return empty/default without logging)

### 2d. Transport
- [ ] stdio transport: reads from stdin, writes to stdout, logs to stderr
- [ ] No stray `console.log` / `print` statements that corrupt stdio transport
- [ ] SSE/HTTP transport: proper CORS headers if browser-facing

### 2e. Security
- [ ] No hardcoded API keys or secrets in source
- [ ] Credentials loaded from environment variables
- [ ] File system access scoped to expected directories (no `../` traversal)
- [ ] Network requests validate URLs (no SSRF vectors)

## Phase 3: Platform Readiness

Check compatibility with emerging platform integration patterns:

### 3a. Sandboxing Compatibility
- [ ] Server does not require filesystem access outside its working directory
- [ ] No hardcoded absolute paths (uses relative paths or environment config)
- [ ] No reliance on system-level commands that may be unavailable in sandboxed environments

### 3b. Capability Declaration
- [ ] Server declares its capabilities in the initialization response
- [ ] Capabilities match what tools actually do (no capability overreach)
- [ ] Server version is declared

### 3c. Graceful Degradation
- [ ] Server starts successfully even if optional dependencies are missing
- [ ] Tools that require external services return clear errors when services are unavailable
- [ ] Server handles reconnection for persistent connections

## Phase 4: Code Quality

Quick quality pass specific to MCP servers:

- [ ] Build step works (`npm run build` / `pip install`)
- [ ] Tests exist and pass
- [ ] README or CLAUDE.md documents available tools and setup
- [ ] Package.json / pyproject.toml has correct entry point

## Phase 5: Report

```
## MCP Compatibility Scan: [Project Name]

**Language:** TypeScript | Python
**Transport:** stdio | SSE | HTTP
**Tools:** N | **Resources:** N

### Protocol Compliance
| Area | Status | Issues |
|------|--------|--------|
| Tool Declarations | PASS/WARN/FAIL | details |
| Resource Declarations | PASS/WARN/FAIL | details |
| Error Handling | PASS/WARN/FAIL | details |
| Transport | PASS/WARN/FAIL | details |
| Security | PASS/WARN/FAIL | details |

### Platform Readiness
| Area | Status | Issues |
|------|--------|--------|
| Sandboxing | PASS/WARN/FAIL | details |
| Capability Declaration | PASS/WARN/FAIL | details |
| Graceful Degradation | PASS/WARN/FAIL | details |

### Code Quality
| Area | Status |
|------|--------|
| Build | PASS/FAIL |
| Tests | PASS/FAIL/NONE |
| Docs | PASS/FAIL |

### Overall Score: N/10
### Critical Issues (fix before shipping):
- [list]

### Warnings (should fix):
- [list]

### Recommendations:
- [list]
```

## Verification

A good MCP scan:
- Reads the actual source code, not just config files
- Catches stdio corruption issues (the #1 cause of MCP server failures)
- Identifies security issues that would block OS-level integration
- Provides actionable fix instructions, not just pass/fail
- Runs the build step to verify it actually compiles

## Source

Extracted from Nate Kadlac newsletter (2026-03-31) -- "The Company Everyone Says Lost the AI Race Is Building the Layer Every AI Winner Has to Use" -- the need for MCP protocol compliance scanning as Apple and others adopt MCP at OS level.
