---
name: delete-before-you-add
description: Run an 8-question diagnostic over an agent's current configuration before adding any new rule, tool, example, or permission. Surfaces what should be deleted first. Based on the finding that removing bloat from an agent often improves it more than adding new capabilities.
---

# Delete-Before-You-Add

A pre-edit linter for agent configuration. Before any new rule, tool, example, source, or permission is added to an agent, run the 8-question diagnostic over what is already there. What gets removed first determines whether the addition is actually needed.

The motivation: Vercel deleted roughly 80% of an agent's tools and the agent got better. Additions are easy to make and hard to undo. This skill forces deletion to come first.

## Trigger

Use when the user says "delete-before-you-add", "should I add this rule", "I want to add a tool to this agent", "the agent keeps making this mistake -- I want to add a rule", "prune this agent", or before any edit to an agent's prompt, tool list, or permissions.

Also use at the end of any maintenance pass (Phase 5 of the Agent Maintenance Loop) before accepting additions.

---

## Phase 1: Intake

Ask the user for:
1. **What they want to add** -- the specific rule, tool, example, source, or permission
2. **The problem it is meant to solve** -- what went wrong that prompted this addition?
3. **The agent's current configuration** -- prompt, tool list, and permission set (or point to the relevant file)

If the user does not know the exact current configuration, ask them to retrieve it before proceeding. Running this diagnostic on a vague mental model produces vague answers.

---

## Phase 2: The 8-Question Diagnostic

Apply each question to the current configuration. Answer YES / NO / UNSURE for each. A YES means the item should be removed before adding anything new. UNSURE means investigate before deciding.

### Q1 -- Stale source?
Is any source in the agent's diet (documents, feeds, APIs, files) no longer current, reachable, or authoritative? A source that was accurate six months ago may now produce confidently wrong output.

*Check: when was each source last verified? Does the agent cite dates that are now old?*

### Q2 -- Bad example?
Does any example in the prompt illustrate a case that no longer represents the desired output? Examples anchor the model's behavior -- a bad example is worse than no example.

*Check: does every example in the prompt still reflect what good output looks like today?*

### Q3 -- Too-broad tool?
Does any tool give the agent access to systems, data, or actions beyond what the job sentence requires? Broad tools increase blast radius and produce off-topic actions.

*Check: for each tool, can you state which specific step in the job requires it? If not, the tool is too broad.*

### Q4 -- Vague job?
Does any rule exist because the job sentence is unclear, rather than because the rule genuinely adds value? Rules that patch an unclear job sentence accumulate without bound and each one degrades model performance.

*Check: if the job sentence were rewritten clearly, would this rule still be needed?*

### Q5 -- Replayed memory?
Is any stored fact, context, or prior-run output being fed to the agent that it no longer needs, or that contradicts current reality? Memory that made sense at setup can become noise or misinformation.

*Check: does any memory item encode something the model could derive from current sources?*

### Q6 -- Over-high permission?
Does the agent have access to systems, channels, or data beyond what the job sentence requires? Excess permission is not just a security risk -- it increases the surface area for unintended actions.

*Check: map each permission to a specific line in the job sentence. Any permission that does not map should be removed.*

### Q7 -- Missing proof standard?
Are there rules that tell the agent what to do but not how to prove it did it? Rules without proof standards cannot be verified and produce output that looks complete but may not be.

*Check: for each behavioral rule, is there a corresponding check the reviewer can apply to confirm compliance?*

### Q8 -- Model now capable enough?
Would the current model handle this correctly without the scaffolding? Models improve; procedures written for a weaker model can actively constrain a stronger one by overriding judgment the model already has.

*Method: remove the procedure from the configuration, run the replay pack (or a representative case), and observe. If the model performs correctly without the rule, the rule is in the way.*

---

## Phase 3: Delete Pass

For every YES or UNSURE answer:
1. State what should be removed
2. State why (which question flagged it)
3. Confirm the removal does not break the job sentence

Document each removal. Do not proceed to Phase 4 until the delete pass is complete.

---

## Phase 4: Addition Decision

After the delete pass, return to the proposed addition from Phase 1.

Ask:
- Does the problem the addition was meant to solve still exist after the delete pass?
- Is the addition the simplest change that addresses the problem, or does the delete pass reveal a better fix (e.g., clarifying the job sentence instead of adding a rule)?
- After deletion, does the replay pack still pass? If yes, the delete pass may have already solved the problem.

**Decision:**
- **ADD** -- the problem persists, the addition is the right fix, and it passes the 8 questions itself
- **CLARIFY INSTEAD** -- the root cause is a vague job sentence; rewrite that instead of adding a rule
- **DEFER** -- the problem is real but the addition is premature; collect more evidence from runs first
- **DISCARD** -- the delete pass resolved the problem; the addition is no longer needed

---

## Output Format

```
# Delete-Before-You-Add Audit: [Agent Name]
Date: [YYYY-MM-DD]
Proposed addition: [what the user wanted to add]
Problem it was meant to solve: [stated problem]

## Diagnostic Results
| # | Question | Answer | Item flagged |
|---|----------|--------|--------------|
| Q1 | Stale source? | YES/NO/UNSURE | [item or "none"] |
| Q2 | Bad example? | YES/NO/UNSURE | [item or "none"] |
| Q3 | Too-broad tool? | YES/NO/UNSURE | [item or "none"] |
| Q4 | Vague job? | YES/NO/UNSURE | [item or "none"] |
| Q5 | Replayed memory? | YES/NO/UNSURE | [item or "none"] |
| Q6 | Over-high permission? | YES/NO/UNSURE | [item or "none"] |
| Q7 | Missing proof standard? | YES/NO/UNSURE | [item or "none"] |
| Q8 | Model now capable enough? | YES/NO/UNSURE | [item or "none"] |

## Delete Pass
Items removed: [N]
- [Item] -- [reason] -- [question that flagged it]

## Addition Decision: ADD | CLARIFY INSTEAD | DEFER | DISCARD
Rationale: [one sentence]
```

---

## Verification

- [ ] All 8 questions applied to the current configuration, not a mental model of it
- [ ] Every YES or UNSURE has a specific item named, not a vague category
- [ ] Delete pass completed before the addition decision
- [ ] Addition decision references the post-deletion state, not the original state

---

## Source

Extracted from Nate Kadlac newsletter (2026-06-17), idea 6 -- "Delete-Before-You-Add Pruning Linter": the 8-question diagnostic before any new rule is added to an agent. Lead anecdote: Vercel deleted ~80% of an agent's tools and the agent improved. The principle: only add what the replay pack proves is needed.
