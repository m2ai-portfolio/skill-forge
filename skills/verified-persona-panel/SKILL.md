---
name: verified-persona-panel
description: Run a fabrication-audited synthetic persona review panel on any deliverable. Each in-character persona reviews the artifact and makes specific claims; every claim is machine-checked against the actual artifact. Claims that cannot be verified are flagged as fabricated. Use when the user says "persona panel", "synthetic user testing", "verified focus group", "character review", "fabrication-checked feedback", "run a focus group", "test this with personas", or wants QA feedback that catches hallucinated reviewer claims.
---

# Verified Persona Panel

Standard code and content review catches objective errors. Persona-based review catches whether a
deliverable works for specific audiences -- but synthetic persona reviews have a failure mode:
a persona can hallucinate evidence, claiming a button is missing or a section is wrong when the
artifact clearly contains it. This skill adds a fabrication audit layer: every specific claim a
persona makes is checked against the actual artifact before the verdict is issued. A persona that
fabricates evidence is flagged, not quoted as authoritative.

## Trigger

Use when the user says "persona panel", "synthetic user testing", "verified focus group",
"character review", "fabrication-checked feedback", "run a focus group", "test this with
personas", or wants QA feedback that exposes audience-specific failures while still catching
reviewer hallucinations.

---

## Phase 1: Define the Panel

Ask the user (or derive from the artifact's context):

1. **What is the artifact?** (A document, a UI design, a set of instructions, a codebase, a
   landing page, a task specification -- state what is being reviewed.)

2. **Who is the intended audience?** (If the user names specific roles, use those. If not,
   derive 3-5 plausible audience segments from the artifact's content and purpose.)

3. **What does a successful review look like?** (What complaints, if validated, would cause the
   team to revise the artifact? What praise, if validated, is signal that a design decision worked?)

Construct the panel: 3-5 personas, each described in 2-3 sentences. Each persona must have:
- A named role or archetype
- One prior expectation they bring to the artifact (what they were hoping to find)
- One known friction point or concern relevant to the domain

Do not invent demographic specifics beyond what is needed to make the persona's perspective
distinct. More concrete = more fabrication risk.

---

## Phase 2: In-Character Review

Run each persona in sequence (or in parallel if the artifact is short). For each persona:

1. Prime the review with the persona description and the artifact.

2. Ask the persona to produce a structured review with exactly three sections:
   - **What works** -- specific elements of the artifact that satisfy their expectation
   - **What fails** -- specific elements that create friction or fail to meet their need
   - **What is missing** -- capabilities or information the persona expected to find but could not locate

3. Require each claim to name a specific location or element in the artifact:
   - Good: "Section 3 does not explain what happens when the file is empty."
   - Not acceptable: "The documentation feels incomplete."

Collect all reviews before the verification pass. Do not edit or filter them first.

---

## Phase 3: Claim Verification

For each claim across all persona reviews, run a binary verification:

**VERIFIED**: The artifact contains evidence that directly supports or directly contradicts the
claim. Quote the relevant excerpt.

**UNVERIFIABLE**: The artifact does not contain enough information to confirm or deny the claim.
This is neutral -- the persona may have a legitimate concern the artifact does not address.

**FABRICATED**: The artifact directly contradicts the claim. The persona asserted something was
missing or wrong, but the artifact clearly contains or correctly handles it.

Verification method (choose the most reliable available):
- For text artifacts: grep or direct read against the exact location the claim names
- For code: run the named function/path/command
- For UI designs: check the named element in the design file or screenshot
- For instruction sets: trace the named step through the actual instructions

A claim that names no specific location defaults to UNVERIFIABLE, not VERIFIED. Specificity is
required for a claim to earn VERIFIED status.

---

## Phase 4: Report

Produce one verdict block per persona, then a summary.

```
## [Persona Name] -- [Role/Archetype]
Prior expectation: [one sentence]

| Claim | Section | Verdict | Evidence |
|-------|---------|---------|----------|
| [claim] | [location] | VERIFIED / UNVERIFIABLE / FABRICATED | [excerpt or "not found"] |

Persona verdict: CREDIBLE | MIXED | FABRICATOR
  CREDIBLE: 0 fabricated claims
  MIXED: 1-2 fabricated claims (discount perspective, do not ignore)
  FABRICATOR: 3+ fabricated claims (treat all claims as unverified; review persona definition)
```

**Panel Summary:**

```
## Panel Summary

Artifact: [name]
Personas reviewed: [N]

Verified complaints (fix these):
- [claim] -- raised by [persona] -- evidence: [excerpt]

Verified praise (design decisions that worked):
- [claim] -- raised by [persona] -- evidence: [excerpt]

Unverifiable concerns (investigate):
- [concern] -- raised by [persona] -- the artifact does not address this question

Fabricated claims (ignored):
- [claim] -- [persona] -- artifact excerpt proving it false: [excerpt]

Fabrication rate: [N fabricated] / [N total claims] = [%]
Highest-confidence action: [the single verified complaint raised by the most personas]
```

---

## Verification

- [ ] Panel defined with 3-5 distinct personas before review begins
- [ ] Each persona's review names specific artifact locations, not vague impressions
- [ ] Every claim verified, unverifiable, or marked fabricated -- no claims left unclassified
- [ ] Fabricated claims are excluded from the action list
- [ ] At least one highest-confidence action named (the most-corroborated verified complaint)
- [ ] Fabrication rate reported so the user can judge persona quality

---

## Source

Extracted from Nate Kadlac newsletter (2026-07-08), idea #11 -- "Synthetic in-character persona
focus group with machine-verified claims": "A swarm of in-character personas reviews a
deliverable, and every claim a persona makes is machine-verified against the artifact, so the
gate even caught a reviewer fabricating evidence (a persona inventing a nonexistent button).
Turns 'get user feedback' into an executable, fabrication-audited check."
Source URL: https://natesnewsletter.substack.com/p/trust-ai-agents
