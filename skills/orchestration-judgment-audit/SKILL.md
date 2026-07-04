---
name: orchestration-judgment-audit
description: Audit an agent codebase to detect orchestration-judgment conflation — where "what to do next" logic (orchestration) has leaked into "whether to do it" logic (judgment), or vice versa. Produces a gap report with specific code locations and a separation plan. Use when asking "does my agent conflate planning with judging?", "orchestration judgment audit", "is my judge logic clean?", "agent architecture separation", "planning vs. judgment split", or before adding specialist judges to an existing agent system.
---

# Orchestration vs. Judgment Audit

Orchestration and judgment are two distinct concerns in an agent system:

- **Orchestration** answers: *What should the agent do next?* (task decomposition, tool selection, step ordering, dependency resolution)
- **Judgment** answers: *Should the agent do that at all?* (risk evaluation, approval routing, reversibility check, intent alignment)

When these concerns are conflated — orchestration logic in the judge, or judgment logic inside the planner — the agent is harder to test, harder to tune, and produces unpredictable behavior under novel inputs. Conflation is the root cause of agents that sometimes ask when they should act (over-cautious planner) or act when they should ask (under-cautious judge embedded in the planner).

## When to Use

- Before adding specialist judges to an existing agent: conflated code must be separated first
- When an agent inconsistently asks for confirmation (sometimes asks, sometimes doesn't, for identical action types)
- When tuning the judge changes the agent's task decomposition behavior unexpectedly
- When reviewing a multi-agent architecture to verify each agent has a single concern

## Inputs

- Path to agent codebase, or natural-language description of the agent's architecture
- Optional: list of agent components (planner, executor, judge, router, etc.)

## Phase 1: Map the Agent's Decision Flow

Identify every point in the agent's code or prompt chain where a decision is made. A decision is any place where the agent evaluates options and selects one.

For each decision point, record:
- **Location**: file, function name, or prompt section
- **Trigger**: what causes this decision to be made
- **Question being answered**: rephrase the decision as a question the agent is implicitly answering

Example mapping:

```
Decision Point         Location                   Question
───────────────────────────────────────────────────────────────────────
Plan decomposition     planner.ts:decompose()     What subtasks are needed?
Tool selection         executor.ts:selectTool()   Which tool handles this step?
Approval check         worker.ts:beforeRun()      Is this action safe to run?
Retry logic            worker.ts:onError()        Should this step be retried?
Intent drift check     monitor.ts:checkDrift()    Is the plan still aligned with goal?
```

## Phase 2: Classify Each Decision Point

For each decision point, classify it as **ORCHESTRATION**, **JUDGMENT**, or **CONFLATED**:

| Classification | Pattern | Examples |
|----------------|---------|---------|
| ORCHESTRATION | Decides *what* or *when* or *how*, with no risk evaluation | task decomposition, tool routing, step ordering, retry scheduling, dependency resolution |
| JUDGMENT | Decides *whether* based on risk, reversibility, or intent alignment | approval gate, blast radius check, intent drift detection, action classification |
| CONFLATED | Mixes both in the same function/prompt | planner that skips unsafe steps rather than flagging them, judge that re-routes to a different task when blocking |

**Conflation markers to look for:**

- A planning function that contains `if action.is_risky() then skip_step()` — judgment logic inside an orchestrator
- A judge that returns `next_action` or modifies the task list — orchestration logic inside a judge
- A single `evaluate()` function that both scores actions and decides what to do next
- Conditional logic in a judge that selects a different tool rather than returning a verdict
- A planner that checks reversibility to decide step order (reversibility is a judgment concern, not a scheduling concern)

## Phase 3: Detect and Score Conflation

For each CONFLATED decision point, document:

```
### Conflation at [Location]
Type: [Orchestration-in-Judge | Judgment-in-Orchestration | Bidirectional]
Evidence: [specific code pattern or prompt excerpt]
Symptom: [what observable behavior this causes]
Risk: [High / Medium / Low] — based on whether this affects external actions
```

**Risk classification:**

- **High**: conflation is in a code path that gates external actions (writes, sends, API calls)
- **Medium**: conflation affects confirmation behavior but only for local, reversible operations
- **Low**: conflation is cosmetic (naming, comments) or affects only logging

Count conflation points by type:
- Orchestration-in-Judge: N
- Judgment-in-Orchestration: N
- Bidirectional: N
- Total conflated decision points: N

**Conflation score:**

| Conflated points | Score |
|------------------|-------|
| 0 | CLEAN |
| 1–2 | MINOR-CONFLATION |
| 3–5 | MODERATE-CONFLATION |
| 6+ | SEVERE-CONFLATION |

## Phase 4: Separation Plan

For each CONFLATED decision point (High and Medium risk first), produce a separation prescription:

```
### Separate: [Location]
Current behavior: [what the conflated function does]
Orchestration responsibility: [what should remain here]
Judgment responsibility: [what should move to a judge]
Refactor: [concrete step — extract function, split module, add verdict type]
Complexity: [hours / day / sprint]
```

Recommended separation pattern:

```
Orchestration layer:
  - input: current state, goal, available tools
  - output: proposed action (type, target, parameters)
  - NEVER: risk scores, approval decisions, reversibility checks

Judgment layer:
  - input: proposed action from orchestration
  - output: verdict (approve / modify / block / queue) + rationale
  - NEVER: next-step selection, tool routing, task decomposition
```

If the codebase uses a single monolithic agent loop, the separation prescription is:
1. Extract all judgment checks into a `judge(proposal)` function
2. Have the main loop call `judge(proposal)` before executing any side-effecting action
3. Make judgment independent of the planner state — judges should not need to know what step comes next

## Phase 5: Output

Lead with the conflation scorecard. Follow with the High-risk separation prescriptions. End with the full plan sorted by risk (High → Medium → Low).

```
Orchestration-Judgment Audit
=============================
Agent: [name or description]
Date: [today]
Decision points mapped: [N]
Conflated: [N] ([score])

High-risk conflation: [N]
Medium-risk conflation: [N]
Low-risk conflation: [N]

Verdict: [CLEAN / MINOR-CONFLATION / MODERATE-CONFLATION / SEVERE-CONFLATION]

[Separation plan for high-risk points first]
```

## Verification Checklist

- [ ] Every decision point is mapped, not just the ones with obvious names like "judge" or "planner"
- [ ] Retry logic is evaluated — retries are orchestration, but retry conditions may embed judgment
- [ ] CONFLATED points are confirmed by evidence (specific code or prompt, not assumption)
- [ ] Separation prescriptions name the exact function or prompt section to split
- [ ] Low-risk cosmetic conflation is noted but not prioritized over high-risk functional conflation

## Related Skills

- `judgment-gate` — if this audit reveals undetected judgment gaps, use judgment-gate to design explicit gate logic for those action types
- `judgment-layer` — generates a full judgment policy and PreToolUse hook from an action inventory

## Source Attribution

Architecture distinction extracted from Nate's Newsletter (natesnewsletter@substack.com), 2026-05-11:
*"You gave your AI agent real tools. Here's the 4-part control layer it's missing + the Judge Layer implementation guide"*
https://natesnewsletter.substack.com/p/agent-judge-layer-production-control

Core insight: "orchestration = what the agent does next; judgment = whether the agent SHOULD do that." Most agent frameworks conflate them. The separation is a prerequisite for adding specialist judges without introducing routing side effects.
