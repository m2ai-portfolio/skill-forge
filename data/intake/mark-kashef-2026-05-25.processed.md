# Mark Kashef — "How to INSTANTLY Run ANY Skill in Claude + Codex"

**Source:** https://www.youtube.com/watch?v=tjjX43FoAUg
**Published:** 2026-05-21
**Intake date:** 2026-05-25

---

## TLDR

Mark introduces "PolySkill" — a universal adapter skill that converts any Claude Code skill to run in Codex (and vice versa) by normalizing the structural differences between the two platforms (sidecar YAML, description truncation, backtick-bang dynamic injection). The core insight is that provider churn (Claude ↔ Codex ↔ Gemini) is inevitable and you need one meta-skill to stay nimble rather than manually re-porting every skill each time you switch.

---

## Buildable Ideas

### 1. `poly-skill` — Cross-provider skill converter

Build a skill that reads an existing SKILL.md + associated assets, identifies the target provider's structural schema (Claude Code vs. Codex vs. others), and emits a converted version in the correct format with a sidecar YAML if needed.

- **[a] Effort:** M — schema comparison logic is mechanical; the Claude Code format is already known; need to reverse-engineer the Codex `agents/` YAML schema from Mark's demo or the Codex docs.
- **[b] Dependencies:** Read tool access to `~/.claude/skills/`; Codex `~/.codex/agents/` path knowledge; Codex sidecar schema spec (external doc needed). No external APIs.
- **[c] Value:** 4/5 — directly addresses the multi-provider skill churn problem Matthew already experiences (e.g., keeping Ravage skills aligned across CLI invocations).
- **[d] Why now or never:** Provider fragmentation is peaking right now; building the adapter at peak fragmentation gives maximum ROI — a year from now one provider may have won.

**Routing:** BUILT — `skills/poly-skill/`

---

### 2. `skill-sync-cron` — Scheduled cross-provider skill parity check

A scheduled task (CMD cron or Claude Code cron) that diffs `~/.claude/skills/` against `~/.codex/agents/` weekly and surfaces any skills present in one but not the other, or where the sidecar YAML is missing/stale.

- **[a] Effort:** S — pure file diffing; no LLM needed except for the summary line.
- **[b] Dependencies:** Access to both skill directories; `skill-sync-cron` could be a bash script wrapped as a CMD scheduled mission. No external APIs.
- **[c] Value:** 3/5 — maintenance hygiene rather than new capability; prevents silent drift without requiring PolySkill re-runs.
- **[d] Why now or never:** Only useful if `poly-skill` (#1) is built first; implement as the follow-on once PolySkill is proven.

**Routing:** NO-GO — `~/.codex/agents` does not exist and there are 0 Codex agents on this box; a weekly diff cron against a nonexistent directory is a textbook orphan loop. Reopen on actual Codex adoption, with owner/sink/kill declared.

---

### 3. `skill-schema-registry` — Provider schema reference doc for skill conversion

A reference file (not a skill — a static artifact) capturing the canonical structural schema for each provider (Claude Code, Codex, optionally Gemini/Cursor) so conversion logic doesn't depend on LLM memory. Stored at `~/projects/skill-forge/data/schemas/`.

- **[a] Effort:** S — research + write once; update when providers change their format.
- **[b] Dependencies:** Codex official docs or `/codex --help` output for sidecar schema; Claude Code SKILL.md frontmatter spec (already known). No runtime dependencies.
- **[c] Value:** 3/5 — load-bearing reference for PolySkill and any future agent that needs to emit skills for a specific provider.
- **[d] Why now or never:** Schemas drift silently; capturing them now while Mark's video is fresh makes the reference authoritative. Low cost, high durability.

**Routing:** CARD — MAI-33. Consumer `poly-skill` is built. The card corrects the target path: the intake names `data/schemas/`, which is gitignored, so the reference goes inside the skill dir instead.

---

### 4. Provider-agnostic skill trigger placement rule (hook / CLAUDE.md rule)

Mark notes that Codex truncates skill descriptions and misses triggers placed at the end. Add a `~/.claude/hooks/` PostToolUse rule (or CLAUDE.md entry) that warns when a new SKILL.md has its `when-to-trigger` field after the 300-character mark of the description, since that pattern would silently misfire in Codex.

- **[a] Effort:** S — regex check on SKILL.md description length + trigger position; hook already wired.
- **[b] Dependencies:** Existing `~/.claude/hooks/` PostToolUse infrastructure; no new dependencies.
- **[c] Value:** 3/5 — pure prevention; low probability of triggering but high cost when it does (invisible Codex skill misfire).
- **[d] Why now or never:** Callsite sponsorship: add to CLAUDE.md now while writing new skills, or the rule never gets written and the pattern silently drifts.

**Routing:** NO-GO — same evidence as idea 2: no Codex agents on this box, so nothing can misfire on trigger placement. It is also a `~/.claude/hooks/` change outside this repo, and would be an extension of the existing `skill-frontmatter-guard.py` rather than a new hook. Reopen on Codex adoption.

---

## Source update

`~/projects/skill-forge/data/state/mark-kashef.last` updated to `2026-05-25T00:00:00Z`.
