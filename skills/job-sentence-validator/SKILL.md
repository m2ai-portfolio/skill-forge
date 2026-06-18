---
name: job-sentence-validator
description: Force any agent, workflow, or automation to produce a complete job sentence before it is trusted to run. Rejects agents whose job cannot be stated as "produce X from these sources for these users, with this review before this consequence." Use before deploying an agent, before extending its permissions, or when it starts producing output that surprises its owner.
---

# Job-Sentence Validator

Forces every agent to earn trust by completing a single sentence before it runs. An agent whose job cannot be stated in one sentence is not ready to run -- and the sentence exposes what is actually unclear before the agent does something about it.

The template: **"This agent's job is to [produce X] from [these sources] for [these users/destinations], with [this review] before [this consequence]."**

An agent that cannot fill all five slots has a design problem, not a prompt problem.

## Trigger

Use when the user says "validate this agent's job", "job sentence", "can this agent run", "is this agent ready", "what does this agent actually do", or before deploying any new agent, extending an agent's permissions, or when an agent's outputs have started to surprise its owner.

Also use as the first phase of an agent maintenance pass -- if the job sentence has drifted from the original, the maintenance finding is already confirmed.

---

## Phase 1: Extract the Five Slots

Ask the user for the agent's current prompt, system instructions, or description. Then attempt to fill the five slots:

### Slot 1: What (produce X)
The concrete output the agent produces on each successful run. Must be specific enough that a reviewer can tell immediately whether the output is there or not.

- **Valid:** "a weekly digest email of three key developments in the user's domain"
- **Invalid:** "insights," "analysis," "a summary" (too vague to verify)

### Slot 2: From (these sources)
The specific, named sources the agent reads or queries. Must be enumerable -- "the internet" does not count.

- **Valid:** "the last 7 days of posts from [RSS feed URL] and [newsletter name]"
- **Invalid:** "recent news," "current information," "web search results"

### Slot 3: For (these users / destinations)
Who receives the output, or where it lands. Must be a specific person, channel, file path, or system -- not a role or category.

- **Valid:** "the user's Slack #weekly-digest channel"
- **Invalid:** "the team," "stakeholders," "wherever it's needed"

### Slot 4: With (this review)
The human or automated check that occurs before the output reaches the consequence. "No review" is a valid answer -- but it must be stated explicitly, not assumed.

- **Valid:** "a 60-second skim by the owner before send," "automated: output must pass the proof checklist"
- **Invalid:** (blank), "whenever someone looks at it," "as needed"

### Slot 5: Before (this consequence)
The real-world effect the output produces if it is wrong. This slot is the most important: it determines how much rigor the other slots require. A low-stakes consequence warrants less review than a high-stakes one.

- **Valid:** "before the email is sent to 300 subscribers," "before the file is committed to main"
- **Invalid:** (blank), "before it goes live" (what does "live" mean here?)

---

## Phase 2: Score the Sentence

For each slot, assign a status:

| Status | Meaning |
|--------|---------|
| **FILLED** | Specific, verifiable, unambiguous |
| **VAGUE** | Present but too broad to act on; needs narrowing |
| **MISSING** | Absent from the available description |

A sentence with any MISSING slot **cannot be trusted to run**. A sentence with VAGUE slots can run with caution -- but each VAGUE slot is a risk that should be resolved before the agent's permissions are extended.

---

## Phase 3: Diagnose the Gaps

For each VAGUE or MISSING slot, apply the standard diagnosis:

**Slot 1 (What) is VAGUE or MISSING:**
The agent has not been given a success criterion. Every run will produce output, but neither the agent nor the reviewer knows whether it is good. Fix: state the output in terms a reviewer can check in under 30 seconds.

**Slot 2 (From) is VAGUE or MISSING:**
The agent will decide its own sources, which means it will use whatever is most available -- not necessarily what is authoritative. Fix: enumerate the specific sources. If the right sources are unknown, that is a design question to resolve before running.

**Slot 3 (For) is VAGUE or MISSING:**
The output has no home. It will be produced and left somewhere the owner may not check. Fix: name the specific destination. If the destination is "me," state that explicitly.

**Slot 4 (With) is VAGUE or MISSING:**
There is no gate between the agent's output and its consequence. If the output is wrong, the consequence fires without a chance to intervene. Fix: state the review explicitly, even if the answer is "none -- I accept the risk."

**Slot 5 (Before) is VAGUE or MISSING:**
The stakes are unknown. Without knowing the consequence, it is impossible to calibrate how much review Slot 4 should require. Fix: state what happens if the output is wrong. If the consequence seems benign, say so -- it removes uncertainty rather than adding it.

---

## Phase 4: Propose or Reject

**If all five slots are FILLED:**
Output the complete sentence. Mark the agent as **READY TO RUN**.

**If any slot is VAGUE:**
Output the partial sentence with the vague slots marked. Mark the agent as **RUNNABLE WITH CAUTION -- [N] VAGUE SLOTS**. List the specific narrowing actions needed.

**If any slot is MISSING:**
Output the partial sentence with the missing slots marked. Mark the agent as **NOT READY**. Do not allow the agent to run until the gaps are resolved.

---

## Output Format

```
# Job Sentence Validation: [Agent Name]
Date: [YYYY-MM-DD]

## Draft Sentence
"This agent's job is to [Slot 1] from [Slot 2] for [Slot 3],
with [Slot 4] before [Slot 5]."

## Slot Scores
| Slot | Status | Current value | Issue (if any) |
|------|--------|--------------|----------------|
| 1 What | FILLED/VAGUE/MISSING | [value] | [issue or "none"] |
| 2 From | FILLED/VAGUE/MISSING | [value] | [issue or "none"] |
| 3 For  | FILLED/VAGUE/MISSING | [value] | [issue or "none"] |
| 4 With | FILLED/VAGUE/MISSING | [value] | [issue or "none"] |
| 5 Before | FILLED/VAGUE/MISSING | [value] | [issue or "none"] |

## Verdict: READY TO RUN | RUNNABLE WITH CAUTION | NOT READY

## Actions Required
- [Slot N]: [specific narrowing or clarification needed]
```

---

## Verification

- [ ] All five slots attempted -- "not stated" is recorded, not skipped
- [ ] Each VAGUE rating has a specific reason, not just "could be clearer"
- [ ] Verdict matches the worst slot score (one MISSING = NOT READY regardless of other slots)
- [ ] Proposed sentence is a single sentence, not a paragraph

---

## Notes

- The job sentence is a living document. Re-validate it whenever the agent's sources, destination, review process, or consequence changes.
- A VAGUE Slot 4 (review) combined with a high-stakes Slot 5 (consequence) is the most common failure pattern. Surface it explicitly -- the user often has not connected the two.
- This skill validates the job definition, not the agent's capability. An agent can have a perfectly clear job sentence and still execute it poorly. The sentence is a necessary condition for trust, not a sufficient one.

---

## Source

Extracted from Nate Kadlac newsletter (2026-06-17), idea 3 -- "Job-Sentence Generator / Validator": forces "This agent's job is to [produce X] from [these sources] for [these users], with [this review] before [this consequence]" and rejects agents whose sentence cannot be completed. Described as a natural upstream add-on to goal-making and ownership discipline.
