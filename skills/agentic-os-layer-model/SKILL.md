---
name: agentic-os-layer-model
description: >
  Walk all five layers of a Claude Code agentic OS — Identity, Rules/Hooks, Skills, Agents, Tools/MCPs — and rate each layer's staleness (rot rate). Produces a prioritized refresh checklist showing which layers need immediate attention vs. which are healthy. Use when your agent setup "feels off", before a major model or workflow change, or as part of a periodic OS maintenance pass. Trigger phrases: "audit my OS", "what's stale in my setup", "rot rate check", "layer audit", "agentic OS health check", "my agent setup needs a refresh".
---

# Agentic OS Layer Model

Every agentic OS has five layers, from most-static (inner) to most-dynamic (outer). Each layer
ages at a different rate — the "rot rate." An identity file can stay valid for months; an MCP
server endpoint might break in a week. This skill walks all five layers and produces a
staleness assessment with concrete refresh actions.

Mental model: layers are like the Earth's crust. Inner layers are slow-changing and
load-bearing. Outer layers are exposed to more volatility. A setup that looks fine from the
outside (polished dashboard, responsive agent) can be silently rotting at the inner layers.
The dashboard is meaningless without the plumbing underneath.

## Layers and Typical Rot Rates

| # | Layer | Typical Rot Rate | What Goes Stale |
|---|-------|-----------------|-----------------|
| 1 | Identity / Soul | Months | Persona claims, business domain, deprecated tool references |
| 2 | Rules & Hooks | Weeks-months | Dead path references, hooks for removed tools, outdated constraints |
| 3 | Skills | Weeks | Stale API endpoints, wrong model IDs, zero-invocation debt |
| 4 | Agents | Days-weeks | Deprecated model IDs, missing tool authorizations, outdated capabilities |
| 5 | Tools / MCPs / CLI | Days | Dead endpoints, expired tokens, missing binaries |

## When to Use

- Agent behavior has shifted without a clear cause
- After a major model upgrade or MCP server migration
- Quarterly or periodic OS maintenance pass
- Before onboarding a new agent or skill that depends on existing infrastructure
- When the OS has not been reviewed in more than 30 days

## Inputs

- **OS root** (optional): path to the top-level config directory. Defaults to `./`.
- **Scope** (optional): layers to audit -- `all` (default), or a comma-separated subset:
  `identity`, `rules`, `skills`, `agents`, `tools`
- **Last-reviewed date** (optional): if provided, flags items not touched since that date

If no OS root is given, scan the current directory and common config locations.

## Phases

### Phase 0 -- Discover the OS Layout

Identify what exists at each layer before auditing:

```bash
# Identity layer
ls *.md CLAUDE.md AGENTS.md soul.md 2>/dev/null

# Rules / hooks layer
ls rules/ hooks/ .claude/rules/ .claude/hooks/ 2>/dev/null

# Skills layer
ls skills/ .claude/skills/ 2>/dev/null | head -30

# Agents layer
find . -maxdepth 3 \( -name "agent.yaml" -o -name "AGENT.md" -o -name "agent.config.json" \) 2>/dev/null

# Tools / MCPs layer
ls .mcp.json mcp.json settings.json .claude/settings.json 2>/dev/null
```

If none of the five layers have discoverable files, ask the user to confirm the OS root before
proceeding.

### Phase 1 -- Identity / Soul

For each identity file found (CLAUDE.md, AGENTS.md, soul.md, or equivalent):

Check for:
1. **Tool references** -- tools, CLIs, or services named that may no longer exist or be installed
2. **Model references** -- hardcoded model names or versions that may have changed
3. **Path references** -- hardcoded paths to deleted or moved files
4. **Domain claims** -- assertions about scope, audience, or purpose that may have shifted
5. **Last-modified age** -- `git log -1 --format="%ar" <file>`; flag if >90 days with no change

Rate the layer:
- **FRESH** -- no stale signals, or only LOW severity
- **AGING** -- 1-2 medium-severity signals; schedule a review
- **STALE** -- 3+ signals OR any HIGH severity; refresh needed now

### Phase 2 -- Rules & Hooks

For each rules file and hook configuration:

Check for:
1. **Dead path references** -- paths in rules or hook scripts that no longer exist
2. **Orphaned hooks** -- hooks registered for tools that are no longer in use
3. **Contradicted rules** -- rules that conflict with newer configuration
4. **Hook script existence** -- for any hook that runs an external script, verify it exists and
   is executable
