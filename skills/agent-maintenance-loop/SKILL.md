---
name: agent-maintenance-loop
description: Run a structured 6-step maintenance audit on any agent -- job check, last-ten-runs review, seven-surface inspection, replay pack, delete-before-you-add pass, and a keep/change/pause/retire decision. Use when an agent has been running for a while, after a model upgrade, or when outputs have started to feel off.
---

# Agent Maintenance Loop

A repeatable 6-step audit that determines whether an agent is still fit for purpose. Prevents the most common silent failure: an agent producing fluent, plausible output from stale sources, drifted permissions, or scaffolding built for a weaker model.

## Trigger

Use when the user says "/agent-maintenance", "audit this agent", "is this agent still good", "my agent feels off", "run a maintenance pass on X", "should I keep this agent", or after any model upgrade, tool change, or connector change that could affect the agent.

---

## Phase 1: Name the Job

Ask the user (or derive from the agent's prompt / AGENT.md):

> "This agent's job is to **[produce what]** from **[these sources]** for **[these users / destinations]**, with **[this review]** before **[this consequence]**."

If any slot cannot be filled, the agent has a job definition problem -- surface it immediately. An agent whose job cannot be stated in one sentence is not ready to run.

Record the job sentence. Every later phase uses it as the success criterion.

---

## Phase 2: Last-Ten-Runs Review

Collect the agent's recent output. Sources to check (use whatever is accessible):
- Session logs, run history, or output files
- Any structured run records the agent maintains
- Annotations, corrections, or feedback left by the human reviewer

For each of the last ten runs (or as many as are available), record:

| Run | Output reached destination? | Human correction made? | Source used | Tool called | Time to review |
|-----|----------------------------|-----------------------|-------------|-------------|----------------|

**Surface patterns:**
- Same correction appearing 3+ times: "fix the harness, not the output"
- Sources the agent consistently relies on -- are they still current?
- Tools that are called but whose outputs are ignored or overridden
- Runs where review took significantly longer than others -- why?
- Runs where the agent stopped before completing -- what triggered the stop?

If fewer than 3 runs are available, note that and proceed; do not skip this phase.

---

## Phase 3: Seven-Surface Inspection

Walk each of the seven surfaces. For each, apply the breaks/signal/action logic.

| Surface | What breaks here | Signal to look for | Maintenance action |
|---------|-----------------|-------------------|-------------------|
| **Job** | Scope creep, unstated assumption, new stakeholder not in the sentence | Output drifting outside the job sentence; reviewer adding context the agent should have had | Rewrite the job sentence; update the prompt |
| **Diet** | Stale source, paywalled feed, renamed endpoint, outdated file | Agent citing old dates, missing recent events, returning 404s | Update or replace the source; add a freshness check |
| **Memory** | Stale fact stored as truth, outdated context carried forward | Agent contradicting current reality with stored facts | Clear or version the memory; add a staleness TTL |
| **Tools** | Tool removed, API changed, permission expired, tool now redundant | Tool call failing silently; agent working around a tool it used to use | Re-verify each tool; remove tools the agent no longer uses |
| **Reach** | Output destination changed, webhook dead, channel renamed | Output going nowhere; sink returning errors | Re-test every output path end-to-end |
| **Proof** | No inspectable evidence, reviewer has to reconstruct what happened | Reviews taking longer; trust declining without clear cause | Add source links, diffs, or logs to every run output |
| **Value** | Output is no longer being used; consumer changed their process | Low review engagement; output sitting unread | Ask whether this agent should still exist |

Score each surface: **OK / WATCH / FIX / RETIRE**. Record one sentence of evidence for any non-OK rating.

---

## Phase 4: Replay Pack

A replay pack is a small set of known cases re-run against the current agent to confirm behavior has not regressed. If the user has one, run it now. If not, construct a minimal one from the last-ten-runs review.

**Minimum replay pack (5 cases):**
1. A run where the agent produced correct output -- does it still?
2. A run where the agent correctly refused or escalated -- does it still?
3. A run with a forbidden file or off-limits source -- does the agent still avoid it?
4. A run that previously produced an output the reviewer corrected -- does the correction still hold?
5. A run at the boundary of the job sentence -- does the agent stay in scope?

Score each case: **PASS / FAIL / DEGRADED**. Any FAIL is a blocker for the keep decision. DEGRADED means behavior changed but output is still acceptable -- flag for monitoring.

---

## Phase 5: Delete-Before-You-Add

Before recommending any additions to the agent's prompt, rules, or tool list, run the 8-question diagnostic on everything currently in the configuration:

1. **Stale source?** -- Is any source in the diet no longer current or reachable?
2. **Bad example?** -- Does any example in the prompt reflect a case that no longer represents good output?
3. **Too-broad tool?** -- Does any tool give the agent access it does not need for the current job?
4. **Vague job?** -- Does any rule in the prompt exist because the job sentence is unclear rather than because the rule adds value?
5. **Replayed memory?** -- Is any stored fact or context being fed to the agent that it no longer needs or that contradicts current reality?
6. **Over-high permission?** -- Does the agent have access to systems, channels, or data beyond what the job sentence requires?
7. **Missing proof standard?** -- Are there rules that tell the agent what to do but not how to prove it did it?
8. **Model now capable enough?** -- Would the current model handle this correctly without the scaffolding? (Delete the procedure and run the replay pack to find out.)

Remove anything flagged YES before considering any additions. Document what was removed and why.

---

## Phase 6: Keep / Change / Pause / Retire

Based on the evidence gathered in Phases 1-5, make exactly one of four decisions. "No decision" is not allowed -- it is the decision that causes the most drift.

| Decision | When to choose it |
|----------|-------------------|
| **KEEP** | Job sentence valid, last-ten-runs clean, seven surfaces mostly OK, replay pack passes, delete pass completed. Agent is fit for purpose. |
| **CHANGE** | Job sentence needs updating, one or more surfaces rated FIX, replay pack shows DEGRADED but no FAILs, delete pass removed meaningful bloat. Agent can be improved in place. |
| **PAUSE** | Replay pack has a FAIL, a surface is rated RETIRE but the agent might be needed again, or a dependency (model, tool, connector) is in flux. Do not run until the blocker is resolved. |
| **RETIRE** | The Value surface is RETIRE, the job sentence cannot be filled, or the cost of maintaining the agent exceeds the value it delivers. Archive the agent config for reference. |

For KEEP and CHANGE: record the decision with a timestamp. For CHANGE: list the specific changes, assign them, and set a re-review date. For PAUSE: state the specific blocker and the condition under which the agent resumes. For RETIRE: document why, so the decision is not relitigated.

---

## Output Format

```
# Agent Maintenance Report: [Agent Name]
Date: [YYYY-MM-DD]
Auditor: [human or automated]

## Job Sentence
[One-sentence job definition]
Status: CLEAR | AMBIGUOUS | MISSING

## Last Ten Runs
Runs reviewed: [N]
Corrections found: [N] | Repeated corrections: [list if any]
Pattern notes: [key findings]

## Seven-Surface Scores
| Surface | Score | Evidence |
|---------|-------|----------|
| Job     | OK/WATCH/FIX/RETIRE | [one sentence] |
| Diet    | ...   | ... |
| Memory  | ...   | ... |
| Tools   | ...   | ... |
| Reach   | ...   | ... |
| Proof   | ...   | ... |
| Value   | ...   | ... |

## Replay Pack
Cases run: [N] | Pass: [N] | Fail: [N] | Degraded: [N]
[List any FAILs or DEGRADEDs]

## Delete-Before-You-Add
Items removed: [N]
[List each removal with reason]
Items to add: [N or "none"]

## Decision: KEEP | CHANGE | PAUSE | RETIRE
Rationale: [2-3 sentences]
Next review date: [date, if KEEP or CHANGE]
Open actions: [list, if CHANGE]
Blocker: [specific condition, if PAUSE]
Archive note: [why, if RETIRE]
```

---

## Verification

- [ ] Job sentence fills all five slots (what, from, for, with, before)
- [ ] Last-ten-runs review has evidence, not guesses
- [ ] Every seven-surface score has one sentence of supporting evidence
- [ ] Replay pack ran at least 3 cases
- [ ] Delete pass ran all 8 questions, not just the obvious ones
- [ ] Decision is exactly one of the four options with a rationale

---

## Source

Extracted from Nate Kadlac newsletter (2026-06-17), flagship idea -- "Agent Maintenance Loop": the 6-step copy-paste audit for keeping agents fit for purpose. Seven-surface table (Job/Diet/Memory/Tools/Reach/Proof/Value) and keep/change/pause/retire decision framework from the same article. The article's lead anecdote: Vercel deleted ~80% of an agent's tools and the agent improved; the delete-before-you-add pass operationalizes that finding.
