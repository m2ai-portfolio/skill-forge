---
name: tier-classifier
description: Lightweight classifier that takes a product description or pitch and returns a five-tier verdict from "Decorating a Model" to "Full Stack" with the missing deployment layers called out. Use as a fast first screen before a deeper audit, or as a public-facing diagnostic to qualify an AI product's enterprise readiness.
---

# AI Deployment Tier Classifier

Paste a product description, pitch paragraph, or feature list. Get back a tier verdict and the specific deployment gaps that explain it. Fast — under one minute.

## Trigger

Use when the user says "tier classifier", "/tier-classifier", "what tier is this", "am I just wrapping the model", "classify this AI product", "decorating a model or owning a workflow", "enterprise AI tier", "how mature is this deployment", or pastes a product description and wants a quick readiness verdict.

## Phase 1: Accept Input

Accept any of:
- A paragraph describing an AI product, feature, or system
- A pitch deck excerpt (pasted text)
- A bullet-point feature list
- A company/product name with a brief description

If the user pastes nothing, ask: "Describe the AI product in a paragraph — what it does, what data it touches, and what actions it can take."

## Phase 2: Scan for Deployment Signals

Look for evidence (or absence) of each of the six deployment layers. Treat absence of mention as a signal worth flagging — enterprise-ready systems describe these explicitly because buyers ask about them.

**Signals to scan for:**

| Layer | PRESENT signals | ABSENT signals |
|-------|----------------|----------------|
| Workflow Design | "human approval", "handoff", "escalation", "step-by-step", "in-the-loop" | No mention of sequencing or human gates |
| Data Access | "permission", "scoped", "row-level", "field-level", "access control" | "full database", "reads all", no access qualification |
| Authority Limits | "can't execute without approval", "spend limit", "read-only", "approve before send" | "autonomous", "handles it automatically", no mention of limits |
| Eval Against Policy | "quality rubric", "policy doc", "custom evals", "scored against", "drift" | "accurate", "smart" with no measurement basis |
| Audit Trails | "log", "audit", "trace", "reconstruct", "tamper-evident" | No mention of traceability |
| Recovery / Ownership | "reverse", "compensate", "owner", "monitors for changes", "rollback" | No mention of what happens when it's wrong |

## Phase 3: Assign Tier

Tier thresholds (each layer counts as 0 = absent, 0.5 = partial mention, 1 = explicit):

| Tier | Score | Label |
|------|-------|-------|
| 5 | 5.5-6.0 | **FULL STACK** — enterprise-grade; audit trails, authority limits, and recovery wired in |
| 4 | 4.0-5.0 | **WORKFLOW OWNER** — real automation with at least four layers present |
| 3 | 2.5-3.5 | **HALF-BUILT** — value delivered but critical enterprise gaps |
| 2 | 1.5-2.0 | **WRAPPER** — model access plus light scaffolding |
| 1 | <1.5   | **DECORATING A MODEL** — UI on an API call; no defensible enterprise moat |

## Phase 4: Output

```
AI Deployment Tier Classifier
==============================
Input: [product name or first 15 words of description]

Tier: [NUMBER] — [LABEL]

Layer Scan:
  Workflow Design      [PRESENT / PARTIAL / ABSENT]
  Data Access          [PRESENT / PARTIAL / ABSENT]
  Authority Limits     [PRESENT / PARTIAL / ABSENT]
  Eval Against Policy  [PRESENT / PARTIAL / ABSENT]
  Audit Trails         [PRESENT / PARTIAL / ABSENT]
  Recovery / Ownership [PRESENT / PARTIAL / ABSENT]

Missing layers (what to build next):
- [Layer]: [One sentence on what's absent and why it matters to buyers]
- [Layer]: [One sentence]

Verdict: [1-2 sentence plain-English summary of where this product stands and the single highest-leverage gap to close]
```

If the product is Tier 4 or 5, confirm which layer is the weakest and what it would take to shore it up.

## Output Format

Fast and tight. One screen. The tier label and missing layers are the deliverable. The verdict sentence is for sharing — write it as something the user could paste into a Slack message or proposal.

## Source Attribution

Tier model derived from Nate's Newsletter (2026-05-14): "The Enterprise AI Deployment Layer: Why Model Access Isn't Enough." The five-tier vocabulary ("Decorating a Model" through "Full Stack") maps the six deployment layers onto a single enterprise-readiness scale.
