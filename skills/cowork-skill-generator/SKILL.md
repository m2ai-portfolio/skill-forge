---
name: cowork-skill-generator
description: Generates a properly formatted Claude Cowork skill file (.md) from a workflow description. Takes the workflow goal, inputs, process steps, output format, trigger type, and connector dependencies, then outputs a deployable skill file in the canonical Cowork anatomy. Use when the user says "create a Cowork skill for X", "write a skill file for this workflow", "package this as a Cowork skill", or when building a Skills Pack.
---

# Claude Cowork Skill Generator

Converts a workflow description into a deployable Claude Cowork skill file. The canonical skill anatomy is fixed — this skill ensures every output is correctly structured so it activates with `/` in Cowork and runs consistently every time.

## Skill File Anatomy (target format)

Every generated skill file follows this structure exactly:

```markdown
---
name: {kebab-case-name}
description: {one sentence — what it does and when to use it}
---

# {Human-Readable Title}

## Purpose
{2–3 sentences: what problem this solves and who uses it}

## Trigger
Type `/{name}` in any Cowork session, or reference it naturally: "{example natural language trigger}"

## Inputs
| Input | Format | Required | Notes |
|-------|--------|----------|-------|
| {input} | {file / text / connector data} | Yes/No | {note} |

## Process
1. {Step 1}
2. {Step 2}
3. {Step 3}
{...}

## Output
**Format:** {file type or structured text}
**Destination:** {path or delivery method}
**Naming:** {naming convention}

## Trigger Type
{Manual / Scheduled: {frequency} / File-event: {watch path} / Webhook: {endpoint}}

## Connectors Required
{List each MCP connector or "Local filesystem only" if none}

## Example
**Prompt:** `/{name} {example-args}`
**Result:** {brief description of what gets produced}

## Notes
{Any caveats, rate limits, auth requirements, or edge cases}
```

## Phase 1: Workflow Intake

Ask the user for (or extract from context):

1. **Goal in one sentence** — what does this workflow accomplish?
2. **Inputs** — what does Claude need to start? (files, CRM data, a URL, user-typed text?)
3. **Process** — what are the steps? (numbered list, or free description)
4. **Output** — what's the deliverable? (file, email, Slack message, spreadsheet row?)
5. **Trigger** — how should it start? (manual `/command`, daily schedule, file drop, webhook?)
6. **Connectors** — which SaaS tools are involved? (or "local filesystem only")
7. **Audience** — who runs this? (the owner, a team member, a scheduled agent?)

If the user provides a workflow from the Catalog (Section 2 of the Cowork Deep Dive), skip intake and extract from the catalog entry directly.

## Phase 2: Generate the Skill File

Apply the anatomy from above. Rules:

- `name` field: kebab-case, max 30 characters, starts with a verb if possible (`process-invoices`, `generate-report`, `triage-inbox`)
- `description` field: written for activation — what it does, when to invoke it. Max 2 sentences.
- Process steps: write as Claude instructions, not user steps ("Read all PDF files in `{input_folder}`", not "The user uploads invoices")
- Output section: always specify destination path, naming convention, and whether it overwrites or appends
- Notes: include any "no undo" warnings (file-altering skills must note this)

## Phase 3: Validate

Before delivering, check against the quality bar:

- [ ] Skill activates with `/name` — no spaces, no special characters in the name field
- [ ] All required inputs are listed in the Inputs table
- [ ] Process steps are written as agent instructions (imperative: "Extract...", "Compare...", "Write...")
- [ ] Output destination is a specific path, not "somewhere useful"
- [ ] File-altering operations include a backup or review note
- [ ] Connectors section matches the process steps (no connector listed that isn't used)

## Phase 4: Deliver

Output the skill file in a code block ready to save. Provide the save path:

```
Save to: ~/Claude-Workspace/skills/{name}.md
Activate: Type /{name} in any Cowork session
```

If this skill is part of a pack, note the full pack structure:
```
~/Claude-Workspace/skills/
├── {name-1}.md
├── {name-2}.md
└── {name-3}.md
```

## Source

Intake: `cowork-2026-06-07.md` — Derived from Claude Cowork Complete Deep Dive, Section 3 (Skills Reference) and Section 1 (Skill File Anatomy). Identified as the production engine for the Real Estate Skills Pack and any client Skills Pack delivery.
