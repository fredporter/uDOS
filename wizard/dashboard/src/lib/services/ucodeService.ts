/**
 * uCode command service - interact with ucode terminal API
 */

import { apiFetch } from "./apiBase";

/**
 * Fetch available ucode commands
 */
export async function fetchUCodeCommands() {
  try {
    const res = await apiFetch("/api/ucode/commands");
    if (res.ok) return await res.json();
  } catch {}
  return { commands: [] };
}

/**
 * Fetch ucode hotkeys
 */
export async function fetchUCodeHotkeys() {
  try {
    const res = await apiFetch("/api/ucode/hotkeys");
    if (res.ok) return await res.json();
  } catch {}
  return { hotkeys: [] };
}

/**
 * Fetch OK status
 */
export async function fetchOkStatus() {
  try {
    const res = await apiFetch("/api/ok/status");
    if (res.ok) return await res.json();
  } catch {}
  return { status: "unavailable" };
}

/**
 * Fetch OK history
 */
export async function fetchOkHistory() {
  try {
    const res = await apiFetch("/api/ok/history");
    if (res.ok) return await res.json();
  } catch {}
  return { history: [] };
}

/**
 * Set OK default model
 */
export async function setOkDefaultModel(model) {
  try {
    const res = await apiFetch("/api/ok/model", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model }),
    });
    return res.ok;
  } catch {}
  return false;
}

/**
 * Dispatch ucode command
 */
export async function dispatchUCodeCommand(command, args = {}) {
  try {
    const res = await apiFetch("/api/ucode/execute", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command, args }),
    });
    if (res.ok) return await res.json();
  } catch {}
  return { success: false, error: "Command failed" };
}

/**
 * Fetch ucode user info
 */
export async function fetchUCodeUser() {
  try {
    const res = await apiFetch("/api/ucode/user");
    if (res.ok) return await res.json();
  } catch {}
  return { user: null };
}

/**
 * Fetch all ucode users
 */
export async function fetchUCodeUsers() {
  try {
    const res = await apiFetch("/api/ucode/users");
    if (res.ok) return await res.json();
  } catch {}
  return { users: [] };
}

/**
 * Switch ucode user
 */
export async function switchUCodeUser(userId) {
  try {
    const res = await apiFetch(`/api/ucode/user/${userId}`, { method: "POST" });
    return res.ok;
  } catch {}
  return false;
}

/**
 * Set ucode user role
 */
export async function setUCodeUserRole(userId, role) {
  try {
    const res = await apiFetch(`/api/ucode/user/${userId}/role`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ role }),
    });
    return res.ok;
  } catch {}
  return false;
}

/**
 * Fetch provider dashboard (AI provider info)
 */
export async function fetchProviderDashboard() {
  try {
    const res = await apiFetch("/api/providers/dashboard");
    if (res.ok) return await res.json();
  } catch {}
  return { providers: [] };
}

/**
 * Fetch dev status
 */
export async function fetchDevStatus() {
  try {
    const res = await apiFetch("/api/dev/status");
    if (res.ok) return await res.json();
  } catch {}
  return { dev_mode: false };
}

/**
 * Toggle dev mode
 */
export async function toggleDevMode(enabled) {
  try {
    const res = await apiFetch("/api/dev/toggle", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ enabled }),
    });
    return res.ok;
  } catch {}
  return false;
}

/**
 * Restart dev mode
 */
export async function restartDevMode() {
  try {
    const res = await apiFetch("/api/dev/restart", { method: "POST" });
    return res.ok;
  } catch {}
  return false;
}

/**
 * Fetch monitoring diagnostics
 */
export async function fetchMonitoringDiagnostics() {
  try {
    const res = await apiFetch("/api/monitoring/diagnostics");
    if (res.ok) return await res.json();
  } catch {}
  return { diagnostics: [] };
}

/**
 * Fetch wizard health
 */
export async function fetchWizardHealth() {
  try {
    const res = await apiFetch("/health");
    if (res.ok) return await res.json();
  } catch {}
  return { status: "unhealthy" };
}

/**
 * Fetch seed template families.
 */
export async function fetchTemplateFamilies() {
  try {
    const res = await apiFetch("/api/ucode/templates");
    if (res.ok) return await res.json();
  } catch {}
  return { families: {} };
}

/**
 * Fetch templates for one family.
 */
export async function fetchTemplateFamily(family) {
  try {
    const res = await apiFetch(`/api/ucode/templates/${encodeURIComponent(family)}`);
    if (res.ok) return await res.json();
  } catch {}
  return { family, templates: [] };
}

/**
 * Read one seeded template.
 */
export async function readTemplate(family, templateName) {
  try {
    const res = await apiFetch(
      `/api/ucode/templates/${encodeURIComponent(family)}/${encodeURIComponent(templateName)}`
    );
    if (res.ok) return await res.json();
  } catch {}
  return { status: "error", template: null };
}

/**
 * Duplicate a seeded template into the user layer.
 */
export async function duplicateTemplate(family, templateName, targetName = "") {
  try {
    const res = await apiFetch(
      `/api/ucode/templates/${encodeURIComponent(family)}/${encodeURIComponent(templateName)}/duplicate`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target_name: targetName || null }),
      }
    );
    if (res.ok) return await res.json();
    return {
      status: "error",
      error: await res.text(),
    };
  } catch (err) {
    return { status: "error", error: err?.message || String(err) };
  }
}
