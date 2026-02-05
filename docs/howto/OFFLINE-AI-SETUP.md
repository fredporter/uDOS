# Offline-First AI Setup: Ollama + OpenRouter Routing

**Scope:** Local LLM inference with optional cloud burst routing through Wizard Server  
**Target User:** uDOS developers wanting offline AI capabilities  
**Status:** v1.0.4.0 Complete

---

## Overview

uDOS provides **offline-first AI** through two complementary systems:

### 1. **Local AI (Ollama)**

- **Model:** Mistral Small (3.7GB) or alternatives
- **Hardware:** Runs on M1/M2 Mac, Linux servers, or desktop systems
- **Performance:** ~50ms inference time on M1/M2
- **Cost:** Zero (just hosting costs)
- **Setup:** Automated via `bin/Setup-Vibe.command`

### 2. **Cloud Burst (OpenRouter)**

- **Routing:** Through Wizard Server API (port 8765)
- **Models:** 150+ LLMs available (Mistral, Claude, GPT-4, etc)
- **Triggering:** Local task fails 2x OR task tagged `burst` OR budget allows
- **Cost:** Pay-per-token only when used (min $1 account)

---

## Part 1: Local Ollama Setup

### Step 1: Install & Start Ollama

**Automated:**

```bash
cd ~/uDOS
bin/Setup-Vibe.command
```

**Manual:**

```bash
# macOS
brew install ollama
brew services start ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &

# Windows
# Download from https://ollama.com
```

**Verify:**

```bash
curl http://127.0.0.1:11434/api/tags
# Shows: {"models": [...]}
```

---

### Step 2: Choose Your Model

#### **Recommended: Mistral Small (3.7GB)**

```bash
ollama pull mistral:small
ollama run mistral:small "Hello, what is uDOS?"
```

| Model             | Size  | Speed     | Quality | Best For             |
| ----------------- | ----- | --------- | ------- | -------------------- |
| **mistral:small** | 3.7GB | ~50ms M1  | Good    | General coding, chat |
| mistral:latest    | 7.4GB | ~100ms M1 | Better  | Complex reasoning    |
| neural-chat       | 4.1GB | ~60ms M1  | Good    | CPU-friendly         |
| llama2            | 3.8GB | ~80ms M1  | Good    | General tasks        |
| openchat          | 3.5GB | ~45ms M1  | Decent  | Fast responses       |

**Installation:**

```bash
# Single pull
ollama pull mistral:small

# Create convenient alias (optional)
ollama cp mistral:small devstral

# List all installed
ollama list
```

---

### Step 3: Configure Vibe CLI

Edit `.vibe/config.toml`:

```toml
[model]
provider = "ollama"
model = "mistral:small"          # or "devstral" (alias), "neural-chat", etc
endpoint = "http://127.0.0.1:11434"
cloud_enabled = false             # Disable cloud by default
```

**Test Vibe:**

```bash
source .venv/bin/activate
vibe chat "What is the capital of France?"

# Or with context
vibe chat --with-context "Explain the uDOS command routing architecture"
```

---

### Step 4: Performance Tuning (Optional)

#### **Apple Silicon (M1/M2/M3)**

```bash
# Enable flash attention + quantization for faster inference
export OLLAMA_FLASH_ATTENTION=1
export OLLAMA_KV_CACHE_TYPE=q8_0
ollama serve

# Or start service with env
brew services stop ollama
OLLAMA_FLASH_ATTENTION=1 OLLAMA_KV_CACHE_TYPE=q8_0 brew services start ollama
```

#### **Memory-Constrained Systems**

```bash
# Use quantized models (lower quality, faster)
ollama pull dolphin-mixtral:7b-q4_0  # 3.5GB, faster
ollama pull mistral:7b-q4_0          # 3.7GB, slightly faster
```

#### **Parallel Inference**

```toml
# .vibe/config.toml
[ollama]
num_parallel = 4  # Use 4 cores for parallel requests
num_gpu = 1       # Use 1 GPU (if available)
```

---

## Part 2: Cloud Routing (OpenRouter)

### Why OpenRouter?

OpenRouter is an **API aggregator** giving you:

- 150+ LLM models available
- Single API key for multiple providers
- No vendor lock-in
- Pay-per-token pricing (starting free tier)
- High reliability (request routing, fallbacks)

