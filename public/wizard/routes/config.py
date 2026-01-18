"""
Configuration Management Routes
================================

REST API endpoints for managing API keys and configuration.

Endpoints:
  GET  /api/v1/config/status     - Overall config status
  GET  /api/v1/config/keys       - List all keys (no values)
  POST /api/v1/config/keys/{name} - Set a key
  GET  /api/v1/config/keys/{name} - Get key status (no value)
  DELETE /api/v1/config/keys/{name} - Delete a key
  POST /api/v1/config/validate/{name} - Validate key format
  GET  /api/v1/config/export     - Export as .env (secret)
  GET  /api/v1/config/panel      - Serve config management UI
"""

import os
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from typing import Dict, Any, Optional
from pydantic import BaseModel

from wizard.services.secure_config import SecureConfigManager, KeyCategory
from wizard.services.config_framework import get_config_framework, ConfigFramework

router = APIRouter(prefix="/api/v1/config", tags=["configuration"])

# Global config manager (initialized in server.py)
_config_manager: Optional[SecureConfigManager] = None


def get_config_manager() -> SecureConfigManager:
    """Dependency injection for config manager."""
    global _config_manager
    if _config_manager is None:
        _config_manager = SecureConfigManager()
    return _config_manager


# Request/Response Models
class KeyRequest(BaseModel):
    """Request to set a key."""
    value: str
    provider: Optional[str] = ""
    category: str = "ai_providers"


class KeyResponse(BaseModel):
    """Response with key info (no value)."""
    name: str
    provider: str
    category: str
    is_set: bool
    is_validated: bool
    validation_error: Optional[str] = None
    created_at: str
    last_updated: str


# Routes
@router.get("/status")
async def get_config_status(config: SecureConfigManager = Depends(get_config_manager)) -> Dict[str, Any]:
    """Get overall configuration status."""
    return config.get_status()


@router.get("/keys")
async def list_keys(
    category: Optional[str] = None,
    config: SecureConfigManager = Depends(get_config_manager)
) -> Dict[str, Dict[str, Any]]:
    """List all keys (without values)."""
    cat = KeyCategory(category) if category else None
    return config.get_all_keys(category=cat, include_values=False)


@router.post("/keys/{key_name}")
async def set_key(
    key_name: str,
    request: KeyRequest,
    config: SecureConfigManager = Depends(get_config_manager)
) -> Dict[str, Any]:
    """Set an API key."""
    category = KeyCategory(request.category)
    success = config.set_key(
        name=key_name,
        value=request.value,
        category=category,
        provider=request.provider
    )

    if not success:
        raise HTTPException(status_code=400, detail="Failed to set key")

    # Try to validate
    config.validate_key(key_name)

    key = config.get_all_keys().get(key_name)
    return {
        "status": "success",
        "message": f"Key {key_name} set successfully",
        "key": key,
    }


@router.get("/keys/{key_name}")
async def get_key_status(
    key_name: str,
    config: SecureConfigManager = Depends(get_config_manager)
) -> Dict[str, Any]:
    """Get key status (without value)."""
    keys = config.get_all_keys()
    if key_name not in keys:
        raise HTTPException(status_code=404, detail=f"Key {key_name} not found")

    return {
        "key_name": key_name,
        **keys[key_name],
    }


@router.delete("/keys/{key_name}")
async def delete_key(
    key_name: str,
    config: SecureConfigManager = Depends(get_config_manager)
) -> Dict[str, Any]:
    """Delete a key."""
    if not config.delete_key(key_name):
        raise HTTPException(status_code=404, detail=f"Key {key_name} not found")

    return {
        "status": "success",
        "message": f"Key {key_name} deleted",
    }


@router.post("/validate/{key_name}")
async def validate_key(
    key_name: str,
    config: SecureConfigManager = Depends(get_config_manager)
) -> Dict[str, Any]:
    """Validate key format."""
    is_valid = config.validate_key(key_name)

    key = config.get_all_keys().get(key_name)
    return {
        "key_name": key_name,
        "is_valid": is_valid,
        "key": key,
    }


@router.get("/export")
async def export_env(
    secret_token: Optional[str] = None,
    config: SecureConfigManager = Depends(get_config_manager)
) -> Dict[str, str]:
    """
    Export all keys as .env format.

    ⚠️  SECURITY: Requires secret token from environment.
    Never share this endpoint publicly!
    """
    expected_token = os.getenv("UDOS_ADMIN_TOKEN")

    if not expected_token or secret_token != expected_token:
        raise HTTPException(status_code=403, detail="Invalid or missing admin token")

    env_content = config.export_env()
    return {
        "status": "success",
        "message": "⚠️  DO NOT COMMIT THIS TO GIT! Save to .env only.",
        "content": env_content,
    }


