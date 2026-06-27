---
name: media-transcription
description: Transcribe a local audio or video file into a plain-text artifact using an AI transcription API (default AssemblyAI), producing a clean transcript file. Use when the user says "transcribe this file", "convert audio to text", "transcribe my recording", "get the transcript from", or provides a path to an .mp3, .mp4, .m4a, .wav, .ogg, or .webm media file and asks for its content.
---

# Media Transcription

Turns a local audio or video file into a clean plain-text transcript using an AI transcription API.

## Trigger

Use when the user says "transcribe this file", "convert audio to text", "transcribe my recording", "get the transcript from", or provides a path to an `.mp3`, `.mp4`, `.m4a`, `.wav`, `.ogg`, `.webm`, or similar media file and asks for its content.

## Phase 1: Identify Input

Accept:
- A file path to a local audio or video file
- A URL to a hosted audio/video file (AssemblyAI accepts direct URLs)

Ask one clarifying question only if the file path is absent: "What is the path or URL of the file you want to transcribe?"

Supported formats: `.mp3`, `.mp4`, `.m4a`, `.wav`, `.ogg`, `.webm`, `.flac`, `.aac`, `.opus`.

## Phase 2: Configure

Determine settings:
- **Speaker diarization** — ask: "Does this recording have multiple speakers?" (yes: enable diarization; no: skip; unknown: skip)
- **Language** — default to English unless the user specifies otherwise
- **Output path** — default to `./transcript-[filename]-[YYYY-MM-DD].txt` in the current working directory unless the user specifies a different location

No other questions. Keep intake minimal.

## Phase 3: Transcribe

Submit the file or URL to the transcription API.

If using AssemblyAI:
- Load the API key from the environment variable `ASSEMBLYAI_API_KEY`
- Use the Python SDK (`assemblyai`) or the REST API
- Poll for completion; default timeout 10 minutes for files under 1 hour

If `ASSEMBLYAI_API_KEY` is not set, check for `OPENAI_API_KEY` and fall back to the OpenAI Whisper API (`/audio/transcriptions`). If neither is set, report which keys are missing and stop.

Never hardcode API keys. Never embed keys in the output file.

## Phase 4: Clean and Format

Post-process the raw transcript:
- Remove filler word artifacts (`[INAUDIBLE]`, `[CROSSTALK]`) unless diarization is on, in which case preserve speaker labels
- Normalize whitespace; add paragraph breaks at natural pause points
- If speaker diarization is enabled, format as:
  ```
  Speaker A: [text]
  Speaker B: [text]
  ```
- If timestamps are available and the user asked for them, include as `[HH:MM:SS]` inline

## Phase 5: Deliver

Write the cleaned transcript to the output path. Report:
- File written to: `[path]`
- Duration transcribed: `[N minutes]`
- Speaker count (if diarization was used): `[N speakers detected]`
- Word count: `[N words]`

If the user says "now synthesize this meeting" or "summarize", hand off to the `meeting-synthesis` skill with the transcript as input.

## Notes

- This skill handles transcription only. Summarization, extraction, and meeting notes are downstream tasks.
- For video files, only the audio track is processed; visual content is not analyzed.
- Large files (>1 hour) may take several minutes. Report estimated wait time if known from the API response.
- Default output path uses `./` — do not assume a vault or notes location.

## Source

Extracted from Nate Kadlac "Open Skills" newsletter (2026-06-19), idea 3 — Media Transcription: "Transcribe local audio/video (default AssemblyAI) into reusable artifacts."
