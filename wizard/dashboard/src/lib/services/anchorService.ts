import { apiFetch } from "$lib/services/apiBase";
import { buildAuthHeaders } from "$lib/services/auth";

const API_BASE = "/api/anchors";

async function fetchJson(path: string, options: RequestInit = {}) {
  const response = await apiFetch(`${API_BASE}${path}`, options);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  return response.json();
}

export async function listAnchors(token?: string) {
  return fetchJson("", { headers: buildAuthHeaders(token) });
}

export async function getAnchor(anchorId: string, token?: string) {
  return fetchJson(`/${encodeURIComponent(anchorId)}`, {
    headers: buildAuthHeaders(token),
  });
}

export async function bindAnchor(payload: any, token?: string) {
  return fetchJson("/bind", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(token),
    },
    body: JSON.stringify(payload),
  });
}
