---
name: audience-model-router
description: Select the right model tier and retrieve a paste-ready prompt for a task, based on who will act on the output — builder, leader, or executive. Extends task-complexity routing with role-specific framing so the output lands at the right level of abstraction.
---

# Audience Model Router

Most model-routing advice focuses on task complexity alone. This skill adds a second axis: **who is acting on the output**. A builder wants implementation prompts and technical context. A leader wants decision frameworks and risk framing. An executive wants a one-page briefing with business impact. Same task, different model tier, different prompt.

Use when someone asks "which model for this?" or "give me a prompt for X" and you know (or can ask) who will receive or act on the output.

## Trigger

Use when the user says:
- "which model should I use for [task]"
- "give me a prompt for [task]"
- "audience model router", "/audience-model-router"
- "I need a prompt for my [exec/manager/team/builder]"
- Describes a task and mentions who will see or use it

If no audience role is stated, ask: "Who's acting on this output — a builder (hands-on), a leader (managing a team or strategy), or an executive (setting direction)?"

## Phase 1: Identify Audience Role

Three mutually exclusive roles:

| Role | Who they are | What they need |
|------|-------------|----------------|
| **Builder** | IC, engineer, AI practitioner, hands-on operator | Implementation prompts, code patterns, technical context, step-by-step instructions |
| **Leader** | Team lead, manager, department head, AI program owner | Decision frameworks, risk/cost framing, team coordination, summaries of technical complexity |
| **Executive** | C-suite, VP, board member, business owner | Business impact, strategic options, 1-page briefings, risk surface, "what does this mean for us?" |

If the role is ambiguous, ask one clarifying question. Don't assume seniority from job title alone — a VP who ships code themselves is often a builder.

## Phase 2: Classify the Task

Rate the task on two dimensions:

**Reasoning depth:**
- Low — formatting, cleanup, simple transforms, fill-in-the-blank
- Medium — standard generation, analysis, content writing, data extraction
- High — architecture, multi-step reasoning, novel design, nuanced judgment

**Output stakes:**
- Low — draft, exploration, brainstorming
- Medium — reviewed artifact, internal deliverable
- High — client deliverable, production code, one-shot external communication

## Phase 3: Route Model Tier

Apply the combined routing table:

| Audience | Reasoning | Stakes | Recommended tier |
|----------|-----------|--------|-----------------|
| Builder | Low | Low/Med | **Haiku** |
| Builder | Low | High | **Sonnet** |
| Builder | Medium | Any | **Sonnet** |
| Builder | High | Any | **Opus** |
| Leader | Low | Any | **Sonnet** |
| Leader | Medium | Low/Med | **Sonnet** |
| Leader | Medium/High | High | **Opus** |
| Leader | High | Any | **Opus** |
| Executive | Any | Low | **Sonnet** |
| Executive | Any | Med/High | **Opus** |

Override rules:
- Executive audiences almost always warrant Opus — low tolerance for misframed output
- Builder + pure formatting → Haiku regardless of audience
- User says "make it good" → upgrade one tier
- User says "quick draft" → downgrade one tier

Verify current pricing via the `/chub` or `/claude-api` skill before citing cost estimates — do not use training-data pricing.

## Phase 4: Deliver the Paste-Ready Prompt

After the routing decision, produce a paste-ready prompt template tailored to the audience role. Each template is opinionated about framing, output structure, and level of abstraction.

### Builder template

```
You are a senior engineer helping me [task description].

Context:
- [relevant technical constraint or stack detail]
- [scope or boundary]

Output:
- [format: code / numbered steps / annotated diff]
- [length target]
- Flag any assumption you make about [specific uncertainty]
```

### Leader template

```
You are a strategic advisor helping me [task description].

Audience: [team lead / department head / AI program owner]

Context:
- [what the team is trying to achieve]
- [key constraint or risk]

Output:
- [format: decision memo / risk matrix / team update]
- Lead with the recommendation
- One paragraph of rationale
- Flag what you'd need to know to be more certain
```

### Executive template

```
You are a business advisor. Give me a [1-page brief / executive summary / options memo] on [task description].

Audience: [CEO / board / VP]

Constraints:
- Max [N] paragraphs or [N] bullets
- No jargon — plain business language
- Lead with the business impact, not the technical detail

Structure:
1. Situation (1 sentence)
2. Options considered (2-3, if applicable)
3. Recommendation + rationale (2-3 sentences)
4. Risk if we don't act / risk of acting (1 sentence each)
```

Customize the template with the actual task details before returning it. The template is a starting point, not the deliverable.

## Phase 5: Pipeline Routing (Optional)

If the task is a multi-step pipeline where different steps serve different audiences (e.g., a builder runs the extraction, a leader reviews the summary, an exec sees the brief), route each step independently:

```
Pipeline: [name]

Step 1: [task for builder] → Haiku/Sonnet   ($X.XX/call)
Step 2: [task for leader]  → Sonnet/Opus    ($X.XX/call)
Step 3: [task for exec]    → Opus           ($X.XX/call)

Total per run: $X.XX
vs all-Opus:   $X.XX (XX% savings)
```

## Output Format

Lead with the routing decision. Show the recommended tier and one-line rationale. Then show the paste-ready prompt. Keep rationale tight — don't over-explain.

```
Audience: [builder / leader / executive]
Task: [short description]
Reasoning depth: [low / medium / high]
Stakes: [low / medium / high]

Recommended model: [Haiku / Sonnet / Opus]
Rationale: [one line]

--- Paste-ready prompt ---
[template filled in with task specifics]
```

## Source Attribution

Technique derived from Nate's Newsletter (natesnewsletter@substack.com), 2026-06-04 intake.
Source: Nate Kadlac, June 2026 restructuring post — "Model-Routing Guide + Role-Specific Paste-Prompts (builder / leader / exec)" as a planned deliverable from the June 3 Opus 4.8 benchmark post.
