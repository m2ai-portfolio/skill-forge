---
name: visual-qa-loop
description: Recursive build-inspect-fix loop that uses Claude-in-Chrome to visually verify UI output, catch rendering issues, and iterate until the result matches requirements. Use when building frontends, HTML, landing pages, or any visual artifact.
---

# Visual QA Loop

Runs a recursive quality assurance cycle: build the artifact, visually inspect it via Claude-in-Chrome, identify mismatches against requirements, fix, and repeat. Eliminates the manual step of "open browser, check, come back and tell Claude what's wrong."

## Trigger

Use when the user says "check how this looks", "visual QA", "does this render right", "inspect the UI", "test the frontend visually", or when building any visual artifact (HTML, landing page, dashboard, email template) that benefits from automated visual verification.

Also use proactively after generating frontend code, HTML pages, or UI components where visual correctness matters.

## Prerequisites

- Claude-in-Chrome MCP must be installed and enabled (`/config` > `claudeInChromeEnabled: true`)
- The artifact must be viewable in a browser (local server, HTML file, or deployed URL)
- Remember: use `10.0.0.46:<port>` for local servers, never `localhost`

## Phase 1: Build

Generate or modify the visual artifact based on the user's requirements. Capture the full list of requirements/specs as a checklist for verification.

Output the checklist:
```
## Visual Requirements
- [ ] Requirement 1
- [ ] Requirement 2
- [ ] ...
```

If the artifact needs a local server, spin one up and note the URL.

## Phase 2: Inspect

Use Claude-in-Chrome to navigate to the artifact URL and capture the current visual state.

Evaluate against each requirement in the checklist:
- **PASS** -- visually matches the requirement
- **FAIL** -- does not match, with specific description of what's wrong
- **PARTIAL** -- partially matches, describe what needs adjustment

```
## Inspection Results (Round N)
- [x] Requirement 1 -- PASS
- [ ] Requirement 2 -- FAIL: button text is cut off on mobile viewport
- [ ] Requirement 3 -- PARTIAL: colors match but spacing is off by ~8px
```

## Phase 3: Fix

For each FAIL or PARTIAL item:
1. Identify the root cause in the code
2. Apply the fix
3. Verify the fix doesn't break any previously PASSing items

Do NOT re-inspect manually in this phase. Just fix the code.

## Phase 4: Re-inspect

Return to Phase 2. Use Claude-in-Chrome again to verify all fixes.

Continue the loop until:
- All requirements are PASS, OR
- 3 rounds have completed (report remaining issues to the user)

## Phase 5: Report

```
## Visual QA Complete

**Rounds:** N
**Result:** ALL PASS | N/M requirements met

### Remaining Issues (if any)
- Issue description and suggested manual fix

### Files Modified
- path/to/file.ext -- what changed
```

## Verification

A good visual QA loop:
- Tests every stated requirement, not just "it looks fine"
- Catches issues a human would notice (alignment, overflow, color, responsive)
- Does not loop endlessly -- hard cap at 3 rounds, then escalate
- Reports clearly what passed and what still needs attention

## Source

Extracted from Mark Kashef video "Every Claude Code Secret Its Creator Just Revealed" (2026-03-31, JcY1LekT954) -- the "recursive visual inspection loop" technique using Claude-in-Chrome for self-review of built artifacts.