**Alternatives:**

- **Anthropic (Claude):** High quality, $5/month API
- **OpenAI (GPT-4):** Best model quality, expensive
- **Together.ai:** Good selection, cheap
- **Replicate:** Image generation + LLMs

---

### Step 1: Create OpenRouter Account

1. Visit https://openrouter.ai
2. Sign up (free account includes $5 monthly free tier)
3. Copy API key from **Keys** section
4. Save securely (never commit to git)

---

### Step 2: Store API Key in Wizard

**Using Secret Store:**

```bash
cd ~/uDOS
source .venv/bin/activate

# Add OpenRouter API key
bin/wizard-secrets add \
    --key-id=openrouter-main \
    --provider=openrouter \
    # You'll be prompted to paste key securely
```

**Verify:**

```bash
bin/wizard-secrets list
# Should show: openrouter-main (no value shown)
```

**Manual Entry (if CLI unavailable):**
Edit `wizard/config/ai_keys.example.json`:

```json
{
  "openrouter": {
    "key_id": "openrouter-main",
    "reference": "secrets.tomb:openrouter-main"
  }
}
```

---

### Step 3: Configure Wizard AI Gateway

Edit `wizard/config/ai_gateway.json`:

```json
{
  "providers": {
    "ollama": {
      "enabled": true,
      "endpoint": "http://127.0.0.1:11434",
      "models": ["mistral:small", "neural-chat"]
    },
    "openrouter": {
      "enabled": true,
      "endpoint": "https://openrouter.ai/api/v1",
      "key_id": "openrouter-main",
      "models": [
        "mistral/mistral-large",
        "anthropic/claude-3-opus",
        "openai/gpt-4",
        "meta-llama/llama-2-70b"
      ]
    }
  },
  "routing": {
    "default": "ollama",
    "fallback": "openrouter",
    "strategy": "local-first"
  }
}
```

---

### Step 4: Test Cloud Routing

**Start Wizard Server:**

```bash
source .venv/bin/activate
python wizard/launch_wizard_dev.py --no-tui
# Server runs on http://localhost:8765
```

**Test Local Route (Ollama):**

```bash
curl -X POST http://localhost:8765/api/ai/route \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is uDOS?",
    "model": "mistral:small",
    "max_tokens": 256
  }'
```

**Test Cloud Route (OpenRouter):**

```bash
curl -X POST http://localhost:8765/api/ai/route \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing",
    "model": "mistral/mistral-large",
    "tags": ["burst"],
    "max_tokens": 512
  }'
```

---

## Part 3: Routing Policy

### Automatic Route Selection

The Wizard AI Gateway automatically chooses based on:

```
┌─────────────────────┐
│   AI Request        │
│  (prompt + tags)    │
└──────────┬──────────┘
           │
    ┌──────▼──────┐
    │ Is task     │
    │ "offline"?  │ ──yes──> Use Ollama (local)
    └──────┬──────┘
           │ no
    ┌──────▼──────┐
    │ Ollama      │
    │ available?  │ ──yes──> Try local first
    └──────┬──────┘
           │ no or failed
    ┌──────▼──────┐
    │ "burst"     │
    │ tag set?    │ ──yes──> Use OpenRouter
    └──────┬──────┘
           │ no
    ┌──────▼──────┐
    │ Cloud       │
    │ budget?     │ ──yes──> Use OpenRouter
    └──────┬──────┘
           │ no
           ▼
        Error: No AI available
```

### Request Tags

Include tags in your request to control routing:

```json
{
  "prompt": "Your question",
  "tags": [
    "offline",      # Force local only (fail if offline)
    "burst",        # Prefer cloud (use if available)
    "private",      # Cannot use cloud (security)
    "code",         # Code generation (prefer Mistral/Claude)
    "math"          # Math reasoning (prefer GPT-4/Claude)
  ]
}
```

### Example Scenarios

**Scenario 1: Document Analysis (Local)**

```json
{
  "prompt": "Summarize this uDOS handler pattern",
  "tags": ["offline", "code"]
  // Uses: mistral:small (local, no API cost)
}
```

**Scenario 2: Complex Code Generation (Cloud)**

```json
{
  "prompt": "Design a distributed consensus algorithm",
  "tags": ["burst", "code"]
  // Tries: Ollama first, then OpenRouter → Claude 3 Opus
}
```

