---
name: setup-marketing-agents
description: Interactive guide for setting up the M2AI marketing agent pack (Creator, Scout, RepMan, LeadGen, Analytics, AdOps). Walks through agent roles, required skills, platform integrations, and Tier 2 prerequisites. Use when onboarding a collaborator or client onto the marketing agent system.
user_invocable: true
allowed-tools: Bash(*), Read(*), Write(*), Edit(*), Glob(*), Grep(*)
---

# /setup-marketing-agents -- Marketing Agent Setup Guide

Interactive setup guide for the M2AI marketing agent pack. Designed for trades and service businesses (contractors, kitchen fitters, bathroom specialists, etc.) but adaptable to any local service business.

This skill walks you through what each agent does, what skills it needs, and what platform integrations are required to make it work.

## Overview

There are 6 marketing agents split into two tiers:

| Agent | Tier | Purpose |
|-------|------|---------|
| **Creator** | 1 (Ready) | Social posts, SEO blogs, case studies, content calendars |
| **Scout** | 1 (Ready) | Competitor monitoring, market research, directory audits |
| **RepMan** | 1 (Ready) | Review monitoring, response drafting, directory management |
| **LeadGen** | 2 (Needs integrations) | Lead response, CRM logging, follow-up sequences |
| **Analytics** | 2 (Needs integrations) | Performance snapshots, channel attribution, reporting |
| **AdOps** | 2 (Needs integrations) | Ad monitoring, budget management, creative refresh |

**Tier 1** agents work immediately with web search and file tools. No external API keys or platform accounts needed.

**Tier 2** agents have full skill definitions and system prompts ready, but need platform API integrations (CRM, Google Ads, Meta Ads, GA4) before they can execute autonomously.

## Step 1: Understand Your Starting Point

Ask the user these questions before proceeding:

1. **What AI assistant platform are you using?** (ClaudeClaw, Claude Code standalone, custom agent framework, other)
2. **Which agents do you want to set up first?** (Show the table above, recommend starting with Tier 1)
3. **What's your business type and location?** (Needed to customise the agent prompts -- e.g. "kitchen fitter in Coventry" vs "general contractor in Austin")

Based on answers, proceed to the relevant sections below.

## Step 2: Tier 1 Agent Setup

### Creator -- Content Creation Agent

**What it does:**
- Creates platform-specific social media posts (Facebook, Instagram, LinkedIn)
- Writes SEO blog posts targeting local keywords
- Produces case studies from completed projects (before/after, testimonial, scope)
- Builds weekly content calendars based on performance and seasonal trends
- Repurposes a single photo or piece of content into multiple formats

**Skills to configure:**

| Skill | Description | Example Prompt |
|-------|-------------|----------------|
| `social-post` | Platform-specific social posts from photos/updates | "Write a Facebook post showcasing this kitchen renovation" |
| `blog-seo` | SEO blog posts targeting local keywords | "Write a blog post targeting 'kitchen fitter near [city]'" |
| `case-study` | Project case studies with scope, before/after, testimonial | "Write a case study for the Johnson bathroom refit" |
| `content-calendar` | Weekly content calendar from performance data | "Build next week's content calendar" |
| `repurpose` | One asset into multiple formats (post, reel script, carousel) | "Turn this project photo into 5 different social posts" |

**Key system prompt rules for this agent:**
- All SEO content targets LOCAL keywords (city/region + service). National generic keywords are useless for local trades.
- Content calendar mix: project showcases 40%, educational/tips 25%, testimonials 20%, behind-the-scenes 15%
- Blog target: 800-1200 words with H1 (keyword), intro (keyword in first para), 3-5 H2 sections, local signals, CTA, meta description
- Platform formatting: Facebook (emoji sparingly, line breaks), Instagram (15-20 hashtags at end), LinkedIn (3-5 hashtags max, professional)
- Always include a CTA in every piece of content

**Tools needed:** Web search (for keyword research, competitor content review), file read/write (for saving drafts)

**No external integrations required.** This agent generates content as text output. Posting to platforms is manual (or via a later social media API integration).

---

### Scout -- Competitive Intelligence Agent

**What it does:**
- Scans competitor online presence (social posts, reviews, ads, website)
- Produces weekly competitive landscape snapshots
- Audits directory listings across platforms (Checkatrade, MyBuilder, Bark, Houzz, Yell)
- Researches competitor pricing signals and positioning

**Skills to configure:**

| Skill | Description | Example Prompt |
|-------|-------------|----------------|
| `competitor-scan` | Scan a competitor's posts, reviews, ads | "Check what ABC Kitchens posted this week" |
| `market-snapshot` | Weekly competitive landscape summary | "Weekly competitor roundup" |
| `directory-audit` | Compare directory listings across platforms | "Audit our listings vs competitors on Checkatrade" |
| `pricing-intel` | Research competitor pricing and positioning | "What are competitors charging for bathroom refits?" |

