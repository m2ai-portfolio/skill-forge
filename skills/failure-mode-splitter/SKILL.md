---
name: failure-mode-splitter
description: Before accepting a complex agentic deliverable, decompose it into four risk buckets — source, visual, operational, and review — then prescribe the specific QA action each bucket needs. Prevents accepting output that looks done but fails silently in one dimension. Use when an agentic task has produced a multi-part deliverable and you need to decide what to check before signing off.
---

# Failure-Mode Splitter

Takes a completed agentic deliverable and decomposes it into four independent risk buckets. Each bucket maps to a different type of failure mode and requires a different QA pass. The output is a per-bucket risk list and a concrete next action — not a single pass/fail verdict.

## Trigger

Use when the user says "/failure-mode-splitter", "check this deliverable before I accept it", "pre-acceptance check", "split this by failure mode", "what could still be wrong with this output", or when an agent has produced a complex deliverable (report, analysis, document, data set, code) that needs structured QA before acceptance.

## Why This Exists

Agentic deliverables fail in at least four distinct ways that don't always co-occur:
- A deliverable can have perfect citations but broken visual layout
- A report can have correct facts but miss operational constraints ("do not email vendors before legal review")
- Content can be visually polished but contain fabricated sources
- Work can be technically complete but blocked from being final because a section requires human sign-off

Checking everything in one pass with one model misses failures that require a different evaluator. This skill forces explicit separation before acceptance.

## Phase 1: Intake

Collect from the user:
1. **Deliverable description** -- what did the agent produce? One paragraph.
2. **Original task** -- what was the agent asked to do?
3. **Stakes** -- what breaks if this deliverable is wrong?

If the deliverable is a file or document, ask for its path or paste its contents.

## Phase 2: Decompose Into Four Risk Buckets

Evaluate the deliverable against each bucket. For every bucket, list specific risks present in this deliverable -- do not list generic risks that don't apply.

### Bucket 1: Source (Provenance and Citation)

**Failure mode**: The deliverable references facts, numbers, or claims that cannot be traced to a real source -- fabricated citations, paraphrased-but-unattributed content, or URLs that don't exist.

**What to check**:
- Every factual claim: is there a traceable source?
- Every citation or URL: does it resolve to a real document?
- Every statistic: does it match the cited source?

**QA action**: Assign a source-grounded model or human to spot-check a random sample of claims against the cited documents. Flag any claim without a verifiable source.

### Bucket 2: Visual (Presentation and Artifact Quality)

**Failure mode**: The deliverable has correct substance but broken, misleading, or low-quality presentation -- layout errors, misaligned diagrams, charts that don't match the data, or formatting that obscures meaning.

**What to check** (skip if deliverable is code or data with no visual component):
- Does every chart, diagram, or table render correctly?
- Does the visual presentation match the underlying data or argument?
- Are there layout breaks, truncated sections, or misaligned elements?

**QA action**: Render the output in its intended format and do a visual review. A visual-capable model or human reviewer is better suited than a text-only model for this bucket.

### Bucket 3: Operational (Constraints and Conflict Detection)

**Failure mode**: The deliverable proposes or describes actions that violate known constraints -- legal, organizational, technical, or process constraints that the agent did not know about or ignored.

**What to check**:
- Does the output recommend any action that is restricted, risky, or explicitly prohibited?
- Are there conflicts with other ongoing work, policies, or dependencies?
- Are review queues or escalation paths surfaced (not smoothed over)?

**QA action**: Have a human or a model with full constraint context review the action items and recommendations. Surface conflicts explicitly -- do not accept "TBD" or "to be confirmed" as a substitute for a real constraint check.

### Bucket 4: Review State (Final vs Reviewable vs Blocked)

**Failure mode**: The deliverable presents all content as equally final when parts of it require human sign-off, are provisional, or depend on blocked information.

**What to check**:
- Which sections or items are truly final?
- Which require human review or approval before use?
- Which are blocked on missing information and should not be used?

**QA action**: Label every major section or output item as one of: FINAL, REVIEW-REQUIRED, or BLOCKED. Do not mark the deliverable complete until REVIEW-REQUIRED items have been reviewed and BLOCKED items are either resolved or explicitly acknowledged as out of scope.

## Phase 3: Output

```
FAILURE-MODE SPLIT
==================
Deliverable: {one-line description}

Bucket 1 -- Source
  Risks found:  {bullet list of specific risks, or NONE}
  QA action:    {concrete next step}

Bucket 2 -- Visual
  Risks found:  {bullet list, or SKIP -- no visual component}
  QA action:    {concrete next step}

Bucket 3 -- Operational
  Risks found:  {bullet list of specific risks, or NONE}
  QA action:    {concrete next step}

Bucket 4 -- Review State
  Final:           {list of sections / items that are truly final}
  Review-required: {list of sections / items needing sign-off}
  Blocked:         {list of items blocked on missing information}
  QA action:       {who reviews what before acceptance}

Overall verdict:
  ACCEPT  -- all buckets clear, no REVIEW-REQUIRED or BLOCKED items remain
  HOLD    -- one or more buckets have open risks requiring QA before acceptance
  REJECT  -- a bucket failure is severe enough to require the agent to redo the work
```

## Phase 4: Route to the Right Reviewer

After splitting, assign each bucket to the appropriate reviewer:

| Bucket | Best reviewer |
|--------|--------------|
| Source | Source-grounded model or human with access to cited documents |
| Visual | Visual-capable model or human with rendering context |
| Operational | Human with knowledge of constraints, or a model briefed on constraints |
| Review state | Human with authority to sign off or escalate |

Do not route all buckets to the same reviewer unless they genuinely have the context for all four.

## What This Does NOT Do

- Does not re-run the agent or regenerate the deliverable -- it evaluates what exists.
- Does not replace a full security, legal, or compliance review.
- Does not apply to deliverables that are purely executable code -- use a testing harness for those.
- Does not pick the right model for the QA pass -- see a model router skill for that.

## Source Attribution

Technique: Pre-Acceptance Failure-Mode Decomposition into Four Risk Buckets
Source: Nate's Newsletter (natesnewsletter@substack.com)
Published: 2026-06-03
Subject: "Opus 4.8 scored 81 in my benchmark. I still wouldn't default to it."
Idea #3 of 11 -- Failure-Mode Splitter (pre-acceptance risk decomposer)
