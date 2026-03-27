<p align="center">
  <img src="assets/skill-forge-banner.jpg" alt="Skill Forge Banner" width="100%">
</p>

<h1 align="center">Skill Forge</h1>
<p align="center"><strong>Content-to-Capability Pipeline</strong></p>
<p align="center">Ingests AI walkthroughs, extracts techniques, and generates production-ready Claude Code skills.</p>

---

## What Is This?

Skill Forge watches for new AI content (YouTube videos, newsletters, blog posts) and transforms the techniques found inside into installable [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills). Instead of watching a 40-minute walkthrough and manually writing a skill file, Skill Forge does the extraction, structuring, and packaging for you.

**The pipeline:**

```
Content Source ──► Technique Extraction ──► SKILL.md Generation ──► Review & Install
 (video, article)   (Gemini / LLM)          (structured phases)     (human-in-the-loop)
```

## Skills Produced So Far

| Skill | What It Does | Source |
|-------|-------------|--------|
| **video-to-skill** | Turns screen recordings into skills via Gemini video understanding | [Mark Kashef](https://www.youtube.com/watch?v=hTWxGSsGDZU) |
| **claude-architect-audit** | Audits your Claude Code setup against Anthropic's 5 Architect domains | [Mark Kashef](https://www.youtube.com/watch?v=vizgFWixquE) |
| **context-hygiene** | Three shields for managing Claude Code context window bloat | [Mark Kashef](https://www.youtube.com/watch?v=iALzJyvgCoM) |
| **context-fork-guide** | Isolates heavy skills in separate context windows | [Mark Kashef](https://www.youtube.com/watch?v=iALzJyvgCoM) |
| **remote-channels** | Sets up Claude Code remote access via Telegram / Discord | [Mark Kashef](https://www.youtube.com/watch?v=RUyqEAXt2YQ) |
| **classify-agent** | Classifies problems into one of four agent architectures | [Nate Kadlac](https://natesnewsletter.substack.com) |
| **decomposition-scorer** | Scores whether parallel agent tasks are properly isolated | [Nate Kadlac](https://natesnewsletter.substack.com) |
| **mismatch-check** | Diagnoses architecture mismatches in your agent setup | [Nate Kadlac](https://natesnewsletter.substack.com) |

## How to Use These Skills

### Install a Single Skill

Each skill is a standalone `SKILL.md` file. To use one in your own Claude Code setup:

1. **Copy the skill directory** into your Claude Code skills folder:
   ```bash
   # Clone the repo
   git clone https://github.com/m2ai-portfolio/skill-forge.git

   # Copy a specific skill to your global skills directory
   cp -r skill-forge/skills/classify-agent ~/.claude/skills/
   ```

2. **Restart Claude Code** (or start a new session). The skill will be available as a slash command:
   ```
   /classify-agent
   ```

3. **Or reference it in conversation** — Claude will auto-detect when a skill matches your request based on its description triggers.

### Install All Skills

```bash
git clone https://github.com/m2ai-portfolio/skill-forge.git
cp -r skill-forge/skills/* ~/.claude/skills/
```

### Skill File Structure

Each skill follows this structure:

```
skills/
  skill-name/
    SKILL.md          # The skill definition (frontmatter + phases)
```

The `SKILL.md` frontmatter tells Claude Code when to trigger:

```yaml
---
name: skill-name
description: >
  What this skill does and when to use it. Include trigger phrases
  like "when the user says X" for reliable activation.
---
```

## How the Pipeline Works

Skill Forge runs on a scheduled cadence (daily at 6 AM) and can also be triggered manually. The process:

1. **Source Monitoring** — Checks configured content sources (YouTube channels, RSS feeds, newsletters) for new material since the last check
2. **Content Ingestion** — Downloads or fetches the content. For videos, uses Gemini's video understanding API to extract a full SOP
3. **Technique Extraction** — Identifies discrete, reusable techniques within the content that could become Claude Code skills
4. **Skill Generation** — Structures each technique into a `SKILL.md` with proper frontmatter, phased instructions, verification steps, and source attribution
5. **Human Review** — Generated skills land in the `skills/` directory for review before being installed into active use

## Project Structure

```
skill-forge/
  skills/               # Generated skills (each is a standalone SKILL.md)
  data/
    last_check.txt      # Timestamp of last content source check
  src/                   # Pipeline source code (WIP)
  templates/             # Skill templates (WIP)
  tests/                 # Pipeline tests (WIP)
```

## Contributing a Skill

Found a great AI walkthrough with a technique worth capturing? Open an issue or PR with:

1. **Source link** — URL to the video, article, or newsletter
2. **Technique summary** — What the technique does in 1-2 sentences
3. **Proposed skill name** — Short, descriptive kebab-case name

Or generate the skill yourself using the `video-to-skill` skill from this repo.

## License

MIT
