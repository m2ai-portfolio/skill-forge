# Provider skill-format reference

Canonical, checked-in schema for skill files across providers. `poly-skill` reads this file
instead of recalling formats from model memory.

**Verified: 2026-08-17.** Every claim below was read from a primary source on that date: vendor
documentation, or the shipped binary/bundle of the version installed on this machine. The
"Evidence" line under each section names the source. Nothing here is written from recall.

Installed versions used as first-party evidence: `@openai/codex@0.122.0`,
`@google/gemini-cli@0.43.0`.

---

## 0. The shared core: Agent Skills open standard

The format originated at Anthropic and was released as an open standard at
<https://agentskills.io>. Claude Code, Codex, Gemini CLI, Cursor, Copilot and others all read the
same basic artifact, so most of a skill is portable and only the extensions differ.

A skill is a directory containing a `SKILL.md`:

```
skill-name/
├── SKILL.md          # required: YAML frontmatter + markdown body
├── scripts/          # optional: executable code
├── references/       # optional: docs loaded on demand
├── assets/           # optional: templates, images, data
└── ...
```

Spec frontmatter, and the only fields guaranteed to travel:

| Field | Required | Constraints |
|-------|----------|-------------|
| `name` | Yes | 1-64 chars, lowercase `a-z0-9` and `-` only, no leading/trailing hyphen, no consecutive hyphens, must match the parent directory name |
| `description` | Yes | 1-1024 chars, non-empty, says what it does AND when to use it |
| `license` | No | License name or reference to a bundled license file |
| `compatibility` | No | Max 500 chars, environment requirements |
| `metadata` | No | Map of string keys to string values, for client-specific extras |
| `allowed-tools` | No | Space-separated string of pre-approved tools. Marked **experimental** in the spec, support varies by implementation |

Progressive disclosure is assumed by every implementation: `name` plus `description` load at
startup, the body loads on activation, files under `references/` and `scripts/` load only when
the body points at them. Spec guidance: keep `SKILL.md` under 500 lines and the body under about
5000 tokens.

Validation: `skills-ref validate ./my-skill` from
<https://github.com/agentskills/agentskills/tree/main/skills-ref>.

**Evidence:** <https://agentskills.io/specification> and <https://agentskills.io> (fetched
2026-08-17).

**Conversion rule:** write the shared core first and keep it spec-clean. Put provider-specific
behavior in that provider's extension surface (Claude Code frontmatter, Codex `agents/openai.yaml`),
never by mangling the core.

---

## 1. Claude Code

Claude Code accepts the full spec plus a large set of its own frontmatter fields. It is the most
permissive target and the one that loses the most on conversion out.

### Discovery

| Location | Path | Applies to |
|----------|------|-----------|
| Enterprise | managed settings | all users in the org |
| Personal | `~/.claude/skills/<skill-name>/SKILL.md` | all your projects |
| Project | `.claude/skills/<skill-name>/SKILL.md` | that project |
| Plugin | `<plugin>/skills/<skill-name>/SKILL.md` | where the plugin is enabled |

Nested `.claude/skills/` directories below the working directory also load, surfacing under a
directory-qualified name such as `apps/web:deploy`. Precedence across levels: enterprise beats
personal, personal beats project. Legacy `.claude/commands/<name>.md` files still work and are
equivalent to a skill, except that `name` and `paths` are ignored in a command file.

Command name: in a personal or project skill the command comes from the **directory** name and
`name` only sets the display label. In a plugin skill, `name` sets the last segment of the
namespaced command (`/my-plugin:fancy`).

### Frontmatter

All fields are optional in Claude Code; only `description` is recommended. Boolean fields accept
`true`/`false`, `yes`/`no`, `on`/`off`, `1`/`0` in any case.

