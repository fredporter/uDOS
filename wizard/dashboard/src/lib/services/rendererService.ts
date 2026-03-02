/**
 * Renderer Service
 *
 * Provides API access to theme validation, site rendering, and spatial data management
 */

import type { ApiFetch } from './apiBase';

export async function listThemes(apiFetch: ApiFetch, token: string): Promise<string[]> {
  const res = await apiFetch('/api/renderer/themes', {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Failed to list themes: ${res.status}`);
  const data = await res.json();
  return data.themes || [];
}

export async function validateTheme(apiFetch: ApiFetch, token: string, themeId: string): Promise<any> {
  const res = await apiFetch(`/api/renderer/themes/${themeId}/validate`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Failed to validate theme: ${res.status}`);
  return await res.json();
}

export async function validateAllThemes(apiFetch: ApiFetch, token: string): Promise<any> {
  const res = await apiFetch('/api/renderer/themes/validate-all', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Failed to validate all themes: ${res.status}`);
  return await res.json();
}

export async function validateContracts(apiFetch: ApiFetch, token: string): Promise<any> {
  const res = await apiFetch('/api/renderer/contracts/validate', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Failed to validate contracts: ${res.status}`);
  return await res.json();
}

export async function listSiteExports(apiFetch: ApiFetch, token: string): Promise<any[]> {
  const res = await apiFetch('/api/renderer/exports', {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Failed to list site exports: ${res.status}`);
  const data = await res.json();
  return data.exports || [];
}

export async function listSiteFiles(apiFetch: ApiFetch, token: string): Promise<any[]> {
  const res = await apiFetch('/api/renderer/files', {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Failed to list site files: ${res.status}`);
  const data = await res.json();
  return data.files || [];
}

export async function listMissions(apiFetch: ApiFetch, token: string): Promise<any[]> {
  const res = await apiFetch('/api/renderer/missions', {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Failed to list missions: ${res.status}`);
  const data = await res.json();
  return data.missions || [];
}

export async function getMissionDetail(apiFetch: ApiFetch, token: string, missionId: string): Promise<any> {
  const res = await apiFetch(`/api/renderer/missions/${missionId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Failed to get mission detail: ${res.status}`);
  return await res.json();
}

export async function listContributions(apiFetch: ApiFetch, token: string): Promise<any[]> {
  const res = await apiFetch('/api/renderer/contributions', {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Failed to list contributions: ${res.status}`);
  const data = await res.json();
  return data.contributions || [];
}

export async function updateContributionStatus(
  apiFetch: ApiFetch,
  token: string,
  contributionId: string,
  status: string
): Promise<void> {
  const res = await apiFetch(`/api/renderer/contributions/${contributionId}/status`, {
    method: 'PUT',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error(`Failed to update contribution status: ${res.status}`);
}

export async function listPlaces(apiFetch: ApiFetch, token: string): Promise<any[]> {
  const res = await apiFetch('/api/renderer/places', {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Failed to list places: ${res.status}`);
  const data = await res.json();
  return data.places || [];
}

export async function listSpatialAnchors(apiFetch: ApiFetch, token: string): Promise<any[]> {
  const res = await apiFetch('/api/renderer/spatial/anchors', {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Failed to list spatial anchors: ${res.status}`);
  const data = await res.json();
  return data.anchors || [];
}

export async function listSpatialPlaces(apiFetch: ApiFetch, token: string): Promise<any[]> {
  const res = await apiFetch('/api/renderer/spatial/places', {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Failed to list spatial places: ${res.status}`);
  const data = await res.json();
  return data.places || [];
}

export async function listSpatialFileTags(apiFetch: ApiFetch, token: string): Promise<any[]> {
  const res = await apiFetch('/api/renderer/spatial/file-tags', {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Failed to list spatial file tags: ${res.status}`);
  const data = await res.json();
  return data.tags || [];
}

export async function triggerRender(apiFetch: ApiFetch, token: string, options: any = {}): Promise<any> {
  const res = await apiFetch('/api/renderer/render', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(options),
  });
  if (!res.ok) throw new Error(`Failed to trigger render: ${res.status}`);
  return await res.json();
}
