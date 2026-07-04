---
name: decision-ladder
description: Classify a recurring workflow as prompt, skill, or plugin using a structured five-question intake. Use before building anything new -- prevents over-engineering one-off tasks and under-engineering high-frequency workflows. Trigger phrases: "decision ladder", "should this be a skill", "prompt or skill", "skill or plugin", "/decision-ladder", "what should I build", "is this worth a skill".
---

# Decision Ladder

Takes a recurring workflow description and recommends the right artifact level: prompt, skill, or plugin. Prevents spending a sprint on a skill for something that belongs in a single sentence, and prevents under-investing in a plugin for something that fires fifty times a day.

## Trigger

Use when the user says "decision ladder", "should this be a skill", "prompt or skill", "skill or plugin", "/decision-ladder", "what should I build", "is this worth a skill", "help me decide if this needs a skill", or before starting any new skill or plugin work.

## The Five Questions

Ask in order. Any question can terminate early with a recommendation.

### Q1: How often does this workflow run?
- Once or twice total: **Prompt** (write it inline, no file needed)
- Weekly or less: tentatively Prompt, continue
- Multiple times per week: tentatively Skill, continue
- Daily or more: Skill or Plugin, continue

### Q2: How many distinct tools or steps does it involve?
- 1 tool, 1-3 steps: **Prompt**
- 2-4 tools or 4-8 steps: **Skill**
- 5+ tools or 9+ steps: **Plugin** (the wiring cost is too high to prompt each time)

### Q3: Are the checks deterministic? (linters, validators, test runners, schema enforcement)
- Yes: lean **Plugin** (deterministic steps belong in configured pipelines, not re-prompted)
- No: continue

### Q4: Do team or project standards apply? (rubrics, style guides, naming rules, review criteria)
- Yes AND standards change infrequently: **Skill** (bake standards in, update when they change)
- Yes AND standards change frequently: **Prompt** (baking in standards would require constant skill churn)
- No: continue

### Q5: Does it need to talk to an external system? (GitHub, Linear, Slack, Drive, CRM, calendar, databases)
- Yes: **Plugin** (integrations need persistent credentials and typed tool manifests, not prompts)
- No: **Skill**

## Recommendation Format

After the five questions, output:

```
RECOMMENDATION: <Prompt | Skill | Plugin>

RATIONALE:
- Q1: <answer> -- <implication>
- Q2: <answer> -- <implication>
- Q3/Q4/Q5: <answer> -- <implication>

NEXT STEP:
Prompt: Write it inline -- no file, no overhead.
Skill:  Create SKILL.md with trigger patterns, phases, and a verification section.
Plugin: Scope the MCP tools needed, the credential surface, and the install/upgrade
        flow before writing any code.
```

## Edge Cases

- **Borderline Skill / Plugin**: if Q2 says Skill but Q5 says Plugin, default to Plugin -- integrations are the deciding factor because they require persistent config the skill format cannot carry.
- **One-off but complex**: even if Q1 says Prompt, if Q2 scores 9+ steps recommend Skill anyway -- the one-time complexity will recur as a maintenance burden if not formalized.
- **Team vs personal**: if the workflow is personal (only you invoke it), lower the Plugin threshold -- plugins pay off at team scale.

## Verification

- The recommendation follows the intake answers, not the user's pre-existing preference
- A Plugin recommendation includes a scoping note (which integrations, which credentials)
- A Skill recommendation includes at least one trigger phrase

## Source Attribution

Technique: Prompt to Skill to Plugin decision ladder
Source: Nate's Newsletter (natesnewsletter.substack.com)
Post: "Codex plugins matter because the bottleneck moved"
Published: 2026-05-09
