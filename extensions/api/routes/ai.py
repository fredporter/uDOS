"""
AI API routes for testing connections and managing providers.
"""

import sys
from pathlib import Path
from flask import Blueprint, jsonify, request

# Add paths
project_root = Path(__file__).parent.parent.parent.parent
core_path = project_root / "core"
wizard_path = project_root / "wizard"
if str(core_path) not in sys.path:
    sys.path.insert(0, str(core_path))
if str(wizard_path) not in sys.path:
    sys.path.insert(0, str(wizard_path))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/api/ai/test", methods=["GET", "POST"])
def test_providers():
    """Test AI provider connections."""
    data = request.json if request.method == "POST" else {}
    provider = data.get("provider") or request.args.get("provider")

    providers_to_test = (
        [provider] if provider else ["gemini", "anthropic", "openai", "devstral"]
    )
    results = {}

    for prov in providers_to_test:
        results[prov] = _test_provider(prov)

    configured = sum(1 for r in results.values() if r.get("configured"))
    working = sum(1 for r in results.values() if r.get("success"))

    return jsonify(
        {
            "results": results,
            "summary": {
                "total": len(providers_to_test),
                "configured": configured,
                "working": working,
            },
        }
    )


@ai_bp.route("/api/ai/test/<provider>", methods=["GET", "POST"])
def test_single_provider(provider: str):
    """Test a specific AI provider."""
    result = _test_provider(provider)
    return jsonify(result)


def _test_provider(provider: str) -> dict:
    """Test a single provider and return results."""
    result = {
        "provider": provider,
        "configured": False,
        "success": False,
        "model": None,
        "response_preview": None,
        "error": None,
        "latency_ms": 0,
    }

    try:
        if provider == "gemini":
            from wizard.providers.gemini_client import GeminiClient, GeminiRequest

            client = GeminiClient()
            if not client.api_key:
                result["error"] = "No API key configured"
                return result

            result["configured"] = True

            req = GeminiRequest(
                prompt="Reply with exactly: 'Connection successful'",
                max_tokens=50,
                temperature=0.0,
            )

            response = client.complete(req)
            if response.success:
                result["success"] = True
                result["model"] = response.model
                result["response_preview"] = response.content[:100]
                result["latency_ms"] = response.latency_ms
            else:
                result["error"] = response.error

        elif provider == "anthropic":
            from wizard.providers.anthropic_client import (
                AnthropicClient,
                AnthropicRequest,
            )

            client = AnthropicClient()
            if not client.api_key:
                result["error"] = "No API key configured"
                return result

            result["configured"] = True

            req = AnthropicRequest(
                prompt="Reply with exactly: 'Connection successful'",
                max_tokens=50,
                temperature=0.0,
            )

            response = client.complete(req)
            if response.success:
                result["success"] = True
                result["model"] = response.model
                result["response_preview"] = response.content[:100]
                result["latency_ms"] = response.latency_ms
            else:
                result["error"] = response.error

        elif provider == "openai":
            from wizard.providers.openai_client import OpenAIClient, OpenOKRequest

            client = OpenAIClient()
            if not client.api_key:
                result["error"] = "No API key configured"
                return result

            result["configured"] = True

            req = OpenOKRequest(
                prompt="Reply with exactly: 'Connection successful'",
                max_tokens=50,
                temperature=0.0,
            )

            response = client.complete(req)
            if response.success:
                result["success"] = True
                result["model"] = response.model
                result["response_preview"] = response.content[:100]
                result["latency_ms"] = response.latency_ms
            else:
                result["error"] = response.error

        elif provider == "devstral":
            from wizard.providers.devstral_client import DevstralClient, DevstralRequest

            client = DevstralClient()
            if not client.api_key:
                result["error"] = "No API key configured"
                return result

            result["configured"] = True

            req = DevstralRequest(
                prompt="Reply with exactly: 'Connection successful'",
                max_tokens=50,
                temperature=0.0,
            )

            response = client.complete(req)
            if response.success:
                result["success"] = True
                result["model"] = response.model
                result["response_preview"] = response.content[:100]
                result["latency_ms"] = response.latency_ms
            else:
                result["error"] = response.error

        else:
            result["error"] = f"Unknown provider: {provider}"

    except ImportError as e:
        result["error"] = f"Package not installed: {str(e)}"
    except Exception as e:
        result["error"] = str(e)

    return result


