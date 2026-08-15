---
name: local-agentic-web-studio
description: Build immersive, scroll-scrubbed 3D websites using a local agentic harness, skill routing, and a local video model, at zero API cost. Use when asked to "build a 3D website with local AI", "create an immersive website without APIs", "scroll-scrub website from a local video", "zero-cost website generation", or "local harness web design".
---

# Local Agentic Web Studio

Produces an immersive, scroll-scrubbed website from a hero video using only local models.
The harness skill-routes to a domain-specific web-building skill, extracts video frames as
scroll beats, self-corrects via browser-use, and delivers a finished site with zero API cost.

## When to Use

Trigger on:
- "build a 3D website with local AI"
- "create an immersive / scroll-scrubbed website"
- "zero-cost website from local video"
- "generate a website with local models"
- "Pi.dev web design" / "local harness website"

## Required Stack (Three Pieces)

All three must be running before invoking this skill.

| Component | Role | Recommended | Minimum |
|---|---|---|---|
| Local text harness | Runs the agentic loop, executes skills, calls browser-use | Pi.dev with skill-router added | Any harness with tool-use + file I/O |
| Local video model | Generates the hero clip | MiniMax H3 via ComfyUI | Any open-source video model reachable from ComfyUI |
| Local text model | Writes code, designs the site | Qwen 3.5 70B (LM Studio) | 15B parameter minimum; 4B/9B models will struggle |

**Hardware note**: video generation is the hardware bottleneck, not text. A hero clip at low
resolution takes 4+ hours on a high-end laptop; budget 1-2 days for higher quality. Generate
at your hardware's ceiling first, then upscale locally (free open-source upscalers close most
of the quality gap). A $2 cloud render of the same clip is the quality ceiling for comparison.

## Phase 1: Extend the Harness with a Skill Router

Before building anything, the harness needs a skill-routing function so the local LM can
select the right domain-specific skill for the task (immersive-web, editorial-web,
effects-menu, or any custom style you define).

**How to add skill routing** (do this once, not every run):

1. Ask your current AI session (cloud or local): "Read my harness config and add a
   skill-router function. It should accept a task description and return the matching
   skill file path from the skills/ directory."
2. Verify the router can list and select skills by name.
3. Add at minimum these three skills to the harness `skills/` directory:
   - `immersive-web`: scroll-scrubbed parallax site using video frames as beats
   - `editorial-web`: long-form editorial layout with prose + image sections
   - `effects-menu`: animation effects library the LM can compose into any site

The skill files are plain text describing the technique, constraints, and examples for
that style. Pull from existing open-source web animation repos and distill them into a
single file the LM can read at prompt time.

## Phase 2: Generate the Hero Video

The hero video is the only visual asset the site needs. All other images come from its
frames.

**Workflow**:
```
ComfyUI → MiniMax H3 → raw_hero.mp4  (low-res draft)
        → upscaler   → hero.mp4       (final, or use $2 cloud render)
```

1. Describe your concept to the video model: the object, environment, lighting mood,
   and the visual "journey" the scroll should follow (e.g., a vault opening into a
   lobby: start closed, end open).
2. Generate at the lowest resolution your model supports first. Confirm the concept
   works before committing to a full-quality run.
3. Upscale the draft with a free local upscaler if quality is sufficient. If not, use
   a cloud render (typically ~$2 for a 10-15s clip) as the hero.
4. Have your AI session analyze the video: "How many frames does this video have at
   [fps]? Describe the 6 most visually distinct keyframes and their approximate timestamps."
   Save this analysis. The prompt in Phase 3 depends on it.

Output: a single `hero.mp4` and a frame-analysis note.

## Phase 3: The One-Prompt Website Build

Construct a detailed prompt. Local models require more explicit instruction than frontier
APIs. Under-specifying leads to generic or broken output.

**Prompt template** (fill in the `[...]` fields):

