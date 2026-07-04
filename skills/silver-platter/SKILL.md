---
name: silver-platter
description: Map all available data sources into a structured three-layer context blueprint (Pantry, Prep, Plate) so an agent session loads exactly the right context at the right fidelity. Use when onboarding a project into an agentic workflow, debugging context-window overload, or auditing what an agent actually has access to. Trigger phrases: "silver platter", "data map", "map my context", "pantry prep plate", "context blueprint", "map my data sources for agents".
---

# Silver Platter — Context Data Mapping

Produce a structured HTML or markdown data map that classifies every available data source into three layers, so agents load the right context at the right fidelity instead of dumping raw data into the context window.

## Layers

| Layer | Name | What Goes Here |
|-------|------|----------------|
| 1 | **Pantry** | Raw data sources: CRM records, email threads, files, databases, API endpoints — anything accessible but not yet processed |
| 2 | **Prep** | Summarized / compressed versions: summary tables, extracted fields, chunked transcripts, deduped contact lists |
| 3 | **Plate** | Agent-ready structured context: the exact keys, schemas, or snippets the agent will inject into its context window for this task |

## Trigger

Use when the user says "silver platter", "data map", "map my context", "pantry prep plate", "context blueprint", "agentic OS data map", "what context does my agent have", or when you observe an agent session failing due to context overload or missing structured data.

## Phase 1: Discovery

Ask or infer:
1. What is the agent's job? (single task, recurring workflow, or always-on role)
2. What systems does it have access to? (file system, APIs, databases, calendars, email, CRM, product analytics, code repos)
3. What output does it produce? (structured data, prose, code, decisions, messages)

## Phase 2: Pantry Inventory

List every raw source by type:

```
SOURCE            | TYPE       | ACCESS METHOD  | REFRESH RATE
------------------|------------|----------------|-------------
<name>            | <type>     | <method>       | <rate>
```

Types: `file`, `api`, `database`, `email`, `calendar`, `crm`, `repo`, `docs`, `feed`.

## Phase 3: Prep Layer

For each Pantry source that would overflow the context window as-is, define a Prep transform:

- Long documents: extractive summary with key fields only
- CRM records: flat summary table (name, status, last action, next step)
- Email threads: chronological bullet summary
- Database: materialized view or pre-computed aggregates
- Repo: README + structure tree + recent commits (not full diffs)

Mark each source as either `fits-raw` (safe to pass directly) or `needs-prep` (must be compressed first).

## Phase 4: Plate Assembly

Produce the final agent context spec: for each task the agent handles, list exactly which Prep outputs get injected and in what order. This is the plate — what the agent actually sees.

Output format:

```
TASK              | CONTEXT INJECTED           | APPROX TOKENS
------------------|----------------------------|---------------
<task name>       | <source 1>, <source 2>     | <estimate>
```

## Phase 5: Data Map Output

Render the complete map as structured markdown or HTML with:
- A Pantry table (all raw sources)
- A Prep table (transforms needed)
- A Plate table (per-task context specs)
- A "gaps" section: sources referenced in the task scope that have no Pantry entry yet

## Verification

- Every data source the agent needs has a Pantry entry
- Every `needs-prep` source has a defined transform
- Every Plate spec has a token estimate under the model's context budget
- No hardcoded paths or credentials in the map

## Source Attribution

Technique: Silver Platter data-mapping method and Pantry/Prep/Plate framework
Source: Mark Kashef YouTube channel, "Build Your Agentic OS Better Than The 99%"
URL: https://www.youtube.com/watch?v=-WCNwxz3uoM
Published: 2026-05-09
