---
name: frontier-model-wargame
description: "Use a frontier or expensive model to wargame your hardest projects before the model becomes unavailable or too costly — simulating action, reaction, and counteraction at each step so any cheaper model can execute the battle plans with confidence. Trigger phrases: \"wargame this project\", \"simulate failures before I build\", \"battle plan for any model\", \"wargame before I lose access\", \"frontier model wargame\", \"action reaction counteraction\", \"simulate unknowns\", \"wargame order\"."
---

# Frontier Model Wargame

## Purpose

A standard plan assumes linearity and blue-sky execution. A wargame surfaces every failure mode the model has seen — move by move, scenario by scenario — so the output is not a plan but a set of *battle plans*: pre-simulated responses to real-world friction that any capable model can execute with confidence, including long after the frontier model is off your subscription.

The technique maps to four knowledge categories:

| Category | What it is | Example |
|----------|-----------|---------|
| Known knowns | Facts you are sure of | Your tech stack, existing APIs |
| Known unknowns | Gaps you are aware of | "I'm not sure how auth will behave" |
| Unknown knowns | Tacit knowledge the model has but you have not surfaced | Race conditions in async handlers |
| Unknown unknowns | Failure modes neither of you has considered yet | Third-party rate limits, env drift |

The wargame is designed to surface the bottom two rows before the build starts.

## When to Invoke

- "wargame this project", "simulate failures", "battle plan for any model", "wargame order"
- Before starting a high-stakes build and you want to transfer frontier-model intelligence into a durable artifact
- Before switching to a cheaper or smaller model for execution
- When prior attempts at a project stalled on unexpected errors

## Phase 1: Build the Laundry List

Ask the user to enumerate 5-10 projects or tasks worth wargaming. These become the input queue.

Prompt to give the user:
> "List every project or task you want wargamed. One line each. Do not filter — anything important counts."

Capture as a numbered list. This is the input queue.

## Phase 2: Write the Wargame Order

For each project, construct a wargame order using this prompt structure:

```
WARGAME ORDER — [Project Name]

Objective: [one-sentence goal]
Executor model: [the cheaper model that will run this, e.g. a mid-tier or open-source model]

You are acting as a battle-tested senior engineer simulating this build in a degraded environment.
For each major step:
1. State the action (what the executor will attempt)
2. Simulate the reaction (what reality is likely to throw back — errors, edge cases, rate limits, state drift)
3. Prescribe the counteraction (how to handle it — specific commands, fallbacks, escape hatches)

Depth of simulation: 2-3 levels of consequence per step.
Output format: numbered steps with Action / Reaction / Counteraction sub-bullets.
Include: a "known unknowns" appendix — questions the executor should resolve before starting.
Include: a "success ledger" — observable signals that confirm the step succeeded.
```

## Phase 3: Generate All Wargames (Batch Mode)

If the user has multiple projects, run all wargames in a single session using a goal-and-loop pattern:

1. Write each project's wargame order to a file under `wargames/`.
2. Use the session's loop or goal mechanism to process all files in sequence.
3. Output lands in `wargames/<project-slug>/battle-plan.md`.

Folder structure:
```
wargames/
  <project-slug>/
    order.md          <- the wargame order prompt
    battle-plan.md    <- the frontier model output
    unknowns.md       <- surfaced unknown-unknowns
    success-ledger.md <- observable success signals
```

## Phase 4: Tailor the Battle Plan to Its Executor

Before handing off to the cheaper model, add a one-paragraph "executor briefing" at the top of `battle-plan.md`:

```
EXECUTOR BRIEFING
Model: [executor model]
Strengths to lean on: [e.g. strong at TypeScript, weaker at multi-file refactors]
Watch-outs: [areas where this model tends to drift or hallucinate]
Escalation trigger: [if you hit X, stop and surface the issue rather than guessing]
```

## Verification

A wargame is done when:
- Every major step has Action / Reaction / Counteraction documented
- The "known unknowns" appendix is non-empty (if it is empty, the simulation was too shallow)
- The success ledger has at least one observable signal per step
- A cheaper model reading only `battle-plan.md` could execute without re-asking the frontier model

## Source

Mark Kashef, "Do THIS Before You Lose Access to Fable 5" (2026-07-05)
https://www.youtube.com/watch?v=nuwlyQXrADg
