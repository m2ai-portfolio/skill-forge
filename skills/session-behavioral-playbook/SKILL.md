---
name: session-behavioral-playbook
description: Mine your own Claude Code JSONL session history to extract a behavioral playbook that makes any model act more like a target model (e.g. Fable 5). Parses session files, strips bloat, filters by model tag, runs a side-by-side behavioral comparison, and distills the delta into an injectable playbook. Use when the user says "make my model act like Fable", "extract behavioral playbook", "analyze my session history", "why does Fable behave differently", "model behavior diff", or wants to close the behavioral gap between two Claude Code models.
---

# Session Behavioral Playbook

Extract the behavioral DNA of a superior model from your JSONL session history and inject it
into any other model via a playbook file. The technique works even if you have little personal
Fable history -- community datasets on Hugging Face provide a substitute corpus.

## Trigger

Use when the user says "make my model act like Fable", "extract behavioral playbook",
"analyze my session history", "model behavior diff", "close the gap between models",
"why does Fable plan better", or wants to replicate a higher-capability model's working rhythm
in a model they currently have access to.

## Prerequisites

- Claude Code session JSONL files at `~/.claude/projects/` (standard location)
- Python available in the shell
- Optional: community Fable session dataset from Hugging Face if personal history is thin

## Phase 1: Assess the Corpus

1. Count available JSONL files across all projects:

```bash
find ~/.claude/projects -name "*.jsonl" | wc -l
```

2. Report the number back to the user. Ask which model pair to compare (e.g. "Fable 5 vs Opus 4.8"). If Fable history is sparse, offer the Hugging Face community corpus as an alternative: `https://huggingface.co/datasets/` (search for open-sourced Claude Fable sessions).

3. Confirm the exact model name strings to filter on (e.g. `claude-fable-5`, `claude-opus-4-8`). These must match the `message_model` tag inside the JSONL files.

## Phase 2: Strip the Bloat

Have Claude Code generate a lightweight transcript extractor script that strips everything except the signal. The script should:

- Accept a single JSONL file path as input
- Skip `tool_result` blocks (raw file contents, command output echoed back into context)
- Keep: timestamp, model name, user message text, assistant message text, tool call names and order (not their full outputs)
- Write output to `/tmp/session-playbook/transcript-{filename}.txt`

Run on one file first to verify the format is correct before processing the full corpus.

## Phase 3: Build the Model Corpus

Once the transcript format is verified, extend the script to process the full history:

- Walk all JSONL files under `~/.claude/projects/`
- Filter to only turns where `message_model` matches the **target model** (e.g. Fable 5)
- Combine all filtered turns into a single corpus file: `/tmp/session-playbook/fable-corpus.txt`
- Add a summary header: total sessions, total turns, date range

If using the Hugging Face dataset instead, download and preprocess it to the same format.

## Phase 4: Behavioral Analysis

Ask Claude Code to analyze the corpus for measurable behavioral patterns. Request **numbers, not impressions**:

- Tool call distribution: which tools called most, in what order
- Read-to-edit ratio: how many reads before the first edit per task
- Test-after-edit rate: how often does a write/edit get followed by a test command
- Planning depth: average number of planning turns before first action
- Turn count per task type: how many total turns for coding tasks vs. research tasks
- Bash chain length: average number of commands chained per Bash call

Output to `/tmp/session-playbook/fable-behavioral-stats.md`.

## Phase 5: Side-by-Side Comparison

Run the exact same behavioral analysis against the **current model** corpus (e.g. Opus 4.8). Then ask Claude Code to produce a side-by-side diff showing:

- The measured delta on each behavioral dimension
- Which gaps are model-weight-driven (cannot be closed with a playbook) vs. behavioral (can be elicited via prompt)
- Specific examples of where Fable showed more disciplined tool sequencing

Output to `/tmp/session-playbook/model-comparison.md`.

## Phase 6: Distill the Playbook

Instruct Claude Code to take the comparison and distill only the **elicitable behaviors** into a playbook file. The playbook should:

- Be written as direct instructions to the model (imperative tone)
- Address: planning discipline, tool call sequencing, read-before-edit ratio, test cadence
- Include concrete examples drawn from the corpus where possible
- Be short enough to inject at session start without meaningful token cost (aim for under 800 tokens)

Write to: `~/.claude/playbooks/fable-behavioral-playbook.md`

## Phase 7: Inject the Playbook

Choose the injection method that fits the workflow:

**Option A: Hook injection (persistent, every session)**

Ask Claude Code to add a `SessionStart` hook in `~/.claude/settings.json` that appends the playbook file to context at session start.

**Option B: CLAUDE.md rule (always-on, workspace-scoped)**

Add a line to the relevant `CLAUDE.md`: `Always apply the behavioral patterns in ~/.claude/playbooks/fable-behavioral-playbook.md`.

**Option C: Manual invocation (on-demand)**

Drag-and-drop the playbook file into a new session, or reference it directly: "Apply the learnings from `~/.claude/playbooks/fable-behavioral-playbook.md` to this session."

Option A is the highest-leverage choice for daily use; Option C is lowest commitment for experimentation.

## What This Does and Doesn't Fix

This playbook approach closes **behavioral gaps** -- planning discipline, tool sequencing rhythm, deliberation before action. It does not recover capabilities that live in the model weights themselves (reasoning depth, novel code synthesis, long-horizon coherence). The expectation should be a measurably stronger Opus execution, not a Fable substitute.

## Source Attribution

Technique from Mark Kashef: "Make ANY Model Think Like Fable in Minutes" (2026-06-14)
https://www.youtube.com/watch?v=B95cu7seTm8
