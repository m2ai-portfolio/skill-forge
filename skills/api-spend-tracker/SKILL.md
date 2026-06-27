---
name: api-spend-tracker
description: Build a local cross-provider API spend tracking dashboard — logs actual dollar costs from Anthropic, OpenAI, and Google API usage into SQLite and renders a lightweight dashboard showing spend by provider, model, day, and project. Trigger: "where's my API money going", "track my API costs", "I can't see my spend", "build a spend dashboard".
---

# API Spend Tracker

Guides building a local dashboard that tracks actual API dollar spend across providers. Distinct from context-window auditing (token overhead in prompts) — this tracks invoice-level cost: how much did each model, project, and day actually cost you?

## When to Use

Trigger when:
- You're running multi-provider workflows (Anthropic + OpenAI + Google) and can't see total spend at a glance
- You suspect one workflow or agent is generating disproportionate costs
- You want to set a weekly/monthly spend alert before a bill surprises you
- You're comparing model costs across providers for the same task class

Do NOT use for:
- Auditing context window overhead (static skill/CLAUDE.md bloat) — use `token-burn-auditor` for that
- Projecting the cost of a workflow before running it — use `agent-cost-model` for that

## Architecture

Three components:

```
API calls → Cost logger (intercept layer) → SQLite DB → Dashboard (local HTTP)
```

1. **Cost logger**: a thin wrapper or post-call hook that records provider, model, input tokens, output tokens, timestamp, and computed cost
2. **SQLite DB**: persistent local store at `./spend.db` (or `$SPEND_DB_PATH`)
3. **Dashboard**: a Node.js/Express server that queries the DB and renders charts

## Phase 1: Schema

Create `spend.db` with a single table:

```sql
CREATE TABLE IF NOT EXISTS api_calls (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  ts           TEXT    NOT NULL,          -- ISO8601
  provider     TEXT    NOT NULL,          -- anthropic | openai | google
  model        TEXT    NOT NULL,          -- e.g. claude-sonnet-4-6, gpt-4o
  project      TEXT,                      -- optional tag for the calling workflow
  input_tokens INTEGER NOT NULL,
  output_tokens INTEGER NOT NULL,
  cache_read_tokens INTEGER DEFAULT 0,
  cache_write_tokens INTEGER DEFAULT 0,
  cost_usd     REAL    NOT NULL           -- computed at write time
);

CREATE INDEX IF NOT EXISTS idx_ts       ON api_calls(ts);
CREATE INDEX IF NOT EXISTS idx_provider ON api_calls(provider);
CREATE INDEX IF NOT EXISTS idx_project  ON api_calls(project);
```

## Phase 2: Cost Logger

### Option A — Wrapper function (TypeScript)

```typescript
import Database from 'better-sqlite3';

const PRICING: Record<string, { input: number; output: number; cacheRead?: number; cacheWrite?: number }> = {
  // prices per 1M tokens in USD — update from provider pricing pages
  'claude-sonnet-4-6':  { input: 3.00,  output: 15.00, cacheRead: 0.30,  cacheWrite: 3.75 },
  'claude-haiku-4-5':   { input: 0.80,  output: 4.00,  cacheRead: 0.08,  cacheWrite: 1.00 },
  'gpt-4o':             { input: 2.50,  output: 10.00 },
  'gemini-2.0-flash':   { input: 0.075, output: 0.30  },
};

export function logCall(opts: {
  provider: string; model: string; project?: string;
  inputTokens: number; outputTokens: number;
  cacheReadTokens?: number; cacheWriteTokens?: number;
}) {
  const p = PRICING[opts.model];
  if (!p) console.warn(`Unknown model pricing: ${opts.model}`);
  const costUsd = p ? (
    opts.inputTokens / 1e6 * p.input +
    opts.outputTokens / 1e6 * p.output +
    (opts.cacheReadTokens ?? 0) / 1e6 * (p.cacheRead ?? 0) +
    (opts.cacheWriteTokens ?? 0) / 1e6 * (p.cacheWrite ?? 0)
  ) : 0;

  const db = new Database(process.env.SPEND_DB_PATH ?? './spend.db');
  db.prepare(`INSERT INTO api_calls
    (ts, provider, model, project, input_tokens, output_tokens,
     cache_read_tokens, cache_write_tokens, cost_usd)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`
  ).run(
    new Date().toISOString(), opts.provider, opts.model, opts.project ?? null,
    opts.inputTokens, opts.outputTokens,
    opts.cacheReadTokens ?? 0, opts.cacheWriteTokens ?? 0, costUsd
  );
}
```