5. **Last-modified age** -- flag rules not touched in >60 days if the associated tooling changed

```bash
# Quick check: hook script paths exist
grep -r '"command"\|"script"\|"path"' .claude/settings.json 2>/dev/null | grep '"/' | head -20
```

Rate the layer: FRESH / AGING / STALE (same criteria as Phase 1).

### Phase 3 -- Skills

For each skill directory found:

Check for:
1. **API/URL references** -- hardcoded endpoint URLs; note each for manual reachability verification
2. **Model name references** -- model ID or version strings; flag for verification against current
   provider docs
3. **Cross-skill references** -- skills that reference another skill by name; verify the referenced
   skill directory exists
4. **Zero-invocation signals** -- if `skill-registry.yaml` is present, check `metrics.invocations_30d`;
   flag skills with 0 invocations and no callsite sponsorship
5. **Last-modified age** -- flag skills not touched in >30 days that reference volatile external services

For each skill, emit one line:
```
[FRESH|AGING|STALE] <skill-name> -- <reason if not FRESH>
```

Summarize: N fresh, N aging, N stale.

### Phase 4 -- Agents

For each agent config found (agent.yaml, AGENT.md, agent.config.json):

Check for:
1. **Model IDs** -- hardcoded model names; flag for human verification against current provider catalog
2. **Tool authorizations** -- tools listed in `allowedTools` or equivalent; verify each is still valid
3. **MCP dependencies** -- MCP servers the agent depends on; confirm they appear in the active MCP config
4. **Budget limits** -- max-turns or token limits; verify still appropriate for the agent's current scope
5. **Last-modified age** -- flag agent configs not touched in >30 days if the model or tool landscape changed

Rate the layer: FRESH / AGING / STALE.

### Phase 5 -- Tools / MCPs / CLI

For each MCP server entry and CLI tool referenced in config:

Check for:
1. **Reachability** -- for HTTP-based MCP servers: `curl -s --max-time 5 <url>/health`; log timeouts as STALE
2. **Binary existence** -- for local CLI tools: `which <tool>` or check the declared install path
3. **Auth token age** -- if config references tokens or API keys, note last rotation date if available
4. **Schema version** -- if the MCP server exposes a version endpoint, compare against last configured version
5. **Last-modified age** -- flag MCP entries not updated in >14 days if the service has published changes

Rate the layer: FRESH / AGING / STALE.

## Report Format

```
AGENTIC OS LAYER AUDIT
======================
OS root: <path>
Audit date: <today>
Layers scanned: <list>

LAYER HEALTH SUMMARY
--------------------
Layer 1 -- Identity/Soul:    [FRESH|AGING|STALE]
Layer 2 -- Rules/Hooks:      [FRESH|AGING|STALE]
Layer 3 -- Skills:           [FRESH|AGING|STALE]  (N fresh, N aging, N stale)
Layer 4 -- Agents:           [FRESH|AGING|STALE]
Layer 5 -- Tools/MCPs/CLI:   [FRESH|AGING|STALE]

OVERALL STATUS: [HEALTHY | MAINTENANCE NEEDED | CRITICAL REFRESH REQUIRED]

FINDINGS (sorted by severity)
------------------------------
[HIGH] Layer N -- <file or item> -- <what is stale and why>
[MEDIUM] ...
[LOW] ...

PRIORITIZED REFRESH ACTIONS
----------------------------
1. [Layer N] <specific action> -- estimated effort: <small|medium|large>
2. ...

NEXT AUDIT DATE
---------------
Recommended next full audit: <today + 14|30|60|90 days based on worst rot rate found>
```

## Verification

- Every STALE or AGING finding must cite the specific file, line, or config key that is stale.
- Do not flag a model name as stale without noting that verification requires the user to check
  the current provider's model catalog.
- If an MCP health check times out, record the URL and timeout value -- do not silently skip it.
- Report every finding, even LOW severity -- the user decides what to act on.

## Source Attribution

Mental model and layer taxonomy from Mark Kashef, YouTube, 2026-06-30:
*"Master All 5 Layers of Every Agentic OS"*
`https://www.youtube.com/watch?v=YjkteijEyzQ`

Rot rate concept: the pace at which a specific piece of context has an expiration date, applied
per-layer. Adaptation: structured audit phases and severity rating across all five layers.
