---
name: verification-view
description: Use after a long coding or planning session to turn a git diff (or a set of changes) into a ranked, evidence-backed HTML verification view that surfaces only the risky changes, pastes real test/command output as proof, and recommends the tests that are missing. Use when the user says "verify this session", "verification view", "what should I check", "I can't review this wall of text", or wants to close the gap between what an AI did and what they can actually judge. Closes the verification gap by surfacing decisions, evidence, and risks instead of a flat narrative.
---

# /verification-view

The user has a growing verification gap: as the model carries more, the floor of changes they can still judge shrinks, and long sessions become walls of text. This skill does NOT make output prettier. It makes output verifiable. Readability and verifiability are different things, and a polished report that raises trust faster than it raises checkability makes the gap worse.

Core principle: surface the ~20% of changes most likely to be WRONG or most EXPENSIVE if wrong, paste real evidence the model cannot fake, and collapse the boring 80% to a one-line count that stays one click away. The user controls the zoom; the model does not get to decide what they see.

## Non-negotiables

1. **Run, do not narrate.** Every evidence claim is backed by a command the skill actually runs (git diff, the test suite, npm audit, a live check) and pastes verbatim. Never paraphrase a test result. If you cannot run it, say so and mark the claim unverified.
2. **Soft fields are promote-only.** Reversibility (inferred part) and the model self-signal can only RAISE risk, never lower it. Absence of a hedge is not proof of correctness.
3. **Domain override.** Any change touching auth, money, data delete/write, or API model/version/endpoint/SDK config is forced into the visible layer regardless of score. The model cannot bury the scary change in the boring pile.
4. **The 80% is collapsed, not deleted.** Routine changes get a one-line count and remain reachable. Deleting them reopens the gap.

## Inputs

- A commit range, single commit, PR/MR number, or uncommitted working tree.
- Default to `git diff --name-status` + `git diff --numstat` for the target range. Group the diff into **change units** (a logical change spanning one or more files), not per-file.

## Step 1 — Gather (deterministic, faking-proof)

For the target range, run and capture verbatim:
- `git diff --numstat <range>` (files, +/- lines)
- `git diff --name-status <range>` (adds/mods/deletes/renames)
- Caller reach: for each changed exported symbol, grep the repo for usages (fallback when no dependency graph exists).
- Test execution: detect the test command from `package.json` scripts / `pyproject.toml` / Makefile, run it, capture pass/fail counts and failures. If there is NO test suite, record that explicitly — it is a finding, not a blank.
- Lockfile/manifest check: if `package-lock.json`, `package.json` deps, `requirements.txt`, `go.mod`, etc. changed, run the ecosystem audit (`npm audit`, `pip-audit`) and treat blast radius as runtime-wide, not "1 file".

## Step 2 — Score each change unit (five fields)

| Field | Source | Fakeable | Weight |
|-------|--------|----------|--------|
| Blast radius | numstat + caller grep; **lockfile/manifest = runtime-wide** | no | 0 to +3 |
| Domain flags | path/content patterns: auth, money, data delete/write, secrets, network, migrations, **API model/version/endpoint/SDK config** | no | sensitive +1; auth/money/delete/API-model +3 and hard floor |
| Reversibility | hard markers (migration, DROP, file delete, deployed config) deterministic; rest inferred (**promote-only**) | partly | irreversible +2 |
| Test coverage | skill runs the suite; maps tests to changed files; untested = flag | no (skill runs it) | untested+nontrivial +2; tested+passing −1 |
| Model self-signal | hedge/assumed/TODO markers the model emitted (**promote-only**) | yes | hedge +1; absent 0 |

Bands: **≥4 HIGH**, **2–3 MED**, **<2 LOW (collapse)**. Domain override (rule 3) forces HIGH-layer regardless of band.

## Step 3 — Recommend tests (the consistency engine)

Do NOT freelance "what should I test." Map every change unit against this FIXED six-category taxonomy so the lens is identical every session:

1. **Happy path** — intended behavior works.
2. **Boundary** — empty, null, zero, max, malformed input.
3. **Error handling** — dependency failure, bad input, exception.
4. **Regression** — for a fix, the exact thing that was broken before.
5. **Contract** — still talks correctly to callers and callees.
6. **Real-risk** — the one tied to the domain flag. API model change: is the ID live-valid (a unit test asserting a constant resolves does NOT prove the value is real — needs /chub or a live ping). Auth: an unauthorized request is actually rejected. Delete: only the intended rows go.

For each unit output: (a) what tests exist and what they actually assert, (b) which of the six categories are NOT covered, (c) a concrete plain-speak test per gap. Explicitly flag tests aimed at the wrong target (green test giving false comfort).

## Step 4 — Render the verification view (three layers, collapsed by default)

Reuse the existing renderer:
`import { renderHtmlToImage } from '/home/apexaipc/projects/claudeclaw/src/image-renderer.js'` for a PNG, or emit a self-contained HTML file (base64 assets, no external links) for browser review. For external sharing use GitLab Pages under `m2ai-portfolio`.

- **Layer 1 (always visible, phone-sized):** verdict line (files, +/-, test result) + the HIGH/MED units, each one line, tagged with confidence and "if wrong: <failure mode>", plus its missing-test recommendation.
- **Layer 2 (collapsed, expand on suspicion):** per unit, the actual diff, the actual test output, the actual command/audit result.
- **Layer 3 (buried):** raw transcript / full log for audit.
- **Routine (collapsed one-liner):** "N import updates, 1 rename, 4 type fixes (routine)".

Serve LAN previews on `10.0.0.46:<port>`, never localhost.

## Optional escalation

For big or high-stakes sessions, run a separate reviewer subagent that sees only the diff + test output and ranks risk independently of the agent that wrote the code (separate the doer from the reporter). Overkill for routine sessions — do not default to it.

## Friction choice (ask once)

Ask whether Layer 1 should be a **judgment** (lower friction, can be rubber-stamped) or an **active checklist** (each item ticked before "verified"; closes the gap harder). Match the user's day-to-day appetite.

## Known boundaries

- Caller grep is imperfect in dynamic languages — a signal, not a proof.
- Real coverage mapping needs a coverage tool wired per project; without it, fall back to "did the module's tests run".
- `understand-diff` can replace the blast-radius/contract analysis with graph-accurate reach, BUT it is static-only (never runs anything) and needs a maintained `/understand` knowledge graph. It covers none of: domain flags, reversibility, test execution/recommendations, model self-signal. Treat it as a later accuracy upgrade for field 1, not the engine.
- Per-project config needed: where tests live and how to run them.

## Validation before trusting it

Dry-run against a diff the user already understands and check the bands match their gut before relying on it on an unknown session. Two dry-runs already hardened this spec (a no-test dep bump that scored HIGH on the untested dimension; a test-backed model-ID change where the existing test proved the wiring but not the value validity).

## 14-day adoption gate

This skill is experimental until 2026-06-14 (created 2026-05-31). It must earn one of: 3 human invocations, an active agent's manifest, or an active callsite. If none, cold-archive to `~/projects/skill-forge/skills/verification-view/` with `status: cold`. The natural sponsor is Data using it to report back on long cross-project sessions — wire it into that path to sponsor it.
