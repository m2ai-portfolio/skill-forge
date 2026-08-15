---
name: native-video-intake
description: "Use a raw MP4, screen recording, or video URL as direct input to Claude Code or Codex, no plugins or extra tools required. The AI breaks the video into frames and audio, giving it full visual + transcript context. Use when you want to feed a Loom walkthrough, a site review recording, or a narrated demo directly to the AI as requirements. Triggers on: \"watch this video\", \"I have a Loom\", \"feed this recording\", \"use this MP4\", \"video input\", \"screen recording as requirements\", \"record my workflow\"."
---

# Native Video Intake

Both Claude Code and Codex can process raw MP4 files natively: no special skill, plugin, or
external API required. The screen-recording feature they both shipped quietly enabled general
video understanding: the runtime breaks the file into micro-frames, pairs each with the audio
track, and feeds both through the model's image and language processing pipeline.

Use this when you have any of these:
- A Loom or screen recording of a website, UI, or process you want to improve
- A narrated walkthrough of a design, platform, or workflow you want to clone or rebuild
- A recording of yourself working that you want turned into an SOP or improvement plan

## When to use each intake method

| Method | When to use |
|--------|-------------|
| **Drag-and-drop MP4** | You have the file locally; want to annotate or compress first |
| **Video URL** | You have a direct link (Loom share link, hosted MP4); fastest path |
| **Screen record (built-in)** | You want the AI to watch you work in real time and audit the session |

## Resolution tip

Lower resolution = smaller context usage = longer videos supported. Record or export at 720p
or lower when possible. High-resolution recordings of a 10+ minute session can saturate the
context window before the AI finishes processing.

## Phase 1: Prepare your video

1. Decide your intake method (file, URL, or built-in record).
2. If using a file: confirm it is under ~500MB. If larger, compress with:

```bash
ffmpeg -i input.mp4 -vcodec libx264 -crf 28 -preset fast -vf scale=-2:720 -acodec aac output.mp4
```

3. If using Loom or a hosted URL: copy the direct share link (not the Loom edit URL).

## Phase 2: Write the intake prompt

The key instruction is: **tell the AI to watch end-to-end, not just pull the transcript.**
Without this, some models default to extracting captions only.

Template:
```
Watch this video end to end. Don't just pull the transcript. Look at what is on screen
at each point. Then [your actual task].
```

Examples by use case:

**Website/UI improvement:**
```
Watch this screen recording end to end, paying attention to what I'm pointing at and any
narration. Produce a prioritized list of improvements to make, with timestamp references
for each issue you found.
```

**Clone or rebuild from a narrated walkthrough:**
```
Watch this recording end to end with audio. I want to build something with this look,
feel, and feature set. Give me a full implementation plan based only on what you observe
in the video.
```

**Workflow audit / SOP generation:**
```
Monitor this recording of my process. After watching, list: (1) every manual step I took,
(2) anything I did more than once that could be automated, (3) a draft SOP that captures
the core workflow.
```

## Phase 3: Submit

**File intake:** Drag the MP4 into the Claude Code or Codex chat, then add your prompt.

**URL intake:** Paste the URL and your prompt together. The AI will download and process
the video automatically.

**Built-in screen record:** Open the record/replay feature, start recording, work through
your process naturally, stop, then send it with your audit prompt. In regions where
built-in recording is unavailable, use Loom or any screen recorder and feed the file
or link as above.

## Phase 4: Verify the AI actually watched the video

Check the response for timestamp references or frame-specific observations. If it only
returns a text summary without visual detail, re-prompt:

```
You appear to have only read the captions. Please review the video frames as well:
specifically, tell me what you observed at [timestamp] visually on screen.
```

## What happens behind the scenes

The AI samples the video into micro-frames at regular intervals and pairs each frame with
the corresponding audio segment. It then processes the full frame-audio pairs through its
vision and language pipeline together, giving it understanding of what was said, what was
shown, and how they relate. This is why lower resolution helps: each frame consumes image
tokens from the context budget.

## Limitations

- Very long videos (30+ min at high resolution) may exceed the context window.
- Audio-only content works but loses the visual channel benefit; a transcript is more efficient.
- The AI cannot take actions based on a video alone if it lacks access to the underlying
  codebase or system shown. Pair this intake with a relevant project context.
