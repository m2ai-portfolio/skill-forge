---
name: tiered-model-orchestration
description: Plan a multi-phase build using a high-tier model for planning and verification, then switch mid-session to cheaper tiers for bulk execution. Produces a phase-by-phase model assignment with effort levels and a `/model` switch checklist.
---

# Tiered Model Orchestration

Prevents the most expensive Claude Code mistake: using a frontier model at max effort for everything. The frontier model earns its cost at two moments -- planning (high reasoning density, low volume) and final verification (high trust required, low volume). Everything between those two gates is execution volume where cheaper tiers produce equivalent results faster for less.

## Trigger

Use when the user says "tiered model orchestration", "plan expensive execute cheap", "how do I use Fable responsibly", "model tier per phase", "when to switch models", describes a multi-step build and asks about model selection, or is about to start a task that clearly has planning + execution + verification phases.

## Phase 1: Task Decomposition

Classify the incoming task into phases. Most builds follow this shape (not all phases are required for every task):

| Phase | What happens here | Token volume |
|-------|------------------|--------------|
| **Planning** | Spec generation, architecture, decomposing into subtasks | Low -- one or two prompts |
| **Execution** | Code generation, content creation, data transforms, file writes | High -- many turns, possibly sub-agents |
| **Assembly** | Stitching outputs together, resolving conflicts | Medium |
| **Verification** | Review, edge-case probing, quality gate | Low -- one targeted pass |

If a task has only one phase (e.g., "fix this one bug"), skip this skill and just pick the right single model.

## Phase 2: Model Assignment

Assign a model tier to each phase using this default mapping:

| Phase | Default tier | Effort level | Rationale |
|-------|-------------|--------------|-----------|
| Planning | Frontier (highest available) | High or Max | Reasoning quality gates everything downstream |
| Execution | Mid-tier or lower | Medium | Bulk volume; reasoning depth is lower per turn |
| Sub-agents spawned during execution | Lower-tier | Automatic | Each agent inherits the executor's model by default |
| Assembly | Mid-tier | Medium | Structural, not creative |
| Verification | Frontier | Low or Medium | Frontier-on-low still exceeds mid-tier-on-max for nuanced review |

**Effort tier calibration** (applies across all frontier models, not just one):
- Frontier-on-medium often exceeds one tier down at max effort -- try medium before reaching for max
- Frontier-on-low is a competent model, not a degraded one
- Match effort to reasoning density, not task importance

## Phase 3: Session Switch Checklist

After the planning phase produces a spec or plan file, walk through this switch before starting execution:

```
[ ] Plan / spec is written and saved to a file (plan.md or spec.md)
[ ] Type /model in the current session to open the model switcher
[ ] Select: [mid-tier model] at [medium|high] effort
[ ] Confirm the session is now on the cheaper tier before typing the first execution prompt
[ ] Note: sub-agents spawned from here will automatically inherit a lower-tier model
```

After execution is complete:

```
[ ] Switch back to frontier tier (or open a new session)
[ ] Use /model or start fresh session with frontier model at low or medium effort
[ ] Run the verification pass: "Review all output against the original plan. Flag edge cases not covered."
[ ] If issues found, dispatch targeted fixes at mid-tier -- not the full frontier at max
```

## Phase 4: Per-Task Recipe

For the three most common build types:

### Simple feature / marketing page
- Planning: frontier high → write spec
- Execution: mid-tier medium → build
- Verification: frontier low → quick review
- Sub-agents: lower tier (automatic)

### Complex framework-dependent build (3D, WebGL, CRM, etc.)
- Planning: frontier max → detailed spec with dependency map
- Execution: mid-tier at high, possibly a dynamic workflow where sub-agents use lower tier
- Assembly: mid-tier medium
- Verification: frontier medium → browser-based check if available

### Multi-agent pipeline / agentic system
- Planning: frontier max → architecture doc
- Execution: dynamic workflow where the orchestrator is mid-tier and sub-agents are lower tier
- Verification: frontier medium → full output review

## Phase 5: Cross-Provider Guidance

Model tier logic is provider-agnostic. If you have access to models from multiple providers:

- Treat equivalent reasoning tiers as substitutable for execution steps
- Reserve your highest-reasoning model (any provider) for planning and verification
- Don't default to one provider because it's familiar -- match the tool to the job

## Verification

The skill is working when:
- The user's plan phase cost is low (1-3 prompts at high effort) and produces a saved artifact
- Execution runs without constant intervention, at a lower model tier
- The verification pass catches something the execution missed (if nothing was caught, consider whether the frontier model was actually used for verification)
- Total session cost is lower than it would have been at frontier-max throughout

## Source Attribution

Extracted from: "Don't Use Claude Fable 5 Until You See This" by Mark Kashef
Published: 2026-06-11
URL: https://www.youtube.com/watch?v=113P6SBWAm8

Core technique: Goldilocks zone heuristics for effort tiers, mid-session `/model` switch pattern, three-phase plan-execute-verify recipe. Original framing: "plan expensive, execute cheap, verify with intent."
