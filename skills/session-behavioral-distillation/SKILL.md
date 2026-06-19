---
name: session-behavioral-distillation
description: Extract a reference model's working rhythm (tool cadence, read:edit ratios, action sequences) from JSONL session history, compare it against your current model, and distill the delta into an injectable behavior playbook. Trigger: "make [model] behave like [reference model]", "distill [model] behavior", "clone Fable's working style", "model behavior playbook", "imitate how [model] planned and used tools".
---

# Session Behavioral Distillation

Mine your Claude Code or Codex JSONL session files to extract a reference model's **working rhythm** as measured numbers, compare it against your current model's rhythm, and produce a compact behavior playbook you can inject at the start of every session to close the gap.

The technique does not replicate the reference model's raw capability. It distills the delta in HOW it worked: what it did first, how it sequenced tools, how disciplined it was about reads before edits and tests after edits. That delta lives in a prompt-sized playbook file.

## When to Use

Trigger when:
- A high-capability model is unavailable and you want your current model to behave more like it
- You have enough session history with a reference model to measure its patterns (10+ sessions is a useful floor)
- You want to inject a behavioral scaffold into every new session without maintaining a long CLAUDE.md

Do NOT use for:
- Personalized model onboarding (what changed for MY workflows with a new release) -- that is `session-history-model-onboarding`
- API compatibility checks before a model switch
- Cost projections for changing models

## Prerequisites

- Python 3 available in your shell
- Claude Code or Codex JSONL session files (default: `~/.claude/projects/` on Linux, `~/.config/claude/projects/` on macOS)
- OR: an open-source session archive from HuggingFace if you lack personal history for the reference model

## Phase 1: Assess Session Volume

Before building any scripts, get a count so you can set realistic scope expectations:

```
Ask Claude Code: "How many JSONL files exist across all my session history?
List the top 5 projects by file count."
```

If you have fewer than 10 sessions for the reference model, pull an open-source archive instead:
search HuggingFace for session datasets tagged with the reference model name.

## Phase 2: Build a Strip Script

Ask Claude Code to build a lightweight Python script that takes a single JSONL session file and strips it down to a clean transcript. Keep only what matters for behavioral analysis; discard everything else:

```
"Write a Python script strip_session.py that takes a Claude Code JSONL session file path
as an argument and outputs a lightweight transcript containing:
  - timestamp of each turn
  - model ID (the message.model field)
  - user message text
  - assistant message text (stripped of tool result echoes, file content blocks, and command output)
  - ordered list of tool names called in this turn

Test it on one file first. Show me the output before proceeding."
```

Verify the output looks like a readable back-and-forth before proceeding. One file, confirmed, then scale.

## Phase 3: Filter and Corpus the Reference Model

Once the strip script works, extract only the reference model's turns across all sessions:

```
"Now use strip_session.py to process all JSONL files under [SESSION_PATH].
For each turn where message.model matches [REFERENCE_MODEL_ID], write that turn to
a combined corpus file called reference_corpus.txt.
Include the session filename and timestamp as context headers for each turn block."
```

The `message.model` field in JSONL files tags exactly which model produced each response,
so you can filter cleanly even in mixed-model sessions.

## Phase 4: Measure Behavioral Patterns as Numbers

Ask Claude Code to analyze the corpus and produce concrete metrics, not impressions:

```
"Analyze reference_corpus.txt and report these behavioral metrics as real numbers:
  - average tool calls per turn
  - ratio of Read/Glob/Grep calls to Edit/Write calls (reads before edits)
  - ratio of test-execution calls after Edit/Write calls (tests after edits)
  - top 5 most-used tools in order
  - average turns before first Edit/Write (planning depth)
  - percentage of turns that opened with a read-only tool vs a write tool

Output as a table."
```

## Phase 5: Run the Same Measurement on Your Current Model

```
"Repeat the exact same behavioral analysis on [CURRENT_MODEL_ID] turns from the same
session history. Output the same table format so I can see both side by side."
```

This gives you the delta: where does your current model diverge from the reference model's rhythm?

## Phase 6: Distill the Delta into a Behavior Playbook

```
"Based on the side-by-side comparison, write a behavior playbook file called
behavior_playbook.md. The playbook should:
  1. State the 3-5 biggest behavioral gaps (e.g., 'current model edits before reading 40% more often')
  2. Translate each gap into a concrete instruction for the current model
  3. Keep the total playbook under 400 tokens so it can be injected at session start

Format it as a tight set of behavioral rules, not a narrative."
```

## Phase 7: Inject the Playbook

Three injection options, in order of persistence:

**Hook (per-session, automatic):**
Create a `SessionStart` hook in your Claude Code settings that prepends the playbook
to the system context at the start of every session.

**Skill (on-demand):**
Save the playbook as a skill you invoke at the start of sessions where you need
the behavioral alignment.

**CLAUDE.md (always-on for a project):**
Append the playbook rules directly to the project's CLAUDE.md. This is the
highest-priority injection but affects every session in that project.

## Verification

A successful distillation produces:
- A playbook with numbered, testable rules (not vague advice)
- Each rule traces back to a measured gap in the comparison table
- At least one rule addresses tool sequencing (reads before writes, tests after edits)
- The playbook fits in one screen without scrolling

Run a session with the injected playbook and spot-check: does the model now pause to
read before editing more often? Does it run a verification step after writes? Measure
the same metrics on one or two new sessions to confirm the gap narrowed.

## Source Attribution

Technique: Behavioral Distillation from JSONL Session History
Source: Mark Kashef YouTube
URL: https://www.youtube.com/watch?v=B95cu7seTm8
Published: 2026-06-14
Title: "Make Any Model Think Like Fable in 10 Minutes (It's Easy)"
