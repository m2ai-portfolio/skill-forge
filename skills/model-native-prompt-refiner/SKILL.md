---
name: model-native-prompt-refiner
description: Rewrite a vague generation prompt into a model-native one by grounding it in the target model's own official prompting guide, parameter schema, and cost table before any generation runs. Use when a request names a specific image, video, or text model (Veo, Kling, Minimax, Seedance, Flux, or any versioned model id), when switching a working prompt from one model to another, when a generation returns off-spec output and the prompt is suspect, or when the user says "refine this prompt", "optimize this prompt for <model>", "port this prompt to <model>", or "what parameters does this model take".
---

# Model-Native Prompt Refiner

A vague prompt plus the wrong parameter set is the most common cause of a wasted paid generation. This skill closes that gap: before anything is generated, it fetches what the model's own provider says about prompting it, rewrites the prompt against that guidance, validates every parameter against the model's actual supported set, and prints a cost estimate the user approves.

The core move is meta-prompting with a citation requirement. Do not rewrite a prompt from recalled knowledge of how a model behaves. Model prompting guidance changes between versions, and a prompt tuned for `model-v2` is frequently wrong for `model-v3`.

## Trigger

Use when:
- A generation request names a specific model or model version.
- A working prompt needs to move from one model to another.
- Output came back off-spec (wrong duration, ignored subject, wrong aspect ratio) and the prompt or parameters are the suspect.
- The user asks what parameters a model takes, or asks for a cost estimate before generating.

Do not use when the model is unspecified and the user has not asked to pick one. Resolve the model first.

## Phase 1: Pin the target

Establish three facts and state them back before doing anything else:

1. **Exact model id and version.** `veo-3.1-fast` is a different model from `veo-3.1`. Never normalize a version away.
2. **Access path.** Direct provider API, or an aggregator that resells many models behind one endpoint. This changes both the parameter names and the price.
3. **Modality and input shape.** Text-only, image-conditioned, first-frame/last-frame, video-to-video. The input shape drives half the parameter set.

If the user named a model that does not resolve to a real, currently listed model id, stop and say so. Do not substitute the nearest name you recognize.

## Phase 2: Ground in the provider's own documentation

Fetch, do not recall. Pull the provider's current material for this model:

- The **prompting guide** for the modality (video generation, image generation, and so on). Providers publish concrete prompt structure advice per model family.
- The **model card / system card**, which states strengths, refusal behavior, and known weaknesses.
- The **parameter reference**, which is the authoritative list of what the model accepts.

Convert the page to markdown and read the whole thing rather than skimming headings. Record the retrieval date alongside the model id, because both go stale.

If documentation is unreachable, say so explicitly and continue in degraded mode with an explicit `unverified` marker on every claim about the model. Do not silently fall back to memory.

## Phase 3: Build the parameter table

Extract the model's actual parameters into a table with four columns: parameter, required or optional, allowed range or enum, and default. Two rules make this useful rather than decorative:

- **Parameters are per model, not per provider.** A parameter that exists on one model in a family often does not exist on its sibling. If a parameter is not in this model's reference, it is not a valid parameter, even if the same provider accepts it elsewhere.
- **Every constraint is a hard constraint.** Clip length, resolution, aspect ratio, and bitrate are model-imposed. A prompt asking for 12 seconds against an 8-second ceiling fails or silently truncates.

Flag any parameter the user's request implies but the model does not support, and name the closest supported alternative.

## Phase 4: Rewrite the prompt against the guidance

Now rewrite. The refined prompt must satisfy all of:

- **Structured to the provider's own recommended shape**, not to a generic template. If the guide asks for subject, action, camera, lighting, and audio as distinct beats, produce those beats.
- **Every documented constraint respected** (character limits, negative-prompt syntax, reference-image token syntax, forbidden constructions).
- **User intent preserved.** Refinement adds specificity the model can act on. It does not add subject matter the user never asked for. If the original prompt is genuinely underspecified, list the assumptions inline rather than burying invented detail in the prose.
- **Traceable.** For each significant change, cite the guidance line that motivated it. A change you cannot cite is a change you guessed at.

Use a cheap, fast model for the rewrite itself. This is a mechanical transformation against retrieved text, not a reasoning task, and paying frontier rates for it defeats the cost savings the skill exists to produce.

## Phase 5: Estimate cost, then stop

Before generating, print:

- Model id and access path.
- The per-unit price and the pricing unit as documented (per second, per clip, per megapixel, per 1k tokens).
- The estimated cost of this specific generation with the chosen parameters.
- A running total if this is part of a batch.

If the price is not documented or not retrievable, say `cost unknown` rather than estimating. A fabricated number is worse than an absent one.

**Hand control back to the user here.** This skill produces a refined prompt, a validated parameter set, and a cost estimate. It does not generate. Generation is a separate, explicitly approved step.

## Output format

```
MODEL:      <exact id>  (docs retrieved <YYYY-MM-DD>)
ACCESS:     <direct provider | aggregator name>
MODALITY:   <text2video | image2video | text2image | ...>

PARAMETERS
  <param>  <required?>  <range/enum>  <chosen value>  <source: doc section>
  ...
  UNSUPPORTED REQUEST: <what the user asked for that this model cannot do, and the nearest alternative>

REFINED PROMPT
  <the rewritten prompt, in the provider's recommended structure>

CHANGES
  <change>  <-  <guidance line that motivated it>
  ...

ASSUMPTIONS
  <detail added that the user did not specify>

COST
  <unit price> x <units> = <estimate>   |   cost unknown

NEXT: awaiting approval to generate.
```

## Verification

The run is correct when all of these hold:

1. The exact model id and the documentation retrieval date both appear in the output.
2. Every parameter in the table traces to a line in the retrieved reference, and no parameter appears that is absent from it.
3. Every entry in CHANGES cites a specific piece of retrieved guidance. Zero uncited changes.
4. Any user request the model cannot satisfy appears under UNSUPPORTED REQUEST rather than being silently dropped.
5. The cost line shows either a computed estimate from a documented price, or the literal string `cost unknown`. Never an invented figure.
6. No generation was executed.

A run that produces a beautiful prompt with no citations has failed. The citations are the deliverable that makes the prompt trustworthy.

## Failure modes this prevents

| Failure | Cause | Caught by |
|---|---|---|
| Parameter rejected by the API | Parameter copied from a sibling model | Phase 3 |
| Output silently truncated | Duration exceeded the model ceiling | Phase 3 |
| Prompt style ignored by the model | Generic template instead of the provider's structure | Phase 4 |
| Prompt drifted from user intent | Refiner invented subject matter | Phase 4, ASSUMPTIONS |
| Surprise bill | Generated before pricing was checked | Phase 5 |
| Confidently wrong guidance | Rewrote from memory of an older model version | Phase 2 |

## Source

Technique extracted from Mark Kashef, "This Simple AI Setup Replaces Your Higgsfield Subscription" (YouTube, 2026-08-15). The video builds a self-owned creative studio over model aggregators and direct provider APIs; the transferable core is its prompt-refinement step, which reads the target model's own documentation and system card to decide how to rewrite a vague prompt, plus the pre-generation cost forecast that makes pay-as-you-go legible.