### Option B — Parse provider usage export

All three major providers export usage CSVs or JSON from their dashboards:
- Anthropic: Settings → Usage → Export
- OpenAI: Platform → Usage → Export CSV
- Google: Cloud Console → BigQuery billing export

Import historical data:

```typescript
// example: import Anthropic CSV export
import { parse } from 'csv-parse/sync';
import { readFileSync } from 'fs';

const rows = parse(readFileSync('./anthropic-usage.csv'), { columns: true });
for (const row of rows) {
  logCall({
    provider: 'anthropic',
    model: row.model,
    project: row.workspace ?? undefined,
    inputTokens: parseInt(row.input_tokens),
    outputTokens: parseInt(row.output_tokens),
  });
}
```

## Phase 3: Dashboard

Minimal Express server with three views:

```typescript
import express from 'express';
import Database from 'better-sqlite3';

const app = express();
const db = new Database(process.env.SPEND_DB_PATH ?? './spend.db');

// Summary: total spend by provider this month
app.get('/api/summary', (req, res) => {
  const rows = db.prepare(`
    SELECT provider, SUM(cost_usd) AS total
    FROM api_calls
    WHERE ts >= date('now', 'start of month')
    GROUP BY provider
    ORDER BY total DESC
  `).all();
  res.json(rows);
});

// Daily spend for the last 30 days
app.get('/api/daily', (req, res) => {
  const rows = db.prepare(`
    SELECT date(ts) AS day, provider, SUM(cost_usd) AS total
    FROM api_calls
    WHERE ts >= date('now', '-30 days')
    GROUP BY day, provider
    ORDER BY day
  `).all();
  res.json(rows);
});

// Top projects by spend this month
app.get('/api/projects', (req, res) => {
  const rows = db.prepare(`
    SELECT project, SUM(cost_usd) AS total
    FROM api_calls
    WHERE ts >= date('now', 'start of month')
    GROUP BY project
    ORDER BY total DESC
    LIMIT 20
  `).all();
  res.json(rows);
});

app.use(express.static('public'));
app.listen(process.env.PORT ?? 3333);
```

Add a static `public/index.html` that fetches these endpoints and renders charts with Chart.js (CDN-linked, no build step required).

## Phase 4: Alerting

Add a daily cron or scheduled check:

```typescript
const ALERT_THRESHOLD_USD = parseFloat(process.env.SPEND_ALERT_USD ?? '10');

const todaySpend = db.prepare(`
  SELECT SUM(cost_usd) AS total FROM api_calls WHERE date(ts) = date('now')
`).get() as { total: number };

if (todaySpend.total > ALERT_THRESHOLD_USD) {
  console.warn(`SPEND ALERT: $${todaySpend.total.toFixed(2)} today (threshold: $${ALERT_THRESHOLD_USD})`);
  // add Slack/email notification here
}
```

## Phase 5: Verification

The tracker is working correctly if:
- `SELECT SUM(cost_usd) FROM api_calls` within 10% of your provider dashboard total for the same period
- Daily chart shows cost spikes on days you ran heavy workflows
- Provider breakdown matches your subjective sense of which model you use most

If the total diverges significantly from provider invoices, the most common causes are:
1. Pricing table out of date — check and update `PRICING` against current provider pages
2. Cache tokens not being logged — confirm `cacheReadTokens` and `cacheWriteTokens` are passed
3. Batch API calls excluded — Batch API has 50% discount; add a `is_batch` flag if relevant

## Source Attribution

Technique: Cross-Provider API Spend Tracking Dashboard
Source: Nate's Newsletter (natesnewsletter@substack.com)
URL: https://natesnewsletter.substack.com/p/why-im-moving-this-substack-from
Published: 2026-06-01
Subject: "Why I'm moving this Substack from daily coverage to deeper weekly work"
