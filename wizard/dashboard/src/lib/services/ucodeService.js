import { apiFetch } from "$lib/services/apiBase";
import { buildAuthHeaders } from "$lib/services/auth";

const jsonHeaders = (token) => ({
  "Content-Type": "application/json",
  ...buildAuthHeaders(token),
});

export async function fetchUCodeCommands(token) {
  const res = await apiFetch("/api/ucode/commands", {
    headers: buildAuthHeaders(token),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function fetchUCodeAllowlist(token) {
  const res = await apiFetch("/api/ucode/allowlist", {
    headers: buildAuthHeaders(token),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function fetchUCodeHotkeys(token) {
  const res = await apiFetch("/api/ucode/hotkeys", {
    headers: buildAuthHeaders(token),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function fetchUCodeKeymap(token) {
  const res = await apiFetch("/api/ucode/keymap", {
    headers: buildAuthHeaders(token),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function updateUCodeKeymap(token, payload) {
  const res = await apiFetch("/api/ucode/keymap", {
    method: "POST",
    headers: jsonHeaders(token),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function fetchOkStatus(token) {
  const res = await apiFetch("/api/ucode/ok/status", {
    headers: buildAuthHeaders(token),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function fetchOkHistory(token) {
  const res = await apiFetch("/api/ucode/ok/history", {
    headers: buildAuthHeaders(token),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function setOkDefaultModel(token, model, profile) {
  const res = await apiFetch("/api/ucode/ok/model", {
    method: "POST",
    headers: jsonHeaders(token),
    body: JSON.stringify({ model, profile }),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function dispatchUCodeCommand(token, payload) {
  const res = await apiFetch("/api/ucode/dispatch", {
    method: "POST",
    headers: jsonHeaders(token),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function fetchUCodeUser(token) {
  const res = await apiFetch("/api/ucode/user", {
    headers: buildAuthHeaders(token),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function fetchUCodeUsers(token) {
  const res = await apiFetch("/api/ucode/users", {
    headers: buildAuthHeaders(token),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function switchUCodeUser(token, username) {
  const res = await apiFetch("/api/ucode/user/switch", {
    method: "POST",
    headers: jsonHeaders(token),
    body: JSON.stringify({ username }),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function setUCodeUserRole(token, username, role) {
  const res = await apiFetch("/api/ucode/user/role", {
    method: "POST",
    headers: jsonHeaders(token),
    body: JSON.stringify({ username, role }),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function fetchProviderDashboard(token) {
  const res = await apiFetch("/api/providers/dashboard", {
    headers: buildAuthHeaders(token),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function fetchDevStatus(token) {
  const res = await apiFetch("/api/dev/status", {
    headers: buildAuthHeaders(token),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function toggleDevMode(token, active) {
  const endpoint = active ? "/api/dev/activate" : "/api/dev/deactivate";
  const res = await apiFetch(endpoint, {
    method: "POST",
    headers: buildAuthHeaders(token),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function restartDevMode(token) {
  const res = await apiFetch("/api/dev/restart", {
    method: "POST",
    headers: buildAuthHeaders(token),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function fetchMonitoringDiagnostics(token) {
  const res = await apiFetch("/api/monitoring/diagnostics", {
    headers: buildAuthHeaders(token),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function fetchWizardHealth() {
  const res = await apiFetch("/health");
  return res.ok;
}
