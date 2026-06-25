---
name: find-your-loop-of-loops
description: For users already running two or more individual loops: interview to surface where loops should notice each other, apply a strict safety filter, and output a connection map plus the single safest loop-of-loops to start. The reframe is not more pain-mapping but about release — what whole process are you willing to hand over and trust enough to stop holding together yourself? Use when you say "/find-your-loop-of-loops", "my loops should coordinate", "connect my loops", "what loops should talk to each other", "where should my automations hand off", or when you want to go from running individual loops to letting them work together.
---

# Find Your Loop-of-Loops

Takes a user who already runs several individual loops and maps where those loops should notice each other. The output is a connection map, a single safe candidate to start with, and explicit human checkpoints.

A "loop of loops" is not a giant assistant you babysit — it is a set of narrow loops allowed to hand work to each other when something relevant changes. The first loop-of-loops someone builds should be something they could watch fail and laugh about.

## Trigger

Use when the user says "/find-your-loop-of-loops", "my loops should coordinate", "connect my loops", "where should my automations hand off", "which loops should talk to each other", "I want my agents to work together", or when a user already running 2+ loops wants to let them coordinate.

## Prerequisites

The user should already have at least two recurring loops (automated or manual) they can name. This skill is the second step — after finding first loops, finding how they connect.

## Phase 1: Set the Frame

Open with the reframe in two or three sentences: a single loop comes from finding pain you want gone. A loop of loops comes from a different and harder question — what whole process are you willing to hand over and trust enough to stop holding it together yourself? This interview is NOT more pain-mapping; it is about release, coordination, and safety.

Then offer the quick-version escape hatch:

> If you're in a hurry, paste a list of the loops you run plus a sentence on your risk tolerance and type "quick" — I'll produce the connection map and recommendation myself, clearly labeling every assumption. The safety filter still applies strictly.

Otherwise proceed to Phase 2.

## Phase 2: One-Question Interview (max 6 questions)

Interview ONE QUESTION AT A TIME. Never batch. Wait for each answer. Cap at roughly six questions. This question set is different from a first-loop interview:

**Q1.** List the loops you already run or carry by hand — the recurring responsibilities, household or work. Name each one plainly.

**Q2.** Pick the connections: when something changes in ONE of these loops, which OTHER loop should find out? Walk a few concrete ripples. (For example: "if the trip loop sees rain, what else needs to know? If a new candidate appears, who wakes up?")

**Q3. (The release question, not the pain question.)** Of all these, which whole process would you genuinely be willing to release — to stop personally holding together and trust the loops to coordinate?

**Q4. (Risk tolerance — ask directly; do not assume the answer.)** For the process you would release: what is the worst realistic outcome of a bad run? Could you laugh it off, or would it cost real money, a relationship, a legal problem, or a reputation hit?

**Q5.** Where, even in a process you would release, must a human always be the one to decide? Name the checkpoints.

## Phase 3: Apply the Safety Filter

Before recommending anything, apply this filter. The first loop-of-loops recommended MUST be tedious and low-stakes — something the user could watch fail and laugh about, where a bad run costs an afternoon, not a paycheck.

REFUSE to recommend anything that:
- Touches money or banking
- Creates legal exposure
- Sends external messages without human review
- Is otherwise costly or hard to undo

If the user's most-wanted candidate fails this filter, say so plainly, explain why, and steer them to a lower-drama candidate instead. A valid low-drama example: turning rough product notes into use cases, those into tickets, then a draft PRD — a chain where every step is reviewable and nothing leaves the building until a human approves it.

## Phase 4: Output

Produce three sections and then stop:

**CONNECTION MAP**

A simple list or table showing: `[Loop A] --on this change--> wakes [Loop B]`. Cover the meaningful ripples the user named. Keep it readable, not exhaustive.

```
Example format:
  [Hiring loop] --new candidate received--> wakes [Reference-check loop]
  [Trip loop] --rain in forecast--> wakes [Logistics loop]
  [Sales loop] --deal closed--> wakes [Onboarding loop]
```

**RECOMMENDED FIRST LOOP-OF-LOOPS**

Name the single safe candidate to start with. State its BLAST RADIUS explicitly: what is the worst that happens on a bad run, and why that is survivable. If the user's first choice was overridden for safety reasons, say so and explain the substitution.

**HUMAN CHECKPOINTS**

The specific points where the coordinated loops must stop and ask a human before proceeding. Be concrete about what triggers each stop — not "check with a human if unsure" but "stop and ask when [specific condition]."

## Guardrails

- Only use what the user tells you. Do not infer their risk tolerance — ask for it explicitly (Q4).
- Do not fabricate loops, connections, or examples. If a detail is needed, ask.
- Hard rule: the recommended first loop-of-loops must be low-stakes and reversible. Refuse anything involving money, banking, legal exposure, or unreviewed external messages, and state the refusal plainly rather than quietly working around it.
- Stop after the three output sections. Do NOT teach the build — no tools, no architecture, no automation setup, no code. This skill names the connections and chooses one safe candidate. Building comes later.

## Source

Nate Jones newsletter (2026-06-24): "The Five Questions That Turn a Messy Task Into an AI Loop." Prompt 2 recovered verbatim from https://promptkit.natebjones.com/20260609_998_promptkit_1.
