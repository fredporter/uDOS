import { apiFetch } from "$lib/services/apiBase";
import { buildAuthHeaders } from "$lib/services/auth";

const API_BASE = "/api/renderer";

async function fetchJson(path: string, options: RequestInit = {}) {
  const response = await apiFetch(`${API_BASE}${path}`, options);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  return response.json();
}

export async function listThemes(token?: string) {
  return fetchJson("/themes", { headers: buildAuthHeaders(token) });
}

export async function validateTheme(theme: string, token?: string) {
  return fetchJson(`/themes/${encodeURIComponent(theme)}/validate`, {
    method: "POST",
    headers: buildAuthHeaders(token),
  });
}

export async function validateAllThemes(token?: string) {
  return fetchJson(`/themes/validate`, {
    method: "POST",
    headers: buildAuthHeaders(token),
  });
}

export async function listSiteExports(token?: string) {
  return fetchJson("/site", { headers: buildAuthHeaders(token) });
}

export async function listSiteFiles(theme: string, token?: string) {
  return fetchJson(`/site/${encodeURIComponent(theme)}/files`, {
    headers: buildAuthHeaders(token),
  });
}

export async function listMissions(token?: string) {
  return fetchJson("/missions", { headers: buildAuthHeaders(token) });
}

export async function listContributions(token?: string, status?: string) {
  const suffix = status ? `?status=${encodeURIComponent(status)}` : "";
  return fetchJson(`/contributions${suffix}`, { headers: buildAuthHeaders(token) });
}

export async function updateContributionStatus(
  contributionId: string,
  status: string,
  reviewer?: string,
  note?: string,
  token?: string,
) {
  return fetchJson(`/contributions/${encodeURIComponent(contributionId)}/status`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(token),
    },
    body: JSON.stringify({ status, reviewer, note }),
  });
}

export async function listPlaces(token?: string) {
  return fetchJson("/places", { headers: buildAuthHeaders(token) });
}

export async function listSpatialAnchors(token?: string) {
  return fetchJson("/spatial/anchors", { headers: buildAuthHeaders(token) });
}

export async function listSpatialPlaces(token?: string) {
  return fetchJson("/spatial/places", { headers: buildAuthHeaders(token) });
}

export async function listSpatialFileTags(token?: string) {
  return fetchJson("/spatial/file-tags", { headers: buildAuthHeaders(token) });
}

export async function getMissionDetail(id: string, token?: string) {
  return fetchJson(`/missions/${encodeURIComponent(id)}`, {
    headers: buildAuthHeaders(token),
  });
}

export async function triggerRender(
  theme: string,
  missionId?: string,
  token?: string,
) {
  return fetchJson("/render", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(token),
    },
    body: JSON.stringify({
      theme,
      mission_id: missionId || undefined,
    }),
  });
}
