---
name: optimization-loop-kill-switch
description: "Detect when an agent optimization loop has plateaued and halt it before it burns further compute on marginal gains. Tracks improvement-per-token (or improvement-per-dollar) across iterations and halts or escalates when the gain curve flattens — preventing the class of incident where an agent spends hundreds of dollars optimizing to an architectural ceiling while a fundamentally better approach exists. Trigger phrases: \"stop the loop when it's not improving\", \"plateau detector\", \"kill the loop when gains flatten\", \"optimization kill-switch\", \"improvement-per-dollar\", \"halt when stuck\", \"loop ceiling\"."
---

# Optimization Loop Kill-Switch

## The Problem

An agent optimization loop (benchmark tuning, prompt refinement, code performance improvement) will spend to the ceiling of the task as framed, whether or not that ceiling is worth reaching. A loop can burn hours and significant compute optimizing to a marginal limit when the correct fix is a fundamentally different architecture — a change the loop cannot discover because the task framing ruled it out.

This skill installs a kill-switch: a heuristic that tracks gain per unit of compute spent and halts (or escalates) when the ratio drops below a threshold, before the loop exhausts its budget.

## When to Invoke

- "stop the loop when gains flatten", "plateau detector", "optimization kill-switch", "loop ceiling"
- Before starting any iterative optimization loop with a non-trivial compute budget
- When a prior optimization run spent its full budget with diminishing returns
- When the improvement metric is numeric and measurable per iteration

## Phase 1: Define the Gain Signal

Ask the user:

1. **What is the metric being optimized?** (benchmark score, latency ms, test pass rate, eval score, etc.)
2. **What unit of compute is being spent?** (tokens, dollars, wall-clock time, API calls)
3. **What is the minimum meaningful improvement per iteration?** (the "noise floor" — gains below this are effectively flat)

Record as:
```
gain_signal: <metric>
compute_unit: <unit>
noise_floor: <value>        <- gains below this count as flat
flat_window: <N iterations> <- halt if gain stays below noise_floor for N consecutive iterations
```

A safe default: `flat_window: 3` and `noise_floor` set to 1% of the target range.

## Phase 2: Instrument the Loop

For each loop iteration, the kill-switch requires three data points logged to a ledger file:

```
iteration: N
metric_before: <value>
metric_after: <value>
compute_spent: <value>
gain: metric_after - metric_before
gain_per_unit: gain / compute_spent
```

Ledger path: `./optimization-ledger.jsonl` (configurable via env var `OPTLOOP_LEDGER`).

Python logging template (adapt to the loop language or tooling):

```python
import json, os

def log_iteration(n, before, after, compute):
    gain = after - before
    entry = {
        "iteration": n,
        "metric_before": before,
        "metric_after": after,
        "compute_spent": compute,
        "gain": gain,
        "gain_per_unit": gain / compute if compute else 0,
    }
    with open(os.getenv("OPTLOOP_LEDGER", "optimization-ledger.jsonl"), "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry
```

## Phase 3: Install the Kill Condition

After each iteration, evaluate whether to halt:

```python
import json

def should_halt(ledger_path, noise_floor, flat_window):
    entries = [json.loads(l) for l in open(ledger_path)]
    if len(entries) < flat_window:
        return False, "not enough data"
    recent = entries[-flat_window:]
    flat = all(abs(e["gain"]) <= noise_floor for e in recent)
    if flat:
        ceiling = entries[-1]["metric_after"]
        total_spent = sum(e["compute_spent"] for e in entries)
        return True, (
            f"Plateau detected: {flat_window} consecutive iterations below noise floor. "
            f"Ceiling estimate: {ceiling}. Total compute spent: {total_spent}."
        )
    return False, "still improving"
```

On halt:
1. Write a plateau report to `./plateau-report.md` containing: metric trajectory, compute spent, ceiling estimate, and the halt reason.
2. Surface the plateau report to the task owner or escalate via the configured sink.
3. Do not resume the loop without an explicit task-reframe decision.

## Phase 4: Post-Halt Triage

Present the plateau report and ask the user:

- "Is this ceiling acceptable, or does the goal need to be reframed?"
- "Did the loop exhaust a local optimum? Should we restart from a different starting point?"
- "Is there a fundamentally different architecture worth exploring before spending more compute?"

If reframe is needed, halt permanently and hand off to a reframe step before relaunching.

## Plateau Report Template

```markdown
# Optimization Loop Plateau Report

**Metric:** <gain_signal>
**Ceiling estimate:** <final metric value>
**Total compute spent:** <sum across all iterations>
**Halt reason:** <flat_window> consecutive iterations below noise floor of <noise_floor>

## Metric Trajectory

| Iteration | Before | After | Gain | Compute Spent |
|-----------|--------|-------|------|---------------|
| ...       | ...    | ...   | ...  | ...           |

## Recommendation

[ ] Accept ceiling — the achieved value is sufficient.
[ ] Restart from a different starting point.
[ ] Reframe the task — the current architecture may be the ceiling.
```

## Verification

The kill-switch is correctly installed when:
- The ledger file is written after every iteration (not just on completion)
- A flat window of N consecutive iterations causes the loop to halt rather than continue
- The plateau report names the ceiling estimate and total compute spent
- The loop cannot auto-resume without a human decision or explicit reframe trigger

## Source

Nate's Newsletter, "Beyond Model Routing" (2026-07-05) — Idea 3, inspired by Mitchell Hashimoto's optimization experiment
https://natesnewsletter.substack.com/p/beyond-model-routing
