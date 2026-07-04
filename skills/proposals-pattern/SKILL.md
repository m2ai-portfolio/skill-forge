---
name: proposals-pattern
description: Refactor an agent's direct-action tool calls into a proposals-first pattern -- the agent generates a structured proposal object before executing, decoupling intent from side effect. Use when asking "proposals pattern", "propose before acting", "decouple intent from execution", "agent acts before I can review", "add a review step before my agent fires", or when building a judge layer that needs a structured input to evaluate.
---

# Proposals Pattern

An agent that executes tool calls directly is one step away from an action that cannot be undone. The proposals pattern inserts a structured intermediate step: before executing, the agent produces a proposal object that describes what it intends to do and why. A judge, a human, or a policy gate then evaluates the proposal before execution proceeds.

This is the difference between an agent that acts and an agent that proposes -- and only acts on approval.

## When to Use

- An agent with write, send, or delete access is executing before you can review
- You want to add a judge layer but need a structured input for the judge to evaluate
- You are building a multi-step workflow where some steps are high-stakes and need sign-off
- You want an audit trail of what the agent intended to do, not just what it did

## Inputs

- Agent or skill name (or free-text description of what the agent does)
- List of consequential actions the agent takes (tool calls, API calls, file writes, messages)
- Optional: current turn loop structure (system prompt, tool definitions, execution code)

## Phase 1: Identify Proposal Candidates

Not every tool call needs a proposal. Apply this filter:

A tool call is a proposal candidate if it meets ANY of the following:
- It is irreversible (cannot be undone in under 5 minutes)
- It affects shared state or external systems (not just the agent's local workspace)
- It sends a message or notification to another person or system
- Its output is visible to anyone other than the user who invoked the agent

Tool calls that do NOT meet any criterion (read-only, local, reversible) can execute directly without a proposal step.

Produce a list:
```
Proposal candidates: [tool1, tool3, tool5]
Direct execution (no proposal needed): [tool2, tool4]
```

## Phase 2: Define the Proposal Schema

For each proposal candidate, the agent will produce a proposal object before calling the tool. Standard schema:

```json
{
  "proposal_id": "string (uuid or short hash)",
  "action_type": "string (one of: write, delete, send, modify, create, cross-system)",
  "tool_name": "string",
  "target": "string (file path, API endpoint, user ID, resource name, etc.)",
  "parameters": "object (the exact tool input the agent intends to send)",
  "justification": "string (one sentence: why this action, tied to the original goal)",
  "reversibility": "string (one of: reversible, reversible-with-effort, irreversible)",
  "estimated_side_effects": "string (free text: what else might change as a result)",
  "proposed_at": "ISO 8601 timestamp"
}
```

Constraints:
- `justification` must reference the original task or goal, not just describe the action
- `reversibility` must be set conservatively -- when in doubt, use `irreversible`
- `parameters` must be the exact input the agent intends to use, not a summary

## Phase 3: Insert the Proposal Step

Modify the agent's turn loop to add a proposal step before each proposal candidate tool call:

### Option A: Prompt-level (no code change)

Add to the agent's system prompt:

```
Before calling any tool in the following list: [tool1, tool3, tool5]
-- first output a JSON proposal object in this exact format:
{
  "proposal_id": "...",
  "action_type": "...",
  "tool_name": "...",
  "target": "...",
  "parameters": {...},
  "justification": "...",
  "reversibility": "...",
  "estimated_side_effects": "...",
  "proposed_at": "..."
}
Then STOP and wait for approval before executing the tool call.
Do not call the tool until the approval message "APPROVED [proposal_id]" is received.
```

### Option B: Code-level (PreToolUse hook or middleware)

Intercept proposal-candidate tool calls and extract the proposal object before forwarding to execution:

```typescript
// Pseudocode: PreToolUse intercept
function interceptToolCall(toolName: string, input: unknown): ProposalOrPassthrough {
  if (!PROPOSAL_CANDIDATES.includes(toolName)) {
    return { type: 'passthrough', input };
  }

  const proposal: Proposal = {
    proposal_id: crypto.randomUUID(),
    action_type: classifyActionType(toolName),
    tool_name: toolName,
    target: extractTarget(toolName, input),
    parameters: input,
    justification: '', // agent fills this in its turn output
    reversibility: classifyReversibility(toolName),
    estimated_side_effects: '',
    proposed_at: new Date().toISOString(),
  };

  return { type: 'proposal', proposal };
}
```

Option B is preferred when the agent runs autonomously (unattended) -- prompt-level gates can be reasoned around by a sufficiently capable model.

## Phase 4: Define the Approval Gate

Specify who or what evaluates proposals:

| Gate type | When to use | Implementation |
|-----------|-------------|----------------|
| Human gate | High-stakes, infrequent actions | Surface proposal in UI, wait for "APPROVED [id]" |
| Policy gate | Repeatable actions with known rules | Run proposal against a rule set (see `judgment-gate`) |
| Judge agent | Complex domain-specific evaluation | Route proposal to a specialist evaluator |
| Auto-approve | Low-risk proposal candidates that still need a trail | Log the proposal, immediately approve, execute |

Document which gate each proposal candidate uses:

```
tool1 -> human gate (irreversible, external-send)
tool3 -> policy gate (reversible-write, applies known rules)
tool5 -> judge agent (cross-system, domain: comms)
```

## Phase 5: Audit Trail

Log every proposal, whether approved or rejected:

```json
{
  "proposal_id": "abc-123",
  "status": "approved | rejected | modified",
  "reviewed_by": "human | policy | judge-agent",
  "reviewed_at": "ISO 8601 timestamp",
  "modification": null,
  "execution_result": "success | error | skipped",
  "executed_at": "ISO 8601 timestamp"
}
```

Store in a local append-only log file, a database table, or a structured output stream. The audit trail is the record that the agent acted on approval, not autonomously.

## Phase 6: Deliver

Present the proposal schema, the modified system prompt (Option A) or intercept pseudocode (Option B), the gate assignments, and the audit log format.

Stop before writing files. The user confirms:
- **Apply** -- write the system prompt update and any hook config
- **Adjust** -- revise gate assignments or schema fields
- **Preview only** -- document the pattern without modifying the agent

## Verification Checklist

- [ ] Every irreversible or external-facing tool call is in the proposal candidate list
- [ ] `justification` requires a reference to the original goal, not just the action
- [ ] `reversibility` defaults conservative (`irreversible`) when uncertain
- [ ] At least one gate type is assigned to each proposal candidate
- [ ] Audit trail captures both approved and rejected proposals
- [ ] Option B (code-level) is used when the agent runs unattended

## Source Attribution

Framework derived from Nate's Newsletter (natesnewsletter@substack.com), 2026-05-11:
"You gave your AI agent real tools. Here's the 4-part control layer it's missing + the Judge Layer implementation guide"
https://natesnewsletter.substack.com/p/agent-judge-layer-production-control

Core concept: Part 2 of the 4-part control layer -- the proposals pattern decouples intent from side-effect. An agent that must produce a proposal before acting is an agent that cannot take an action it hasn't explicitly committed to in structured form.
