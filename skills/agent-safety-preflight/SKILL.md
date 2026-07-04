---
name: agent-safety-preflight
description: Audit an agent's architecture against the 4-part safety control layer (action classification, proposals pattern, specialist judges, memory governance) before deploying it with real tools. Returns a green/yellow/red assessment per layer and a prioritized implementation order. Use when asking "is my agent safe to deploy?", "agent safety audit", "judge layer audit", "pre-deployment agent check", "does my agent have a judge layer", or before giving an agent write, send, or modify access to external systems.
---

# Agent Safety Preflight

Before an agent is given real tools -- write access, send-message capability, file modification, external API calls -- audit whether its architecture includes the 4 safety layers that prevent justified-seeming compound drift: individual actions that each look correct but collectively produce an outcome nobody wanted.

## When to Use

- Before enabling an agent to operate with destructive or external-facing tools
- When reviewing an existing agent for production safety gaps
- When a new agent fails silently and the failure mode is unclear
- When designing a multi-agent system and assessing whether the control boundary is explicit

## Inputs

- Agent name and brief description of what it does
- List of tools the agent has access to (or will have)
- Optional: path to agent codebase, config file, or CLAUDE.md/AGENTS.md

## Phase 1: Tool Inventory

List every tool the agent can call. For each tool, note:

- **Name**: the tool or function call
- **Side-effect class**: read-only / writes local state / writes shared state / sends external message / spans multiple systems
- **Reversibility**: fully reversible / reversible with effort / irreversible

If no tool list is available, ask the user to enumerate the top 5-10 most consequential tools before proceeding.

## Phase 2: 4-Layer Audit

Assess each layer as GREEN (present and enforced), YELLOW (partial or ad-hoc), or RED (absent).

---

### Layer 1: Action Classification

**The question**: Before executing a tool call, does the agent assign it to a risk bucket?

Check for:
- [ ] Explicit risk taxonomy (e.g., read-only / reversible-write / irreversible-write / external-send / cross-system)
- [ ] Classification runs before tool execution, not after
- [ ] Classification output routes to different approval paths, not a single universal gate

Evidence to look for: a classifier function, a routing config, a tool-call interceptor, or a PreToolUse hook that branches on action type.

| Status | Criteria |
|--------|----------|
| GREEN | Classification is explicit, runs pre-execution, and drives different approval paths |
| YELLOW | Some tools are gated but classification is implicit or based on tool name alone |
| RED | No classification -- all tool calls treated identically |

---

### Layer 2: Proposals Pattern

**The question**: Before executing a consequential action, does the agent generate a structured proposal for review?

Check for:
- [ ] Agent produces a proposal object (action, target, parameters, justification, reversibility) before acting
- [ ] Proposals are surfaced for review before execution -- not logged after
- [ ] A proposal step is distinct from the execution step in the agent's turn loop

Evidence: a proposal schema, a "plan then execute" turn structure, a HIL gate at the tool-call level (not just mission level).

| Status | Criteria |
|--------|----------|
| GREEN | Explicit proposal objects generated and reviewed before each consequential action |
| YELLOW | Approval gates exist at mission/task level but not at individual tool-call level |
| RED | Agent acts directly on tool calls with no intermediate proposal step |

---

### Layer 3: Specialist Judges

**The question**: Are there domain-specific evaluators that validate actions in their domain before execution?

Check for:
- [ ] At least one domain-specific judge (e.g., file-write judge, comms judge, data-privacy judge)
- [ ] Judges receive the proposed action and context, not just the tool name
- [ ] Judge output blocks or modifies the action, not merely logs it

Evidence: a judge agent, a domain-specific evaluation prompt, a routing rule that sends "external-send" class actions to a comms evaluator, etc.

| Status | Criteria |
|--------|----------|
| GREEN | One or more specialist judges are active, domain-scoped, and blocking |
| YELLOW | A single general-purpose judge exists but is not domain-scoped |
| RED | No judge layer -- all actions execute without evaluation |

---

### Layer 4: Memory Governance

**The question**: Does the agent track and audit what it is accumulating in context across turns?

Check for:
- [ ] Context snapshots or summaries captured at turn boundaries
- [ ] Drift detection: does the agent's current plan still align with the original intent?
- [ ] A pruning or reset trigger when context drift exceeds a threshold

Evidence: intent-vs-plan diffing logic, context summarization with source tracking, a "return to original goal" mechanism, or a memory audit log.

| Status | Criteria |
|--------|----------|
| GREEN | Drift detection is active, context is pruned on drift, original intent is preserved across turns |
| YELLOW | Token budget is tracked but intent drift is not explicitly monitored |
| RED | No context governance -- accumulated context can silently steer the agent away from original intent |

---

## Phase 3: Scorecard

Present the results:

```
Agent Safety Preflight: [agent-name]
Date: [today]

Layer                   Status   Gap Summary
----                    ------   -----------
Action Classification   [R/Y/G]  [one line]
Proposals Pattern       [R/Y/G]  [one line]
Specialist Judges       [R/Y/G]  [one line]
Memory Governance       [R/Y/G]  [one line]

Overall: [SAFE TO DEPLOY / DEPLOY WITH CAUTION / DO NOT DEPLOY]
```

Thresholds:
- **SAFE TO DEPLOY**: all 4 layers GREEN
- **DEPLOY WITH CAUTION**: no RED layers; at least 2 GREEN; document the YELLOW gaps before deploying
- **DO NOT DEPLOY**: any RED layer -- especially Layer 1 (classification) or Layer 2 (proposals)

---

## Phase 4: Implementation Order

For each RED or YELLOW layer, produce a fix item:

```
### [Layer Name] -- [Status]
Gap: [what is missing]
Fix: [concrete implementation step]
Effort: [hours / days]
Blocks: [which other layers depend on this one]
```

Recommended implementation order: Layer 1 (classification) → Layer 2 (proposals) → Layer 3 (judges) → Layer 4 (memory governance). Do not skip to Layer 3 without Layer 1 -- specialist judges need a classification input to route against.

---

## Verification Checklist

- [ ] Every tool in Phase 1 maps to at least one layer's assessment
- [ ] No layer scored GREEN without checking at least 2 concrete indicators
- [ ] RED layers are not papered over with "we plan to add this"
- [ ] Implementation order respects layer dependencies

## Source Attribution

Framework derived from Nate's Newsletter (natesnewsletter@substack.com), 2026-05-11:
"You gave your AI agent real tools. Here's the 4-part control layer it's missing + the Judge Layer implementation guide"
https://natesnewsletter.substack.com/p/agent-judge-layer-production-control

Core insight: "The next serious agent failure won't look like a jailbreak -- it will look like routine operations that individually seem justified but produce an outcome nobody wanted." The 4-part control layer (action classification, proposals, specialist judges, memory governance) is the structural fix.
