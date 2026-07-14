---
name: effort-ladder
description: Calibrate the effort level for any AI model task -- start at low, climb only when evidence demands it, and never reach for max unless deep multi-path reasoning is proven necessary for THIS specific task. Use when the user asks "what effort level should I use", "when does max effort help", "low vs high thinking budget", "effort dial", "is high effort worth it", or is about to run a task and wondering where to set the effort slider.
---

# Effort Ladder

Prevents the second most expensive Claude Code mistake: treating effort level as a proxy for intelligence and defaulting to max/ultra on every task. More effort does not mean a smarter model. It means more thinking budget -- which can backfire on simple tasks by causing the model to overthink an obvious answer.

## Trigger

Use when the user asks "what effort level should I use", "when does max effort help", "low vs high thinking budget", "effort dial", "is high effort worth it", or is about to run a task and wondering where to set the effort slider. Also use when a high-effort run produced a worse or over-engineered result than expected.

## Core Mental Model

**Pick the right model first, then calibrate effort within that model.**

Effort does not select a smarter model. It controls the reasoning token budget -- how many internal thinking steps the model takes before producing output. A frontier model on low effort is still a frontier model; it just won't deliberate as long.

The slot machine habit: picking effort levels by their names ("extra high sounds better than medium") builds a bad default toward always living on the right side of the dial, wasting tokens, and sometimes producing worse results.

The exam analogy: a student who has studied correctly knows the answer is B. If they overthink (max effort on a simple question), they may talk themselves into selecting D. The same failure mode applies to models on unnecessarily high effort.

## Phase 1: Classify the Task

Before setting effort, classify the task:

| Task type | Characteristics | Recommended start |
|-----------|----------------|-------------------|
| **Generation / transform** | Change a UI element color, rewrite a doc, rename a variable, Excel/PowerPoint edits, simple API call | Low |
| **Single-objective build** | Build a specific component, write a function to spec, generate content with clear constraints | Low or Medium |
| **Ambiguous or multi-path** | Tasks with unclear success criteria, multiple possible approaches, need to weigh tradeoffs | Medium or High |
| **Complex reasoning chain** | Architecture decisions, debugging a subtle race condition, comparing 5+ options, security audit | High |
| **Deep exploration** | Novel research, exhaustive edge-case coverage, tasks where missing a path has high cost | Max (rarely) |

When in doubt, start at Low. You can always re-run at Medium if the output is underwhelming. One extra turn at medium is cheaper than paying for max on everything.

## Phase 2: What Each Level Actually Does

| Level | Token budget behavior | When it helps | When it backfires |
|-------|----------------------|---------------|-------------------|
| **Low** | Small thinking budget; uses 1-2 tools; takes the first reasonable result | Routine tasks, generation, transforms, tasks with a clear and obvious path | Ambiguous tasks where checking alternatives would have found a better path |
| **Medium** | Larger budget; checks its own work; considers alternative paths before committing | Tasks where correctness matters and re-checking adds value | Over-budget for pure generation tasks |
| **High** | Creates a plan, checks the plan, executes, then verifies the output matches intent | Multi-step tasks where a wrong early decision cascades into expensive rework | Over-engineers simple tasks; you get a plan, sub-plan, and verification loop for a three-line change |
| **Max / Ultra / Extra High** | Explores many possible paths; deliberates over alternatives at every step | Genuinely novel problems with no obvious path where missing a branch has high real-world cost | Almost everything else; path A vs. path B vs. path C vs. path D for a UI button change; burns token budget in one afternoon |

## Phase 3: The Effort Ladder Protocol

Apply this sequence for any task where the right effort level is unclear:

```
1. Run at Low.
   - If the output is correct and complete: done. Stop here.
   - If the output is missing nuance or took the wrong path: continue.

2. Run at Medium.
   - If the output improves meaningfully and is now correct: done.
   - If Medium and Low are indistinguishable for this task type: set Low as your default for this task class.
   - If Medium is still missing something: continue.

3. Run at High only with a specific reason.
   - Name the reason: "this task has multiple valid paths and I need the model to evaluate them" or
     "this is a plan-then-execute task where an unchecked plan will cause rework."
   - If High adds clear value: use it. Note the task type so you can default to High next time.

4. Max/Ultra: requires a strong affirmative case.
   - "The task is genuinely novel with no established path."
   - "Missing a reasoning branch here has high real-world cost (financial, security, data loss)."
   - "Low/Medium/High all underwhelmed on this exact task type."
   If you cannot state the case, do not use Max. The cost in tokens is real; the improvement is rarely proportional.
```

## Phase 4: Calibrating a New Model

When a new model family drops and you do not yet know its effort rhythm:

1. Take one representative task from your most common use case.
2. Run it at Low, Medium, and High -- same prompt, same task, all three.
3. Compare outputs side by side.
4. Note where the quality delta between levels becomes negligible. That is your calibration point.
   - If Low and Medium are nearly identical: Low is your new default for this task class.
   - If High adds no visible value over Medium: High is not worth it for this task class.
5. Most users find: the biggest quality delta is between Low and Medium, and between Medium and High -- **not** between High and Max.

This one-hour calibration exercise eliminates slot-machine effort selection permanently for that model family.

## Phase 5: Cross-Provider Notes

Effort levels are NOT equivalent across providers. "High" on Claude is not the same reasoning budget as "High" on GPT, Grok, or Gemini. Each provider sets effort relative to that model family's own capability spectrum.

- Do not compare effort level names across providers when estimating cost or quality.
- Calibrate each provider separately using the Phase 4 protocol.
- The principle (start low, climb with evidence) holds universally even when the level names differ.

## The Harness Reminder

The model's effort level controls its reasoning budget. The harness (Claude Code, Codex, or any agentic wrapper) provides the limbs -- file access, code execution, browser control, tool use. A well-specced prompt with the right tools enabled at Low effort will outperform a vague prompt at Max effort because the harness is doing 80-90% of the real work. Effort is a multiplier on reasoning, not a substitute for a clear task spec.

## Verification

This skill is working when:

- Low-effort runs handle the majority of generation and transform tasks without rework.
- Max/Ultra is invoked fewer than once per five tasks.
- When a high-effort run produces an over-engineered result, the user recognizes the pattern and re-runs at Medium.
- New model calibration takes one hour, not a week of guessing.

## Source Attribution

Extracted from: "THIS Is the AI Setting Everyone Gets Wrong" by Mark Kashef
Published: 2026-07-13
URL: https://www.youtube.com/watch?v=4__5q76f04s

Core technique: effort ladder (start low, climb with evidence), task-type classification table, effort-level behavior breakdown, new-model calibration protocol, harness-vs-reasoning-budget distinction. Original framing: "effort is not a proxy for intelligence -- it's a thinking budget, and more budget can backfire."
