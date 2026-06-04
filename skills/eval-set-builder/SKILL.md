---
name: eval-set-builder
description: Turn 3–5 representative real tasks from your actual workflow into a reusable routing benchmark. Scores models and harnesses on correctness, source discipline, review burden, time-to-accepted-artifact, cost, and failure behavior. Re-run on each new model release to get evidence instead of vibes. Trigger: "eval set builder", "build a benchmark", "routing benchmark", "compare models on real work", "test suite for model selection", "eval-set-builder".
---

# Eval Set Builder

Builds a reusable benchmark from your actual work — not synthetic tasks — so you can compare models and harnesses with evidence instead of benchmarks that don't reflect your use case.

The core insight: most model comparisons fail because they test generic tasks (summarize this paragraph, write a function) that don't predict performance on YOUR specific work. A 5-task eval set built from your real tasks is a standing test you can rerun on every new model or harness change and get directly comparable results.

## When to Use

- You want to know whether a new model version is actually better for your workflows before migrating.
- You're choosing between two harnesses (e.g., two agent frameworks, two prompting approaches) and need more than intuition.
- You're onboarding a team to model routing and need a shared benchmark they can all run.
- A new model has been released and you want fast evidence on whether to switch defaults.

## Phase 1: Collect Real Tasks

Ask the user to provide 3–5 representative tasks from their actual work. Aim for one task per category if possible:

| Category | What it tests |
|----------|---------------|
| **Writing / synthesis** | Long-form output quality, source discipline, citation fidelity |
| **Messy data / reconciliation** | Handling inconsistency, provenance, rejection logic |
| **Coding / repo** | Correctness, test coverage, context window efficiency |
| **Visual / artifact** | Diagram quality, formatting, presentation judgment |
| **Long-running / state-loss prone** | Memory across steps, goal persistence, context churn |

If the user has fewer than 5 tasks, use what they have. Do not pad with invented tasks — a 3-task eval is better than a 5-task eval where 2 tasks are synthetic.

For each task, collect:
1. **Task description** — the full prompt or task brief as you'd actually send it
2. **Accepted output example** (optional but strongly recommended) — a real past output you considered good
3. **Known failure modes** — what went wrong the last time this task was run on a model that didn't perform well

## Phase 2: Build the Scoring Rubric

For each task, define the scoring dimensions relevant to that task type. Use this default set and trim dimensions that don't apply:

| Dimension | Description | Scoring |
|-----------|-------------|---------|
| **Correctness** | Is the output factually or functionally correct? | 0–3 (0=wrong, 1=mostly wrong, 2=mostly right, 3=fully correct) |
| **Source discipline** | Are claims traceable? No hallucinated citations? | 0–2 (0=untraceable, 1=partial, 2=fully sourced) |
| **Review burden** | How much human review is required before the output is usable? | 0–3 (0=full rework, 1=heavy edits, 2=light edits, 3=ship as-is) |
| **Time to accepted artifact** | Wall-clock time from prompt to output you'd accept | Record actual time in seconds/minutes |
| **Cost** | Token cost or API cost for the run | Record in tokens or $ |
| **Failure behavior** | When wrong, does it fail loudly or silently? | 0–2 (0=silent error, 1=partial disclosure, 2=clear failure signal) |
| **Visual quality** | If the output has a visual dimension, does it present well? | 0–2 (0=confusing, 1=adequate, 2=clear) |
| **Epistemic honesty** | Did the model flag what it didn't know? | 0–2 (0=confident and wrong, 1=partial, 2=appropriately hedged) |

Write the rubric to a file named `eval-rubric.md` in the output directory. This prevents the model from silently setting a low bar.

## Phase 3: Run the Eval

For each task × model/harness combination:

1. Send the task prompt without modification (the rubric scores consistency, not a hand-tuned best effort).
2. Record the output and the metadata: model name, harness version, effort level (if applicable), timestamp, token count.
3. Score the output against the rubric immediately — before running the next task or the next model. Delayed scoring introduces recency bias.
4. Record the score in a results file.

Recommended results file format (`eval-results.csv`):

```
task_id,task_name,model,harness,effort_level,correctness,source_discipline,review_burden,time_sec,cost_usd,failure_behavior,visual_quality,epistemic_honesty,total_score,notes
```

## Phase 4: Comparison Report

After all runs are complete, produce a comparison table:

```
EVAL SET RESULTS — <date>
Tasks: <n>
Models / harnesses compared: <list>

TASK-BY-TASK SUMMARY
Task 1 — <name>: Winner = <model/harness> (score: N/M) | <key differentiator>
Task 2 — <name>: Winner = <model/harness> (score: N/M) | <key differentiator>
...

AGGREGATE RANKING (total score across all tasks)
1. <model/harness> — <total score>
2. <model/harness> — <total score>
...

DIMENSION WINNERS (which model won each scoring dimension)
Correctness:       <winner>
Source discipline: <winner>
Review burden:     <winner>
...

ROUTING RECOMMENDATION
For <task type>: use <model/harness> — <one sentence reason>
For <task type>: use <model/harness> — <one sentence reason>
...

CAVEATS
- <any dimension where results were close or inconclusive>
- <any task where the scoring was ambiguous>
```

## Phase 5: Schedule Recurring Runs

To get value from this benchmark over time, it must be re-run when models change. Provide the user with a rerun prompt they can paste into a scheduled task:

```
Re-run the eval set at <path>/eval-tasks.md against the following models: <list>.
Use the rubric at <path>/eval-rubric.md.
Append results to <path>/eval-results.csv with today's date.
Produce a comparison against the previous run and flag any dimension where the new model performs worse than the prior winner.
```

## Common Pitfalls

- **Never let the model self-select the tasks.** It will choose tasks it handles well. Insist the user provides real past examples.
- **Score immediately after each run.** Batch scoring at the end produces compressed scores with low variance.
- **Keep the accepted-output example separate from the scoring session.** If the model sees its own prior output as the "accepted example," it will score toward it.
- **Record effort level.** High vs. extra vs. max effort can change scores dramatically. An "extra" run that beats a "max" run at lower cost is a meaningful result.
- **Don't trim tasks to make the benchmark easier to run.** A 3-task benchmark you actually run is better than a 5-task benchmark you skip.

## Output Files

| File | Contents |
|------|----------|
| `eval-tasks.md` | One section per task: prompt, accepted-output example, known failure modes |
| `eval-rubric.md` | Scoring dimensions and scale definitions |
| `eval-results.csv` | One row per task × model × run |
| `eval-report.md` | Latest comparison report (overwritten on each run) |

Default output location: current directory unless the user specifies otherwise.

## Source Attribution

Technique: 5-task real-work routing benchmark with per-dimension scoring
Source: Nate's Newsletter (natesnewsletter@substack.com) — "Opus 4.8 scored 81 in my benchmark"
Published: 2026-06-03
Idea reference: Idea #5 — Eval Set Builder
