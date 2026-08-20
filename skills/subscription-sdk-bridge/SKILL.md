---
name: subscription-sdk-bridge
description: Replace the pay-per-call API-key layer in a self-built internal tool with a headless bridge to an AI coding-agent subscription you already pay for (Codex SDK via cached ChatGPT login, or Claude Agent SDK via Claude Code login), so every request runs on the flat subscription instead of metered credits. Use when the user says "stop paying API costs for my internal app", "use my Codex/Claude subscription as the backend", "swap the API key for the SDK", "headless agent behind my tool", or is vibe-coding an internal tool and asks how to avoid a second AI bill.
---

# Subscription SDK Bridge

Internal tools built with Claude Code, Codex, Lovable, or similar usually end with the same step: "add an API key." From then on every click in the tool is metered on a credit card, separate from the subscription that built it. This skill swaps that one layer. The tool stays the same; the AI calls go through the agent SDK, which reuses the cached login of the subscription already on the machine. No key, no meter.

The same approach applies to any subscription-backed agent runtime that exposes an SDK constructed with no arguments and resolves credentials from the local login: the Codex SDK (ChatGPT/Codex subscription) and the Claude Agent SDK (Claude Code login) are the two documented cases.

## Phase 0: Eligibility gate (do this first, do not skip)

Both SDKs' terms restrict subscription-backed use to **personal or internal** use. Ask and record the answer before building anything:

1. **Who uses the tool?** You, your team, your company internally: proceed. Paying customers, a public SaaS, or resold access: **stop**. That is a terms-of-service violation, and the correct layer for that product is a metered API key with its own billing.
2. **Which subscription is on this machine?** Run one of:
   - `codex --version` and confirm a prior `codex login` has succeeded (cached ChatGPT auth present)
   - `claude --version` and confirm a prior interactive Claude Code login
3. **Which runtime will the tool run on?** Node.js (TypeScript) is the primary SDK surface for both; confirm the host where the tool runs is the host with the cached login (a headless server with no login has nothing to bridge to).

If any answer is "no" or "unknown," resolve it here. The bridge only works where the login already lives.

## Phase 1: Map the swap point

Every AI-backed internal tool has the same shape:

```
UI / trigger  ->  app logic  ->  [AI call layer]  ->  model  ->  result
                                      ^
                                swap ONLY this
```

Inventory the tool's AI call sites:

| Find | Ask |
|------|-----|
| Every place an API key is read (`process.env.*_API_KEY`, config files, secret managers) | Which model(s), which capabilities (text, structured output, image generation)? |
| Every SDK client construction (`new OpenAI(...)`, `new Anthropic(...)`, raw `fetch` to a provider URL) | What effort/reasoning tier does the call expect? |
| Every place the result is parsed | Does the app expect streaming, JSON, or a file artifact? |

Write this as a short table in the project (e.g. `docs/ai-calls.md`). It is the contract the bridge must satisfy. Nothing else in the app changes.

## Phase 2: Build the bridge module

Create ONE module that owns all AI calls, e.g. `src/ai/bridge.ts`. Rules for the module:

1. **Construct the SDK client with no arguments.** The SDK locates the cached subscription auth itself. Do not pass a key, do not read a key from env, do not fall back to a key. If construction fails, surface "no cached login found, run `<cli> login` on this host" and stop.
2. **Expose the app's verbs, not the SDK's.** Functions like `summarizeMeeting(text, {model, effort})`, `generateThumbnail(brief)`, `classifyEmail(raw)`. Callers never touch the SDK directly, so a future SDK change is a one-file edit.
3. **Make model and effort tier parameters, with defaults in one config object.** Whatever models and effort levels the subscription grants are the menu; a new model that joins the subscription becomes available by changing a string.
4. **Headless means no interactive prompts.** Run the agent in non-interactive mode, set a working directory the tool owns, and pass the task context (the pasted text, the brief) as the prompt plus any files the task needs. Capture the final result, not the turn-by-turn transcript.
5. **Capabilities follow the subscription.** If the subscription's agent can generate images, the bridge can expose `generateImage(...)`; if it cannot, do not fake it with a keyed fallback (that silently re-introduces the meter).

Example prompt to hand your coding agent for the rewrite (adapt names):

> Refactor this app so that ALL AI calls go through `src/ai/bridge.ts`, which uses the <Codex SDK | Claude Agent SDK> constructed with no arguments and relies on my cached subscription login. There must be no API key anywhere: no env var, no config field, no fallback. Do not ask me for a key. Keep the existing function signatures the rest of the app calls. Model and effort must be parameters with defaults in one config object.

For a **net-new** tool, lead the build prompt with the same defining constraint before the spec: "The defining constraint: all AI calls go through the SDK using my cached login; there is no API key anywhere. Do not ask for one." Then give the architecture, file list, and run command as usual.

## Phase 3: Wire, run, share

1. `npm run dev` (or the tool's run command) on the host with the cached login.
2. Trigger one real request from the UI. Confirm in the terminal that the bridge spun up a headless agent session and returned the result to the UI.
3. Optional team access: put the host on a private mesh network (Tailscale or equivalent) and share the tool's mesh address with teammates. Each request still executes on the host's subscription; teammates need no login of their own. Keep this inside the internal-use boundary from Phase 0.

## Phase 4: Verification checklist

- [ ] `grep -ri "api_key\|apikey" src/` returns no live code paths (comments explaining the absence are fine)
- [ ] The SDK client is constructed with no arguments in exactly one module
- [ ] One end-to-end request from the UI completes with the provider's metered dashboard showing **zero** new usage
- [ ] Changing the default model string in the config object changes the model used on the next request
- [ ] Revoking or logging out of the subscription on the host makes the tool fail loudly with a "run `<cli> login`" message, not a silent fallback
- [ ] Phase 0 answer ("internal use only") is recorded in the repo README or docs

## When NOT to use this

- Customer-facing or resold products (terms violation; use a metered key)
- Hosts without a local login (CI runners, shared servers, serverless): nothing to bridge to
- Workloads where you need provider SLAs, rate-limit guarantees, or per-tenant billing: those are API features, not subscription features

## Source

Extracted from: "THIS AI Hack Could Save You Thousands" by Mark Kashef
URL: https://www.youtube.com/watch?v=JlXfoZvTwzk
Published: 2026-08-19