@router.get("/panel", response_class=HTMLResponse)
async def get_config_panel():
    """Serve configuration management UI."""
    return _get_config_panel_html()


# Helper function for UI
def _get_config_panel_html() -> str:
    """Generate HTML for config panel."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><span class="emoji-mono">🔐</span> uDOS Secrets Manager</title>
    <link rel="stylesheet" href="/static/css/global.css">
</head>
<body class="app">
    <div class="shell">
        <div class="main pane">
            <div class="container">
                <div class="config-header">
                    <h1><span class="emoji-mono">🔐</span> uDOS Secrets Manager</h1>
                    <p>Securely manage API keys and credentials • Encrypted with AES-256</p>
                </div>

                <div class="instructions card">
                    <div class="card-header"><span class="emoji-mono">📋</span> How to Add/Update Keys</div>
                    <div class="card-body">
                        <ol>
                            <li><strong>Copy your new API key</strong> from the provider (Google, OpenAI, etc.)</li>
                            <li><strong>Paste into the input field</strong> under the relevant category</li>
                            <li><strong>Click "Save"</strong> to encrypt and store securely</li>
                            <li><strong>Run</strong> <code>./bin/setup-secrets.sh</code> to generate config files</li>
                            <li><strong>Verify</strong> the key works in your code</li>
                        </ol>
                    </div>
                </div>

                <div id="message" class="message"></div>

                <div class="card" id="status">
                    <div class="card-header"><span class="emoji-mono">📊</span> Configuration Status</div>
                    <div class="card-body">
                        <div class="status-grid" id="statusGrid">
                            <div class="stat">
                                <div class="stat-label">Total Keys</div>
                                <div class="stat-value" id="totalKeys">-</div>
                            </div>
                            <div class="stat">
                                <div class="stat-label">Keys Set</div>
                                <div class="stat-value" id="keysSet">-</div>
                            </div>
                            <div class="stat">
                                <div class="stat-label">Validated</div>
                                <div class="stat-value" id="keysValidated">-</div>
                            </div>
                            <div class="stat">
                                <div class="stat-label">Encryption</div>
                                <div class="stat-value" id="encryption">-</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="categories-grid" id="categories">
                    <!-- Populated by JavaScript -->
                </div>
            </div>
        </div>

        <!-- Global Bottom Bar (like /app) -->
        <div class="bottom-bar">
            <div class="bottom-bar__group">
                <span class="bottom-bar__item"><span class="emoji-mono">🔐</span> Encrypted • AES-256</span>
            </div>
            <div class="bottom-bar__group">
                <span class="bottom-bar__item" id="statusIndicator"><span class="emoji-mono">⏳</span> Loading...</span>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = "/api/v1/config";

        async function loadStatus() {
            try {
                const response = await fetch(`${API_BASE}/status`);
                const data = await response.json();

                document.getElementById("totalKeys").textContent = data.total_keys;
                document.getElementById("keysSet").textContent = data.keys_set;
                document.getElementById("keysValidated").textContent = data.keys_validated;
                document.getElementById("encryption").textContent = data.encryption_enabled ? "✅ Enabled" : "⚠️ Disabled";
                document.getElementById("statusIndicator").innerHTML = `<span class="emoji-mono">✅</span> Ready`;

                await loadCategories(data);
            } catch (error) {
                showMessage("❌ Error loading status: " + error.message, "error");
                document.getElementById("statusIndicator").innerHTML = `<span class="emoji-mono">❌</span> Error`;
            }
        }

        async function loadCategories(statusData) {
            try {
                const keysResponse = await fetch(`${API_BASE}/keys`);
                const allKeys = await keysResponse.json();
                const container = document.getElementById("categories");
                container.innerHTML = "";

                // Build category map from allKeys instead of statusData
                const byCategory = {};
                for (const [keyName, keyInfo] of Object.entries(allKeys)) {
                    const cat = keyInfo.category || "uncategorized";
                    if (!byCategory[cat]) {
                        byCategory[cat] = { keys: [], total: 0, set: 0 };
                    }
                    byCategory[cat].keys.push(keyName);
                    byCategory[cat].total++;
                    if (keyInfo.is_set) byCategory[cat].set++;
                }

                if (Object.keys(byCategory).length === 0) {
                    container.innerHTML = '<div class="message info"><span class="emoji-mono">ℹ️</span> No keys configured yet. Add one above.</div>';
                    return;
                }

                for (const [category, categoryInfo] of Object.entries(byCategory)) {
                    const card = document.createElement("div");
                    card.className = "category-card";

                    const header = document.createElement("div");
                    header.className = "category-header";
                    header.innerHTML = `<span class="emoji-mono">📦</span> ${formatCategory(category)} <span style="float: right; opacity: 0.7;">${categoryInfo.set}/${categoryInfo.total}</span>`;
                    card.appendChild(header);

                    const list = document.createElement("div");
                    list.className = "keys-list";

                    // categoryInfo.keys contains the key names for this category
                    const keyNames = categoryInfo.keys || [];

                    for (const keyName of keyNames) {
                        const keyInfo = allKeys[keyName];
                        if (!keyInfo) continue;

                        const item = document.createElement("div");
                        item.className = "key-item";

                        // Build status badges
                        let statusHtml = '';
                        if (keyInfo.is_set) {
                            statusHtml += '<span class="badge badge-success"><span class="emoji-mono">✓</span> Set</span>';
                        } else {
                            statusHtml += '<span class="badge badge-warning"><span class="emoji-mono">✗</span> Not Set</span>';
                        }

                        if (keyInfo.is_validated) {
                            statusHtml += '<span class="badge badge-info"><span class="emoji-mono">✓</span> Valid</span>';
                        }

                        item.innerHTML = `
                            <div class="key-name">${keyName}</div>
                            <div class="key-provider">${keyInfo.provider || "—"}</div>
                            <div class="key-status">
                                ${statusHtml}
                            </div>
                            <div class="key-input-group">
                                <input type="password" class="key-input" placeholder="Paste new key here" id="input_${keyName}">
                                <button class="btn btn-save" onclick="saveKey('${keyName}', '${category}')">Save</button>
                                <button class="btn btn-delete" onclick="deleteKey('${keyName}')" title="Delete key">🗑️</button>
                            </div>
                        `;
                        list.appendChild(item);
                    }

                    card.appendChild(list);
                    container.appendChild(card);
                }
            } catch (error) {
                console.error("Error loading categories:", error);
                showMessage("❌ Error loading categories: " + error.message, "error");
            }
        }

        async function saveKey(keyName, category) {
            const input = document.getElementById(`input_${keyName}`);
            const value = input.value.trim();

            if (!value) {
                showMessage("❌ Please enter a value", "error");
                return;
            }

            try {
                const response = await fetch(`${API_BASE}/keys/${keyName}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        value: value,
                        category: category,
                        provider: keyName.split("_")[0]
                    })
                });

                if (response.ok) {
                    showMessage(`✅ ${keyName} saved successfully!`, "success");
                    input.value = "";
                    setTimeout(loadStatus, 1000);
                } else {
                    const error = await response.json();
                    showMessage(`❌ Error: ${error.detail}`, "error");
                }
            } catch (error) {
                showMessage("❌ Network error: " + error.message, "error");
            }
        }

        async function deleteKey(keyName) {
            if (!confirm(`Delete ${keyName}? This cannot be undone.`)) return;

            try {
                const response = await fetch(`${API_BASE}/keys/${keyName}`, {
                    method: "DELETE"
                });

                if (response.ok) {
                    showMessage(`✅ ${keyName} deleted`, "success");
                    setTimeout(loadStatus, 1000);
                } else {
                    const error = await response.json();
                    showMessage(`❌ Error: ${error.detail}`, "error");
                }
            } catch (error) {
                showMessage("❌ Network error: " + error.message, "error");
            }
        }

        function formatCategory(cat) {
            return cat.replace(/_/g, " ").split(" ").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
        }

        function showMessage(text, type) {
            const msg = document.getElementById("message");
            msg.innerHTML = text;
            msg.className = `message ${type} show`;
            setTimeout(() => {
                msg.classList.remove("show");
            }, 5000);
        }

        # Load on startup
        loadStatus();
        setInterval(loadStatus, 30000); // Refresh every 30 seconds
    </script>
</body>
</html>
    """


# Config Framework Routes
# =======================
# These endpoints support the new global config framework
# used by the simplified config panel with Micro editor integration.

@router.get("/framework/registry")
async def get_framework_registry(
    category: Optional[str] = None,
    framework: ConfigFramework = Depends(get_config_framework)
) -> Dict[str, Any]:
    """Get API registry organized by category."""
    registry = framework.get_registry_by_category()

    if category:
        # Return only the requested category
        if category in registry:
            return {
                "category": category,
                "apis": registry[category],
            }
        else:
            raise HTTPException(status_code=404, detail=f"Category {category} not found")

    return {
        "status": "success",
        "total": sum(len(apis) for apis in registry.values()),
        "categories": {
            cat: {
                "count": len(apis),
                "apis": apis,
            }
            for cat, apis in registry.items()
        }
    }


@router.get("/framework/status")
async def get_framework_status(
    framework: ConfigFramework = Depends(get_config_framework)
) -> Dict[str, Any]:
    """Get current status of all configured APIs."""
    return {
        "status": "success",
        "statuses": {
            api.env_key: api.status.value
            for apis in framework.get_registry_by_category().values()
            for api in apis
        }
    }
