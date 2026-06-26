---
name: enterprise-ai-os-port
description: Map a personal or small-team agentic OS to enterprise cloud infrastructure. Given a description of a personal setup (local files, env secrets, single user, local DB, hosted API calls), produces a cloud-agnostic service mapping, a six-domain security checklist, and a compliance remediation brief for SOC 2 or HIPAA targets. Use when someone asks "how do I take my agent setup to enterprise", "where does the data go?", "map this to AWS/Azure/GCP", or "make this HIPAA/SOC2 ready".
---

# Enterprise AI OS Port

Takes an existing personal or small-team agentic setup and produces an enterprise-grade blueprint: a component-by-component service mapping to cloud infrastructure, a six-domain security checklist, and a compliance remediation brief.

## Trigger

Use when the user:
- Says "how do I take this to enterprise", "make this HIPAA-ready", "map my setup to AWS/Azure/GCP"
- Is facing the IT question: "where does our data go? how long is it retained?"
- Wants to build an enterprise version of their personal agent platform for a client
- Has a working personal agentic OS and needs to hand a compliance blueprint to a security team

## Phase 1: Current Setup Intake

Ask the user to describe their current setup. Collect:

1. **Agent framework** - what runs the agents? (Claude Code, a custom server, SDK-based, etc.)
2. **Model access** - how do you call LLMs? (direct API keys in env file, proxy, etc.)
3. **File storage** - where does the agent read/write files? (local filesystem, Dropbox, Google Drive, etc.)
4. **Secrets** - where do credentials live? (`.env` file, environment variables, a local secrets file, etc.)
5. **Database** - where is persistent state stored? (SQLite, local Postgres, Supabase, Airtable, etc.)
6. **Users** - how many people use this, and how is access controlled? (single user, shared login, role-based, etc.)
7. **Audit trail** - what logging exists? (none, local logs, Slack notifications, etc.)
8. **Compliance target** - which standard is required, if any? (SOC 2 Type II, HIPAA, GDPR, ISO 27001, none)
9. **Cloud preference** - AWS, Azure, Google Cloud, or cloud-agnostic?

If any of the above is not provided, ask for it before proceeding. Do not assume.

## Phase 2: Component Mapping

Produce a table mapping each personal component to its enterprise cloud equivalent. Use three columns: **Personal** (what they have now), **Enterprise Equivalent** (cloud-native replacement), **Notes** (key behavioral differences, migration concerns).

### Standard mapping by cloud provider

| Personal Component | AWS Equivalent | Azure Equivalent | GCP Equivalent |
|---|---|---|---|
| Direct API key to hosted LLM | Amazon Bedrock (VPC-isolated) | Azure OpenAI Service | Vertex AI |
| Local filesystem / shared drive | S3 (versioned, encrypted at rest) | Azure Blob Storage | Google Cloud Storage |
| `.env` file / env vars | AWS Secrets Manager + KMS | Azure Key Vault | Secret Manager |
| Single-user or shared login | IAM roles + least-privilege policies | Azure RBAC + Managed Identity | IAM + Workload Identity |
| Local SQLite / self-hosted Postgres | DynamoDB or RDS (VPC-isolated) | Cosmos DB or Azure SQL | Cloud Spanner or Firestore |
| No audit trail | CloudTrail + CloudWatch Logs | Azure Monitor + Activity Log | Cloud Audit Logs |
| No content filtering | Bedrock Guardrails | Azure Content Safety | Vertex AI safety filters |
| Single server / local process | Fargate / ECS (containerized) | ACI or AKS | Cloud Run or GKE |
| Direct internet egress | VPC with NAT Gateway + security groups | VNet + NSG | VPC + Cloud NAT |

Apply only the rows relevant to what the user described. Add rows if the user describes components not in the table.

For each row, note:
- Cost model difference (fixed infra cost vs. pay-per-call)
- The key behavioral difference an agent developer needs to know
- Any migration steps required to switch the component over

## Phase 3: Six Security Domains

For each of the six domains, produce a checklist of what needs to be implemented and a current-state assessment (NOT STARTED / PARTIAL / COMPLETE) based on what the user described.

### Domain 1: Identity and Access (Least Privilege)

- [ ] Every agent, service, and human user has a dedicated identity (no shared credentials)
- [ ] Each identity is scoped to the minimum permissions needed for its role
- [ ] Service-to-service calls use role-based identities, not long-lived API keys
- [ ] Access is revocable per identity without affecting others

### Domain 2: Secrets Management

- [ ] No credentials in source code, environment files, or version control
- [ ] All secrets stored in a managed vault with encryption at rest
- [ ] Secrets are accessed at runtime via short-lived tokens or role assumption
- [ ] Secret rotation is automated or has a documented manual schedule

### Domain 3: Audit Logging

