---
name: kill-switch-audit
description: For a named agent in production, verify that a real kill path exists at each of the 5 layers (runtime cancel, credential revocation, gateway tool-call block, payment freeze, workflow interrupt). Produces a per-layer pass/fail checklist and a KILLABLE / NOT KILLABLE verdict. Use when asked "can we actually stop this agent", "kill switch audit", "verify kill paths", "agent kill check", "/kill-switch-audit".
---

# Kill-Switch Audit

Verifies that a real, tested kill path exists at each of the 5 shutdown layers for a named agent in production. A single-layer kill is not a kill switch — this audit confirms all 5.

## When to Invoke

Trigger on: "can we actually stop this agent", "kill switch audit", "verify kill paths", "is our kill switch real", "agent shutdown audit", "do we have a real kill switch", "/kill-switch-audit".

## Inputs

Ask the user (skip any already answered):

1. **Agent name and role** — what does the agent do, what systems does it call?
2. **Deployment environment** — where does it run? (container, Lambda, cron, long-running process, orchestration framework)
3. **Identity credential** — what credential does the agent use? (API key, service account, OAuth token, IAM role)
4. **Tool-call gateway** — does the agent route tool calls through a proxy, MCP server, or API gateway, or does it call external APIs directly?
5. **Payment authority** — can the agent initiate any financial transaction or incur billable cost? (yes/no, and which instrument if yes)
6. **Workflow orchestrator** — is the agent embedded in an orchestration framework? (LangGraph, Temporal, Prefect, custom scheduler, or none)
7. **Last tested** — when was any kill path last tested in a non-production environment? (date or "never")

## The 5-Layer Kill Matrix

Evaluate each layer in order. A layer is PASS only if both a mechanism and an owner exist.

### Layer 1 — Runtime Cancel / Pause

*Can the running process be stopped within 60 seconds without a full redeploy?*

Gather:
- What command or API call stops the agent mid-run? (SIGTERM, container stop, Lambda abort, queue drain)
- Who has access to run that command in production?
- Has it been tested against a live (non-prod) run in the last 90 days?

Pass condition: Named mechanism + named owner + tested within 90 days.

Partial: Mechanism exists but not tested, OR mechanism exists but owner is "the team."

Fail: "We would redeploy" / "we would restart the service" / no clear mechanism.

### Layer 2 — Credential Revocation

*Can the agent's identity credential be revoked within 5 minutes, independent of runtime state?*

Gather:
- Where is the credential issued? (IAM console, API key management UI, OAuth provider dashboard)
- Can a single person revoke it without a deployment or code change?
- Does revocation propagate immediately to all in-flight calls, or does the agent cache the credential?
- Is the credential shared with other agents or services?

Pass condition: Single-person revocation, propagates in < 5 min, credential is not shared.

Partial: Revocation possible but takes > 5 min, OR credential is shared (revoking it breaks other services).

Fail: Credential is hardcoded in source, embedded in a deploy artifact, or requires a deployment to rotate.

### Layer 3 — Gateway / Tool-Call Block

*Can the agent's outbound tool calls be blocked at a gateway layer, independent of credential and runtime?*

Gather:
- Do the agent's tool calls pass through a proxy, MCP server, or API gateway that has a deny-list?
- Can a specific agent's client ID or session be blocked without blocking all traffic?
- Does the gateway log which agent made each call?

Pass condition: Gateway deny-list exists, per-agent block is possible, and gateway logs are queryable.

Partial: Gateway exists but blocks at the API-key level (same as credential revocation, not independent).

Fail: Agent calls external APIs directly with no proxy layer. No gateway.

### Layer 4 — Payment Instrument Freeze

*If the agent has payment authority, can it be frozen at the payment layer within 10 minutes?*

If the agent cannot initiate financial transactions and cannot trigger billable actions (LLM API calls billed externally, database writes, etc.): mark Layer 4 as **N/A** and note why.

Otherwise, gather:
- What payment instrument does the agent use? (Stripe payment method, corporate card, spend-limited service account)
- Who can freeze or revoke it in the payment provider's UI?
- Is there a hard spend cap enforced at the payment layer (not in the agent prompt)?
- Has the freeze mechanism been tested?

Pass condition: Named payment instrument + named owner who can freeze it + hard cap enforced at payment layer.

Partial: Spend cap exists but is prompt-enforced only, OR freeze requires a support ticket.

Fail: No spend cap. Agent can spend without a ceiling. No identified freeze mechanism.

### Layer 5 — Workflow / Orchestration Interrupt

*If the agent runs inside an orchestration framework, can its workflow be interrupted without killing the runtime?*

If the agent runs standalone with no orchestration framework: mark Layer 5 as **N/A** and note it.

Otherwise, gather:
- What orchestration framework manages the agent? (LangGraph, Temporal, Prefect, Airflow, custom scheduler)
- Is there a cancel/interrupt API for in-flight workflow runs?
- Can a specific run be interrupted without stopping the entire worker pool?
- Are workflow interrupts distinguished from failures in the run log?

Pass condition: Per-run interrupt API exists, distinguishable from failure in logs, tested within 90 days.

Partial: Interrupt exists but stops the whole worker pool, OR interrupt is not tested.

Fail: Workflow interrupts the only option is stopping the underlying runtime (same as Layer 1). No orchestration-level kill.

## Output Format

```
KILL-SWITCH AUDIT — [Agent Name]
Assessed: [date]
Environment: [deployment target]

| Layer | Name | Status | Owner | Mechanism | Last Tested |
|-------|------|--------|-------|-----------|-------------|
| 1 | Runtime Cancel | PASS / FAIL / PARTIAL / N/A | [name] | [command/API] | [date] |
| 2 | Credential Revocation | PASS / FAIL / PARTIAL | [name] | [system/console] | [date] |
| 3 | Gateway Block | PASS / FAIL / PARTIAL / N/A | [name] | [gateway name] | [date] |
| 4 | Payment Freeze | PASS / FAIL / PARTIAL / N/A | [name] | [instrument/system] | [date] |
| 5 | Workflow Interrupt | PASS / FAIL / PARTIAL / N/A | [name] | [framework/API] | [date] |

LAYERS PASSED: [N/5 applicable]
BLOCKING GAPS: [layer names that are FAIL or PARTIAL]

KILL-SWITCH VERDICT: KILLABLE / NOT KILLABLE
[One-sentence reason if NOT KILLABLE — the specific layer that makes a real kill impossible]

REMEDIATION PRIORITY:
1. [Highest-risk gap — concrete action, not a suggestion]
2. [Second gap if present]
```

## Verification

A complete audit:
- Distinguishes each layer as mechanically independent (credential revocation ≠ runtime stop)
- Does not accept "we can redeploy to stop it" as a runtime cancel
- Does not accept "we would email the ops team" as an owner
- Does not accept untested mechanisms as PASS (at most PARTIAL)
- Produces a KILLABLE verdict only when all applicable layers are PASS

## Source Attribution

Technique derived from Nate's Newsletter (2026-05-20): "Seven questions decide whether your AI agent ships. Most teams can answer two." — the 5-Layer Kill-Switch Audit idea (#3), grounded in the 5-layer kill path taxonomy for production agent control.