| Field | Portable? | Meaning |
|-------|-----------|---------|
| `name` | spec | Display name in listings. Defaults to the directory name |
| `description` | spec | What it does and when to use it. `description` + `when_to_use` are truncated at **1,536 characters** in the skill listing |
| `license` | spec | Accepted, not acted on |
| `compatibility` | spec | Accepted, not acted on, max 500 chars |
| `metadata` | spec | Free-form YAML map for your own tooling. A non-map value is dropped |
| `allowed-tools` | spec (experimental) | Tools pre-approved for the invoking turn. Space- or comma-separated string, or a YAML list. Grant clears on the next user message |
| `when_to_use` | Claude Code only | Extra trigger context, appended to `description`, counts toward the 1,536-char cap |
| `argument-hint` | Claude Code only | Autocomplete hint, e.g. `[issue-number]` |
| `arguments` | Claude Code only | Named positional arguments for `$name` substitution |
| `disable-model-invocation` | Claude Code only | `true` = only the user can invoke it. Default `false` |
| `user-invocable` | Claude Code only | `false` = only Claude can invoke it, hidden from the `/` menu. Default `true` |
| `disallowed-tools` | Claude Code only | Tools removed from the pool while the skill is active |
| `model` | Claude Code only | Model override for the rest of the turn, or `inherit` |
| `effort` | Claude Code only | `low` \| `medium` \| `high` \| `xhigh` \| `max` |
| `context` | Claude Code only | `fork` runs the skill in a forked subagent context |
| `agent` | Claude Code only | Subagent type to use when `context: fork` |
| `paths` | Claude Code only | Glob patterns limiting automatic activation |
| `shell` | Claude Code only | `bash` (default) or `powershell` for inline command execution |

Field names are **kebab-case** (`allowed-tools`, `disable-model-invocation`, `user-invocable`),
with the two exceptions `when_to_use` and `arguments`. There is no camelCase form.

### Body extensions

Dynamic context injection: the `` !`<command>` `` syntax runs a shell command before the body
reaches the model and substitutes the output. Note the order, bang **then** backticks. Substitution
runs once over the original file and output is not rescanned. This is a Claude Code extension, not
part of the standard, so it must be converted to prose or a script call for any other target.

String substitutions available in the body: `$ARGUMENTS`, `$ARGUMENTS[N]`, `$N`, `$name`,
`${CLAUDE_SESSION_ID}`, `${CLAUDE_EFFORT}`, `${CLAUDE_SKILL_DIR}`, `${CLAUDE_PROJECT_DIR}`, and in
plugin skills `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}`. `${CLAUDE_SKILL_DIR}` and
`${CLAUDE_PROJECT_DIR}` are also substituted inside Bash rules in `allowed-tools`.

### Portability trap

Claude Code accepts every field above, but **claude.ai uploads, the Skills API, and
`package_skill.py` accept only six**: `name`, `description`, `license`, `compatibility`,
`metadata`, `allowed-tools`. Any other field is a hard error, not a warning:

```
Unexpected key(s) in SKILL.md frontmatter: argument-hint. Allowed properties are: allowed-tools, compatibility, description, license, metadata, name
```

So a Claude Code skill that carries `argument-hint` or `context: fork` is not uploadable as-is.

**Evidence:** <https://code.claude.com/docs/en/skills> (fetched 2026-08-17), frontmatter reference,
"Where skills live", and "Inject dynamic context" sections.

---

## 2. OpenAI Codex

Codex reads the spec core and nothing else from frontmatter. Everything product-specific lives in
a sidecar under `agents/`.

### Layout

```
skill-name/
├── SKILL.md            # required, frontmatter: name + description only
├── agents/
│   └── openai.yaml     # recommended: UI metadata, dependencies, invocation policy
├── scripts/            # optional
├── references/         # optional
└── assets/             # optional
```

The sidecar is `agents/openai.yaml`, a fixed path and filename. It is not `<skill-name>.yaml` and
it does not sit at the skill root. It is read by the harness, not by the model.

### Discovery

| Scope | Location |
|-------|----------|
| Repo | `$CWD/.agents/skills` |
| Repo | `$CWD/../.agents/skills` |
| Repo | `$REPO_ROOT/.agents/skills` |
| User | `$HOME/.agents/skills` |
| Admin | `/etc/codex/skills` |
| System | built-in, bundled by OpenAI |

The installed binary also resolves `.codex/skills` (the OpenAI-bundled system skills on this box
live at `~/.codex/skills/.system/`). Explicit invocation is `$skill-name`; `/skills` lists them.

### Frontmatter

`name` and `description`, both required. Codex's own skill-creator states these "are the only
fields that Codex reads to determine when the skill gets used." Do not invent frontmatter keys for
Codex; there is no `## Metadata` body section and no `shortDescription` frontmatter field. The
human-facing short blurb is `interface.short_description` in the sidecar.

### `agents/openai.yaml`

