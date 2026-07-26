---
name: local-ai-bootstrap
description: Guide the user through setting up a local open-source AI stack (Ollama + Open WebUI + Tailscale) as a resilient complement to closed-source APIs. Use when the user says "I want to run AI locally", "set up Ollama", "local LLM setup", "open source AI", "self-hosted AI", "vendor lock-in backup", "run models without API costs", or "local AI command center".
---

# Local AI Bootstrap

Sets up a self-hosted AI stack as a resilient backup to closed-source providers. Guides hardware assessment, model selection, stack installation, and remote access. Uses your current AI assistant (Claude Code or similar) to scaffold config, debug errors, and maintain the setup over time.

## Trigger

Use when the user says:
- "I want to run AI locally" / "set up local LLMs"
- "set up Ollama" / "Open WebUI" / "self-hosted AI"
- "I'm worried about vendor lock-in" / "AI access got cut off"
- "run models without API costs"
- "local AI command center" / "open source AI backup"

## Phase 1: Hardware Assessment

Ask the user:

1. **What machine will host the models?** (laptop, desktop, Mac Mini, NAS, server)
2. **How much RAM does it have?** (this is the primary constraint for model size)
3. **GPU?** (NVIDIA with CUDA, Apple Silicon, or CPU-only)
4. **Do you need remote access** from other devices on the same network, or from anywhere?

Use answers to set expectations before any installation begins:

| RAM | Max model size | Suitable for |
|-----|---------------|--------------|
| 8 GB | 7B (quantized) | Chat, basic summarization |
| 16 GB | 13–14B | Most daily tasks, light coding |
| 32 GB | 30–34B | Coding, longer context, agent tasks |
| 64 GB+ | 70B+ | Near-frontier local performance |

If the machine has less than 8 GB RAM, flag this before proceeding -- most useful models will be too slow.

## Phase 2: Model Selection

Do not recommend a single model. Match by use case:

| Use case | Recommended model family | Notes |
|----------|-------------------------|-------|
| General chat / Q&A | Llama 3.1, Qwen 2.5 | Good quality-to-size ratio |
| Code generation | DeepSeek Coder, Qwen2.5-Coder | Code-tuned variants matter |
| Light classification, triage | Mistral 7B | Fast, low memory footprint |
| Long-context document Q&A | Qwen 2.5 14B+ | Better context utilization |
| Image understanding | LLaVA, Qwen-VL | Multimodal; needs more VRAM |

Always pull the quantized (Q4 or Q5) variant first -- it fits in less RAM with minimal quality loss.

## Phase 3: Stack Installation

Install in this order. Each step must succeed before the next.

### Step 1: Ollama

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# Verify
ollama --version
```

Pull a starter model to confirm Ollama works:
```bash
ollama pull llama3.1:8b
ollama run llama3.1:8b "Say hello"
```

If this fails, surface the full error output. Common issues:
- Permission denied: run with appropriate privileges
- Model not found: check `ollama list` for available model names
- Out of memory: try a smaller quantized variant (`llama3.1:8b-q4_0`)

### Step 2: Open WebUI

Open WebUI provides a browser-based interface over Ollama.

```bash
docker run -d \
  --name open-webui \
  -p 3000:8080 \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  -v open-webui:/app/backend/data \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```

For Apple Silicon Macs (no Docker GPU passthrough needed for Ollama):
```bash
docker run -d \
  --name open-webui \
  -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  -v open-webui:/app/backend/data \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```

Access at `http://localhost:3000` (or the host machine's LAN IP if accessing from another device on the same network).

Verify the connection: click the model dropdown in Open WebUI -- Ollama models should appear.

### Step 3: Tailscale (optional, for remote access)

Install Tailscale on the host machine and on every device that needs access:

```bash
# Linux
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# macOS: install from tailscale.com, then
tailscale up
```

Once both devices are on the same Tailnet, use the host's Tailscale IP instead of `localhost`:
- Ollama API: `http://<tailscale-ip>:11434`
- Open WebUI: `http://<tailscale-ip>:3000`

No port-forwarding or VPN configuration required.

## Phase 4: Use Claude Code as Your Setup Assistant

This is the key meta-technique: use your current AI session to scaffold, debug, and maintain the local stack.

**For each error encountered:**
1. Paste the full error output into this session
2. Ask: "What is the root cause and the minimal fix?"
3. Apply the fix, verify it resolves the error, then continue

**For model config tuning:**
- Ask: "Given [RAM] GB and [GPU], what Modelfile settings should I use for [use case]?"
- Use the generated `Modelfile` with `ollama create` to set system prompts, context length, and temperature

**For ongoing maintenance:**
- When a model update is available, pull it: `ollama pull <model>:latest`
- When Open WebUI has an update: `docker pull ghcr.io/open-webui/open-webui:main && docker restart open-webui`
- When something breaks, paste `docker logs open-webui` or `ollama logs` into this session

## Phase 5: Verification Checklist

Before declaring setup complete, confirm:

- [ ] `ollama list` shows at least one pulled model
- [ ] `ollama run <model> "test"` returns a response
- [ ] Open WebUI loads in browser and shows the model in the dropdown
- [ ] A test prompt in Open WebUI returns a response
- [ ] (If Tailscale) Open WebUI accessible from a second device via Tailscale IP

If any item fails, surface the error before moving on.

## Philosophy Note

This stack is a **resilience layer**, not a replacement for frontier models. For high-stakes work -- complex reasoning, large codebases, nuanced writing -- closed-source models remain stronger. Use local AI for:
- Tasks where privacy matters (sensitive documents, internal data)
- Cost-sensitive high-volume tasks (classification, triage, summarization at scale)
- Offline or air-gapped environments
- Vendor redundancy when API access is cut or costs spike

The goal is to be nimble: able to shift workloads between local and cloud as the situation changes.

## Source

Extracted from: "How to FINALLY Use Local AI in 45 Minutes" by Mark Kashef
URL: https://www.youtube.com/watch?v=84POiAUhtSI
Published: 2026-07-22
