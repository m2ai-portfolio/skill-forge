---
name: action-proposal-schema
description: Generate a typed action-proposal schema and execution wrapper for any agent or skill so the agent produces a structured proposal object before executing a side effect. Decouples intent from execution — proposals flow to evaluation before any action fires. Use when asking "proposals pattern", "decouple intent from action", "agent proposal wrapper", "pre-execution proposal", "action schema for my agent", or wiring a judgment layer into an agent that currently executes actions directly.
---

# Action Proposal Schema

The most common gap between an agent that executes tasks and one that is safe for production: the agent fires actions directly from its output. The proposals pattern inserts a typed intermediary — the **action proposal** — between the agent's intent and any side-effecting execution. The agent's job becomes producing proposals; the judge's job becomes evaluating them; execution only fires on approval.

This skill generates the proposal schema, execution wrapper, and evaluation stub for a specific agent.

## When to Use

- An agent currently calls tools directly and you want to add a judgment layer without rewriting the agent
- Designing a new agent and choosing its output contract up front
- Standardizing proposal shapes across multiple agents in a system
- Wiring a judgment gate into an agent that has no current evaluation step

## Prerequisites

- A list of the agent's side-effecting actions (or the agent's codebase/description)
- A target language: TypeScript (default) or Python
- Optional: an existing judgment policy or gate to wire the proposals into

## Phase 1: Inventory Side-Effecting Actions

