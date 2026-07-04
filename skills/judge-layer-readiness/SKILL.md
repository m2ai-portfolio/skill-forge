---
name: judge-layer-readiness
description: Audit a production agent architecture against the 4-part Judge Layer control model (action classification → proposals pattern → specialist judges → memory governance). Returns a green/yellow/red scorecard per layer plus a recommended implementation order. Use when asking "is my agent safe for production actions?", "judge layer check", "does my agent have action governance?", "agent safety audit", "4-part control layer", or before deploying any agent that has write access, messaging, or external API calls.
---

# Judge Layer Readiness Audit

Before giving an agent real tools — write access, send messages, modify files, call APIs — verify it has the four control-layer components that make those actions safe at scale. Each component addresses a different failure mode in production agent systems.

## When to Use

- Before deploying an agent that takes external actions (file writes, messages, API calls, DB mutations)
- After adding new tools to an existing agent
- When an agent has produced unexpected compound side effects across multiple channels
- When designing the authority boundary for a new agent

## Inputs

- Path to the agent codebase, config files, or a description of what the agent does and what tools it has
- Optional: existing policy files, hook configs, or judge implementations

## Phase 1: Discover the Agent's Tool Surface

1. Identify every action the agent can take. Look for:
   - Tool calls / function calls (Edit, Write, Bash, HTTP POST, send_message, create_event, etc.)
   - API integrations with external services
   - Database writes or deletes
   - Messaging or notification sends
   - File system mutations
2. Group actions by type: **read-only**, **local-write**, **external-write**, **send**, **delete**
3. Count the total number of distinct side-effecting actions (anything that mutates state or sends to an external system)

If the agent is described in natural language rather than code, ask the user to list the top actions the agent takes before proceeding.

## Phase 2: Evaluate the 4-Part Control Layer

Score each layer as **PRESENT**, **PARTIAL**, or **ABSENT**. Use the indicators below.

---

### Layer 1: Action Classification

**The agent assigns every proposed action to a risk bucket before executing it.**

Indicators of PRESENT:
- A function, module, or prompt segment that categorizes actions (e.g., read-only, reversible-write, irreversible-write, external-send, cross-system)
- The classification result is used to route to a different approval path or judge
- The taxonomy is documented or enforced in code

Indicators of PARTIAL:
- Some actions are classified (e.g., hardcoded `if action == "delete"` checks) but there is no uniform taxonomy
- Classification exists in prompts but is not enforced at the tool-call level

Indicators of ABSENT:
- No classification step exists; all actions flow directly to execution
- Classification is described in comments but not implemented

---

### Layer 2: Proposals Pattern

**The agent generates a structured proposal object before executing any side-effecting action.**

A proposal captures: action type, target, parameters, justification, and reversibility estimate. Execution fires only after the proposal passes evaluation.

Indicators of PRESENT:
- A proposal schema exists (TypeScript type, Pydantic model, YAML schema, or equivalent)
- The agent's output for side-effecting actions is a proposal, not a direct tool invocation
- Proposals flow to an evaluation step before execution

Indicators of PARTIAL:
- Some actions produce proposal-like output (e.g., a plan step before executing) but the schema is informal and inconsistently applied
- Proposals exist for high-stakes actions but not all side-effecting actions

Indicators of ABSENT:
- No proposal layer; agent executes actions directly from its output

---

### Layer 3: Specialist Judges

**Domain-specific evaluation logic runs for each action class, not a single general-purpose gatekeeper.**

Indicators of PRESENT:
- Separate judge functions, agents, or evaluation prompts exist per action domain (e.g., comms judge, file-write judge, calendar judge, data-delete judge)
- Specialist judges are registered and dispatched based on the action classification from Layer 1
- Each specialist outputs a structured verdict (approve / modify / block) with rationale

Indicators of PARTIAL:
- A single general judge evaluates all actions (acceptable early-stage, but a scaling bottleneck and domain accuracy risk)
- Specialist prompts exist but are embedded in a monolithic evaluation function rather than dispatched per domain

Indicators of ABSENT:
- No evaluation step between classification and execution
- Approval is only a human approval modal with no automated evaluation

---

### Layer 4: Memory Governance

**The agent tracks whether accumulated context across turns is drifting from the original intent.**