@ai_bp.route("/api/ai/keys", methods=["GET"])
def check_keys():
    """Check which API keys are configured (without revealing them)."""
    import os

    env_keys = {
        "GEMINI_API_KEY": bool(
            os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        ),
        "ANTHROPIC_API_KEY": bool(os.environ.get("ANTHROPIC_API_KEY")),
        "OPENAI_API_KEY": bool(os.environ.get("OPENAI_API_KEY")),
        "MISTRAL_API_KEY": bool(os.environ.get("MISTRAL_API_KEY")),
    }

    config_file = (
        Path(__file__).parent.parent.parent.parent
        / "wizard"
        / "config"
        / "ai_keys.json"
    )
    config_keys = {}
    config_exists = config_file.exists()

    if config_exists:
        try:
            import json

            data = json.loads(config_file.read_text())
            for key in [
                "GEMINI_API_KEY",
                "ANTHROPIC_API_KEY",
                "OPENAI_API_KEY",
                "MISTRAL_API_KEY",
            ]:
                config_keys[key] = bool(data.get(key))
        except Exception:
            pass

    return jsonify(
        {
            "environment": env_keys,
            "config_file": {
                "exists": config_exists,
                "path": str(config_file),
                "keys": config_keys,
            },
        }
    )


# NOTE: list_prompts moved to PROMPT MANAGEMENT ENDPOINTS section below