**Scenario 3: Sensitive Analysis (Local Only)**

```json
{
  "prompt": "Analyze security of this SSH key exchange",
  "tags": ["private", "offline"]
  // Forces: Local Ollama only (no cloud allowed)
}
```

---

## Part 4: SVG Graphics Generation

### Goal: Stylized SVG Line Drawings

uDOS needs AI-generated vector graphics for documentation, diagrams, and interfaces.

### Option 1: Prompt-Based (Recommended)

**Local (Mistral Small):**

```python
from wizard.services.ai_gateway import AIGateway

gateway = AIGateway()
svg = await gateway.query(
    prompt="""Generate an SVG diagram of a distributed system:
    - 3 nodes (circles labeled A, B, C)
    - Arrows showing message flow
    - Use clean strokes, no fills
    - Include a title

    Output ONLY the SVG code, no markdown.""",
    tags=["offline", "graphics"],
    model="mistral:small"
)
# Returns: <svg>...</svg>
```

**With OpenRouter (Better Quality):**

```python
svg = await gateway.query(
    prompt="""Generate a stylized SVG line drawing...
    Style: Minimalist, black lines only, no fills
    """,
    tags=["burst", "graphics"],
    model="anthropic/claude-3-opus"
)
```

### Option 2: Specialized Tools

**Graphviz (Diagrams + Flowcharts):**

```bash
# Install
brew install graphviz

# Generate SVG from DOT language
dot -Tsvg input.dot -o output.svg
```

**Mermaid (Modern Diagrams):**

```bash
npm install -g @mermaid-js/mermaid-cli

# Generate SVG
mmdc -i diagram.mmd -o diagram.svg
```

**Comparison:**
| Tool | Quality | Speed | Local | Cost |
|------|---------|-------|-------|------|
| Mistral AI | Good | ~100ms | Yes | $0 |
| Claude 3 | Excellent | ~2s | No | $0.015/req |
| Graphviz | Basic | <10ms | Yes | $0 |
| Mermaid | Good | ~100ms | Yes | $0 |

---

## Part 5: Troubleshooting

### Issue: "Ollama API not responding"

```bash
# Check if running
pgrep ollama

# Start service
brew services start ollama
# OR
OLLAMA_FLASH_ATTENTION=1 ollama serve

# Verify endpoint
curl http://127.0.0.1:11434/api/tags
```

### Issue: "Model not found" (mistral-small2 error)

**Root cause:** Setup script used wrong model name

**Fix:**

```bash
# Pull correct model
ollama pull mistral:small

# Verify
ollama list | grep mistral

# Update .vibe/config.toml if needed
model = "mistral:small"  # Not "mistral-small2"
```

### Issue: "Out of memory"

```bash
# Check available models (sorted by size)
ollama list

# Use smaller model
ollama pull neural-chat      # 4.1GB
ollama pull openchat         # 3.5GB

# Increase system swap (macOS)
# Automatic via Memory Pressure
```

### Issue: "OpenRouter 401 Unauthorized"

```bash
# Verify key stored correctly
bin/wizard-secrets list | grep openrouter

# Re-add key
bin/wizard-secrets rotate --key-id=openrouter-main

# Check Wizard logs
tail -f memory/logs/api_server.log | grep openrouter
```

---

## Part 6: Performance Benchmarks

### M1/M2 Mac (mistral:small)

| Task             | Model         | Latency | Quality | Token/sec |
| ---------------- | ------------- | ------- | ------- | --------- |
| Code review      | mistral:small | 50ms    | Good    | 40        |
| Simple Q&A       | mistral:small | 80ms    | Good    | 25        |
| Document summary | mistral:small | 120ms   | Good    | 15        |

### OpenRouter (claude-3-opus)

| Task              | Model         | Latency | Quality   | Cost      |
| ----------------- | ------------- | ------- | --------- | --------- |
| Code generation   | Claude 3 Opus | 2-3s    | Excellent | $0.015/1k |
| Complex reasoning | Claude 3 Opus | 3-5s    | Excellent | $0.015/1k |
| SVG generation    | Claude 3 Opus | 4-6s    | Excellent | $0.015/1k |

---

## Part 7: Integration Examples

### Example 1: Code Review Handler

