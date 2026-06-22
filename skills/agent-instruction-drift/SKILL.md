---
name: agent-instruction-drift
description: >
  Diff an agent's live system prompt or policy against its last-approved baseline to detect silent instruction drift. Flags paraphrasing, scope expansion, removed constraints, and permission creep. Use when an agent's behavior has subtly shifted, before a periodic ownership review, or when you say "instruction drift", "rotted instructions", "prompt drift", "agent drift audit", "spec drift", or "has my agent's prompt changed".
---

# Agent Instruction Drift

Detect silent instruction drift: the gradual divergence between an agent's live system prompt
(or governing CLAUDE.md / policy file) and the version that was last reviewed and approved.

Nate's failure mode label: "rotted instructions." An agent's prompt gets paraphrased by an
orchestrator, edited in a quick fix, or silently updated by a cron rewrite — and nobody notices
the scope expanded, a key constraint disappeared, or the output target changed. The agent still
runs, still produces polished output, and the drift compounds until a real failure surfaces.

Related: the known failure mode where orchestrators paraphrase pinned specs and subtly alter
scope (spec-attrition). This skill runs the same check for any agent prompt or policy file,
not just orchestrators.

## When to Use

- Before or during a periodic ownership review
- After any model upgrade, orchestrator refactor, or pipeline change that might have touched
  the agent's governing prompt
- When an agent's behavior "feels different" but you cannot pin down why
- As a scheduled audit step after changes to `AGENT.md`, `CLAUDE.md`, or policy files
- Any time you update an orchestrator that passes prompts downstream

## Inputs

- **Live prompt**: the agent's current system prompt, CLAUDE.md, or policy file (path or paste)
- **Baseline**: the last-approved version — one of:
  - A git ref (commit SHA, tag, branch): `git show <ref>:path/to/AGENT.md`
  - A pinned file in a `baselines/` directory
  - A paste of the approved text
- Optional: a list of known-important constraints to check explicitly (e.g. "must not draft
  external emails", "max-turns limit must be 15 or fewer")

If no baseline is provided: use the most recent git commit touching the file as the baseline
and note that this may not be the "approved" version.

## Phases

### Phase 1 — Establish baseline

```bash
git show <ref>:<path> > /tmp/agent-baseline.txt
```

If using git: find the last commit that touched the prompt file and one prior to that.
If no git history: ask the user to provide a baseline before proceeding.

### Phase 2 — Structural diff

Produce a structured diff focused on semantic changes, not whitespace:

- **Removed constraints**: lines or sentences that existed in the baseline and are gone
- **Scope expansion**: new capabilities, tool authorizations, or output targets not in baseline
- **Paraphrase drift**: sentences where the meaning subtly changed (e.g. "must not" → "should not",
  "always ask the user" → "ask the user when appropriate")
- **Permission creep**: new tool names, MCP server references, or allowed-actions in the live version
- **Escalation path changes**: any modification to how the agent handles edge cases or errors

### Phase 3 — Score the drift

Classify each finding:

| Severity | Definition |
|----------|------------|
| CRITICAL | Removed safety constraint, added external-communication capability, or changed kill/escalation path |
| HIGH | Scope expansion (new tools, new output targets, new data sources) |
| MEDIUM | Paraphrase that weakens a "must" to a "should" or adds ambiguity to a boundary |
| LOW | Wording cleanup, reordering, whitespace — no semantic change |

### Phase 4 — Report

```
AGENT INSTRUCTION DRIFT REPORT
===============================
Agent: <name>
Live prompt: <path or "pasted">
Baseline: <git ref or "pasted"> — <commit date if known>

FINDINGS
--------
[CRITICAL] <finding description>
  Baseline: "<exact quote>"
  Live:     "<exact quote or REMOVED>"

[HIGH] ...
[MEDIUM] ...
[LOW] ...

SUMMARY
  Critical: N | High: N | Medium: N | Low: N
  Verdict: CLEAN / DRIFT DETECTED

[If DRIFT DETECTED:]
RECOMMENDED ACTIONS
1. Review each CRITICAL and HIGH finding with the named owner.
2. Decide: restore baseline wording, or approve the change and update the baseline.
3. If approved: create a new baseline commit tagged as approved (e.g. git tag approved-YYYY-MM-DD).
4. Do not let the live prompt diverge from the approved baseline without a documented decision.
```

### Phase 5 — Optional: propose restore

For each CRITICAL or HIGH finding, offer a one-line restore patch:

```diff
- <live wording>
+ <baseline wording>
```

Do not apply patches automatically. Present them for human review; the owner decides.

## Verification

- Run `git diff <baseline-ref> HEAD -- <prompt-path>` as a sanity check against Phase 2 output.
- Every finding must quote both the baseline and live text exactly — no paraphrase of the diff.
- If the baseline is a git ref, record the full SHA in the report for reproducibility.

## Source Attribution

Concept from Nate's Newsletter, 2026-06-21: *"Executive Briefing: Your team is running agents
nobody owns. The one-page card and two prompts that fix it."* — specifically the "rotted
instructions" failure mode.
`https://natesnewsletter.substack.com/p/ai-agent-ownership`
Also informed by the known spec-attrition failure mode (orchestrators paraphrasing pinned specs)
documented in learned-rules.md.