```yaml
interface:
  display_name: "Optional user-facing name"
  short_description: "Optional user-facing description"
  icon_small: "./assets/small-400px.png"
  icon_large: "./assets/large-logo.svg"
  brand_color: "#3B82F6"
  default_prompt: "Optional surrounding prompt to use the skill with"

dependencies:
  tools:
    - type: "mcp"
      value: "github"
      description: "GitHub MCP server"
      transport: "streamable_http"
      url: "https://api.githubcopilot.com/mcp/"

policy:
  allow_implicit_invocation: true
```

| Field | Meaning |
|-------|---------|
| `interface.display_name` | Human-facing title in UI skill lists and chips |
| `interface.short_description` | Short UI blurb, 25-64 chars |
| `interface.icon_small` | Path to a small icon, relative to the skill dir, conventionally `./assets/` |
| `interface.icon_large` | Path to a larger logo, same convention |
| `interface.brand_color` | Hex color for UI accents |
| `interface.default_prompt` | Default prompt snippet inserted on invoke. One sentence, and it must mention the skill as `$skill-name` |
| `dependencies.tools[].type` | Dependency category. Only `mcp` is supported today |
| `dependencies.tools[].value` | Tool or dependency identifier |
| `dependencies.tools[].description` | Human-readable purpose |
| `dependencies.tools[].transport` | Connection type when `type: mcp` |
| `dependencies.tools[].url` | MCP server URL when `type: mcp` |
| `policy.allow_implicit_invocation` | `false` keeps the skill out of model context by default; explicit `$skill` still works. Defaults to `true` |

Style constraints from the shipped reference: quote all string values, leave keys unquoted.

There is no tool-permission field. Codex has no equivalent of `allowed-tools`, so that grant is
dropped on conversion, and no equivalent of `disable-model-invocation` other than
`policy.allow_implicit_invocation: false`.

**Evidence:** <https://learn.chatgpt.com/docs/build-skills> (the current redirect target of
<https://developers.openai.com/codex/skills>, fetched 2026-08-17);
`~/.codex/skills/.system/skill-creator/references/openai_yaml.md` and `SKILL.md` shipped with
`@openai/codex@0.122.0`; strings `agents/openai.yaml`, `.agents/skills`, `.codex/skills`,
`allow_implicit_invocation` present in the installed codex binary.

---

## 3. Gemini CLI

### Discovery

| Scope | Paths |
|-------|-------|
| User | `~/.gemini/skills/`, and `~/.agents/skills/` as a higher-precedence alias |
| Project | `.gemini/skills/`, and `.agents/skills/` as a higher-precedence alias |

Built-in and extension skills also participate; higher-precedence locations override duplicates.
Discovery globs `SKILL.md` and `*/SKILL.md` under each skills dir. The model activates a skill via
an `activate_skill` tool; `/skills` manages them in-session and `gemini skills` installs and
uninstalls from the terminal.

### Frontmatter

`name` and `description` only. The loader in the installed bundle parses the frontmatter and
returns exactly `{name, description, location, body}`, so any other key is read and discarded.
Characters `: \ / < > * ? " |` in `name` are rewritten to `-`.

Duplicate skill names across source dirs are a hard error on install.

There is no Gemini sidecar. Gemini's `--allowed-tools` flag and `tools.allowed` setting are CLI and
settings surfaces, are deprecated in favor of the Policy Engine, and are unrelated to skill
frontmatter. Do not emit an `allowed-tools` frontmatter field expecting Gemini to honor it.

**Evidence:** <https://geminicli.com/docs/cli/skills/> (fetched 2026-08-17) for discovery paths;
`loadSkillFromFile` / `loadSkillsFromDir` in the `@google/gemini-cli@0.43.0` bundle for the parsed
field set and the name sanitizer.

---

## 4. Cursor

### Discovery

| Scope | Paths |
|-------|-------|
| Project | `.cursor/skills/`, `.agents/skills/`, nested dirs inside a monorepo |
| User | `~/.cursor/skills/`, `~/.agents/skills/` |
| Legacy | `.claude/skills/` and `.codex/skills/` also load |

Discovery is recursive, and a nested skill is automatically scoped to its containing subdirectory.

### Frontmatter

| Field | Required | Meaning |
|-------|----------|---------|
| `name` | Yes | Lowercase letters, numbers, hyphens |
| `description` | Yes | What it does and when to use it |
| `paths` | No | Glob patterns restricting the skill to matching files |
| `disable-model-invocation` | No | `true` requires explicit `/skill-name` |
| `metadata` | No | Arbitrary key-value mapping |

