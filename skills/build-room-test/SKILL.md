---
name: build-room-test
description: Stress-tests a vendor proposal, roadmap, or RFP against real-world deployment constraints — data access, permissions, audit boundaries, and forward-deployed engineering capacity. Outputs a pass/fail verdict with named gaps.
---

# Build-Room Test

Takes a vendor roadmap, proposal, or platform pitch and runs it through the four deployment realities that kill AI projects after procurement: data access, permission model, audit boundaries, and engineering capacity. Returns a structured pass/fail with specific named gaps.

## Trigger

Use when the user says "build-room test", "vendor test", "does this roadmap survive", "stress-test this proposal", "build room check", "/build-room-test", or pastes/links a vendor proposal and asks whether it will work in practice.

## Input

Accept any of:
1. **Pasted text** — the vendor proposal, roadmap, or executive summary
2. **File path** — read a local PDF, markdown, or text file
3. **URL** — fetch the landing page or public proposal (use WebFetch)

If no input is given, ask: "Paste the vendor roadmap or proposal, or give me a file path / URL."

## Phase 1: Extract Claims

Parse the input and extract every concrete claim the vendor makes about:
- Data access requirements ("connects to your existing data sources", "reads from your CRM")
- Permission model ("role-based", "admin approval", "SSO-ready")
- Audit and compliance ("audit log", "SOC 2", "GDPR")
- Integration surface ("REST API", "MCP", "webhook", "custom connector")
- Engineering effort ("no-code setup", "deploys in hours", "IT team optional")
- Model or AI capabilities ("uses GPT-4", "fine-tuned on your data", "runs on-premise")

List each claim as a numbered item. If fewer than 5 claims are found, note this as a signal that the proposal is abstract and likely risky.

## Phase 2: Run the Four Gates

Test each claim against four deployment realities. For each gate, mark: PASS / WARN / FAIL.

### Gate 1: Data Access Reality
**Question**: Can the agent actually reach the data it claims to need?
- Does the proposal specify WHERE the data lives (cloud, on-prem, behind VPN)?
- Does it account for real-world data governance (RBAC, PII masking, data residency rules)?
- Does it require read-write access? If yes, is rollback addressed?
- Does it assume clean, structured data? If yes, flag that most enterprise data is not.

### Gate 2: Permission Model Reality
**Question**: Who approves what the agent does, and can the vendor's model enforce that?
- Is there an explicit approval workflow for sensitive actions?
- Does the proposal address escalation when the agent is uncertain?
- Is the permission scope locked (principle of least privilege) or does the agent request broad access?
- Are there named roles (data owner, approver, auditor)?

### Gate 3: Audit Boundary Reality
**Question**: Can you prove what the agent did, when, and why?
- Does the proposal include audit logs with timestamps and actor attribution?
- Are logs immutable and exportable?
- Is there a chain-of-custody for AI-generated outputs?
- Does compliance language (SOC 2, HIPAA, GDPR) map to specific technical controls — or is it marketing language?

### Gate 4: Forward-Deployed Engineering Reality
**Question**: What ongoing engineering work does this actually require?
- "No-code" claims: what breaks first and who fixes it?
- Is there a named integration engineer or customer success engineer responsible for the deployment?
- What happens when the upstream data source changes schema?
- Who owns prompt tuning, context window management, and model updates?

## Phase 3: Score and Verdict

Produce a gate-by-gate verdict:

```
Gate 1 — Data Access:     [PASS / WARN / FAIL]
Gate 2 — Permissions:     [PASS / WARN / FAIL]
Gate 3 — Audit Boundary:  [PASS / WARN / FAIL]
Gate 4 — Engineering Req: [PASS / WARN / FAIL]

OVERALL: [PASS / CONDITIONAL / FAIL]
```

Scoring:
- **PASS**: 3–4 gates pass, 0–1 WARN, 0 FAIL
- **CONDITIONAL**: any gate is WARN or any single FAIL
- **FAIL**: 2+ FAIL gates, or Gate 1 + Gate 2 both FAIL

## Phase 4: Gap Report

For each WARN or FAIL gate, produce a named gap:

```
GAP [number]: [One-line name]
Gate: [which gate]
Claim at issue: "[exact vendor claim]"
Reality: [what the vendor didn't account for]
Ask before signing: [the specific question to put to the vendor]
```

End with a prioritized list of gaps to resolve before signing.

## Output Format

```
## Build-Room Test: [Vendor / Product Name]

**Claims extracted**: [count]
**Gates run**: 4

### Verdict
Gate 1 — Data Access:     PASS / WARN / FAIL
Gate 2 — Permissions:     PASS / WARN / FAIL
Gate 3 — Audit Boundary:  PASS / WARN / FAIL
Gate 4 — Engineering Req: PASS / WARN / FAIL

OVERALL: PASS / CONDITIONAL / FAIL

### Gap Report
[numbered gaps]

### Questions for the Vendor
[numbered questions to ask before signing]
```
