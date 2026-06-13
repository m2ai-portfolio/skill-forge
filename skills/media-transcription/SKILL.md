---
name: media-transcription
description: Transcribe any audio or video recording and produce timestamped, speaker-labeled, chaptered artifacts ready for downstream workflows (meeting synthesis, paper edits, content pipelines).
---

# Media Transcription

Takes any audio or video input and produces structured transcription artifacts: a timestamped transcript, speaker labels, and auto-generated chapter markers. Output format is designed to feed downstream skills — analysis, publishing, or video production.

## Trigger

Use when the user says "transcribe this", "get the transcript for", "convert this recording to text", "extract chapters from this video", or when a workflow step needs a textual representation of audio or video content.

## Phase 1: Input

Accept the recording in any of these forms:

1. **Local file path** — audio or video file (MP3, MP4, WAV, MOV, M4A, WebM)
2. **URL** — a direct link to an audio/video file or a supported platform URL (YouTube, etc.)
3. **Inline audio** — if the model supports audio input natively, pass it directly

Ask the user if not provided:
- "What is the recording? (file path, URL, or describe it)"
- "Do you need speaker labels? (yes / no / best-effort)"

## Phase 2: Choose Transcription Method

Select the transcription backend in priority order:

1. **MCP audio tool** — if any `transcribe`, `whisper`, or audio MCP tool is present in the session
2. **Gemini with audio** — if a Gemini tool is available and the file is under the provider's size limit; use the prompt:
   > "Transcribe this audio with timestamps every 30 seconds. Label speakers as Speaker A, Speaker B, etc. when distinguishable. Add chapter markers where the topic clearly shifts."
3. **yt-dlp + local Whisper** — if `yt-dlp` and `whisper` are available:
   ```bash
   yt-dlp -x --audio-format mp3 -o /tmp/transcription-input.%(ext)s "{URL}"
   whisper /tmp/transcription-input.mp3 --output_format vtt --output_dir /tmp/
   ```
4. **Manual** — instruct the user to transcribe externally and paste the result; offer to process the pasted text into chapters and a summary.

If none of the above is available, explain clearly what is missing and which option would be cheapest to set up.

## Phase 3: Structure the Transcript

From the raw transcription, produce three artifacts:

### Artifact 1: Timestamped Transcript (`transcript.md`)

```
[00:00] Speaker A: ...
[00:42] Speaker B: ...
[01:15] Speaker A: ...
```

### Artifact 2: Chapter Markers (`chapters.md`)

Identify topic shifts and label them:

```
[00:00] Introduction / context
[03:20] {topic name}
[12:45] {new topic name}
[24:10] Wrap-up / next steps
```

Aim for 3-8 chapters for recordings under 60 minutes. Fewer for shorter recordings. Chapters do not need to be evenly spaced — label actual topic transitions, not intervals.

### Artifact 3: Speaker Summary (`speakers.md`, optional)

Only produce if speaker labels are present:

```
Speaker A — {inferred role or context based on content}
Speaker B — {inferred role or context}
Total speaking time: A: Xmin, B: Ymin
```

## Phase 4: Output

Save all artifacts to `./transcription-{slug}/` by default, where `{slug}` is a short descriptor derived from the filename or URL (e.g., `transcription-team-call-2026-06-12/`). Return the paths of all saved files.

If a downstream skill is waiting (e.g., meeting-synthesis, a video editing workflow), pass `transcript.md` and `chapters.md` directly as its input and skip saving to disk unless the user asks.

## Configuration

Set `TRANSCRIPTION_PROVIDER` in your environment to pin a backend:
```
export TRANSCRIPTION_PROVIDER=whisper
```

Supported values: `whisper`, `gemini`, `mcp`, `manual`.

## What This Does NOT Do

- Does not perform high-accuracy speaker diarization on overlapping speech — it provides best-effort labels.
- Does not translate — transcribes in the source language unless explicitly asked to translate.
- Does not summarize or analyze the content (use a synthesis or summarization skill for that).
- Does not manage audio quality issues (noise removal, normalization) — pre-process if quality is poor.

## Source

Extracted from Nate Kadlac newsletter (2026-06-12): "Grab my Ultimate Guide to Codex and catch up to the 1 in 1,600 people using it every week." Idea 3: "Any recording → timestamped, speaker-labeled, chaptered artifacts." Category: Core Infrastructure Skills.
