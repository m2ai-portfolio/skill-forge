---
name: agentic-harness-designer
description: Walk through a structured interview covering tools, permissions, state, memory, evaluation, and observability to produce a phased implementation plan for a new agent system. Use when starting a new agent project and wanting a complete architectural blueprint before writing any code.
---

# Agentic Harness Designer

Produces a complete, phased implementation plan for a new agent system through a structured architectural interview. Prevents the most common failure mode in agent design: jumping to code before the ownership model, state boundaries, and failure modes are understood.

## Trigger

Use when the user says "design my agent", "plan an agent system", "agentic harness", "architecture for my agent", "what should I build before I write agent code", "design the harness for", or starts a new agent project without a plan.

## Phase 1: Purpose

Ask:
1. "What is this agent's single sentence of purpose?" (One sentence. If they can't say it in one sentence, the scope is not defined yet.)
2. "Who or what triggers this agent? (human message, schedule, event, another agent, file arrival)"
3. "What does 'done' look like for a single run?" (One verifiable outcome, not a vague goal.)

Do not proceed until all three are answered. The purpose statement is the foundation; everything else is scaffolding.

## Phase 2: Tool and Permission Inventory

Ask:
4. "What tools does this agent need?" (Read files? Write files? Run shell commands? Call APIs? Browse the web? Control a browser? Spawn sub-agents?)
5. "Which of those actions are reversible, and which are permanent or visible to others?"
6. "What should this agent never be allowed to do?" (Hard constraints — e.g., write to a production database, delete files, send external messages without approval.)

From the answers, produce a **permission tier map**:
- **Auto-approved:** read-only operations that are always safe
- **HIL-gated:** actions that require human approval before execution
- **Blocked:** actions the agent must refuse entirely

## Phase 3: State and Memory

Ask:
7. "What state does this agent need to carry between runs?" (None? A config file? A database? A vector store?)
8. "Where should that state live?" (Local file, cloud DB, repo, environment variable)
9. "What happens to the state if the agent crashes mid-run?" (Is partial state recoverable? Is it safe to re-run?)

Produce a **state boundary diagram** (text):
```
[Input source] → [Agent] → [State store: path/type] → [Output destination]
```

## Phase 4: Failure and Observability

Ask:
10. "What does a silent failure look like for this agent?" (Produces no output? Wrong output? Crashes? Loops indefinitely?)
11. "Where does output go, and how will you know if it's missing?" (Who is the owner? Where is the sink?)
12. "How does the agent stop or escalate if it fails repeatedly?" (Retry limit, kill switch, or escalation path)

These three map directly to **owner, sink, and kill** — the three guards required for any autonomous loop. If any guard is missing, name it explicitly and refuse to proceed until it is defined.

## Phase 5: Evaluation

Ask:
13. "How will you know if a run was good?" (A human reviews it? A downstream system accepts it? A metric improves?)
14. "What is the minimum acceptable output quality?" (Threshold for auto-accept vs. flagging for review)

Produce an **evaluation contract**:
```
Success: [measurable condition]
Failure: [measurable condition]
Review trigger: [condition that sends output to a human]
```

## Phase 6: Phased Plan

Synthesize all answers into a phased implementation plan:

```markdown
## [Agent Name] — Implementation Plan

### Purpose
[One sentence]

### Phase 1: Skeleton (Day 1)
- [ ] Minimal trigger → run → output loop with no tools
- [ ] State store initialized
- [ ] Output delivered to sink

### Phase 2: Tools (Day 2-3)
- [ ] Add each tool from the permission tier map
- [ ] Add HIL gates for gated actions

### Phase 3: Hardening (Day 4-5)
- [ ] Add kill switch / retry logic
- [ ] Add evaluation check (success/failure signal)
- [ ] Test failure modes explicitly

### Phase 4: Observability (Day 6-7)
- [ ] Wire owner notification on failure
- [ ] Add a health check or heartbeat
- [ ] Document the owner/sink/kill triple

### Out of Scope (confirm before adding)
- [Anything the agent must not do, from Phase 2 answers]
```

## Notes

- This skill designs **new** agent systems from scratch. To audit an existing one against production primitives, use `agent-architecture-audit` instead. To define the harness for a specifically **scheduled** (cron-driven) agent, use `scheduled-agent-harness` instead.
- The owner/sink/kill triple is non-negotiable. Any plan missing one of the three is incomplete.
- Phase 1 must be shippable on its own. Never spec all four phases and build none.
- Keep the purpose statement to one sentence. If the user needs two sentences, the scope needs narrowing first.

## Source

Extracted from Nate Kadlac "Open Skills" newsletter (2026-06-19), idea 31 — Agentic Harness Designer: "Walk through agent-system architecture questions (tools, permissions, state, memory, evaluation, observability) to produce a phased implementation plan."