"Justified-seeming compound drift" is the failure mode: each individual action seems locally correct, but the sequence violates the original goal. Memory governance detects this before it produces an unintended outcome.

Indicators of PRESENT:
- The agent records a baseline intent at task start (explicit goal or constraint set)
- Each turn's proposed actions are compared against the baseline intent
- A drift score or alert fires when cumulative context has steered the agent materially away from the original goal
- Pruning or reset logic exists for when drift exceeds a threshold

Indicators of PARTIAL:
- Token budget tracking exists (turns, context window usage) but intent drift is not measured
- The agent has a system prompt reminding it of the original goal, but no automated drift detection

Indicators of ABSENT:
- No intent baseline is recorded
- No comparison between current proposed actions and original goal
- Context is only managed by context-window limits, not by intent alignment

---

## Phase 3: Score and Classify

Produce a scorecard:

```
Judge Layer Readiness Audit
===========================
Agent: [name or description]
Date: [today]
Side-effecting actions: [count]

Layer 1: Action Classification    [PRESENT / PARTIAL / ABSENT]
Layer 2: Proposals Pattern        [PRESENT / PARTIAL / ABSENT]
Layer 3: Specialist Judges        [PRESENT / PARTIAL / ABSENT]
Layer 4: Memory Governance        [PRESENT / PARTIAL / ABSENT]

Score: X/4   (PRESENT=1, PARTIAL=0.5, ABSENT=0)
```

Classify overall readiness:

| Score | Classification |
|-------|---------------|
| 4.0 | **GOVERNED** — all four layers present; agent is safe for production external actions |
| 3.0–3.5 | **MOSTLY-GOVERNED** — strong foundation; close one remaining gap before production |
| 1.5–2.5 | **PARTIAL-CONTROL** — functional for low-risk actions; not safe for irreversible or cross-system writes |
| 0–1.0 | **UNCONTROLLED** — agent should not take external actions without explicit human approval on each action |

## Phase 4: Remediation Plan

For each layer that is PARTIAL or ABSENT, produce:

```
### [Layer Name] (PARTIAL / ABSENT)
Gap: [what's missing in one sentence]
Fix: [concrete implementation step]
Complexity: Weekend project / Multi-sprint
Priority: P1 (block deployment) / P2 (address within two weeks) / P3 (nice to have)
Dependencies: [other layers that should come first, if any]
```

Recommended implementation order if starting from scratch: Layer 1 → Layer 2 → Layer 3 → Layer 4 (each layer feeds the next; classification must precede routing to specialists; proposals must precede memory governance comparison).

## Phase 5: Output

Lead with the scorecard. Follow with the remediation plan sorted by priority. End with a one-line deployment recommendation:

- **GOVERNED**: safe to deploy; monitor compound action sequences in production.
- **MOSTLY-GOVERNED**: address the one remaining gap first; document any exceptions.
- **PARTIAL-CONTROL**: limit to reversible, local-only actions until Layers 1–2 are complete.
- **UNCONTROLLED**: do not deploy with external actions; add human approval modal as interim gate.

## Verification Checklist

- [ ] Every side-effecting action is accounted for in the Layer 1 assessment
- [ ] Layer 2 (proposals) is not scored PRESENT if it only exists in a system prompt hint — must be enforced in code
- [ ] Layer 3 is not scored PRESENT if only a human approval modal exists — specialist judges are automated
- [ ] Layer 4 is not scored PRESENT if only token budget tracking exists — intent drift is a semantic check, not a token count
- [ ] Remediation items have concrete, actionable steps (no vague "add a judge")
- [ ] Deployment recommendation is stated explicitly

## Source Attribution

Framework extracted from Nate's Newsletter (natesnewsletter@substack.com), 2026-05-11:
*"You gave your AI agent real tools. Here's the 4-part control layer it's missing + the Judge Layer implementation guide"*
https://natesnewsletter.substack.com/p/agent-judge-layer-production-control

The 4-part control layer (action classification → proposals pattern → specialist judges → memory governance) is the structural spine of the article. The Lindy multi-channel incident is the canonical failure case: an agent with messaging, calendar, and file-write capabilities took individually-justified actions whose accumulated side effects violated the original intent.
