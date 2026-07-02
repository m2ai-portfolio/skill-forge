---
name: agentic-work-loop
description: "Stand up a complete personal agent stack using the five-part loop: Memory (what the agent knows), Method (how it works), Boundary (what requires human approval), Receipt (what it did), Judgment (what stays human). Produces a concrete implementation plan with one small, auditable loop the user can run today. Trigger on: 'I want to set up an AI agent for my work', 'how do I actually use AI agents day to day', 'build me a personal agent system', 'autonomous agent setup', 'I want AI to handle X without me babysitting it', or any request to design a repeatable personal agent workflow."
---

# agentic-work-loop — five-part personal agent implementation

Turns an abstract goal ("I want AI to help with my work") into one concrete, running loop
with clear memory, method, boundary, receipt, and judgment components. The risk in
personal AI has moved from capability to intent — agents can now act reliably, so the
real question is what the agent thought it had permission to do. This loop makes
permission explicit before the first run.

## Purpose

Most personal AI setups fail not because the model is bad but because the setup is
ambiguous: the agent has no persistent memory of how you work, no defined procedure
to follow, no stated limits, and no way to leave a trail you can audit. One small loop,
wired correctly, beats a hundred ad-hoc prompts.

## Trigger

Use when the user wants to move from one-off AI prompts to a repeatable, partially
autonomous workflow. Do NOT use when the user only needs a single task answered —
this skill is for recurring or ongoing work patterns.

Activation phrases:
- "I want to set up an AI agent for my work"
- "how do I actually use AI agents day to day"
- "build me a personal agent system"
- "I want AI to handle X autonomously"
- "make this repeatable without me babysitting it"
- "I want a personal AI assistant that remembers"

## Phase 1 — Identify the candidate loop

Ask the user to name ONE recurring task they do repeatedly and would trust an agent
to do if the agent knew their preferences and had clear limits.

Good candidates:
- A weekly review that collects information from the same sources
- A triage process that classifies incoming items by the same rules each time
- A draft-and-wait workflow where the agent prepares but the human sends

Bad candidates for a first loop:
- Tasks with unpredictable inputs that require fresh judgment every time
- Tasks where a mistake has high real-world cost before it can be caught
- Tasks the user has never done themselves (the method isn't known yet)

Name the candidate loop in one sentence: "[Agent] will [action] every [frequency],
starting from [input], producing [output], delivered to [sink]."

## Phase 2 — Wire the five components

For the named loop, specify each component explicitly. Do not leave any component blank.

**1. Memory — what the agent knows before it starts**

What context must the agent have to do this task the user's way, not a generic way?
Produce a memory file (plain markdown, stored locally) containing:
- The user's identity and role as it relates to this task
- The working style preferences that apply (tone, format, level of detail)
- Any standing decisions or heuristics the agent should apply without asking

Example: for a weekly digest task, memory contains "audience is my team of 5 engineers,
prefer bullet points over prose, flag anything touching security or cost first."

**2. Method — the runbook the agent follows**

Write the step-by-step procedure the agent executes each time. This becomes a SKILL.md
(see `open-skills-authoring-kit` if that skill is available). Minimum fields:
- Input: what the agent starts from
- Steps: numbered, specific actions
- Output: the artifact the agent produces
- Done-when: one observable condition that signals completion

**3. Boundary — what requires human approval**

List every action the agent must pause before taking. Three categories to cover:

| Category | Must ask before | Can proceed without asking |
|----------|----------------|---------------------------|
| External | Any send, publish, or post to a third party | Drafting, summarizing, classifying |
| Destructive | Deleting, overwriting, or moving source data | Reading, copying, appending |
| Identity | Changing credentials, permissions, billing | Everything else |

Also name the boundary for this specific task: what is the one action that, if taken
automatically, would cause the most harm?

**4. Receipt — what the agent leaves behind**

Define the completion record the agent writes after every run:
- Where it is written (a local file path or folder, env-configurable)
- What it contains: DONE/FAILED, what changed, what was checked, what needs human review
- Append-only: the agent may never overwrite a prior receipt

The receipt is the audit trail. If the user cannot read the receipt and understand
exactly what the agent did, the receipt format is wrong.

**5. Judgment — what stays human**

Name the decisions that the agent should never make autonomously, even when it has
all the information it needs. Examples:
- Final approval before anything reaches an external party
- Any action based on ambiguous input (agent must ask, not guess)
- Priority calls when multiple valid options exist

Write this as a one-line rule the agent can check: "If [condition], stop and ask."

## Phase 3 — Stand up the loop

Produce a concrete starter implementation:

1. **Memory file**: `memory/[task-name].md` — the context block the agent loads first
2. **Method file**: `skills/[task-name]/SKILL.md` — the procedure the agent follows
3. **Receipt location**: `receipts/[task-name]/` — folder for append-only run logs
4. **First-run prompt**: the exact prompt the user pastes to start the first run,
   which loads the memory file, references the method file, and ends with
   "Leave your receipt at [path] when done."
5. **Approval gate**: the specific phrase the user says to approve the agent's draft
   before any external action is taken

## Phase 4 — Verify before first run

Walk through the loop mentally before executing:

- [ ] Can the agent complete the task without asking a follow-up question? If not, the
      method or memory is incomplete.
- [ ] Does every boundary have a concrete named action, not a vague caution?
- [ ] Is the receipt location a real path the user can open and read?
- [ ] Is there exactly one place the agent stops and waits for human approval before
      any external action?
- [ ] Can the user reproduce this loop from the files alone, without relying on chat history?

## Verification

Before handing off the implementation:
- [ ] Candidate loop is named in one sentence with action, frequency, input, output, sink
- [ ] Memory file exists and contains role context + at least two working-style preferences
- [ ] Method file (SKILL.md) has numbered steps, output artifact, and done-when condition
- [ ] Boundary table covers external, destructive, and identity categories
- [ ] Receipt location is a local, env-configurable path (no hardcoded absolute paths)
- [ ] Judgment rule is one sentence the agent can evaluate as a boolean

## Source

Nate's Newsletter, 2026-07-01 — "You can build 80% of your own AI memory by talking to the agent already on your computer"
Pattern: five-part agent loop — Memory, Method, Boundary, Receipt, Judgment.
Core principle: rent the intelligence, own the memory, give the agent a method, make it leave receipts.
URL: https://natesnewsletter.substack.com/p/open-stack-ai-memory
Field guide: https://unlock-ai.natebjones.com/guides/open-stack/open-stack-field-guide
