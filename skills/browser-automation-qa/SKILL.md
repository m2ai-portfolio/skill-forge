---
name: browser-automation-qa
description: Runs a Playwright-powered QA pass against a web page or user flow, capturing Core Web Vitals, console errors, network failures, device emulation screenshots, and a structured evidence report — so QA produces artifacts, not just assertions.
---

# Browser Automation QA

Executes a structured browser QA pass using Playwright MCP. Every run produces verifiable evidence: screenshots, console output, network log, and a metrics summary. The goal is QA that leaves proof, not just a thumbs-up from the agent.

## Trigger

Use when the user says "run browser QA", "playwright check", "verify this page", "test [URL] in mobile", "check for console errors on [page]", "does [feature] work on [device]", or after shipping a UI change and wanting automated verification.

## Prerequisites

Playwright MCP must be connected in the current Claude Code session. If `mcp__playwright__browser_navigate` is not available, report this and stop -- do not attempt to simulate browser behavior without it.

## Phase 1: Define Scope

Collect from the user or infer from context:

1. **Target URL** -- the page or flow to test
2. **Test scenario** -- what user action or flow to exercise (default: page load and visual check)
3. **Devices** -- which viewports to test (default: desktop 1280x720 + mobile 375x667)
4. **Acceptance criteria** -- what "passing" looks like (default: no console errors, no failed network requests, page renders within 3s)

If no URL is provided, ask once. If URL is provided but scenario is absent, default to "page load and visual check."

## Phase 2: Execute

For each device in scope:

### 2a. Navigate and Capture Initial State
- Navigate to the target URL
- Take a full-page screenshot immediately after load
- Capture the browser snapshot (accessibility tree)

### 2b. Run the Scenario
Execute the test scenario step by step. For each significant step:
- Take a screenshot before and after
- Note any visible errors or unexpected state

### 2c. Collect Evidence
After the scenario completes, collect:
- **Console messages** -- filter for errors and warnings, log counts by level
- **Network requests** -- flag any 4xx/5xx responses, slow requests (>2s), and blocked resources
- **Performance** -- record load timing if available via `browser_evaluate` (window.performance.timing)

### 2d. Repeat for Each Device
Run the same scenario on each viewport. Take at minimum one screenshot per device showing the page in its rendered state.

## Phase 3: Assess

Score the run against the acceptance criteria:

| Check | Result | Detail |
|-------|--------|--------|
| Page renders | Pass / Fail | HTTP status, any render-blocking error |
| Console errors | Pass / Fail | Count of console errors (warnings: note but don't fail) |
| Network failures | Pass / Fail | Any 4xx/5xx or blocked requests |
| Mobile layout | Pass / Fail | Visual inspection of mobile screenshot |
| Performance | Pass / Info | Load time vs. 3s threshold |

Overall status: **Pass** (all checks pass) / **Fail** (any check fails) / **Warning** (no failures, but items worth addressing).

## Phase 4: Report

Produce a structured QA evidence report:

```markdown
# Browser QA Report — [URL]
**Date:** [date]
**Scenario:** [scenario description]
**Overall:** [PASS / FAIL / WARNING]

## Evidence

### Desktop (1280x720)
[Screenshot reference or description]

### Mobile (375x667)
[Screenshot reference or description]

## Checks

| Check | Result | Detail |
|-------|--------|--------|
| Page renders | [result] | [detail] |
| Console errors | [result] | [count and summary] |
| Network failures | [result] | [list of failures if any] |
| Mobile layout | [result] | [observation] |
| Performance | [result] | [load time] |

## Console Output
**Errors ([n]):**
- [message]

**Warnings ([n]):**
- [message, or "None"]

## Network Issues
- [failed request URL + status, or "None"]

## Notes
[Any observations that didn't fit a check, flakiness, suggestions]
```

Deliver the report in the conversation. If the user wants to save it, write to `./qa-report-[slug]-[YYYY-MM-DD].md`.

## Notes

- Evidence-first is the point. An agent that says "it looks fine" without screenshots or console output has not run QA -- it has run theater.
- Console warnings do not fail the run but should be listed. Errors always fail.
- Network requests with 3xx redirects are informational, not failures.
- This skill is a natural input to a testing runbook: the runbook records how to reproduce the test; this skill generates the evidence that the test ran.
- If Playwright MCP is unavailable, do not attempt to simulate this pass via static analysis or inference. Report the missing dependency clearly.

## Source

Extracted from Nate Kadlac newsletter (2026-06-12), idea 24 — Browser Automation QA: "Core Web Vitals, console/network capture, device emulation, screenshots+metrics as evidence."
