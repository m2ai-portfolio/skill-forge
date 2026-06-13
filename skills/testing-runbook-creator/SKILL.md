---
name: testing-runbook-creator
description: Generates a repo-local runbook entry for each QA pass, capturing safe-vs-destructive context, seed data requirements, verify commands, and the exact state needed to reproduce the test — so QA knowledge accumulates in the repo instead of disappearing after each session.
---

# Testing Runbook Creator

Every time a QA pass is performed, this skill writes a structured runbook entry to the current repository. The goal is a bankable, growing record of how to test each area: what state is required, which commands are safe, which are destructive, and how to verify the outcome independently of the agent that ran the test.

## Trigger

Use when the user says "create a testing runbook", "document this QA pass", "write runbook for [feature]", "how do I re-run this test", "capture what we just tested", or after a debugging or verification session where test knowledge was gained.

## Phase 1: Ingest Context

Collect the following, prompting the user only for what cannot be inferred from the current session:

1. **Feature or area under test** -- what was being tested
2. **Entry point** -- the URL, command, or function that starts the test
3. **Required state** -- database fixtures, env vars, feature flags, seeded data, external services
4. **Test steps** -- the sequence of actions performed
5. **Verify commands** -- the exact commands or checks that confirm success (not "it looked right" -- a command or observable artifact)
6. **Safe vs. destructive** -- which steps are idempotent, which create/modify/delete persistent state
7. **Known flakiness** -- timing issues, order dependencies, environment-specific behavior observed

If any of items 5 or 6 are absent, ask explicitly before writing the runbook. A runbook without verify commands is not a runbook.

## Phase 2: Write Runbook Entry

Create or append to `.claude/testing-runbook.md` in the root of the current repository. Each entry uses this structure:

```markdown
## [Feature / Area] — [YYYY-MM-DD]

**Entry point:** [URL, command, or function]
**Status:** [passing | failing | flaky | untested]

### Required State
- [ ] [Setup step: seed data, env var, feature flag, etc.]
- [ ] [Setup step]

### Test Steps
1. [Action]
2. [Action]
3. [Action]

### Verify Commands
```bash
# [What this checks]
[command that exits 0 on success]

# [What this checks]
[command or observable]
```

### Safe vs. Destructive
- **Safe (idempotent):** [steps that can be run repeatedly without side effects]
- **Destructive:** [steps that create, modify, or delete persistent state — list explicitly]

### Seed Data
[SQL, fixture file path, or CLI command needed to create required state. "None required" if applicable.]

### Known Flakiness
[Timing issues, order dependencies, environment-specific behavior. "None observed" if clean.]

### Notes
[Anything that would surprise a future runner.]
```

If `.claude/testing-runbook.md` does not exist, create it with a header:

```markdown
# Testing Runbook

Accumulated QA knowledge for this repository. Each entry documents how to reproduce a test pass, including required state, verify commands, and safe/destructive boundaries.

Last updated: [date]
```

Update the "Last updated" line on every append.

## Phase 3: Confirm and Deliver

Show the user the entry before writing. Ask: "Does this capture the test accurately? Anything missing from required state or verify steps?"

Apply any corrections, then write the file.

Confirm write with: `Runbook entry added to .claude/testing-runbook.md — [entry title].`

## Global vs. Repo-Local Boundary

- **Global skills** (like this one) carry the process: how to structure a runbook, what to capture, what counts as a verify command.
- **Repo-local runbooks** carry the specifics: the selectors, the test accounts, the seed commands that only work in this repo's context.

Never put repo-specific values (URLs, account credentials, database names) into global skill files. They belong in the local `.claude/testing-runbook.md`.

## Notes

- A runbook entry without verify commands is incomplete. "It looked right" is not a verify command.
- Destructive steps should be listed explicitly even if they seem obvious -- the purpose is to prevent accidental re-runs in production or shared environments.
- The `.claude/` directory is a natural home for repo-local QA knowledge alongside `CLAUDE.md` and other repo guidance files.
- This skill pairs naturally with a browser automation QA skill: the automation generates evidence artifacts; this skill documents how to reproduce and extend the test suite.

## Source

Extracted from Nate Kadlac newsletter (2026-06-12), idea 22 — Testing Runbook Creator: "Every QA pass leaves a repo-local runbook entry (safe vs destructive, seed data, verify commands)."