**Key system prompt rules:**
- Cross-reference 2+ sources before stating competitor claims as fact
- Always cite URLs and date-stamp findings (competitive intel decays fast)
- Focus on ACTIONABLE insights, not data dumps
- Weekly snapshot format: table (Competitor | New Reviews | Avg Rating | Social Posts | Notable Activity) + Top Insight + Threats + Opportunities

**Tools needed:** Web search, web fetch/scrape (for review platforms, social pages, directory listings)

**No external integrations required.** All research done via public web sources.

**Customisation needed:** Add specific competitor names and your business's directory profile URLs to the system prompt so the agent knows who to track.

---

### RepMan -- Reputation Management Agent

**What it does:**
- Monitors Google reviews and other review platforms for new reviews
- Drafts professional responses to positive and negative reviews
- Generates personalised review request messages for completed jobs
- Audits directory listings for NAP (Name, Address, Phone) consistency
- Monitors Google Business Profile Q&A

**Skills to configure:**

| Skill | Description | Example Prompt |
|-------|-------------|----------------|
| `review-monitor` | Check for new reviews, rating changes, sentiment trends | "Check for new Google reviews this week" |
| `review-respond` | Draft on-brand responses to reviews | "Draft a response to this 5-star kitchen review" |
| `review-request` | Generate personalised review request messages | "Write a review request for the Smith kitchen project" |
| `directory-manage` | Audit directory listings for consistency | "Audit all our directory listings" |
| `gbp-manage` | Monitor and draft GBP Q&A responses and posts | "Check for new GBP questions" |

**Key system prompt rules:**
- ALL review responses are DRAFTS -- never auto-post. Label them "DRAFT -- Review before posting"
- Positive reviews: thank by name, reference specific project, under 100 words
- Negative reviews: acknowledge, take offline ("please contact us at..."), NEVER argue or offer compensation publicly, under 80 words
- Review requests: personal, reference the specific job, SMS version under 160 chars
- Directory audit format: Platform | Listed? | NAP Correct? | Services Current? | Photos? | Action

**Tools needed:** Web search, web fetch (for checking review platforms, GBP, directories)

**No external integrations required.** Monitoring is via web search; responses are drafted as text for human review and posting.

**CRITICAL: Human-in-the-loop gate.** This agent should NEVER post directly. All review responses and GBP answers must be approved by the business owner before posting.

---

## Step 3: Tier 2 Agent Prerequisites

These agents have full skill definitions and system prompts ready, but each needs specific platform integrations before they can execute autonomously. Until those integrations are in place, they still work as **advisory agents** -- you can give them data and they'll produce analysis, templates, and recommendations.

### LeadGen -- Lead Response & CRM Agent

**What it does (when fully integrated):**
- Responds to inbound leads within minutes (website, social DMs, email)
- Logs leads into CRM with source, service interest, follow-up schedule
- Generates and schedules follow-up message sequences
- Qualifies leads by extracting budget, timeline, scope, location

**What it can do NOW (without integrations):**
- Draft lead response templates for different channels (website, social, email)
- Write follow-up message sequences (Day 0, 2, 5, 14)
- Score/qualify leads from pasted enquiry text
- Structure lead data for manual CRM entry

**Integrations needed:**

| Integration | Purpose | Options |
|------------|---------|---------|
| **CRM** | Lead logging, pipeline tracking, follow-up automation | HubSpot API, Pipedrive API, Salesforce API, or a lightweight CRM MCP server |
| **Email** | Reading inbound enquiries, sending responses | Gmail API, Outlook API, or SMTP/IMAP |
| **Social DM inbox** | Reading and responding to social messages | Meta Business Suite API (Facebook/Instagram DMs) |

**Minimum viable integration:** CRM + Email. Social DM inbox is a nice-to-have -- most serious leads move to email/phone quickly.

**Key system prompt rules:**
- Speed matters: templates optimised for sub-5-minute response
- Never promise pricing in initial responses
- Follow-up sequence: Day 0 (acknowledge + qualify), Day 2 (value add -- share project photo), Day 5 (gentle nudge), Day 14 (last chance)
- Lead qualification scoring: Budget signal (high weight), Timeline (high), Scope clarity (medium), Location (medium), Source (low)

---

### Analytics -- Marketing Analytics & Reporting Agent

**What it does (when fully integrated):**
- Pulls weekly performance snapshots (leads, cost per lead, traffic, engagement)
- Measures channel attribution (which channels drive booked jobs, not just leads)
- Generates campaign performance reports
- Recommends budget allocation based on ROI data

**What it can do NOW (without integrations):**
- Structure report templates for manual data input
- Analyse data pasted into conversation (CSV, numbers)
- Produce formatted comparison reports from raw data
- Apply budget recommendation frameworks

