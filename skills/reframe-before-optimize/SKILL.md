---
name: reframe-before-optimize
description: Run a mandatory frontier-model Phase 0 that challenges the task frame and success metric before dispatching any engine-layer optimization loop — catches architectural ceilings before they become expensive receipts.
---

# Reframe Before Optimize

Interrogates the task framing and success metric of a pending optimization loop using a frontier-model reasoning pass, before any engine loop is launched. Returns either a green-lit frame (proceed) or a reframed task description that addresses the ceiling risk.

## Trigger

Use when the user:
- Says "reframe before optimizing", "challenge this task", "is this the right metric?", or "/reframe-before-optimize"
- Is about to launch a benchmark run, iterative tuning loop, or automated optimization workflow
- Has received an ESCALATE verdict from /optimization-loop-plateau-halt
- Wants to sanity-check whether the success metric captures what actually matters

## Phase 1: Task Frame Intake

Ask for (or read from context):
- **What is being optimized?** (latency, accuracy, throughput, cost, pass-rate, etc.)
- **The current approach** (architecture, algorithm, model, prompt structure)
- **Success metric** (the number the loop is trying to move, including units and direction)
- **Target value** (if stated; "as low as possible" counts)
- **Constraints** (time budget, cost budget, must-not-change components)

If the user is mid-loop and received an ESCALATE verdict, also ask for the best metric value achieved and the iteration count where improvement stalled.

## Phase 2: Frame Interrogation

Apply each of the following challenges in order. Stop and surface the result to the user at the first challenge that reveals a material issue; do not silently pass through all five:

1. **Metric validity** — Does the success metric actually proxy for the real goal? Example failure: optimizing token count when the real goal is response quality. Ask: "If this metric reaches the target, does the original problem go away?"

2. **Architectural ceiling scan** — Is the current approach structurally incapable of reaching the target? Look for: wrong algorithm class, wrong data representation, missing components, a known theoretical bound the approach cannot exceed. Ask: "Is there a reason this approach CANNOT reach the target, regardless of how well it's tuned?"

3. **Task scope check** — Is the task framed at the right level of abstraction? Example failure: tuning a renderer's inner loop when the real win is in the render pipeline's architecture. Ask: "Is there a higher-leverage version of this task that would make this optimization unnecessary?"

4. **Metric ownership** — Who defined the success metric, and is that person still the right authority? Example failure: chasing a benchmark score that was set for an older system. Ask: "Is this metric still the right one for the current system?"

5. **Diminishing returns scan** — If the user is mid-loop, is the current ceiling consistent with the approach's known performance envelope, or is it anomalously low? Ask: "Does this plateau make sense given the approach, or does it suggest something is broken?"

## Phase 3: Verdict and Reframe

Return one of two outcomes:

**GREEN-LIGHT** (no material issues found):
```
VERDICT: PROCEED
Frame assessment: [one sentence — what was checked and why it passed]
Proceed with your optimization loop. Suggested kill budget: [X] based on the approach's typical convergence behavior.
```

**REFRAME REQUIRED** (one or more challenges flagged):
```
VERDICT: REFRAME BEFORE RUNNING

Issue found at: [which challenge, e.g. "Architectural ceiling scan"]
Finding: [one sentence describing the ceiling or metric problem]

Reframed task:
  Original: [user's original task description]
  Reframed: [new task description that addresses the finding]
  New success metric: [if the metric needs to change]
  Why this matters: [one sentence on the expected leverage of the reframe vs. continuing the original loop]

Next step: verify the reframed task with the requester before dispatching any loop.
```

## Verification

The verdict is sound when:
- [ ] At least the first two challenges (metric validity and architectural ceiling) were applied
- [ ] Any REFRAME verdict names the specific challenge that fired, not a generic "consider reframing"
- [ ] No fabricated cost or performance figures appear in the reframe — only values the user supplied
- [ ] The reframed task is more specific than the original, not more abstract

## Source

Mitchell Hashimoto experiment 1 (renderer optimization ceiling analysis) and Nate's Newsletter "Beyond Model Routing" two-layer architecture concept (steering model vs. engine model), surfaced 2026-07-05. The pattern is the distributable form of the recon-gated planning discipline: verify the frame before building on it.
