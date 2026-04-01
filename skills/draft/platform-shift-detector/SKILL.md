---
name: platform-shift-detector
description: Monitors tech company announcements, API changes, hiring patterns, and product signals to detect platform-level shifts early -- distinguishing feature moves from infrastructure plays. Feeds IdeaForge research pipeline.
---

# Platform Shift Detector

Analyzes a set of signals from a tech company to determine whether they indicate a platform-level shift (new runtime, new protocol, new infrastructure layer) versus incremental feature work. Designed to catch moves like Apple's MCP/iOS integration, Google's Gemini-in-Android push, or Microsoft's Copilot platform play before market consensus forms.

## Trigger

Use when the user says "is this a platform shift", "platform shift analysis", "detect platform moves", "what's [company] actually building", or when reviewing research-agent output that contains multiple signals from a single company.

Also use as a scheduled analysis pass on accumulated IdeaForge signals.

## Phase 1: Signal Intake

Accept signals. These can be:
- A company name + recent announcements ("analyze Apple's last 90 days")
- A set of IdeaForge/research-agent signals about a single company
- A specific announcement the user wants contextualized
- A URL to a press release, blog post, or keynote summary

Gather at least 3 signals before proceeding. If fewer are provided, use WebSearch to find recent announcements, API changes, developer docs updates, and hiring patterns for the company.

## Phase 2: Signal Classification

For each signal, classify:

| Signal | Type | Layer |
|--------|------|-------|
| Description | PRODUCT / API / PROTOCOL / HIRING / PARTNERSHIP / ACQUISITION | APP / PLATFORM / RUNTIME / INFRASTRUCTURE |

**Type definitions:**
- PRODUCT -- end-user feature or UI change
- API -- developer-facing interface change
- PROTOCOL -- standard or interop specification
- HIRING -- job postings indicating strategic direction
- PARTNERSHIP -- cross-company alignment
- ACQUISITION -- talent or technology acquisition

**Layer definitions:**
- APP -- feature on top of existing platform
- PLATFORM -- new surface area for third-party builders
- RUNTIME -- execution environment that others must conform to
- INFRASTRUCTURE -- physical or foundational layer (chips, data centers, network)

## Phase 3: Pattern Detection

Check for interlocking signal patterns that indicate a platform shift:

1. **Protocol + Runtime** -- company is defining how others must integrate (strongest signal)
2. **API + Hiring + Partnership** -- building developer ecosystem for something new
3. **Multiple PLATFORM/RUNTIME signals** -- consistent investment at infrastructure layer
4. **Acquisition + Protocol** -- bought the capability, now standardizing it
5. **Single APP signal** -- likely just a feature, not a shift

Score the overall pattern:

- **PLATFORM SHIFT** -- 2+ signals at PLATFORM/RUNTIME/INFRASTRUCTURE layer with interlocking pattern
- **POSSIBLE SHIFT** -- mixed signals, some at platform layer but pattern incomplete
- **FEATURE PLAY** -- signals concentrated at APP layer, no infrastructure investment
- **TOO EARLY** -- insufficient signals to determine

## Phase 4: Timeline and Window

If PLATFORM SHIFT or POSSIBLE SHIFT:

1. **Catalyst events** -- upcoming conferences, product launches, regulatory deadlines
2. **Positioning window** -- how long builders have before the shift is priced in
3. **First-mover opportunities** -- what to build now that will have advantage when the shift lands
4. **Risk of being wrong** -- what you lose if this isn't actually a platform shift

## Phase 5: Output

```
## Platform Shift Analysis: [Company]

**Verdict:** PLATFORM SHIFT | POSSIBLE SHIFT | FEATURE PLAY | TOO EARLY
**Confidence:** HIGH | MEDIUM | LOW
**Signals analyzed:** N

### Signal Map
[Table from Phase 2]

### Pattern
[Which interlocking pattern was detected, or why none was]

### Timeline
- **Next catalyst:** [event + date]
- **Positioning window:** [N weeks/months]

### Builder Actions
- **Build now:** [what to prototype before the shift lands]
- **Wait for:** [what requires more information]
- **Avoid:** [what will be obsoleted or commoditized by the shift]

### M2AI Relevance
[How this affects M2AI's product bets, consulting practice, or research pipeline]
```

## Verification

A good platform shift analysis:
- Uses 3+ distinct signals, not just one announcement
- Distinguishes clearly between APP-layer noise and PLATFORM/RUNTIME investment
- Provides specific, actionable builder recommendations
- Acknowledges uncertainty honestly -- does not oversell POSSIBLE as CERTAIN
- Includes timeline with concrete catalyst events

## Source

Extracted from Nate Kadlac newsletter (2026-03-31) -- "The Company Everyone Says Lost the AI Race Is Building the Layer Every AI Winner Has to Use" -- the analytical framework for detecting platform-level moves vs. feature-level responses.
