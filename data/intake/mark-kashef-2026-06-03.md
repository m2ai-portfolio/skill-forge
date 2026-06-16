# Mark Kashef — "Master All 6 Claude Code Dynamic Workflows"

**Source:** https://www.youtube.com/watch?v=g9b9G8dcS8Y
**Published:** 2026-06-03
**Intake date:** 2026-06-03

---

## TLDR

Mark breaks down an Anthropic-published masterclass on dynamic workflows, extracting 6 named design patterns: Classify and Act, Fan Out and Synthesize, Adversarial Verification, Generate and Filter, Tournament, and Loop Until Done. The core insight is that dynamic workflows fix three specific single-session failure modes — agent laziness (incomplete task execution), self-preference bias (Claude auto-approving its own output), and goal drift (the original intent degrading through compaction). Each pattern targets a distinct task shape, and patterns can be stacked in a single prompt using keyword-based composition.

---

## Buildable Ideas

### 1. `dynamic-workflow-pattern-selector` — Pattern decision guide skill

Build a skill that maps a task description to the correct one (or combination) of the 6 named workflow patterns, explains the selection reasoning, and produces a ready-to-run prompt using the right keywords.

- **[a] Effort:** S — pure decision logic and prompt templates; no external APIs or tool dependencies
- **[b] Dependencies:** None beyond knowing the 6 patterns (self-contained decision table)
- **[c] Value:** 5/5 — bridges the gap between "I know dynamic workflows exist" and "I know which shape to use and how to prompt it." The existing `dynamic-workflow-orchestration` skill covers invocation mechanics but not pattern selection.
- **[d] Why now or never:** The masterclass framing of exactly 6 named patterns is fresh and well-structured; capturing it now while the taxonomy is clear prevents the patterns from blurring together as models evolve. Pairs with the already-present `dynamic-workflow-orchestration` and `workflow-fit-scorer` skills.

**Status:** Built — `skills/dynamic-workflow-pattern-selector/`

---

### 2. Pattern-specific prompt library (reference artifact, not a skill)

A static markdown file at `data/references/dynamic-workflow-prompt-library.md` collecting one battle-tested prompt template per pattern (and one per common 2-pattern stack). Not a skill — a reference document that feeds into pattern-selector and other agents.

- **[a] Effort:** S — write once; extend as new use cases are validated
- **[b] Dependencies:** None. Could be co-located with `dynamic-workflow-pattern-selector/` as a supplementary file.
- **[c] Value:** 3/5 — extends the skill's utility but is not independently valuable without the selector
- **[d] Why now or never:** The video provides ready-made prompt examples for each pattern; transcribing them as a reference library costs nothing now and saves re-derivation later.

---

### 3. Self-preference bias detection hook (PreToolUse on workflow prompts)

A Claude Code hook that detects when a workflow prompt asks one agent to both generate and evaluate the same output (violating the "generator and judge must be different agents" rule) and warns before execution.

- **[a] Effort:** M — regex-based heuristic on workflow prompt text; tricky to catch all cases without false positives
- **[b] Dependencies:** `~/.claude/hooks/` PreToolUse infrastructure; no new tools
- **[c] Value:** 3/5 — prevents a subtle but real workflow quality failure. The generate-and-filter pattern is the most likely site for this mistake.
- **[d] Why now or never:** Low adoption risk — needs validation that the hook's regex is precise enough before wiring it in. Defer to the 14-day window.

---

## Notes on Context Window Failure Modes Covered

Mark explicitly names three failure modes that dynamic workflows address. These may be worth encoding in an existing audit skill:

1. **Agent laziness** — given 15 tasks, completes only 7. Fix: decompose into per-agent tasks with explicit completion criteria.
2. **Self-preference bias** — a single session rates its own output favorably. Fix: adversarial verification by separate agents.
3. **Goal drift** — original intent degrades through auto-compaction over a long session. Fix: fresh context windows per subtask anchor each agent to the original goal.

---

## Source update

`~/projects/skill-forge/data/state/mark-kashef.last` updated to `2026-06-03T00:00:00Z`.
