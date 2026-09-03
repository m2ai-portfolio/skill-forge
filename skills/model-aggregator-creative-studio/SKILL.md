---
name: model-aggregator-creative-studio
description: Build a self-owned creative generation interface that routes prompts to any of dozens of image/video generation models through a model-aggregator API instead of a single-vendor subscription (e.g. Higgsfield). Adds a meta-prompting refinement step that reads each target model's documentation or model card to rewrite a vague user prompt into an optimized, model-specific prompt before sending the request. Use when a user is paying for a locked, single-vendor creative subscription and wants transparent per-call cost, model choice, and control over the interface and routing layer.
---

# Model-Aggregator Creative Studio

## Trigger pattern

Use this skill when someone wants to:
- Replace a fixed-price, single-vendor image/video generation subscription with pay-as-you-go access to many models
- Own the prompt-routing and cost-tracking layer instead of depending on a vendor's roadmap and pricing
- Give an AI coding agent (Claude Code, Codex, or similar) the ability to call arbitrary generation models from inside a terminal, MCP, or custom UI

## Prerequisites

- An account and API key with a model-aggregator service (a provider that indexes many labs' image/video models behind one API and keeps its catalog current), OR direct API keys for the specific model vendors you want to use (e.g. a video model, an image model)
- An AI coding agent capable of writing HTTP client code and reading web documentation
- Basic budget for pay-as-you-go generation credits

## Complexity

Intermediate — no novel infrastructure, but requires wiring together API discovery, a meta-prompting step, and a cost ledger correctly.

## Procedure

1. **Choose a routing path.**
   - Path A — Aggregator: sign up with a model-aggregator provider that maintains an up-to-date catalog of image/video models, their required inputs, and per-model parameters (resolution, duration, bitrate, start/end frame support, etc.). This is the lower-effort path since the aggregator already normalizes each model's parameter differences.
   - Path B — Direct vendor: for each specific model you want (e.g. a named video or image model), pull that vendor's official API documentation page, convert it to markdown, and feed the full page to your coding agent so it can generate a correct request builder for that model.

2. **Build (or have the agent build) a thin UI or CLI** that:
   - Accepts a source asset (image/video) as optional input
   - Accepts a plain-language task description (e.g. "UGC ad demoing this product")
   - Lets the user pick a target model from the catalog
   - Displays only the parameters relevant to the chosen model (parameters differ per model — a video-length field with no meaning for an image model should not appear)

3. **Add the meta-prompting refinement step.** Before sending the user's vague prompt to the generation model:
   - Fetch or cache that model's own prompting guidance (a model/system card, "tips for prompting X" doc, or vendor best-practices page)
   - Use a cheap, fast model (a small/flash-tier model is sufficient) to rewrite the user's prompt into one optimized for the target model, using that guidance as context
   - Send the rewritten prompt, not the raw one, to the generation model

4. **Add a cost ledger.** Before each generation call, estimate cost from the aggregator's pricing (or the vendor's published per-second/per-image rate) and display it. After the call, log actual spend. This is the main advantage over a subscription: full visibility into what each generation costs.

5. **Wire it into your coding agent as a connector.** Expose the same routing/generation logic as an MCP server or CLI tool so Claude Code, Codex, or another agent session can invoke "generate a video/image of X using model Y" directly, without a separate UI.

## Verification

- Confirm the interface can generate at least one asset via two different underlying models (proves the routing layer, not just one hardcoded model, works)
- Confirm the meta-prompting step actually changes the prompt sent to the model (log both the raw and refined prompt and diff them)
- Confirm the cost ledger's pre-call estimate is within a reasonable margin of the actual post-call charge

## Common pitfalls

- Treating every model's parameter set as identical — video length, resolution, and start/end-frame support vary per model and must be looked up per model, not assumed
- Skipping the meta-prompting step: a generic prompt sent to a specialized model tends to underperform a prompt tuned for that model's known quirks
- Not tracking spend before generation: pay-as-you-go is only an advantage over a subscription if the cost is visible before the call, not just after

## Source attribution

- Derived from a YouTube video by Mark Kashef (channel ID `UCHkzp52CldSPZqU5T49mOnA`), published 2026-08-15, describing a personal creative-studio build that routes prompts across dozens of generation models via aggregator and direct-vendor APIs.
