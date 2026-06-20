---
name: skill-portability-auditor
description: Audit a SKILL.md file and answer "if I had to move this skill to Codex, Cursor, or ChatGPT tomorrow, what would break?" Produces a ranked portability-debt report covering hook dependencies, MCP-server assumptions, permission requirements, install-path conventions, and runtime-specific syntax.
---

# Skill Portability Auditor

Runs the one-question portability test against a single skill file: **"If I had to move this skill to a different agent runtime tomorrow, what would break?"** Returns a ranked debt report that doubles as a migration checklist.

## Trigger

Use when the user says "audit this skill for portability", "what would break if I moved this", "skill portability check", "port this skill to Codex", "check this skill for lock-in", or provides a SKILL.md path and asks whether it is portable.

## Phase 1: Locate the Skill

Accept:
- A direct file path to a `SKILL.md`
- A skill name (search common skill directories for `<name>/SKILL.md`)

If neither is provided, ask: "Which skill do you want to audit for portability? Provide the name or file path."

## Phase 2: Categorize Dependencies

Read the SKILL.md and scan for the following dependency classes. For each one found, record: the specific line or reference, which runtimes it blocks, and the severity.

### Dependency classes

| Class | What to look for | Portability risk |
|-------|-----------------|-----------------|
| **Hook calls** | References to hooks (`PostToolUse`, `PreToolUse`, `Stop`, `SessionStart`, `UserPromptSubmit`) or hook file paths | High — hooks are Claude Code-specific |
| **MCP server calls** | Any `mcp__*` tool name, `--mcp-config` flag, or named MCP server | High if the MCP server is only registered in one runtime |
| **Permission assumptions** | Tool names (`Bash`, `Edit`, `Write`, `WebFetch`, `Read`) assumed to be pre-approved | Medium — approval models differ by runtime |
| **Runtime-specific syntax** | Frontmatter keys or YAML fields specific to one runner | Medium — other runtimes use different install paths and trigger syntax |
| **Install path assumptions** | Hardcoded paths to skills or rules directories | Medium — path conventions differ across runtimes |
| **Script/binary dependencies** | CLI tools invoked via Bash that may not be in PATH in sandboxed runtimes | Low-Medium |
| **Memory/state path assumptions** | Specific file paths for state or shared memory | Medium — path conventions differ |
| **Env var assumptions** | API keys or env vars assumed to be set without documentation | Low — portable if documented |

## Phase 3: Score and Rank

Compute a portability score:

```
score = max(0, 100 - (high_count × 20) - (medium_count × 8) - (low_count × 3))
```

Classify:
- **Portable (80-100):** minimal changes needed to move
- **Conditionally portable (50-79):** move requires documented substitutions
- **Runtime-locked (0-49):** significant rewrite needed to move

Rank debts from most-blocking to least-blocking.

## Phase 4: Report

Output the portability report:

```markdown
# Portability Report — [skill-name]
**Score:** [N]/100 — [Portable / Conditionally portable / Runtime-locked]
**Audited:** [YYYY-MM-DD]

## Blocking Issues (High)
- [line ref] [Dependency class]: [what it is] → [what breaks] → [migration path]

## Conditional Issues (Medium)
- [line ref] [Dependency class]: [what it is] → [what breaks] → [migration path]

## Low-Risk Items
- [line ref] [Dependency class]: [what it is] → [note]

## Migration Checklist
- [ ] [specific action to make portable]
- [ ] [specific action to make portable]
```

If the skill scores 100: "No portability debt found. This skill can be moved without changes."

## Notes

- This skill audits **SKILL.md files** (agent behavioral skills). To audit MCP extensions, plugins, and agent-runner integrations for vendor lock-in, use `mcp-portability-auditor` instead.
- The score is directional, not a guarantee — some platform differences are undocumented.
- The migration checklist is the actionable output; the score is context.

## Source

Extracted from Nate Kadlac "Open Skills" newsletter (2026-06-19), idea 41 — "What Would Break?" Portability Auditor: "run the one-question test against an existing skill and emit a ranked procedural-debt report (MCP gaps, hook deps, permission diffs, script/runtime assumptions)."
