---
name: reframe-before-optimize
description: "Run a mandatory frontier-model steering pass that challenges the task framing before dispatching any optimization loop, iterative agent run, or batch execution. Prevents the class of error where an engine-layer loop optimizes hard against a bad objective — the architectural ceiling problem. Trigger phrases: \"reframe before I optimize\", \"challenge my task framing\", \"steering pass before the loop\", \"is this the right problem\", \"pre-loop reframe gate\", \"architecture ceiling check\", \"check my framing before I run\"."
---

# Reframe Before Optimize

## The Problem

The most expensive optimization loops fail not because the executor model is weak, but because the task framing contained a false ceiling. The loop optimizes brilliantly against the wrong objective. A loop can burn significant compute improving latency by 2ms when the correct fix is a fundamentally different architecture that the framing never allowed the loop to discover.

The fix is a mandatory "steering pass" before any loop launches: a high-reasoning phase that challenges the task framing itself — before engine-layer execution begins.

## When to Invoke

- Before dispatching any optimization loop, benchmark run, iterative agent chain, or multi-step batch build
- "reframe before I optimize", "challenge my task framing", "steering pass", "pre-loop reframe gate"
- When a prior loop ran to budget with disappointing results
- When the success metric feels inherited from the problem statement rather than chosen deliberately

## Phase 1: Write Down the Current Frame

Ask the user to state (or confirm) the current task frame in one structured block:

```
CURRENT FRAME
Objective:          <what you are trying to achieve>
Success metric:     <how you measure success>
Approach:           <the method, architecture, or loop you are about to dispatch>
Budget:             <time and/or compute you are willing to spend>
Ceiling assumption: <what do you believe the upper limit of this approach is?>
```

This becomes the input to the steering pass. Do not proceed to Phase 2 until this block is written down — not inferred from a vague prompt.

## Phase 2: Run the Steering Pass

Submit the current frame to a high-reasoning model with this prompt:

```
You are acting as a strategic advisor reviewing this task frame before execution begins.
Your job is NOT to execute the task. Your job is to challenge the frame.

FRAME:
[paste the current frame block]

Challenge each element:
1. Objective: Is this the right goal? Is there a higher-leverage objective the executor is not seeing?
2. Success metric: Does this metric actually measure what matters? Can it be gamed or saturated? Is there a better proxy?
3. Approach: Is the proposed approach the right architecture for this objective, or does a fundamentally different approach exist that the current framing rules out?
4. Ceiling assumption: What is the actual ceiling of the proposed approach? Is that ceiling acceptable?
5. Unknown unknowns: What is the executor most likely NOT considering that will cause this to fail or stall?

Output a brief reframe report (under 400 words) with one of these recommendations:
- PROCEED: the frame holds. State what the executor should watch for during the run.
- REFRAME (minor): adjust the success metric or scope, then re-run the steering pass once before launching.
- REFRAME (major): stop. Do not launch. Redesign the approach.
```

The steering model should be a different (higher-reasoning) model than the one that will execute the loop — the whole point is a second opinion from a different reasoning tier.

## Phase 3: Triage the Steering Output

Three outcomes:

| Recommendation | Action |
|----------------|--------|
| **PROCEED** | Launch the loop. Keep the steering output as a preamble in the executor context. |
| **REFRAME (minor)** | Adjust the metric or scope. Run Phase 2 once more on the corrected frame before launching. |
| **REFRAME (major)** | Stop. Redesign the approach. Do not launch until the new frame passes a PROCEED from Phase 2. |

Never auto-approve a REFRAME recommendation. Require explicit confirmation before proceeding with the original frame after a reframe flag.

## Phase 4: Attach Steering Output to the Executor

If PROCEED, prepend the steering output as a context header in the executor's starting prompt:

```
STEERING PASS RESULT: PROCEED
[paste the steering model PROCEED note here]

Watch for during execution:
- [copy the watch-for items from the steering output]

Do not override these watch-outs without escalating to a human decision.
```

This ensures the executor model is aware of the ceiling and identified risks from the start, without re-running the full steering pass at execution cost.

## Verification

The reframe gate is correctly applied when:
- The current frame is written down before the steering pass (not inferred post-hoc)
- The steering pass runs against a higher-reasoning model than the executor
- A PROCEED recommendation is recorded in writing before the loop launches
- No loop is dispatched after a REFRAME (major) without a new steering pass on the corrected frame
- The steering output is attached to the executor context, not discarded

## Source

Nate's Newsletter, "Beyond Model Routing" (2026-07-05) — Idea 4, steering-layer recon pattern
https://natesnewsletter.substack.com/p/beyond-model-routing
