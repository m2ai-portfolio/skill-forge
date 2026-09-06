---
name: computer-use-to-cli-distiller
description: "Turn a one-off computer-use / browser-automation session into a reusable, scriptable CLI or workflow for a web platform or app that has no API, connector, or MCP. An agent with computer-use ability performs the target task manually once (searching a site, filling a form, comparing options), then reverse-engineers what it did into a small parameterized command-line tool that any future agent or lower-tier model can call directly, skipping the browser entirely on repeat runs. Use when you keep asking an agent to manually click through the same site or app, need repeated programmatic access to a UI-only surface, or want to distill a browser workflow into a script instead of redoing the walkthrough every time."
---

# computer-use-to-cli-distiller

## Trigger

Use when someone says: "I keep asking an agent to manually click through the same site/app", "there's no API for this platform but I need to check it on a schedule", "distill this browser workflow into a script", "build a CLI for a site that doesn't have one", or a computer-use session just finished a UI task that's likely to repeat.

## Prerequisites

- An agent with genuine computer-use / browser-automation capability (drives a real browser or app window, not a static HTTP fetch), with permission to control that browser/app session.
- A target workflow that is deterministic enough to encode as a script: stable selectors/DOM structure or a consistent app UI, not one gated behind a rotating CAPTCHA or a layout that changes on every visit.
- A follow-up coding-capable step: after performing the task once, the agent needs to write, test, and save a script, not just describe what it did.
- A way to re-run the resulting script later (a local shell, a scheduled task runner, or another agent invoking it directly) — otherwise there is nothing to distill it into.

## Complexity

Intermediate. The manual pass itself is easy; the reverse-engineering pass (turning clicks and requests into a parameterized script) is the part that takes iteration.

## Phase 1: Perform the task once, live

1. Have the computer-use agent execute the target task end-to-end through the real UI (search, filter, form submit, whatever the workflow is). Instruct it explicitly to use its own internal browser/session rather than hijacking an already-logged-in browser, so the resulting session and any captured requests stay isolated and reproducible.
2. Have it narrate or log what it did as it goes: which fields it filled, which pages or endpoints it hit, what the responses looked like. This log is the raw material for Phase 2.

## Phase 2: Reverse-engineer into a script

1. Ask the agent to inspect its own trace (network requests, page structure, or its own step-by-step actions) and draft a small command-line script that reproduces the same result without a browser where possible (hitting the same backend calls the UI made), or, where the platform has no scrapeable backend at all, a script that re-drives headless browser automation but is now parameterized instead of one-off.
2. Parameterize the script for the dimensions that will vary later (dates, locations, search terms, counts) instead of hardcoding the values from the first example.
3. Test the script standalone, outside the original computer-use session, to confirm it reproduces the same result on its own.

## Phase 3: Broaden and hand off

1. Ask the agent to test edge cases and alternate shapes of the same workflow (different combinations, multi-step variants) so the script is not overfit to the first example it happened to see.
2. Verify the distilled script is actually faster than repeating the manual computer-use pass by timing both and comparing. If it is not meaningfully faster or more reliable, the distillation did not pay for itself and the manual pass may still be the right tool.
3. Hand the script to whatever will call it going forward: a lower-tier model, a scheduled job, or another agent, so the expensive computer-use pass only has to happen once per workflow shape, not once per invocation.

## Verification

- The distilled script runs standalone (no computer-use agent involved) and reproduces the original manual pass's result, confirmed on at least one re-run.
- Re-running the script end-to-end is measurably faster than repeating the full computer-use walkthrough — a direct time comparison, not an assumption.
- The script accepts the parameters that will actually vary in real use, not just the values from the first example.
- If the platform later changes its UI or backend and the script breaks, that is expected: this technique produces a fast but brittle tool tied to the platform's current shape, not a stable integration.

## Source

YouTube video transcript, Mark Kashef channel, published 2026-09-05: "GPT-6 Astra's Computer Use Is Ridiculously Good." Technique: use one computer-use pass through a UI-only platform to reverse-engineer a reusable, parameterized command-line tool, so future runs skip the browser and any agent or model tier can call it directly.
