---
name: personal-model-benchmark
description: Mine your own AI conversation history to discover your recurring task categories, build a personal rubric, and run automated head-to-head comparisons of any two AI models at configurable effort levels. Produces a comparative report grounded in your actual work -- not synthetic benchmarks. Use when a new model drops and you want to know whether it improves your specific tasks before switching.
---

# Personal Model Benchmark

Turns your conversation history into a test suite. Instead of watching model-comparison videos that test tasks you'll never do, this skill identifies what you actually ask AI to do, scores two models against it with your own rubric, and gives you a clear verdict.

## Trigger

Use when the user says "benchmark this model", "compare these models for my work", "is it worth switching to X", "personal benchmark", "does X actually improve my workflow", "test model against my real tasks", or a new model has dropped and the user wants to know if it changes anything for them.

## Phase 1: Locate Conversation History

Ask the user where their conversation JSONL or transcript files live. Common paths:
- Claude Code: `~/.claude/projects/*/` (session transcript files)
- Generic: any directory containing `.jsonl` files with conversation data

Scan up to 500 most-recent files to keep the discovery pass bounded. Report how many files were found and the approximate date range they cover.

## Phase 2: Mine Recurring Task Categories

Read a sample of the conversation files (up to 100, newest first) and extract the user's recurring task patterns:

For each conversation, identify:
- The core task type (email writing, code review, research, summarization, data analysis, copywriting, etc.)
- Approximate frequency across the sample
- A representative prompt that captures the pattern

Produce a **task inventory** -- a ranked list of the top 5-10 task categories by frequency, each with:
- `task_id`: short slug (e.g. `cold-email`, `code-review`, `research-brief`)
- `description`: one sentence describing what the user asks for
- `frequency_pct`: estimated share of total conversations
- `sample_prompt`: a representative prompt from the history (anonymized -- remove names, URLs, PII)

Present the task inventory to the user and ask them to confirm, remove any tasks they don't want tested, or add tasks the mining missed.

## Phase 3: Define the Rubric

Offer the user a default rubric and let them customize it:

**Default rubric dimensions** (each 0-10):

| Dimension | What it measures |
|-----------|-----------------|
| `quality` | Output quality for the task type -- does it actually answer well? |
| `instruction_fidelity` | Did the model follow the exact instructions given? |
| `token_efficiency` | Was the response appropriately sized -- not bloated, not truncated? |
| `speed_turns` | Fewer turns to completion is better; more tool calls = more context bloat |
| `vibe` | Tone calibration -- appropriate formality, not preachy, not sycophantic |

Ask the user:
1. Are these the right dimensions? Any to add or remove?
2. Do you want to weight any dimension more heavily? (Default: equal weight)
3. Any dimension-specific rubric clarifications (e.g. "quality for cold email means concise + clear CTA")?

Save the finalized rubric as a structured block the model will use for scoring.

## Phase 4: Configure the Comparison

Ask the user which models to compare and at what effort levels:

```
Model A: [e.g. claude-opus-5 at medium effort]
Model B: [e.g. claude-sonnet-5 at low effort]
Trials per task: [default 3]
Tasks to test: [from confirmed inventory, default all]
```

Effort levels: `low`, `medium`, `high` (maps to the model's reasoning/extended-thinking settings where available).

Confirm the full test matrix before running: `N tasks × 2 models × effort level × trials = X total runs`. For large matrices, warn if X > 30 and suggest reducing trials or tasks.

## Phase 5: Run the Comparisons

For each cell in the test matrix:
1. Send the sample prompt to the specified model at the specified effort level.
2. Collect: response text, approximate token count, number of tool calls (if any), wall-clock time.
3. Score the response against each rubric dimension.
4. Record the raw scores and a one-sentence justification for each dimension.

**Grading discipline**: score each response independently before comparing -- do not let seeing Model B's response change your score for Model A.

Output a live progress table as cells complete:

```
Task            | Model A (low) | Model B (low) | Status
----------------|---------------|---------------|-------
cold-email      |   7.4         |   8.1         | done
code-review     |   running...  |   queued      | ...
```

## Phase 6: Generate the Report

Produce a structured comparative report:

```markdown
# Model Benchmark Report
Generated: <date>
Models compared: <Model A config> vs <Model B config>
Tasks tested: N | Trials per task: N | Total runs: N

## Summary Verdict
[ONE OF:]
- SWITCH: Model B clearly outperforms Model A across your actual work (+X% weighted score)
- STAY: Model A holds its own; switching provides marginal or no benefit for your tasks
- SPLIT: Model B wins on [task types], Model A wins on [task types] -- consider routing
- EVEN: Results are within noise; switch only if cost or speed favor one

## Per-Task Results
[For each task: weighted score for each model, winning model, margin, notes]

## Dimension Breakdown
[Radar-style table: how each model scored per rubric dimension]

## Notable Findings
[Any dimension where one model clearly dominates; any tasks with surprising results]

## Raw Scores
[Full trial-by-trial data for reproducibility]
```

## Verification

A good benchmark run:
- Tests at least 3 task categories (single-task results are noisy)
- Uses representative prompts from real history, not synthetic ones
- Has at least 2 trials per cell to reduce single-response variance
- The Summary Verdict matches the per-task data -- no softening a clear result
- Raw scores are included so the user can audit any surprising verdict

## Source

Extracted from Mark Kashef YouTube: "Stop Guessing Which Model to Use. Build THIS Instead." (2026-07-26)
URL: https://www.youtube.com/watch?v=3ICM9ZdflZA