@ai_bp.route("/api/ai/generate", methods=["POST"])
def generate_content():
    """Generate content using AI."""
    data = request.json or {}

    prompt = data.get("prompt", "")
    provider = data.get("provider", "gemini")
    gen_type = data.get("type", "custom")
    max_tokens = data.get("max_tokens", 2000)
    temperature = data.get("temperature", 0.7)

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    try:
        from core_beta.services.ai_generation import (
            AIGenerationService,
            GenerationRequest,
            GenerationType,
            AIProvider,
        )

        service = AIGenerationService()

        # Map string to enum
        provider_map = {
            "gemini": AIProvider.GEMINI,
            "anthropic": None,  # Not in AIProvider enum yet
            "openai": None,
            "devstral": AIProvider.DEVSTRAL,
            "mistral": AIProvider.MISTRAL,
        }

        type_map = {
            "guide": GenerationType.MAKE_GUIDE,
            "do": GenerationType.MAKE_DO,
            "suggest": GenerationType.SUGGEST,
            "encyclopedia": GenerationType.ENCYCLOPEDIA,
            "custom": GenerationType.CUSTOM,
        }

        request_obj = GenerationRequest(
            prompt=prompt,
            gen_type=type_map.get(gen_type, GenerationType.CUSTOM),
            max_tokens=max_tokens,
            temperature=temperature,
            provider=provider_map.get(provider),
        )

        response = service.generate(request_obj)

        return jsonify(
            {
                "success": response.success,
                "content": response.content,
                "provider": response.provider.value if response.provider else None,
                "model": response.model,
                "tokens_used": response.tokens_used,
                "cost_usd": response.cost_usd,
                "error": response.error if hasattr(response, "error") else None,
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@ai_bp.route("/api/ai/generate/image", methods=["POST"])
def generate_image():
    """Generate an image using Gemini's image generation model."""
    data = request.json or {}

    prompt = data.get("prompt", "")
    style = data.get("style", "technical")  # technical, sketch, diagram, photo

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    try:
        from wizard.providers.gemini_client import GeminiClient, GeminiRequest

        client = GeminiClient()

        # Use the experimental image generation model
        req = GeminiRequest(
            prompt=f"Generate a {style} style image: {prompt}",
            model="gemini-2.0-flash-exp-image-generation",  # Image generation model
            max_tokens=1000,
            temperature=0.7,
        )

        response = client.complete(req)

        if response.success:
            # Check if response contains image data
            # The Gemini API may return image as base64 or URL depending on configuration
            return jsonify(
                {
                    "success": True,
                    "content": response.content,
                    "model": response.model,
                    "tokens_used": response.tokens_used,
                    "cost_usd": response.cost_usd,
                    # Note: Actual image data handling depends on Gemini's response format
                    # May need to parse response.content for image data
                }
            )
        else:
            return jsonify({"success": False, "error": response.error}), 500

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==============================================================================
# PROMPT MANAGEMENT ENDPOINTS
# ==============================================================================


@ai_bp.route("/api/ai/prompts", methods=["GET"])
def list_prompts():
    """
    List all available AI prompts.

    Query params:
        provider: Filter by provider (gemini, mistral, all)
        tags: Filter by tags (comma-separated)
    """
    try:
        from core_beta.services.prompt_loader import get_prompt_loader

        loader = get_prompt_loader()
        provider = request.args.get("provider")
        tags_str = request.args.get("tags")
        tags = tags_str.split(",") if tags_str else None

        prompts = loader.list_prompts(provider=provider, tags=tags)

        return jsonify({"success": True, "prompts": prompts, "count": len(prompts)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@ai_bp.route("/api/ai/prompts/<prompt_id>", methods=["GET"])
def get_prompt(prompt_id: str):
    """
    Get a specific prompt by ID.

    Returns full prompt data including body.
    """
    try:
        from core_beta.services.prompt_loader import get_prompt_loader

        loader = get_prompt_loader()
        prompt = loader.get_prompt(prompt_id)

        if not prompt:
            return (
                jsonify({"success": False, "error": f"Prompt not found: {prompt_id}"}),
                404,
            )

        return jsonify(
            {
                "success": True,
                "prompt": {
                    "id": prompt_id,
                    "provider": prompt.get("provider", "all"),
                    "version": prompt.get("version", "1.0.0"),
                    "tags": prompt.get("tags", []),
                    "source": prompt.get("source", "system"),
                    "body": prompt.get("body", ""),
                    "frontmatter": prompt.get("frontmatter", {}),
                },
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@ai_bp.route("/api/ai/prompts/<prompt_id>/section/<section>", methods=["GET"])
def get_prompt_section(prompt_id: str, section: str):
    """
    Get a specific section from a prompt.

    Useful for extracting system prompts or specific instructions.
    """
    try:
        from core_beta.services.prompt_loader import get_prompt_loader

        loader = get_prompt_loader()
        content = loader.get_system_prompt(prompt_id, section.replace("-", " ").title())

        if not content:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Section '{section}' not found in prompt '{prompt_id}'",
                    }
                ),
                404,
            )

        return jsonify(
            {
                "success": True,
                "prompt_id": prompt_id,
                "section": section,
                "content": content,
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@ai_bp.route("/api/ai/prompts/reload", methods=["POST"])
def reload_prompts():
    """Reload all prompts from disk."""
    try:
        from core_beta.services.prompt_loader import get_prompt_loader

        loader = get_prompt_loader()
        loader.reload()

        return jsonify(
            {
                "success": True,
                "message": "Prompts reloaded",
                "count": len(loader.list_prompts()),
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@ai_bp.route("/api/ai/prompts/styles", methods=["GET"])
def list_image_styles():
    """
    List available image generation styles.

    Returns styles from gemini-image.md prompt.
    """
    styles = [
        {
            "id": "technical-kinetic",
            "name": "Technical-Kinetic",
            "description": "MCM geometry with kinetic elements, black & white only",
            "provider": "gemini",
            "format": "svg",
        },
        {
            "id": "nano-banana",
            "name": "Nano-Banana",
            "description": "Playful minimal geometric illustrations",
            "provider": "gemini",
            "format": "svg",
        },
        {
            "id": "teletext",
            "name": "Teletext",
            "description": "WST mosaic, 8-color retro graphics",
            "provider": "gemini",
            "format": "teletext",
        },
        {
            "id": "ascii",
            "name": "ASCII/PETSCII",
            "description": "C64-inspired character art",
            "provider": "gemini",
            "format": "text",
        },
    ]

    return jsonify({"success": True, "styles": styles})