```
Read the [immersive-web] skill and build a scroll-scrubbed website in one shot for
[BRAND NAME] with the tagline "[TAGLINE]".

Hero video: [absolute path to hero.mp4]
The video has approximately [N] frames at [fps] fps.
The video depicts: [one-sentence description of the visual journey].

Instructions:
1. Watch the footage first: extract [6] keyframes at evenly-spaced timestamps and
   read them (you have vision). Confirm you can see each frame before proceeding.
2. Map scroll position 0% → 100% to video frames 0 → [N]. Each scroll beat should
   reveal the next keyframe.
3. Build the full website in a single HTML file: hero section with scroll-scrub,
   [N_SECTIONS] below-the-fold sections, call-to-action at the end.
4. Style: [describe color palette, font vibe, accent elements].
5. Also apply the [effects-menu] skill for the page transitions.
6. Output file: ./[brand-slug]-site/index.html

After generating, open the file in a browser via browser-use. Scroll through fully.
If the video does not play or scroll-scrub does not respond, diagnose and fix in the
same session. Loop until the scroll-scrub and all sections render correctly.
```

Key principles:
- **Overexplain**: local models don't have the same inference depth as frontier models.
  Spell out frame count, exact paths, vision-use instruction, and expected sections.
- **Single-file output**: simpler to verify and iterate; the LM writes one file, checks
  it, fixes it.
- **Browser-use loop**: instruct the model to keep fixing until the browser check passes.
  This replaces the human QA loop.

## Phase 4: Self-Correcting Browser Loop

The harness will:
1. Generate `index.html`.
2. Open it in a headless browser (browser-use capability).
3. Scroll from top to bottom and capture screenshots at 10% intervals.
4. Compare each screenshot to the expected keyframe. If the video is not visible or
   scroll-scrub is not responding, read the error, patch the file, and retry.
5. Continue until all 10 scroll positions render the correct video frame.

This loop runs entirely unattended. Tokens are free (local compute only). Wall-clock
time is the constraint: a 5-10 minute build per site is typical on a well-configured
local model.

If the loop stalls after 3+ identical failures (same error, same frame), stop and
surface the failure to the user. Common causes:
- Video codec not supported by the browser (convert to VP9 or H.264)
- Incorrect frame count in the prompt (re-analyze the video)
- Model below the 15B threshold struggling with multi-step code generation

## Phase 5: Verification Checklist

Before accepting the output:
- [ ] `index.html` exists at the specified output path
- [ ] Opening the file in a real browser (not headless) shows the hero video loading
- [ ] Scrolling from 0 to 100% plays the video end-to-end via scroll-scrub
- [ ] Below-the-fold sections are visible and styled
- [ ] No JavaScript console errors on load
- [ ] Mobile viewport (375px) does not break layout

## The Named Techniques

**Skill-routing in a local harness**: the design principle that unlocks agentic web
generation: instead of writing one giant prompt that describes every website style, you
maintain a small library of domain-specific skill files. The harness selects the
relevant one at runtime. The LM reads the skill, understands the constraints, and
produces output calibrated to that style. Generalizes to any asset type (video,
presentation, PDF report).

**Video-to-frames scroll beat mapping**, the core animation mechanism: a single
hero video is divided into N frames; the user's scroll position (0-100%) maps linearly
to frame index (0-N). The LM extracts keyframes via vision, designs scroll beats around
them, and writes the CSS/JS to drive the animation. Requires no additional images or
animations. The hero video supplies all visual content.

**The overexplain principle**: local models (below ~70B) lack the implicit
instruction-following depth of frontier APIs. Compensate with explicit frame counts,
exact file paths, step-by-step numbered instructions, and a vision-use reminder even
when the model has vision capability. A prompt that feels over-specified for a cloud
model is often just right for a local one.

## Source

Mark Kashef, "3D Websites Just Became FREE (One Prompt)"
https://www.youtube.com/watch?v=FSnubu4Lpz8
Published: 2026-08-11
Channel: Mark Kashef