**Integrations needed:**

| Integration | Purpose | Options |
|------------|---------|---------|
| **Google Analytics (GA4)** | Website traffic, conversion tracking | GA4 Data API |
| **Google Ads** | PPC performance, cost per lead | Google Ads API |
| **Meta Ads** | Facebook/Instagram ad performance | Meta Marketing API |
| **CRM** | Lead-to-job conversion data (the critical metric) | Same as LeadGen CRM |

**Minimum viable integration:** GA4 + CRM. Without CRM conversion data, you can only measure leads, not booked jobs -- and cost per lead is a vanity metric.

**Key system prompt rules:**
- Distinguish LEADS from BOOKED JOBS. Cost per booked job is the metric that matters.
- Always compare to baseline (last week, last month, same period last year)
- Channel attribution verdicts: Scale, Maintain, Optimise, Reduce, Pause
- Flag anomalies prominently (sudden traffic spikes, cost jumps, conversion drops)

---

### AdOps -- Paid Advertising Operations Agent

**What it does (when fully integrated):**
- Monitors active ad campaigns for performance issues and budget pacing
- Pauses underperformers, adjusts bids/budgets
- Drafts new ad copy when fatigue metrics indicate refresh needed
- Plans and structures new campaigns with targeting and budget recommendations

**What it can do NOW (without integrations):**
- Draft ad copy (Google RSA headlines, Facebook ad text, creative briefs)
- Plan campaign structures and targeting strategies
- Check Facebook Ad Library for competitor ads (via web search)
- Analyse performance data provided in conversation

**Integrations needed:**

| Integration | Purpose | Options |
|------------|---------|---------|
| **Google Ads API** | Campaign management, bid/budget adjustments, performance data | Google Ads API (requires developer token + MCC account) |
| **Meta Marketing API** | Facebook/Instagram ad management | Meta Business Suite + Marketing API access |

**Minimum viable integration:** One ad platform (whichever they spend more on). Google Ads API has a steeper setup (developer token application) but is typically higher ROI for trades businesses.

**Key system prompt rules:**
- ALL budget changes are RECOMMENDATIONS until human-confirmed. Never auto-adjust.
- Google RSA limits: headlines 30 chars, descriptions 90 chars
- Facebook: 125 chars visible before "See more"
- Creative fatigue signals: CTR decline >20% over 2 weeks, frequency >3.0, CPA >30% above target
- Never change more than 20% of budget per day (resets learning phase)

---

## Step 4: Customisation Checklist

After setting up agents, the business owner should customise:

1. **Business name and location** -- Replace placeholder cities/regions with actual service area
2. **Brand voice** -- Add a voice guide or tone notes to each agent's system prompt (default: professional but approachable)
3. **Competitor list** -- Add 3-5 specific competitors to Scout's configuration
4. **Directory platforms** -- Adjust for country:
   - UK: Checkatrade, MyBuilder, Bark, Houzz, TrustATrader, Yell
   - US: Yelp, Angi, HomeAdvisor, Houzz, BBB, Thumbtack
   - AU: hipages, ServiceSeeking, Houzz, Yellow Pages
5. **Review platforms** -- Which platforms the business actively uses (Google, Checkatrade, Trustpilot, etc.)
6. **CTA preferences** -- Default call-to-action style (phone call, WhatsApp, email, web form)

## Step 5: Recommended Setup Order

1. **Start with Creator** -- Immediate value, no integrations, tangible output from day one
2. **Add Scout** -- Gives competitive context that informs Creator's content strategy
3. **Add RepMan** -- Review management is high-impact and time-sensitive
4. **Set up CRM integration** -- Unlocks LeadGen (biggest revenue impact of all Tier 2 agents)
5. **Connect analytics platforms** -- Unlocks Analytics for data-driven decisions
6. **Connect ad platforms** -- Unlocks AdOps (only worth it if actively running paid ads)

## Integration Priority Matrix

For Tier 2, here's where to invest integration effort first based on business impact:

| Integration | Unlocks | Business Impact | Setup Complexity |
|------------|---------|----------------|-----------------|
| CRM (HubSpot/Pipedrive) | LeadGen + Analytics attribution | **HIGH** -- faster lead response = more conversions | Medium |
| Gmail/Email API | LeadGen inbound + outbound | **HIGH** -- automates the most time-consuming part | Low |
| GA4 | Analytics website metrics | **MEDIUM** -- insight, not direct revenue | Low |
| Google Ads API | AdOps + Analytics ad data | **MEDIUM** -- only if running Google Ads | High (developer token) |
| Meta Marketing API | AdOps + Analytics social ads | **MEDIUM** -- only if running Facebook/IG ads | Medium |
| Social DM inbox | LeadGen social responses | **LOW** -- most leads move to email/phone | High (Meta Business verification) |