- [ ] Every agent action is logged with: who, what, when, which resource
- [ ] Logs are append-only and cannot be modified by the agent or operator
- [ ] Logs are queryable and exportable for incident review
- [ ] Log retention meets the compliance target (SOC 2: 1 year; HIPAA: 6 years)

### Domain 4: Kill Switches and Circuit Breakers

- [ ] Any individual agent or service can be disabled without bringing down the whole system
- [ ] A panic-mode kill path exists that halts all agent activity with one action
- [ ] Rate limits are enforced to prevent runaway spend or accidental data exfiltration
- [ ] Kill actions are themselves logged and attributed to the operator who triggered them

### Domain 5: Response Scanning

- [ ] Every outbound response is scanned for PII, credentials, and sensitive patterns before delivery
- [ ] Scan failures surface to the operator and are logged, not silently swallowed
- [ ] Block patterns can be updated without redeploying agents
- [ ] False-positive rates are monitored so scanning does not become a noise source

### Domain 6: Compliance Readiness

- [ ] A live readiness score exists against the target standard (SOC 2 or HIPAA) based on current setup
- [ ] Each failing control has a documented remediation path
- [ ] A remediation brief (see Phase 4) is maintained and updated as the system evolves
- [ ] A security reviewer (human) has signed off on the architecture before production use

## Phase 4: Compliance Remediation Brief

For the user's stated compliance target, produce a prioritized remediation brief:

```
COMPLIANCE REMEDIATION BRIEF
Target: {SOC 2 Type II | HIPAA | GDPR | none}
As-of: {today's date}

## Controls Currently Failing

| Control | Domain | Gap | Remediation | Effort |
|---------|--------|-----|-------------|--------|
| {e.g., CC6.1: Logical Access} | Identity & Access | No IAM roles — single shared credential | Create per-agent IAM role with least-privilege policy | Low |
| ... | ... | ... | ... | ... |

## Quick Wins (1-2 days each)
1. {action} — closes {control}
2. ...

## Medium Effort (1-2 weeks each)
1. {action} — closes {control}
2. ...

## Hard Dependencies (requires architecture change)
1. {action} — closes {control}

## What a Security Reviewer Will Still Need to Check
{plain-text paragraph — the model does not replace a qualified security reviewer}
```

Include a clear disclaimer: this brief is a starting point. A qualified security reviewer must validate the architecture before claiming compliance.

## Phase 5: Claude Code + Cloud CLI Walkthrough (Optional)

If the user wants a hands-on path, offer a step-by-step walkthrough for using their AI coding tool with the cloud CLI to build the mapped infrastructure:

1. Install and authenticate the cloud CLI (AWS CLI, Azure CLI, or gcloud).
2. Use plan mode in the AI coding tool to describe the desired infrastructure in plain English, referencing the mapping table from Phase 2.
3. Have the tool generate and execute the setup commands one domain at a time, starting with identity and secrets (Domains 1 and 2 first, as they gate everything else).
4. Verify each domain's checklist before moving to the next.
5. Run a compliance readiness scan (using the cloud provider's native tool or a third-party scanner like ScoutSuite) and compare against the brief from Phase 4.

Remind the user: building infrastructure with an AI coding tool is faster but not self-certifying. Every resource created needs manual review and tagging before it touches production data.

## Output Format Summary

```
ENTERPRISE AI OS PORT — {cloud provider or cloud-agnostic}
===============================================================
Current setup summary: {1-2 sentences}

COMPONENT MAPPING
{table from Phase 2}

SECURITY DOMAIN CHECKLIST
{six-domain checklist from Phase 3, with current-state assessments}

COMPLIANCE REMEDIATION BRIEF
{brief from Phase 4}

RECOMMENDED NEXT STEP
{one concrete action — e.g., "Start with IAM roles and Secrets Manager, then move to audit logging.
These two domains are prerequisites for the others and can be stood up in under a day."}
===============================================================
```

## What This Skill Does Not Do

- Does not generate working infrastructure-as-code (Terraform, CloudFormation, Bicep). Use Phase 5's CLI-driven approach or a dedicated IaC tool for that.
- Does not replace a qualified cloud architect or security reviewer.
- Does not evaluate specific vendor pricing or negotiate enterprise contracts.
- Does not cover multi-region replication, disaster recovery, or SLA engineering beyond the six domains.

## Verification

A good output from this skill:
- Maps every component the user described to a concrete cloud equivalent
- Produces a current-state assessment for all six domains (not just lists them)
- Flags the compliance controls that are actually failing, not a generic checklist
- Ends with one concrete next step that a developer can execute today

## Source

Extracted from Mark Kashef, "Claude Code + AWS Bedrock = Enterprise AI" (YouTube, 2026-06-25).
Video ID: T17DYl_4Z-U. Channel: UCHkzp52CldSPZqU5T49mOnA.
Technique: Personal-to-enterprise agentic OS mapping via cloud service substitution, six security domain framework, and compliance remediation brief pattern.
