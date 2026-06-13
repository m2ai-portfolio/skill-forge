---
name: image-generation-gateway
description: Route any image generation request through a single configured gateway. Eliminates per-tool hardcoding; every image workflow calls one skill, which dispatches to the configured provider (Flux, DALL-E, Imagen, or any MCP-connected image tool).
---

# Image Generation Gateway

A thin dispatch layer that routes image generation requests to whichever provider is configured in the current session. Instead of every workflow hardcoding a specific image tool, all requests flow through this gateway — making provider swaps a one-place change.

## Trigger

Use when the user says "generate an image", "create an image", "produce a visual", invokes any workflow that needs image output, or when configuring a shared image generation entry point for the session.

## Phase 1: Detect Available Provider

Check which image generation tool is available in the current session by probing in priority order:

1. Any MCP-connected image tool (check session tool list for tools named `generate_image`, `create_image`, `image`, or similar)
2. Environment variable `IMAGE_GATEWAY_PROVIDER` (values: `flux`, `dalle`, `imagen`, `replicate`, `custom`)
3. Fall back to describing the image generation prompt so the user can copy-paste it to their preferred tool

If no provider is found, output: "No image provider detected. Set `IMAGE_GATEWAY_PROVIDER` in your environment or connect an image generation MCP tool."

## Phase 2: Normalize the Request

Accept the image request in any of these forms and normalize to a structured prompt:

- Free-form description: "a sunset over mountains in watercolor style"
- Structured object: `{ subject, style, dimensions, quality, negative_prompt }`
- Downstream request from another skill (e.g., from a content pipeline or design workflow)

Normalized format:
```
SUBJECT: {what to depict}
STYLE: {visual style, e.g., "photorealistic", "flat illustration", "watercolor"}
DIMENSIONS: {width x height, default 1024x1024}
QUALITY: {standard | high | ultra, default standard}
NEGATIVE: {what to avoid, optional}
FULL_PROMPT: {assembled prompt string ready to send to provider}
```

## Phase 3: Dispatch

Send the normalized prompt to the detected provider using the provider's native tool call or API.

On success, return:
- The image (inline or as a file path)
- The provider used
- The full prompt sent (for reproducibility)
- Output path if saved to disk (default: `./generated-{timestamp}.png` or provider default)

On failure, return the error verbatim and suggest the fallback: "Copy `FULL_PROMPT` to your image tool of choice."

## Phase 4: Confirm and Route

If the image was generated as part of a larger workflow, confirm the output path with the caller and return a structured handoff:

```
IMAGE_PATH: {path or URL}
PROVIDER: {which tool was used}
PROMPT_USED: {full prompt, for reproducibility}
```

## Configuration

Set `IMAGE_GATEWAY_PROVIDER` in your environment to pin a provider:
```
export IMAGE_GATEWAY_PROVIDER=flux
```

Supported values: `flux`, `dalle`, `imagen`, `replicate`, `custom`. If `custom`, the skill expects an MCP tool named `generate_image` to be present in the session.

## What This Does NOT Do

- Does not own visual style decisions — it routes what it receives.
- Does not retry on rate limits — the caller is responsible for retry logic.
- Does not watermark or post-process images.
- Does not store credentials — API keys must be in the environment before invocation.

## Source

Extracted from Nate Kadlac newsletter (2026-06-12): "Grab my Ultimate Guide to Codex and catch up to the 1 in 1,600 people using it every week." Idea 1: "One fixed-once image API connection shared by every image workflow." Category: Core Infrastructure Skills.
