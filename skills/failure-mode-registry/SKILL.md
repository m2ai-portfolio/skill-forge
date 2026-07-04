---
name: failure-mode-registry
description: Create or update a per-project FAILURE_MODES.md registry that captures recurring agent mistakes, then surface matching failure modes at session start so agents do not repeat known errors. Use when a project is starting, after a postmortem, or after the same mistake happens twice. Trigger phrases: "failure mode registry", "log failure mode", "failure modes file", "project failure modes", "add to failure modes", "session failure modes".
---

# Failure Mode Registry

Every project accumulates unwritten rules about mistakes agents must not repeat -- but those rules get re-explained per thread, silently forgotten, or never written down. This skill externalizes that tribal knowledge into a versioned registry that agents read at session start.

## Trigger

Use when the user says "failure mode registry", "log failure mode", "failure modes file", "project failure modes", "add to failure modes", "failure-mode-registry", "what are my project failure modes", or after any session where the same mistake occurred for the second time.

## Phase 1: Registry Check

Look for `FAILURE_MODES.md` in the current project root.
- If found: read it and proceed to Phase 2A (log) or Phase 2B (surface), depending on user intent.
- If not found: proceed to Phase 3 (bootstrap).

## Phase 2A: Log a New Failure Mode

When the user reports a mistake or postmortem finding, append an entry to `FAILURE_MODES.md`:

```markdown
### FM-<N>: <short title>

- **Trigger pattern**: the specific situation that provokes this failure
- **What goes wrong**: exact symptom (not vague -- what did the agent do or not do)
- **Why it happens**: root cause if known
- **Prevention**: the rule the agent must apply instead
- **Date logged**: YYYY-MM-DD
- **Times seen**: 1
```

Increment `<N>` from the highest existing ID + 1. If the same failure has been seen before, update the existing entry and increment **Times seen**.

## Phase 2B: Surface Failure Modes

When starting a new session on a project that has `FAILURE_MODES.md`:

1. Read the file.
2. Identify entries whose trigger pattern matches the current task or domain.
3. Present matching entries as a brief watch list before proceeding:

```
FAILURE MODE WATCH LIST (project: <name>)
FM-1: <title> -- <one-line prevention rule>
FM-3: <title> -- <one-line prevention rule>
```

If no entries match the current task, say nothing -- do not load the entire registry unprompted.

## Phase 3: Bootstrap

When no `FAILURE_MODES.md` exists, create it:

```markdown
# Failure Mode Registry -- <project name>

Entries are added after postmortems or when the same mistake occurs twice.
Each entry has a trigger pattern so agents can surface relevant modes at session start.

<!-- entries below -->
```

Then ask: "What is the first failure mode to log? Describe the situation and what went wrong."

## Phase 4: SessionStart Hook (Optional)

Suggest adding a `SessionStart` hook so the registry loads automatically when the project directory is opened. This eliminates the need to invoke the skill manually every session.

Minimal hook configuration (add to the project's agent config or settings):

```json
{
  "hooks": {
    "SessionStart": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "test -f FAILURE_MODES.md && echo '--- Failure Mode Registry ---' && cat FAILURE_MODES.md || true"
      }]
    }]
  }
}
```

Only suggest this if the project already has a populated registry with 3+ entries -- the overhead is not worth it for an empty file.

## Verification

- Each entry has a unique FM-N ID
- Each entry has a trigger pattern specific enough to match (not "any coding task")
- The **Prevention** field contains an actionable rule, not a description of the problem
- The file lives in the project root, not a user-specific path
- No credentials, secrets, or team-internal names in the registry

## Source Attribution

Technique: Per-project failure mode registry pattern
Source: Nate's Newsletter (natesnewsletter.substack.com)
Post: "Codex plugins matter because the bottleneck moved"
Published: 2026-05-09
