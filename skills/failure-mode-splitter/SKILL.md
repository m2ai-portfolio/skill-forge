---
name: failure-mode-splitter
description: Before accepting any agentic deliverable, decompose it into four risk buckets — source/provenance, visual/quality, operational/conflict, and review/status — and generate a targeted second-pass action for each. Trigger: "split failure modes", "pre-acceptance review", "bucket this deliverable", "what could go wrong with this output", "failure-mode-splitter".
---

# Failure-Mode Splitter

Before accepting an agentic deliverable — a report, a migration, a content packet, a code artifact — decompose it into four orthogonal risk buckets. Each bucket has its own failure profile, so a single all-in-one QA pass misses failures that only show up under the right lens. This skill generates a per-bucket risk list and a specific remediation or second-pass action for each.

## When to Use

- You've received output from an agent and need to decide whether to accept it before acting, shipping, or forwarding.
- The deliverable has multiple dimensions of quality (factual accuracy AND visual presentation AND operational completeness).
- You want a structured pre-acceptance checklist rather than ad-hoc review.
- You're routing the deliverable to a specialist model or a human reviewer and need to brief them efficiently.

Do NOT use for simple, single-dimension outputs (e.g., a one-line code fix). The overhead isn't justified.

## Phase 1: Intake

Ask the user to describe or paste the deliverable. Collect:

1. **Deliverable type** — what kind of artifact is it? (report, code, data migration, marketing packet, diagram, etc.)
2. **Intended audience or next step** — who receives it or what happens to it next?
3. **Source material** — was the deliverable produced from specific documents, a database, external URLs, or purely from the model's knowledge?

If the user provides a file path or URL, read or fetch the content before proceeding.

## Phase 2: Classify Into Four Buckets

For each bucket, identify 2–5 concrete risks present in THIS deliverable based on its type and content. Do not generate generic risks — anchor each item to something observable in the artifact.

### Bucket 1 — Source / Provenance

**What fails here**: Citations are missing, invented, or untraceable. Source IDs are stripped. Claims reference "the data" without a pointer to which data. Hallucinated statistics.

**Questions to ask**:
- Does every factual claim have a traceable source path (URL, file, row ID)?
- Are all sources cited present in the input context, or are some inferred from training data?
- Would a reviewer be able to verify each key claim in under 2 minutes?

**Second-pass action**: Run a source-discipline model pass — feed the deliverable alongside the original source material and ask specifically: "Flag every factual claim not traceable to the provided sources."

---

### Bucket 2 — Visual / Presentation Quality

**What fails here**: Structure is wrong for the audience. Diagrams are inaccurate. Formatting is inconsistent. The content is correct but will be rejected or misread because of how it looks.

**Questions to ask**:
- Is the visual hierarchy appropriate for the intended audience?
- Do any diagrams, tables, or charts misrepresent the underlying data?
- Are there formatting inconsistencies that signal low quality to the reader?

**Second-pass action**: Run a design-pass or ask a model optimized for presentation quality to review layout and structure separately from factual accuracy.

---

### Bucket 3 — Operational / Conflict

**What fails here**: The deliverable recommends an action that conflicts with a constraint, policy, or prior decision. It omits a "do not do X" that should be in scope. Review queues that should have been populated weren't. Edge cases are smoothed over instead of surfaced.

**Questions to ask**:
- Does the deliverable surface constraints or blockers, or silently paper over them?
- Are any recommended actions in conflict with known policies, dependencies, or prior decisions?
- Is there a review queue — a set of items needing human judgment — and has it been explicitly populated rather than resolved by assumption?

**Second-pass action**: Route to a human reviewer or a constraints-aware model pass: "Here is the deliverable and here are the hard constraints. Flag any action or recommendation that violates a constraint or requires a human decision before execution."

---

### Bucket 4 — Review / Status Classification

**What fails here**: It's unclear which parts of the deliverable are final vs. still reviewable vs. blocked. Accepting the whole artifact when only part of it is finalized leads to downstream rework. Blocked items go unnoticed.

**Questions to ask**:
- Is each section or record clearly labeled as: final, needs-review, or blocked?
- Are blocked items accompanied by a clear reason and a resolution path?
- Is there an explicit acceptance criteria — a done condition — for this deliverable?

**Second-pass action**: If the artifact lacks status labels, ask the producing agent to re-emit it with explicit `[FINAL]`, `[REVIEW]`, `[BLOCKED: reason]` tags on each section or record. Do not accept an unlabeled artifact as final.

---

## Phase 3: Output

Produce a structured report:

```
FAILURE-MODE SPLIT REPORT
Deliverable: <type + brief description>
Intended next step: <who receives it / what happens>

BUCKET 1 — SOURCE / PROVENANCE
Risks identified:
  - <specific risk 1>
  - <specific risk 2>
Second-pass action: <what to do>
Severity: [HIGH / MEDIUM / LOW]

BUCKET 2 — VISUAL / PRESENTATION
Risks identified:
  - <specific risk 1>
  - <specific risk 2>
Second-pass action: <what to do>
Severity: [HIGH / MEDIUM / LOW]

BUCKET 3 — OPERATIONAL / CONFLICT
Risks identified:
  - <specific risk 1>
  - <specific risk 2>
Second-pass action: <what to do>
Severity: [HIGH / MEDIUM / LOW]

BUCKET 4 — REVIEW / STATUS
Risks identified:
  - <specific risk 1>
  - <specific risk 2>
Second-pass action: <what to do>
Severity: [HIGH / MEDIUM / LOW]

ACCEPTANCE RECOMMENDATION: [ACCEPT / HOLD — resolve bucket N first / REJECT — redeliver]
Reason: <one sentence>
```

If any bucket has severity HIGH and no action has been taken on it, the recommendation must be HOLD or REJECT — never ACCEPT.

## Common Pitfalls

- **Don't collapse buckets.** Each bucket captures a distinct failure mode. Merging source and visual into "quality" causes the operational/conflict bucket to get dropped.
- **Anchor risks to the artifact.** Generic risks ("the model might hallucinate") are not actionable. Name what you actually see.
- **Severity drives the gate.** A LOW-severity source risk with a clear second-pass action can coexist with an ACCEPT recommendation. A HIGH-severity conflict risk cannot.
- **The producing agent's self-assessment is not a substitute.** Asking the same session that produced the deliverable to rate its own quality is the self-preference bias this skill is designed to bypass.

## Source Attribution

Technique: Pre-acceptance risk decomposition into four failure-mode buckets
Source: Nate's Newsletter (natesnewsletter@substack.com) — "Opus 4.8 scored 81 in my benchmark"
Published: 2026-06-03
Idea reference: Idea #3 — Failure-Mode Splitter
