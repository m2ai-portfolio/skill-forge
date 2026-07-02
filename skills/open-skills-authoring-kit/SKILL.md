---
name: open-skills-authoring-kit
description: "Author a complete, structured SKILL.md (agent runbook) from scratch using the five-part schema: trigger, tools, boundaries, verification, and phases. Produces a ready-to-use skill file that any Claude Code agent can invoke. Trigger on: 'help me write a skill', 'create a runbook for this task', 'draft a SKILL.md', 'I want to teach my agent to do X', 'make this repeatable', or any request to codify a repeatable agent behavior into a reusable file."
---

# open-skills-authoring-kit — structured agent skill authoring

Turns a description of a repeatable task into a complete SKILL.md that an agent can load
and execute reliably. The five-part schema (trigger, tools, boundaries, verification, phases)
makes the resulting file both agent-readable and human-auditable.

## Purpose

Skills fail in three ways: the agent invokes them at the wrong moment (bad trigger),
exceeds its authority while running them (missing boundaries), or has no way to know
if the run succeeded (no verification). This kit forces all three to be explicit before
any code or automation is written.

## Phase 1 — Elicit the skill spec

Ask only what isn't already clear. If the user has described the task in their message,
fill in what you can infer and ask for only the missing fields in a single exchange.

**1. Name**
A hyphen-separated slug: `verb-noun` or `noun-action`. Examples: `weekly-digest-sender`,
`invoice-validator`, `code-review-summary`. Keep it under 32 characters.

**2. One-line description (for the frontmatter)**
Complete this sentence: "Use this skill when ___." It must name the trigger condition
AND the outcome. This is what the agent reads to decide whether to invoke the skill.
Cap at 200 characters.

**3. Trigger**
What does the user say (or what condition is true) that should activate this skill?
List 3-5 example phrases or observable states. Vague triggers cause false invocations;
over-specific triggers cause missed invocations. Test both directions.

**4. Tools**
What tools or capabilities does the agent need during this skill's execution?
Examples: Read, Write, Bash, WebFetch, a specific CLI, an external API. List each
with a one-line note on what it is used for.

**5. Boundaries**
What must the agent NOT do during this skill without explicit human approval?
Start with the universal minimums: no external send/publish, no destructive writes,
no credential or billing changes. Then add task-specific limits.

**6. Verification**
How does the agent (or the user) confirm the skill ran correctly?
Prefer artifact-first checks: "file X exists at path Y", "command exits 0",
"field Z in output matches expected pattern". At least two criteria.

**7. Phases**
Break the task into 2-5 sequential phases. Each phase is a named step with a one-line
description of what happens and what the output is. Order matters — later phases should
depend on earlier outputs, not re-do work.

## Phase 2 — Generate the SKILL.md

Produce the file in this format:

```markdown
---
name: [slug]
description: "[one-line trigger + outcome description]"
---

# [skill name] — [subtitle]

[One paragraph: what this skill does and why it exists. No bullet lists here.]

## Trigger

Use when [specific condition or phrase]. Do NOT use when [anti-trigger].

Activation phrases:
- "[example phrase 1]"
- "[example phrase 2]"
- "[example phrase 3]"

## Tools required

- **[Tool 1]** — [what it does in this skill]
- **[Tool 2]** — [what it does in this skill]

## Boundaries

The agent must NOT do the following without explicit human approval:
- [Boundary 1]
- [Boundary 2]
- Send, publish, or post to any external party
- Modify credentials, billing, or access controls
- Delete or overwrite source data

## Phase 1 — [Phase name]

[What happens. What input is consumed. What output is produced.]

## Phase 2 — [Phase name]

[What happens. What input is consumed. What output is produced.]

(Add phases as needed. Two minimum, five maximum.)

## Verification

Before reporting completion:
- [ ] [Criterion 1 — artifact or observable state]
- [ ] [Criterion 2 — artifact or observable state]

## Source
[Attribution if applicable]
```

## Phase 3 — Anti-pattern review

Before handing off the draft, check for these common authoring failures:

- **Vague trigger**: "use when the user wants to do something related to X" — not specific enough
- **Missing anti-trigger**: if the trigger phrase could fire in the wrong context, add a DO NOT USE clause
- **Tool without purpose**: listing a tool without saying what the skill uses it for adds noise
- **Open-ended boundaries**: "be careful" is not a boundary — name the specific action that requires approval
- **Quality-only verification**: "looks good" is not verifiable — require an artifact or exit code

## Verification

Before delivering the SKILL.md:
- [ ] Name is `verb-noun` or `noun-action`, under 32 characters
- [ ] Description completes "Use this skill when ___" in under 200 characters
- [ ] At least 3 trigger phrases listed
- [ ] Every tool has a one-line purpose note
- [ ] Boundaries explicitly name actions (not just "be careful")
- [ ] At least 2 artifact-first verification criteria

## Source

Nate's Newsletter, 2026-07-01 — "You can build 80% of your own AI memory by talking to the agent already on your computer"
Pattern: Open Skills — reusable agent runbook format with trigger/tools/boundaries/verification/phases schema.
URL: https://natesnewsletter.substack.com/p/open-stack-ai-memory
Field guide: https://unlock-ai.natebjones.com/guides/open-stack/open-stack-field-guide
