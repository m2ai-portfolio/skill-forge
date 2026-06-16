# Mark Kashef — "Make ANY Model Think Like Fable in Minutes"

**Source:** https://www.youtube.com/watch?v=B95cu7seTm8
**Published:** 2026-06-14
**Intake date:** 2026-06-16

---

## TLDR

Mark teaches a technique for extracting the behavioral DNA of a superior model (Fable 5) from Claude Code JSONL session history, distilling it into a portable playbook file, and injecting that playbook into any other model (Opus, Codex, open-source) at session start. The core insight is that Claude Code session files tag every response with `message_model`, so you can filter by model, strip tool-result bloat, run a side-by-side behavioral comparison (tool cadence, read-to-edit ratio, planning turns), and distill only the elicitable behaviors into a short injectable file. For users with thin Fable history, open-source Fable session datasets on Hugging Face provide a substitute corpus.

---

## Buildable Ideas

### 1. `session-behavioral-playbook` — JSONL-to-behavioral-playbook pipeline

Build a skill that walks Claude Code session JSONL files, strips bloat (tool results, echoed file contents), filters by `message_model`, runs a behavioral stats pass (tool cadence, read/edit ratio, test rate), diffs two model corpora side-by-side, and distills elicitable behaviors into an injectable `~/.claude/playbooks/` file.

- **[a] Effort:** M -- script generation is mechanical; the behavioral stat definitions need to be explicit to get numbers rather than impressions; the injection options (hook vs. CLAUDE.md vs. manual) require a clear decision flow.
- **[b] Dependencies:** Python in shell for JSONL parsing; `~/.claude/projects/` access; optional Hugging Face community dataset for sparse-history fallback. No external APIs required.
- **[c] Value:** 4/5 -- directly actionable for anyone who had any Fable history; the Hugging Face fallback makes it viable even for users who had minimal access. Addresses a real gap: model behavioral gaps are often elicitable, but nobody has a systematic way to identify which gaps those are.
- **[d] Why now or never:** The Fable 5 outage created acute demand exactly when the technique was demonstrated. Capturing it now gives a durable reference that survives model churn -- the JSONL format and `message_model` tag are stable across Claude Code versions.

---

### 2. Community corpus ingestion adapter

A lightweight adapter that downloads a Hugging Face Fable session dataset and normalizes it to the same stripped-transcript format produced by the local JSONL parser, so both paths (personal history and community corpus) feed into the same behavioral analysis stage.

- **[a] Effort:** S -- the normalization is mechanical once the target format is defined by the main skill.
- **[b] Dependencies:** `requests` or `huggingface_hub` Python library; Hugging Face dataset URL from the video description. Could be folded into the main skill as a fallback branch rather than a separate skill.
- **[c] Value:** 3/5 -- primarily a fallback path; most heavy users will have enough personal Fable history for the main path.
- **[d] Why now or never:** The community datasets may disappear or become stale as Fable recedes -- worth capturing the reference now while the datasets are fresh and the community is actively uploading sessions.

---

### 3. Playbook injection hook template

A CLAUDE.md pattern and `settings.json` `SessionStart` hook template that automatically injects a named playbook file at every session start without requiring manual drag-and-drop.

- **[a] Effort:** S -- the hook pattern already exists in the workspace; this is a documented template, not new infrastructure.
- **[b] Dependencies:** `~/.claude/settings.json` hook infrastructure (already live).
- **[c] Value:** 3/5 -- quality-of-life improvement; the manual Option C from the main skill already works. The hook makes it persistent without user intervention.
- **[d] Why now or never:** Most useful immediately after the playbook is generated; easy to defer until the playbook has been validated manually a few times first.

---

## Source update

`~/projects/skill-forge/data/state/mark-kashef.last` updated to `2026-06-14T00:00:00Z`.
