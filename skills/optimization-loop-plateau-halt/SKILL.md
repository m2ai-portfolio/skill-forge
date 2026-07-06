---
name: optimization-loop-plateau-halt
description: Track improvement-per-dollar across an active optimization loop and halt or escalate when marginal gains flatten below a configurable threshold — prevents runaway spend on a ceiling that belongs to the task framing, not the model.
---

# Optimization Loop Plateau Halt

Audits an in-progress iterative optimization loop (benchmark tuning, prompt refinement, code performance) for plateau conditions and returns a HALT / CONTINUE / ESCALATE verdict with a cost receipt and diagnosis.

## Trigger

Use when the user:
- Says "plateau halt", "stop the loop if it's not improving", "check if this loop is worth continuing", or "/optimization-loop-plateau-halt"
- Reports consecutive iterations without meaningful improvement while cost accumulates
- Asks "when should I stop tuning this?"
- Is about to launch a benchmark or optimization loop and wants an auto-stop plan

## Phase 1: Gather Loop Metrics

Ask for (or read from context):
- **Metric being optimized** (latency ms, pass-rate %, benchmark score, etc.)
- **Per-iteration results** (a table or list: iteration, metric value, cost spent this iteration)
- **Total cost so far** (in dollars or tokens)
- **Target metric** (if any) or "keep improving until stopped"
- **Kill budget** (max spend or max iterations — required; if missing, ask before continuing)

If the user cannot supply per-iteration values, ask for the last 3 data points minimum. Fewer than 3 data points is insufficient for plateau detection.

## Phase 2: Plateau Detection

Compute the following over the last N iterations (default N=3, configurable):

1. **Marginal gain** = (current metric - prior metric) / prior metric × 100%
2. **Cost efficiency** = marginal gain % / cost of this iteration
3. **Trend** = is marginal gain increasing, flat, or decreasing over the window?

Apply thresholds:
- **HALT** if marginal gain < 1% for the last 3 consecutive iterations AND total spend > $5 (or user-supplied budget × 50%)
- **ESCALATE** if HALT condition holds AND the best metric achieved is still below the user's stated target — this means the ceiling belongs to the task framing, not progress
- **CONTINUE** if marginal gain > 1% or the trend is still positive

If no budget was stated and HALT fires, set the default kill budget to the current total spend (stop now) and surface it as an assumption.

## Phase 3: Verdict and Diagnosis

Return a structured verdict block:

```
VERDICT: [HALT | CONTINUE | ESCALATE]

Loop summary:
  Iterations run: N
  Total spend: $X.XX
  Best metric achieved: X.X (target: Y.Y or "none stated")
  Last 3 marginal gains: +X%, +X%, +X%
  Cost efficiency trend: [improving | flat | declining]

Diagnosis:
  [One sentence: why this verdict was reached]

If HALT:
  Recommended action: stop the loop; the last N iterations returned diminishing returns.
  Save the best checkpoint from iteration [K].

If ESCALATE:
  Recommended action: stop the loop AND reframe the task before retrying.
  Suspected ceiling: [describe the likely architectural constraint based on what the user told you]
  Next step: run /reframe-before-optimize with the original task description.

If CONTINUE:
  Next check-in: after [N] more iterations or $[X] more spend.
  Watch for: [specific metric threshold that would trigger a re-check]
```

## Phase 4: Hook Config (Optional)

If the user wants an automated version, generate a PostToolUse hook stub they can install:

```python
# ~/.claude/hooks/loop-plateau-check.py
# Runs after each tool call in a session; reads .plateau-state.json in cwd.
# Requires: a .plateau-state.json written by the loop driver with keys:
#   iteration, metric_value, cost_this_iteration, total_cost, kill_budget
# Action: writes HALT signal to .plateau-halt if threshold exceeded.
```

Note: this hook requires the loop driver to emit `.plateau-state.json` each iteration. Without that file, the hook cannot fire. The skill (Phase 1-3) is the reliable path for one-off checks; the hook is for automated loops that can write their own state.

## Verification

The verdict is sound when:
- [ ] Marginal gain calculation uses the same metric units across all iterations (no unit mismatch)
- [ ] Kill budget was confirmed with the user (not assumed)
- [ ] ESCALATE is only fired when the ceiling analysis is grounded in the loop's actual metric type
- [ ] No cost figures are fabricated — only values the user supplied are used

## Source

Mitchell Hashimoto experiment 1 (renderer optimization; ~$350 spent reaching a 2 ms plateau while a 75x-better architecture existed), surfaced in Nate's Newsletter "Beyond Model Routing" (2026-07-05).
