---
name: tufte-token-charts
description: Visualize LLM token-burn data as Tufte-style minimal charts (log y-scale, moving average, per-source breakdown) with five decision rules for reading the pattern, turning raw usage into delegation signals. Use when the user says "chart my token usage", "visualize my token burn", "show me my usage over time", or after running token-burn-auditor and wanting to explore the numbers visually over a date range.
---

# Tufte Token Charts

Applies Tufte-style data visualization to token burn data from Claude Code and other LLM tools. Produces compact, information-dense charts that reveal patterns invisible in raw numbers: which sessions burn the most, when burn correlates with useful output vs. waste, and where to focus reduction effort.

## Trigger

Use when the user says "chart my token usage", "visualize my token burn", "show me my usage over time", "I want to see my token patterns", or after running `token-burn-auditor` and wanting to explore the numbers visually over a date range.

## Prerequisite Check

Before starting, confirm:
- [ ] Token usage data is available (JSON, CSV, or markdown table)
- [ ] Node.js / npx available if generating static HTML (`node --version`)
- [ ] Output format decided: terminal sparkline, static HTML file, or markdown table

If no historical data exists yet, collect a snapshot from the audit first, then return to this skill for future trend runs.

## Phase 1 — Prepare Data

Acceptable input formats:

1. **Audit snapshot** — structured table from a token audit (copy/paste into context)
2. **Tool usage export** — CSV from account/billing settings (Claude.ai, OpenAI, Codex)
3. **API logs** — JSON with `input_tokens`, `output_tokens`, `timestamp`, `model` fields
4. **Manual entry** — ask the user for session totals if no logs exist

Normalize each record to this schema before charting:

```json
{
  "date": "YYYY-MM-DD",
  "tool": "claude-code",
  "input_tokens": 45000,
  "output_tokens": 12000,
  "model": "claude-sonnet-4-6",
  "fidelity": "exact"
}
```

Tag each record's fidelity:
- `exact` — came directly from API billing or platform export
- `measured` — exported from tool UI, may be rounded or bucketed
- `estimated` — derived from session time, word count, or other proxy

Report the fidelity mix in the final output — a chart built on estimates is read differently than one built on exact API logs.

## Phase 2 — Apply Tufte Principles

Core rules for token data charts:

| Rule | Why it matters for token data |
|------|-------------------------------|
| Log y-scale | Token counts are heavy-tailed — a few sessions dwarf the rest. Linear scale compresses all the low-burn days into a flat baseline. |
| Maximize data-ink ratio | No grid lines, no chart borders, no decorative markers. Pixels not carrying data should be white. |
| Label outliers directly | Annotate the top 3 outlier sessions inline (task label if known), not in a legend that requires eye travel. |
| Small multiples | One panel per tool or model, identical scales — differences read at a glance without mental math. |

**Terminal chart (ASCII sparkline):**
```bash
# Install spark (sparkline CLI) once:
#   npm install -g @littleBobbyTables/spark  (or any sparkline CLI)
# Feed daily totals, one value per day:
echo "45000 23000 67000 12000 89000 34000 78000" | spark
```

**Static HTML layout (data-dense targets):**
- X-axis: dates (30 days, unlabeled except month boundaries)
- Y-axis: total tokens on log₁₀ scale
- Series: one line per tool, distinct color
- Overlay: 7-day moving average as a lighter line
- Annotations: top-3 outlier sessions labeled directly on chart

The HTML file can be opened locally — no server needed.

## Phase 3 — Read the Chart (Five Decision Rules)

Once the chart is rendered, apply these heuristics in order:

| Pattern | Diagnosis | Action |
|---------|-----------|--------|
| High burn + accepted output | Productive session — candidate for encoding as a recurring skill or automation | Encode the workflow |
| High burn + weak / discarded output | Inefficient prompting or wrong tool for the task | Redesign prompt or route to a cheaper model |
| Low burn + visible manual work | Imagination gap — this task could be delegated but wasn't | Write a delegation spec or trigger a skill |
| Model split skewed | Routing is not matching task types to model tiers | Review model routing rules |
| Repeated correction spikes | Known failure mode surfacing repeatedly | Encode the guard as a hook, validator, or pre-check |

These five rules work on any chart resolution — daily, weekly, or per-session.

## Phase 4 — Output

Produce one of:
- **Terminal summary** — ASCII sparkline + top-5 session table
- **Static HTML file** — `./token-chart.html` (open in browser, no server)
- **Markdown table** — paste-ready for a daily note or session log

Always include a summary block:

```
Date range:    YYYY-MM-DD to YYYY-MM-DD
Total tokens:  N
Average/day:   N
Peak session:  YYYY-MM-DD (N tokens) — [task label if known]
Fidelity mix:  X% exact / Y% measured / Z% estimated
```

If fidelity is less than 80% exact, note it as a caveat on any delegation decisions made from the chart.

## Source Attribution

Technique derived from Nate's Newsletter (2026-06-05): "You can't trust one token number across your tools. Here's the guide to a dashboard that keeps Codex, Claude, and …" — Tufte-style charting applied to multi-tool token burn, log y-scale for heavy-tailed distribution, fidelity lane separation, and the five chart-reading heuristics. Open-source MIT charting skill (238★) referenced as an implementation vehicle in the original article.
