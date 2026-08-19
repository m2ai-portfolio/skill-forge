---
name: poly-skill
description: Convert a skill between Claude Code, OpenAI Codex, Gemini CLI, and Cursor by applying a structural adapter that handles frontmatter field differences, sidecar generation, trigger placement, tool-permission fields, and shell-injection syntax. Reads the checked-in provider schema at references/skill-formats.md rather than recalling formats.
---

# Poly-Skill

Cross-platform skill adapter. Given a skill written for one provider, produces a version that works correctly on another. Handles the structural mismatches that cause skills to silently misfire when ported.

## Trigger

Use when the user says "poly skill", "convert this skill to codex", "port this skill to claude code", "make this skill work in both", "cross-platform skill", "skill adapter", or provides a SKILL.md and asks why it doesn't work in the other environment.

## Schema source of truth

**Read `references/skill-formats.md` before emitting any converted file.** It carries the verified
per-provider schema: the shared Agent Skills core, each provider's frontmatter table, discovery
paths, sidecar shape, and the conversion matrix of what survives, what translates, and what is
lost. Never write a frontmatter field, a sidecar path, or a body syntax from memory. If the
reference does not cover the target provider, say so and stop rather than guessing.

The reference also records its own verification date and a re-verification procedure. If it is
visibly stale relative to the user's installed CLI versions, flag that before converting.

## Background: Why Skills Misfire Across Platforms

All four providers read the same artifact: a directory with a `SKILL.md` whose frontmatter carries
`name` and `description`. That core is portable. Skills misfire when a provider-specific extension
is carried across unchanged, or when a field the source relied on is silently dropped.

The four failure areas, in full detail in `references/skill-formats.md` §5:

| Area | Failure when ported |
|------|--------------------|
| Extra frontmatter | Claude Code honors 15+ extra fields; Codex and Gemini CLI read none of them, Cursor reads three. Everything else is silently ignored, or rejected outright on a claude.ai upload |
| Trigger placement | Every provider truncates the listing text and `description` is the only shared trigger signal, so a trigger buried at the end of the body never fires |
| Shell injection | Claude Code's `` !`command` `` body syntax exists nowhere else and must become prose or a `scripts/` call |
| Tool permissions and invocation policy | `allowed-tools` has no equivalent on Codex or Gemini CLI; `disable-model-invocation` maps to `policy.allow_implicit_invocation: false` on Codex only |

## Phase 1: Read Source Skill

Ask the user for the path to the skill directory (or accept it as an argument). Read:
- `SKILL.md` (or equivalent) for frontmatter, trigger, phases, and any terminal commands
- Any `.yaml` / `.yml` sidecar files
- Any `scripts/` subdirectory contents

Identify the source platform from structural fingerprints (fields per `references/skill-formats.md`):
- Frontmatter carries a Claude Code-only field (`allowed-tools`, `context`, `argument-hint`, `when_to_use`, `disallowed-tools`, `model`, `effort`, `agent`, `shell`), or the body uses `` !`command` `` injection? Claude Code.
- Directory contains `agents/openai.yaml`? Codex.
- Frontmatter is core-only plus `paths` or `disable-model-invocation` and nothing Claude Code-specific? Cursor.
- Core fields only, no sidecar, no provider-specific field? Spec-clean, portable as-is.
- Ambiguous? Ask the user. Do not guess from the install path alone, Cursor also loads `.claude/skills/`.

## Phase 2: Extract Shared Structure

Produce a platform-neutral representation:

```
skill_name: <kebab-case name>
description: <full description>
short_description: <one-sentence summary, max 120 chars>
trigger_phrases: [list of trigger strings]
phases: [ordered list of phase names and bodies]
terminal_commands: [list of shell commands referenced]
allowed_tools: [bash commands, file tools, etc.]
requires_approval: true | false
assets: [paths to scripts, reference files]
```

Injection patterns in the body (`` !`command` ``, bang before the backticks) are extracted as `terminal_commands` items with their context.

## Phase 3: Apply Target Platform Adapter

Reduce to the shared Agent Skills core first (`name`, `description`, and only the optional spec
fields the source actually used), then re-extend for the target. Take every field name, sidecar
path, and syntax from `references/skill-formats.md` §1-§4. The rules below are the shape of the
work, not the schema.

### Every target

- `name` must equal the output directory name, lowercase alphanumerics and single hyphens.
- The primary trigger phrase goes at the very start of `description`, because every provider
  truncates the listing text.
- Anything the target cannot express is DROPPED, not renamed. Record each drop for Phase 5.

### Claude Code adapter

Output: `<skill-name>/SKILL.md`, no sidecar. Extension fields available in
`references/skill-formats.md` §1, kebab-case. Shell injection may be re-expressed as
`` !`command` ``. If the skill is destined for a claude.ai upload or the Skills API rather than the
CLI, restrict frontmatter to the six spec fields; anything else is a hard error there.

### Codex adapter

Output: `<skill-name>/SKILL.md` with core-only frontmatter, plus `agents/openai.yaml`. Sidecar
field list and constraints are in `references/skill-formats.md` §2. `disable-model-invocation`
becomes `policy.allow_implicit_invocation: false`. `allowed-tools` has no target and is dropped.
Injection commands become prose or a `scripts/` entry point.

### Gemini CLI adapter

Output: `<skill-name>/SKILL.md` with `name` and `description` only, no sidecar. Every other field
is parsed and discarded. Invocation policy and tool grants cannot be expressed, so both are dropped.

### Cursor adapter

Output: `<skill-name>/SKILL.md` carrying the core plus `paths`, `disable-model-invocation`, and
`metadata` if the source used them. Cursor also reads `.claude/skills/` directly, so if the source
is a Claude Code skill already installed there, say so instead of emitting a redundant copy.

## Phase 4: Write Output

Write output files to `./output/<skill-name>/` by default (or user-specified path). Print the file tree on completion.

If the user asked for both platforms in one run, write both adapters to `./output/<skill-name>-claude/` and `./output/<skill-name>-codex/`.

## Phase 5: Validation Check

After writing, self-verify against `references/skill-formats.md`:
- Does `name` match the output directory name and the spec's naming rules? (discovery safety)
- Does `description` begin with a trigger phrase and stay inside the target's cap? (truncation safety)
- Does the output carry ONLY frontmatter fields the target honors, per §5's matrix? (silent-ignore safety)
- Is the Codex sidecar at `agents/openai.yaml`, using `interface:` / `dependencies:` / `policy:`? (sidecar safety)
- Are any `` !`command` `` injections still present in a non-Claude-Code output? (syntax safety, they should have been prose-converted)

Report a one-line pass/fail per check, then list every field dropped in conversion and the behavior
change each drop causes. A silent drop is the failure mode this skill exists to prevent.

## Source Attribution

Technique derived from Mark Kashef YouTube video "How to INSTANTLY Run ANY Skill in Claude + Codex" (2026-05-21): https://www.youtube.com/watch?v=tjjX43FoAUg

Provider schemas in `references/skill-formats.md` are verified against vendor documentation and
installed CLI versions, not derived from the video. See that file's Evidence lines.
