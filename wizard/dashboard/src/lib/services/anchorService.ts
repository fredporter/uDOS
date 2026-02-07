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

export async function registerAnchor(payload: {
  anchor_id: string;
  title: string;
  description?: string;
  version?: string;
  capabilities?: Record<string, unknown>;
}, token?: string) {
  return fetchJson("/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(token),
    },
    body: JSON.stringify(payload),
  });
}

export async function createAnchorInstance(payload: {
  anchor_id: string;
  profile_id?: string;
  space_id?: string;
  seed?: string;
  meta_json?: Record<string, unknown>;
}, token?: string) {
  return fetchJson("/instances", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(token),
    },
    body: JSON.stringify(payload),
  });
}

export async function destroyAnchorInstance(instanceId: string, token?: string) {
  return fetchJson(`/instances/${encodeURIComponent(instanceId)}`, {
    method: "DELETE",
    headers: buildAuthHeaders(token),
  });
}

export async function listAnchorInstances(anchorId?: string, token?: string) {
  const suffix = anchorId ? `?anchor_id=${encodeURIComponent(anchorId)}` : "";
  return fetchJson(`/instances${suffix}`, { headers: buildAuthHeaders(token) });
}

export async function listAnchorEvents(
  params: { anchorId?: string; instanceId?: string; limit?: number; type?: string },
  token?: string,
) {
  const query = new URLSearchParams();
  if (params?.anchorId) query.set("anchor_id", params.anchorId);
  if (params?.instanceId) query.set("instance_id", params.instanceId);
  if (params?.type) query.set("type", params.type);
  if (params?.limit) query.set("limit", String(params.limit));
  const suffix = query.toString() ? `?${query.toString()}` : "";
  return fetchJson(`/events${suffix}`, { headers: buildAuthHeaders(token) });
}
