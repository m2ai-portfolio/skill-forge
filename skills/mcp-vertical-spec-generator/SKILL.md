---
name: mcp-vertical-spec-generator
description: Generates a complete, buildable MCP server specification for named industry-vertical software — GoHighLevel, Follow Up Boss, WellSky, AppFolio, Clio, athenahealth, ServiceTitan — using known API patterns and vertical-specific data models. Use when the user says "spec an MCP for GoHighLevel", "build a Follow Up Boss MCP", "connect Claude to [vertical CRM/EMS/PMS]", or when a client needs a custom connector for proprietary or vertical-specific software.
---

# MCP Vertical Spec Generator

Extends `mcp-spec-generator` with deep knowledge of industry-specific software schemas and auth patterns. Vertical software often has non-obvious data models (WellSky's EVV compliance requirements, GoHighLevel's sub-account architecture, Clio's matter-centric object graph) that generic spec generation misses. This skill encodes those patterns.

**Relationship to `mcp-spec-generator`:** This skill IS `mcp-spec-generator` with a vertical pre-processing layer. For any unlisted software, fall back to `mcp-spec-generator` directly.

---

## Supported Verticals

### Real Estate

**GoHighLevel (GHL)**
- Architecture: Agency account → sub-accounts (one per client). Every API call scopes to a `locationId`.
- Primary objects: Contact, Opportunity (deal), Pipeline, Campaign, Conversation, Appointment
- Auth: OAuth 2.0 per sub-account; Agency-level key for provisioning
- Key agent workflows: lead routing, follow-up sequence enrollment, opportunity stage updates
- MCP priority tools: `get_contact`, `update_opportunity_stage`, `create_appointment`, `add_contact_tag`, `send_sms`, `get_pipeline_opportunities`
- Rate limits: 100 req/10s per location

**Follow Up Boss (FUB)**
- Primary objects: Person (contact), Deal, Task, Event, Stage
- Auth: API Key (basic auth, key as username)
- Key agent workflows: lead assignment, stage progression, drip campaign enrollment
- MCP priority tools: `get_person`, `update_deal_stage`, `create_task`, `assign_person`, `list_people_by_stage`
- Notable: FUB uses "events" (not webhooks) for real-time triggers — agents poll or use FUB's webhook→HTTP push

---

### Home Care / Senior Services

**WellSky (formerly Kinnser)**
- Regulatory context: EVV (Electronic Visit Verification) data must be preserved; HIPAA BAA required
- Primary objects: Client, Episode, Visit, Caregiver, Schedule, Billing Record
- Auth: OAuth 2.0; requires WellSky partner agreement for API access
- Key agent workflows: visit scheduling, caregiver assignment, billing code validation, EVV compliance checks
- MCP priority tools: `get_client`, `schedule_visit`, `assign_caregiver`, `validate_evv_record`, `get_billing_status`
- Compliance note: Flag `[SENSITIVE]` on any tool touching PHI; include audit log reads

---

### Legal

**Clio**
- Architecture: Matter-centric. Everything (documents, time entries, tasks, contacts) relates to a Matter.
- Primary objects: Matter, Contact, Document, TimeEntry, Task, CalendarEntry, Bill
- Auth: OAuth 2.0; user-level tokens (not org-level)
- Key agent workflows: matter intake, document assembly, time capture, billing draft
- MCP priority tools: `get_matter`, `create_document`, `create_time_entry`, `get_matter_documents`, `list_tasks_for_matter`, `create_bill_draft`
- Rate limits: 10 req/s; 429 responses include `Retry-After`

---

### Healthcare

**athenahealth**
- Regulatory context: HIPAA — all data is PHI; OAuth 2.0 with practice-specific `practiceId`
- Primary objects: Patient, Appointment, Encounter, Prescription, Insurance, Claim
- Auth: OAuth 2.0 (athenahealth partner program required)
- Key agent workflows: appointment scheduling, patient intake, prior auth status
- MCP priority tools: `get_patient`, `schedule_appointment`, `get_appointment`, `create_encounter_note`, `check_insurance_eligibility`
- Compliance note: Every tool is `[SENSITIVE]`; include `audit_log` tool in spec

---

### Field Service / Trades

**ServiceTitan**
- Architecture: Tenant-per-business; job-centric (jobs are the primary work unit)
- Primary objects: Customer, Location, Job, Estimate, Invoice, Technician, Campaign
- Auth: OAuth 2.0 (ServiceTitan partner API; application key + tenant key)
- Key agent workflows: job scheduling, estimate generation, invoice processing, technician dispatch
- MCP priority tools: `get_job`, `create_job`, `assign_technician`, `get_estimate`, `create_invoice`, `list_open_jobs_by_technician`

---

### Property Management

**AppFolio**
- Primary objects: Unit, Tenant, Lease, WorkOrder, Owner, Transaction
- Auth: API key per property management company
- Key agent workflows: maintenance ticket routing, rent delinquency escalation, lease renewal
- MCP priority tools: `get_unit`, `get_tenant`, `create_work_order`, `get_lease`, `list_delinquent_tenants`, `send_owner_statement`

---

## Spec Generation Process

### Step 1: Identify the vertical and software

If the software is in the supported list above, load the vertical context automatically.
If not listed, ask: "Is there public API documentation for this tool? If so, provide the URL or key schema details."

### Step 2: Clarify the agent workflows

Ask: "What will the agent *do* with this connector? List 2–3 workflows."
Map the workflows to the priority tools for that vertical.

### Step 3: Generate the spec

Follow the full `mcp-spec-generator` Phase 2–6 process, but pre-populate:
- Core data model from the vertical knowledge above
- Tool list seeded from priority tools (add/trim per stated workflows)
- Auth section with the specific mechanism and known scopes
- Compliance flags pre-applied for regulated verticals (HIPAA, EVV)

### Step 4: Flag compliance requirements

For WellSky, athenahealth, or any healthcare tool:
- Add `[SENSITIVE]` to every tool touching patient data
- Include `get_audit_log` in the Read Operations
- Note: "Deployment requires HIPAA BAA with the API provider"

For Clio and legal matter data:
- Add `[PRIVILEGED]` annotation where matter content may be privileged
- Note: "Token is user-scoped — each attorney needs their own auth"

---

## Output Format

Same as `mcp-spec-generator` Phase 6, with an added section:

```markdown
## Vertical Compliance Notes
{Any regulatory flags, data classification, auth constraints specific to this software}

## Known API Quirks
{Documented gotchas: rate limit patterns, pagination shape, common 4xx causes}

## Estimated Build Complexity
{S / M / L — with brief justification}
{Estimated hours for a TypeScript @modelcontextprotocol/sdk implementation}
```

---

## Pricing Reference (for client proposals)

| Vertical | Tool | Typical custom MCP build | M2AI rate reference |
|----------|------|--------------------------|---------------------|
| Real estate | GoHighLevel | $8,500 | Market: $65–$128/hr |
| Real estate | Follow Up Boss | $6,500 | |
| Home care | WellSky | $12,000–$15,000 (compliance overhead) | |
| Legal | Clio | $8,500 | |
| Healthcare | athenahealth | $15,000+ (HIPAA) | |
| Field service | ServiceTitan | $10,000 | |
| Property mgmt | AppFolio | $8,500 | |

Use these ranges in the `cowork-launchpad-assessment` skill when quoting Custom MCP builds.

---

## Source

Intake: `cowork-2026-06-07.md` — Derived from Freelance Market Intelligence Report (Section 5: MCP Server Development is fastest-growing category; Section 4: vertical specialists charge $8,500+/connector; Section 6: industry verticals). Extends existing `mcp-spec-generator` (skill-forge) with vertical pre-loading to reduce spec time from ~90 min to ~20 min per connector.
