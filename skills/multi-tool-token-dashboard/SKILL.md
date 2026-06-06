---
name: multi-tool-token-dashboard
description: Build a cross-tool AI token usage dashboard that ingests usage data from multiple providers (Claude, Codex, ChatGPT, etc.) into fidelity lanes (exact/measured/estimated), produces a static site with contribution-grid charts and a 30-day moving average, and drives delegation decisions rather than vanity metrics.
---

# Multi-Tool Token Dashboard

Turns scattered, provider-specific token reports into a single source of truth. Separates data by fidelity (exact API counts vs. measured via logs vs. estimated from session patterns) so the chart drives decisions: high-burn + useful work means automate; high-burn + weak output means redesign the prompt.

## Trigger

Use when the user says "build a token dashboard", "track my AI costs across tools", "I want to see Codex and Claude usage together", "multi-tool token tracking", "token burn dashboard", or describes wanting to unify usage data from multiple AI providers.

## Phase 1: Inventory Sources

Ask the user which providers to include and how data is accessible:

| Provider | Typical source |
|---|---|
| Claude (Anthropic) | Usage dashboard CSV export or API `/usage` endpoint |
| Codex / OpenAI | Usage dashboard export or API `/dashboard/billing/usage` |
| ChatGPT | Manual log from conversation export or browser extension capture |
| OpenRouter | `/api/v1/usage` endpoint with API key |
| Other | Describe the available format |

For each source, ask:
- **Exact** -- API-reported token counts with timestamps? (highest fidelity)
- **Measured** -- log files or exports with counts but possible gaps?
- **Estimated** -- session-length heuristics, no hard numbers?

Assign each provider a fidelity tag. Never blend fidelity tiers in the same chart series.

## Phase 2: Data Pipeline Design

Design a nightly ingestion job:

1. **Fetch** -- one fetcher per provider (script or cron job); output normalized JSONL:
   ```
   {"date":"2026-06-05","provider":"claude","model":"sonnet","input_tokens":12400,"output_tokens":3200,"fidelity":"exact"}
   ```

2. **Aggregate** -- group by date + provider + fidelity; compute daily totals and costs.

3. **Write** -- append to a local SQLite or flat JSONL store. Keep raw rows for auditability; never overwrite.

4. **Export** -- generate `data.json` for the static site on each run.

Output a shell script or TypeScript/Node script for the user's stack. Default to Node.js + `better-sqlite3`.

## Phase 3: Dashboard Layout

Produce a self-contained HTML file (no external CDN dependencies) with these panels:

### Panel 1 -- Contribution Grid (GitHub-style)
52 weeks x 7 days grid. Cell color = log scale of daily token total. Color axis labeled with absolute values at three breakpoints (low / medium / high). Fidelity indicated by cell border style (solid = exact, dashed = estimated).

### Panel 2 -- 30-Day Rolling Average Line
Two series: input tokens and output tokens. Log y-scale so low-activity days remain visible. Annotation markers for model changes or pricing changes.

### Panel 3 -- Provider Split Bar
Stacked horizontal bar per day for the last 30 days. One color per provider. Direct labels on bars (no legend).

### Panel 4 -- Driver Analysis Table
Top 10 sessions or workflows by token spend for the trailing 30 days. Columns: workflow name, provider, tokens, cost estimate, outcome (useful / weak / unknown). The outcome column is user-editable so the chart can drive delegation decisions.

## Phase 4: Hosting

Deploy as a static site. Recommended targets (pick one):

- **GitHub Pages** -- `gh-pages` branch, push on each nightly run.
- **Vercel** -- connect repo, auto-deploys on push to main.
- **Local only** -- serve from `npx serve` on the build machine; no external hosting required.

Provide the CI/CD step (GitHub Actions or cron command) that regenerates `data.json` and pushes.

## Phase 5: Reading the Chart

After generating the dashboard, explain these heuristics for acting on it:

| Pattern | Signal | Action |
|---|---|---|
| High burn + accepted work | This workflow earns its tokens | Promote to a scheduled agent |
| High burn + repeated corrections | Prompt design is wrong | Redesign or add a verification step |
| Low burn + still doing manually | Imagination gap | Try delegating to an agent |
| Model split skewed to expensive tier | Routing could be optimized | Move classification/routing steps to a cheaper model |
| Repeated corrections in one context | Encode as a rule or skill | Write it down; stop paying for it every session |

## Notes

- Never blend fidelity tiers in a single chart series. A "total" line that mixes exact API counts with guesses is worse than no total line.
- Costs shown are estimates unless the provider gives cost directly. Always show the token count alongside the cost estimate so readers can verify.
- If a provider's API changes, the fetcher breaks silently. Add a staleness warning to the dashboard if the most recent data point is more than 48h old.

## Source

Derived from Nate's Newsletter (2026-06-05) -- "You can't trust one token number across your tools" -- multi-source ingestion + fidelity-lane pattern for token dashboards. Dashboard design informed by GitHub contribution grid pattern; fidelity-lane taxonomy originated in the newsletter.