Cursor reads `.claude/skills/` directly, so a Claude Code skill usually needs no conversion at all
for Cursor beyond dropping fields Cursor ignores.

**Evidence:** <https://cursor.com/docs/context/skills> (fetched 2026-08-17).

---

## 5. Conversion matrix

What survives a port, what has to be translated, and what is simply lost.

| Concern | Claude Code | Codex | Gemini CLI | Cursor |
|---------|-------------|-------|-----------|--------|
| Core frontmatter | `name`, `description` | same | same | same |
| Extra frontmatter honored | 15+ fields (see §1) | none | none | `paths`, `disable-model-invocation`, `metadata` |
| Sidecar file | none | `agents/openai.yaml` | none | none |
| Tool pre-approval | `allowed-tools` | not supported, drop it | not supported, drop it | not supported, drop it |
| Suppress auto-invocation | `disable-model-invocation: true` | `policy.allow_implicit_invocation: false` | not supported | `disable-model-invocation: true` |
| Explicit invocation | `/skill-name` | `$skill-name` | `/skills`, `activate_skill` | `/skill-name` |
| Shell injection in body | `` !`cmd` `` | not supported, convert to prose or a `scripts/` call | not supported | not supported |
| UI display name / icon | none | `interface.*` in the sidecar | none | none |
| Path scoping | `paths` | not supported | not supported | `paths` |
| Subagent execution | `context: fork`, `agent` | not supported | not supported | not supported |
| Description budget | 1,536 chars for `description` + `when_to_use` in the listing | spec cap 1024 chars | spec cap 1024 chars | spec cap 1024 chars |

### Rules that follow from the matrix

1. **Convert down to the core, then re-extend.** Reduce the source to the six spec fields, then add
   the target's extensions. Do not hand-map Claude Code fields onto invented target fields.
2. **A dropped field is a behavior change, report it.** `allowed-tools` disappearing means the
   ported skill will prompt for permission. Say so in the conversion output rather than silently
   losing it.
3. **Fold Claude Code-only body syntax into prose or scripts.** Any `` !`cmd` `` placeholder must
   become an instruction to run the command, or a `scripts/` entry point, before the skill leaves
   Claude Code.
4. **Keep `name` equal to the directory name.** The spec requires it and Claude Code plugin
   namespacing is the only place where `name` legitimately differs from what the user types.
5. **Trigger phrases belong at the front of `description`.** Every provider truncates the listing
   text, and `description` is the only trigger signal all four share.

### Corrections to older poly-skill assumptions

These were wrong in the pre-2026-08-17 version of `SKILL.md` and are recorded so the same recalled
values do not creep back:

| Old claim | Verified reality |
|-----------|-----------------|
| `allowedTools` / `disableModelInvocation` (camelCase) | Claude Code uses `allowed-tools` and `disable-model-invocation` |
| Codex needs a `## Metadata` body section with `shortDescription` | No such section. Use `interface.short_description` in `agents/openai.yaml` |
| Codex sidecar is `<skill-name>.yaml` with `display:` / `tools:` / `policies:` | Sidecar is `agents/openai.yaml` with `interface:` / `dependencies:` / `policy:` |
| Terminal syntax is `` `!command` `` | It is `` !`command` ``, bang before the backticks |
| Codex and Claude Code have fundamentally different skill formats | They share the Agent Skills core. Only the extension surfaces differ |

---

## 6. Re-verification

Providers change these formats without notice, so this file is stale the moment a provider ships.
Re-verify when a conversion fails in a way the matrix does not predict, or on a scheduled review.

1. Refetch the four doc pages listed under Evidence and diff them against §1-§4.
2. Re-read the shipped Codex reference for the sidecar, it is authoritative for the installed
   version: `~/.codex/skills/.system/skill-creator/references/openai_yaml.md`.
3. Confirm the installed versions still match the ones this file was verified against:
   `npm ls -g --depth=0 | grep -E "codex|gemini-cli"`.
4. Update the "Verified" date at the top and add a row to §5's corrections table if a claim moved.

### Sources

| Provider | URL |
|----------|-----|
| Agent Skills spec | <https://agentskills.io/specification> |
| Claude Code | <https://code.claude.com/docs/en/skills> |
| Codex | <https://developers.openai.com/codex/skills> (redirects to <https://learn.chatgpt.com/docs/build-skills>) |
| Gemini CLI | <https://geminicli.com/docs/cli/skills/> |
| Cursor | <https://cursor.com/docs/context/skills> |
