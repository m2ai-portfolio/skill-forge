---
name: newsletter-digester
description: Generalized scheduled intake pipeline for curated newsletters. Given a Substack URL or RSS feed, extracts, scores, and saves buildable ideas to a local intake folder. Parameterizable for any newsletter source and output path. Use when the user says "/newsletter-digester", "set up newsletter intake", "subscribe a newsletter to forge", "add newsletter source", "digest this newsletter", or wants to run scheduled idea extraction from a curated feed.
---

# Newsletter Digester

Turns any curated newsletter (Substack, RSS, email archive) into a structured idea intake stream. Fetches the latest issue, extracts buildable ideas, scores them by platform/complexity/relevance, and saves them to a local intake folder for downstream processing.

Designed to run on a schedule (e.g., daily cron) with zero manual intervention after setup.

## Trigger

Use when the user says "/newsletter-digester", "set up newsletter intake", "subscribe a newsletter to forge", "add newsletter source", "digest this newsletter", or provides a Substack/RSS URL and asks to extract ideas from it.

## Phase 1: Configuration

Collect the following parameters (ask if not provided):

| Parameter | Description | Default |
|-----------|-------------|---------|
| `feed_url` | Substack RSS URL or generic RSS/Atom feed URL | — (required) |
| `author_slug` | Short identifier for the author/newsletter (e.g., `nate`, `swyx`) | Inferred from domain |
| `output_dir` | Local directory to write intake files | `./intake/` |
| `relevance_context` | One paragraph describing what's relevant to the user's work | — (optional, improves scoring) |
| `lookback_days` | How far back to fetch if no prior state exists | `7` |
| `state_file` | Path to the last-check state file | `./data/last_check.txt` |

**Substack RSS URL pattern**: `https://{subdomain}.substack.com/feed`

If the user provides a Substack post URL instead of an RSS feed, derive the feed URL by replacing the post path with `/feed`.

## Phase 2: Fetch Latest Issue

1. Read `state_file` to get the last-processed date. If missing, use `today - lookback_days`.
2. Fetch the RSS feed. Parse entries newer than the last-processed date.
3. For each new entry, fetch the full post HTML (follow the entry `<link>` URL).
4. Convert HTML to markdown (strip nav, ads, footers — keep body text only).
5. If no new entries found, write "no new content" to output and exit cleanly.

**Fetch method**: standard HTTP GET with a descriptive User-Agent. No authentication required for public Substack feeds.

## Phase 3: Extract Buildable Ideas

For each fetched issue, scan the text for:

- Techniques, workflows, or frameworks described step-by-step
- Tool recommendations with use-case rationale
- Patterns that could be formalized into a repeatable process
- Explicit calls-to-action ("here's how to do X")
- Named concepts with a trigger condition ("when Y happens, do Z")

For each candidate idea, extract:
- **Title**: a short descriptive name (3–7 words)
- **Summary**: what the idea does (2–3 sentences)
- **Trigger pattern**: when would someone invoke this
- **Complexity**: `weekend-project` or `multi-sprint`
- **Platform**: `claude-code`, `cross-platform`, or `mcp`
- **Relevance**: `HIGH`, `MEDIUM`, or `LOW` (relative to `relevance_context` if provided; otherwise use general AI-tooling utility as the bar)

Discard ideas that are:
- Purely informational with no actionable technique
- Product announcements without implementation guidance
- Already covered by ideas from prior issues (deduplicate by concept)

## Phase 4: Write Intake File

Write a markdown file to `output_dir` named `{author_slug}-{YYYY-MM-DD}.md`.

**File format:**

```markdown
# {Author/Newsletter Name} Intake — {YYYY-MM-DD}

**Source**: {post_url}
**Title**: "{post_title}"

---

## TLDR

{2–3 sentence summary of the issue's main thesis}

---

## Extracted Ideas

### {N}. {Idea Title}

{Summary}

- **Platform**: {platform}
- **Complexity**: {complexity}
- **Relevance**: {relevance}

{Any specific implementation notes or caveats}

---

## Notes for dedup pass

- Likely overlaps to verify: {list any techniques that sound similar to known tools}
- Cleanest greenfield candidates: {list the LOW-overlap HIGH-relevance ideas}
```

## Phase 5: Update State

1. Write today's date to `state_file` (overwrite). This prevents re-processing the same issue.
2. Log: `Processed {N} ideas from {author_slug} issue dated {post_date}. Output: {output_dir}/{filename}`.

## Phase 6: Dedup Pass (Optional, if downstream pipeline is active)

If a skills directory path is provided (`skills_dir`), check each HIGH-relevance idea against existing skill names using fuzzy keyword matching. Flag likely overlaps in the intake file's "Notes" section. Do not block writing the intake file — flag only, let the human decide.

## Scheduling

To run on a schedule:
1. Wrap this skill in a cron-triggered agent task.
2. Confirm the output `intake/` folder is monitored by a downstream forge-scan process (or run manually).
3. Recommended cadence: daily at a fixed time, 30 minutes after the newsletter's typical send time.

## What This Does NOT Do

- Does not read paywalled content — public posts only.
- Does not ingest email directly — works from RSS or public web URLs.
- Does not create skills automatically — it populates an intake folder for human review.
- Does not deduplicate across authors — if two newsletters cover the same idea, both appear.

## Error Handling

| Condition | Behavior |
|-----------|----------|
| Feed URL unreachable | Log error, exit cleanly, do NOT update state file |
| No new issues since last check | Write brief log, exit cleanly, update state file |
| Issue has no extractable ideas | Write intake file with empty ideas section, note "no buildable ideas found" |
| State file missing | Treat as first run; fetch `lookback_days` of history |

## Source

Extracted from Nate B. Jones newsletter (2026-05-09):
"OpenAI made Codex smart enough that the bottleneck moved. Most people haven't noticed where it went."
https://natesnewsletter.substack.com/p/codex-plugins-bottleneck-moved

The intake pipeline pattern is the meta-level application of Nate's thesis: the bottleneck is workflow packaging, so the extraction of packaging candidates should itself be automated and recurring.
