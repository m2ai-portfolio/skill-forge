---
name: cowork-context-file-builder
description: Generates the three Claude Cowork context files (about-me.md, brand-voice.md, working-preferences.md) for a new Cowork workspace from a short intake interview. Use when onboarding a client to Claude Cowork, setting up a new workspace, or when the user says "set up my Cowork context files", "write my about-me for Cowork", or "help me configure my Cowork workspace."
---

# Claude Cowork Context File Builder

Generates all three required Claude Cowork context files from a guided intake interview. These files are loaded by Cowork at the start of every session — they are the difference between generic AI output and output that sounds like the client's best employee.

## Why these files matter

Without context files, every Cowork session starts blank. With them, Claude knows the business's voice, operating preferences, team structure, and what "done" looks like. This is the single highest-leverage setup step — every subsequent workflow benefits from it.

## Output files

The skill produces three files, ready to drop into `~/Claude-Workspace/context/`:

| File | Purpose |
|------|---------|
| `about-me.md` | Who the person/business is, role, team, tools in use, current goals |
| `brand-voice.md` | Tone, style, vocabulary, what to avoid, example sentences |
| `working-preferences.md` | Output format preferences, autonomy level, how to handle ambiguity, approval gates |

## Phase 1: Intake Interview

Ask these questions in a single message. Collect all answers before writing any files.

```
1. What's your name, your role, and what does your business do in one sentence?
2. Who do you primarily serve? (clients, customers, internal team — describe them briefly)
3. What tools do you use daily? (CRM, project tracker, comms, accounting — list them)
4. What are your top 2–3 goals for the next 90 days?
5. Share 2–3 samples of writing you're proud of (emails, docs, social posts — anything).
6. What words or phrases should Claude NEVER use when writing for you?
7. When Claude produces a draft, do you want it to: (a) act and show you the result, (b) show the plan first and wait, or (c) ask before every significant step?
8. How long should written outputs be by default? (bullet points, 2–3 paragraphs, full doc)
9. What does good work look like? Describe one piece of work you've delivered that you were genuinely proud of.
10. Anything else Claude should know about how you work or what's important to you?
```

Wait for all answers. Do not begin writing files until all 10 questions are answered.

## Phase 2: Generate Files

### about-me.md

```markdown
---
context: about-me
last-updated: {YYYY-MM-DD}
---

# About Me

## Who I Am
{Name}, {role}, {business description — 2 sentences max}

## My Team
{Team structure, key people Claude might interact with}

## My Tools
{Numbered list of tools, one per line, with brief purpose note}

## My Current Goals (next 90 days)
{Numbered list — direct from intake Q4}

## My Clients / Customers
{Who I serve — direct from intake Q2, expanded slightly}
```

### brand-voice.md

```markdown
---
context: brand-voice
last-updated: {YYYY-MM-DD}
---

# Brand Voice

## Tone
{3–5 adjectives describing the voice, derived from the writing samples}

## Style Rules
- {Rule 1 derived from samples}
- {Rule 2 derived from samples}
- {Rule 3 derived from samples}

## Vocabulary
**Use:** {words and phrases that appear in samples}
**Avoid:** {words from intake Q6 + any that contradict the samples}

## Signature Patterns
{1–3 patterns observed in the writing samples: how they open, how they close, sentence length, use of lists vs. prose}

## Example Sentences
> {1 sentence in their voice}
> {1 sentence in their voice — different register}
```

### working-preferences.md

```markdown
---
context: working-preferences
last-updated: {YYYY-MM-DD}
---

# Working Preferences

## Autonomy Level
{Map intake Q7 to one of: "Act and report" / "Show plan, then act" / "Confirm each step"}

## Default Output Format
{Map intake Q8 to specific format description}

## Ambiguity Handling
{Derived from Q7 + Q9: how to handle unclear instructions}

## Quality Bar
{What "done" looks like — from intake Q9, made concrete}

## Approval Gates
{Any step types that always require human approval before execution}

## What Good Looks Like
{1 paragraph distilled from intake Q9}
```

## Phase 3: Deliver and Explain

After writing the three files:

1. Show each file in full, one at a time.
2. After each file, ask: "Anything to adjust in this one before we move on?"
3. After all three are approved, provide the save instruction:

```
Save these files to:
  ~/Claude-Workspace/context/about-me.md
  ~/Claude-Workspace/context/brand-voice.md
  ~/Claude-Workspace/context/working-preferences.md

Then in any Cowork session, these files will load automatically if you've added context/ to your Cowork projects. To verify, open a new Cowork session and ask: "What do you know about me?"
```

## Source

Intake: `cowork-2026-06-07.md` — Derived from Claude Cowork Complete Deep Dive, Section 1 (Workspace Folder Structure + Skill File Anatomy) and Section 8 (Pre-Training Checklist). Identified as the highest-leverage low-effort build for Cowork client onboarding.
