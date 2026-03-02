# Offline OK Setup Reference

Updated: 2026-03-03
Status: active how-to reference

## Scope

Detailed reference for:
- local Ollama setup
- optional OpenRouter burst routing
- routing policy
- troubleshooting
- performance notes
- security notes

## Local Setup

Key local setup tasks:
- install and start Ollama
- choose an appropriate local model
- configure `.vibe/config.toml`
- optionally tune Apple Silicon or memory-constrained systems

Recommended local model:
- `mistral:small`

## Cloud Burst

Optional cloud burst setup includes:
- OpenRouter account creation
- secret storage in Wizard
- local-first fallback configuration in Wizard gateway settings

## Routing Policy

Typical policy:
- local first
- cloud fallback when local work fails or explicit burst conditions are met
- budget-aware cloud usage through Wizard

## Troubleshooting

Common issues:
- Ollama API not responding
- local model not found
- out-of-memory during local inference
- OpenRouter authorization failures

## Performance and Cost

Track:
- local latency by model and hardware
- cloud latency and quality tradeoffs
- monthly burst cost exposure

## Security

Local:
- prefer local execution for sensitive prompts

Cloud:
- route through managed Wizard policy where possible
- keep secrets in Wizard-managed storage

## Canonical Front Door

Start with:
- [Offline OK Setup Quickstart](/Users/fredbook/Code/uDOS/docs/howto/OFFLINE-OK-SETUP-QUICKSTART.md)