```python
# core/commands/review_handler.py
from wizard.services.ai_gateway import AIGateway

class ReviewHandler(BaseHandler):
    async def handle_review(self, code: str):
        gateway = AIGateway()

        review = await gateway.query(
            prompt=f"Review this Python code:\n{code}",
            tags=["code", "offline"],  # Try local first
            model="auto"               # Auto-select best model
        )
        return review
```

### Example 2: SVG Diagram Generator

```python
# wizard/services/graphics_service.py
async def generate_diagram(description: str) -> str:
    """Generate stylized SVG diagram from description"""
    gateway = AIGateway()

    svg = await gateway.query(
        prompt=f"""Generate an SVG diagram:
        {description}

        Requirements:
        - Minimalist black line style
        - No fills, clean strokes
        - Proper viewBox and sizing
        - Return ONLY <svg>...</svg>""",
        tags=["graphics", "burst"],  # Use cloud if available
        max_tokens=2048
    )
    return svg
```

### Example 3: Documentation Assistant

```python
# bin/doc-assistant
#!/usr/bin/env python3
import sys
from wizard.services.ai_gateway import AIGateway

async def help_with_docs(topic: str):
    gateway = AIGateway()

    help_text = await gateway.query(
        prompt=f"""Help write documentation for: {topic}
        Style: Technical, clear examples, offline-first approach
        """,
        tags=["docs", "offline"]
    )
    print(help_text)

if __name__ == "__main__":
    asyncio.run(help_with_docs(sys.argv[1]))
```

---

## Part 8: Cost Analysis

### Monthly Cost Estimate

**Scenario: Active Development (50 AI queries/day)**

| Usage               | Local (Ollama) | Cloud (OpenRouter) | Hybrid      |
| ------------------- | -------------- | ------------------ | ----------- |
| 50 queries/day      | $0             | ~$15-30/mo         | ~$5-10/mo   |
| 100 queries/day     | $0             | ~$30-60/mo         | ~$10-20/mo  |
| Heavy use (500/day) | $0             | ~$150-300/mo       | ~$50-100/mo |

**Hybrid Strategy (Recommended):**

- Default: Local Mistral Small (free)
- When needed: OpenRouter Claude 3 (pay-per-use)
- Breaks even: ~5-10 cloud queries per month

---

## Part 9: Security Considerations

### Local (Ollama)

✅ All data stays on device  
✅ No network transmission  
✅ No API key exposure  
⚠️ Requires adequate disk space (3-8GB)

### Cloud (OpenRouter)

✅ Encrypted HTTPS connections  
✅ API key stored encrypted (secret store)  
✅ No prompt caching across users  
⚠️ Requests logged by OpenRouter  
⚠️ Never send: passwords, private keys, PII

### Wizard Server Routing

✅ All cloud requests validated by Wizard  
✅ Request redaction (removes tokens/secrets)  
✅ Per-device quotas enforced  
✅ Budget limits prevent overspending

---

## Quick Reference

```bash
# Start local AI
brew services start ollama
bin/Setup-Vibe.command

# Download model
ollama pull mistral:small

# Test local
vibe chat "Hello"

# Store cloud key
bin/wizard-secrets add --key-id=openrouter-main --provider=openrouter

# Start routing server
python wizard/launch_wizard_dev.py --no-tui

# Test cloud (with Wizard running)
curl -X POST http://localhost:8765/api/ai/route \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test", "tags": ["burst"]}'

# Check status
curl http://localhost:8765/api/health
```

---

## Next Steps

1. ✅ Run `bin/Setup-Vibe.command` (fixes model name)
2. ✅ Test with `vibe chat`
3. ⏳ Store OpenRouter key via `bin/wizard-secrets`
4. ⏳ Start Wizard Server for cloud routing
5. ⏳ Integrate into handlers (code review, docs, graphics)
6. ⏳ Monitor costs on OpenRouter dashboard

---

## References

- [Ollama Documentation](https://ollama.ai)
- [OpenRouter Models](https://openrouter.ai)
- [Wizard AI Gateway](../../wizard/services/ai_gateway.py)
- [Vibe (Mistral CLI)](https://github.com/mistralai/vibe)
- [Model Routing Policy](../decisions/wizard-model-routing-policy.md)

---

_Last Updated: 2026-01-17_  
_v1.0.4.0: Offline-First Complete_