List every action the agent takes that mutates state or sends to an external system. Exclude read-only operations (they don't need proposals — proposals add latency and should be reserved for consequential actions).

For each action, identify:
- **Name**: the tool call or operation (e.g., `send_email`, `write_file`, `delete_record`, `post_message`)
- **Target type**: filesystem, database, messaging, external API, calendar, etc.
- **Typical parameters**: what inputs does this action take?
- **Reversibility**: can this be undone, and at what cost?

If working from a codebase, scan for: `Edit`, `Write`, `Bash`, HTTP POST/PUT/DELETE calls, database mutations, send/publish operations.

## Phase 2: Define the Base Proposal Schema

Generate the base proposal type. All proposals share a common envelope:

**TypeScript:**

```typescript
export type ActionCategory =
  | "local-write"      // file system, local DB
  | "reversible-write" // DB update with rollback path
  | "irreversible-write" // delete, drop, truncate
  | "external-send"    // email, message, notification
  | "cross-system"     // modifies state in another service
  | "read-only";       // no mutation — should not need a proposal

export interface ActionProposal {
  id: string;                    // unique per proposal (UUID or cuid)
  agentId: string;               // which agent is proposing this
  actionName: string;            // the tool or operation name
  category: ActionCategory;
  target: string;                // human-readable description of what is affected
  parameters: Record<string, unknown>; // the action's inputs
  justification: string;         // why the agent believes this action is needed
  reversibility: {
    reversible: boolean;
    undoSteps?: string;          // how to undo, if reversible
  };
  estimatedImpact: "low" | "medium" | "high";
  timestamp: string;             // ISO 8601
}

export type ProposalVerdict =
  | { decision: "approve" }
  | { decision: "modify"; modifiedParameters: Record<string, unknown>; reason: string }
  | { decision: "block"; reason: string }
  | { decision: "queue"; queueReason: string };
```

**Python:**

```python
from dataclasses import dataclass, field
from typing import Literal, Optional
from datetime import datetime
import uuid

ActionCategory = Literal[
    "local-write", "reversible-write", "irreversible-write",
    "external-send", "cross-system", "read-only"
]

@dataclass
class ReversibilityInfo:
    reversible: bool
    undo_steps: Optional[str] = None

@dataclass
class ActionProposal:
    action_name: str
    category: ActionCategory
    target: str
    parameters: dict
    justification: str
    reversibility: ReversibilityInfo
    estimated_impact: Literal["low", "medium", "high"]
    agent_id: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

@dataclass
class ProposalVerdict:
    decision: Literal["approve", "modify", "block", "queue"]
    reason: str = ""
    modified_parameters: Optional[dict] = None
    queue_reason: str = ""
```

## Phase 3: Generate Action-Specific Proposal Constructors

For each side-effecting action inventoried in Phase 1, generate a typed constructor that builds a valid proposal:

**TypeScript example — `send_email`:**

```typescript
export function proposeSendEmail(params: {
  to: string[];
  subject: string;
  body: string;
  justification: string;
}): ActionProposal {
  return {
    id: crypto.randomUUID(),
    agentId: AGENT_ID,
    actionName: "send_email",
    category: "external-send",
    target: `email to ${params.to.join(", ")}`,
    parameters: { to: params.to, subject: params.subject, body: params.body },
    justification: params.justification,
    reversibility: { reversible: false },
    estimatedImpact: "high",
    timestamp: new Date().toISOString(),
  };
}
```

Generate one constructor per action. The constructor enforces that `justification` is always provided — it cannot be empty.

## Phase 4: Generate the Execution Wrapper

Produce a wrapper function that:
1. Accepts a proposal and a judge function
2. Calls the judge with the proposal
3. Executes the action only if the verdict is `approve` or `modify`
4. Logs the proposal and verdict regardless of outcome

**TypeScript:**

```typescript
export async function executeWithProposal(
  proposal: ActionProposal,
  judge: (proposal: ActionProposal) => Promise<ProposalVerdict>,
  executor: (action: string, parameters: Record<string, unknown>) => Promise<unknown>
): Promise<{ verdict: ProposalVerdict; result?: unknown }> {
  const verdict = await judge(proposal);

  const logEntry = {
    proposalId: proposal.id,
    actionName: proposal.actionName,
    verdict: verdict.decision,
    timestamp: new Date().toISOString(),
  };
  // Emit to your audit log here
  console.log("[proposal-audit]", JSON.stringify(logEntry));

  if (verdict.decision === "approve") {
    const result = await executor(proposal.actionName, proposal.parameters);
    return { verdict, result };
  } else if (verdict.decision === "modify") {
    const result = await executor(proposal.actionName, verdict.modifiedParameters);
    return { verdict, result };
  }

  // block or queue: do not execute
  return { verdict };
}
```

## Phase 5: Wire to a Judgment Gate (Optional)

If this agent uses `judgment-gate` or `judgment-layer`, the judge function in Phase 4 maps directly to those evaluations. Pass the proposal's `category`, `reversibility`, and `estimatedImpact` fields as the input to the gate's classification rubric.

For agents without an existing judge, generate a default judge stub that:
- Approves all `read-only` proposals (should not reach here, but defensive)
- Approves `local-write` proposals with `reversible: true` and `estimatedImpact: "low"`
- Queues `external-send` and `cross-system` proposals for human review
- Blocks `irreversible-write` proposals unless an explicit override flag is set

```typescript
export async function defaultJudge(proposal: ActionProposal): Promise<ProposalVerdict> {
  if (proposal.category === "read-only") return { decision: "approve" };

  if (
    proposal.category === "local-write" &&
    proposal.reversibility.reversible &&
    proposal.estimatedImpact === "low"
  ) {
    return { decision: "approve" };
  }

  if (proposal.category === "external-send" || proposal.category === "cross-system") {
    return { decision: "queue", queueReason: "external action requires human review" };
  }

  if (proposal.category === "irreversible-write") {
    return { decision: "block", reason: "irreversible writes require explicit override" };
  }

  // Default: ask
  return { decision: "queue", queueReason: "action did not match an approval rule" };
}
```

## Phase 6: Output

Deliver all generated files:

1. **`proposal-schema.ts`** (or `.py`) — base types and interfaces
2. **`proposal-constructors.ts`** — one constructor per action
3. **`execution-wrapper.ts`** — `executeWithProposal` function
4. **`default-judge.ts`** — stub judge (replace with your evaluation logic)

Present each file clearly labeled. Stop before writing any files to the filesystem — confirm with the user which files to write and where.

The user confirms:
- **Apply** — write all files to the specified path
- **Schema only** — write only `proposal-schema.ts`; the user will implement constructors manually
- **Preview** — show files inline without writing

## Verification Checklist

- [ ] Every side-effecting action has a proposal constructor (no direct tool calls remain)
- [ ] `justification` field is required in every proposal — constructors do not accept empty strings
- [ ] The execution wrapper logs every proposal and verdict before deciding whether to execute
- [ ] Default judge does not approve `external-send` or `irreversible-write` automatically
- [ ] Read-only operations are NOT wrapped in proposals (unnecessary latency)
- [ ] User confirmed before writing files

## Related Skills

- `judgment-gate` — evaluator that classifies a proposed action by reversibility, cost, blast radius, and observability
- `judgment-layer` — generates a full judgment policy from an action inventory; plugs into Phase 5 above

## Source Attribution

Proposals pattern extracted from Nate's Newsletter (natesnewsletter@substack.com), 2026-05-11:
*"You gave your AI agent real tools. Here's the 4-part control layer it's missing + the Judge Layer implementation guide"*
https://natesnewsletter.substack.com/p/agent-judge-layer-production-control

Core idea: Part 2 of the 4-part control layer. Rather than an agent executing actions directly, it first generates a proposal object that captures intent, target, justification, and reversibility. Execution is decoupled from intent — proposals flow to evaluation; evaluation decides whether execution fires.
