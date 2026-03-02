/**
 * Anchor Service
 *
 * Provides API access to spatial anchor management
 */

import { apiFetch } from './apiBase';

export async function listAnchors(token: string): Promise<any[]> {
  const res = await apiFetch('/api/anchors', {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Failed to list anchors: ${res.status}`);
  const data = await res.json();
  return data.anchors || [];
}

export async function getAnchor(token: string, anchorId: string): Promise<any> {
  const res = await apiFetch(`/api/anchors/${anchorId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Failed to get anchor: ${res.status}`);
  return await res.json();
}

export async function registerAnchor(token: string, anchorData: any): Promise<any> {
  const res = await apiFetch('/api/anchors', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(anchorData),
  });
  if (!res.ok) throw new Error(`Failed to register anchor: ${res.status}`);
  return await res.json();
}

export async function bindAnchor(token: string, anchorId: string, target: any): Promise<void> {
  const res = await apiFetch(`/api/anchors/${anchorId}/bind`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(target),
  });
  if (!res.ok) throw new Error(`Failed to bind anchor: ${res.status}`);
}

export async function listAnchorInstances(token: string, anchorId: string): Promise<any[]> {
  const res = await apiFetch(`/api/anchors/${anchorId}/instances`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Failed to list anchor instances: ${res.status}`);
  const data = await res.json();
  return data.instances || [];
}

export async function createAnchorInstance(token: string, anchorId: string, instanceData: any): Promise<any> {
  const res = await apiFetch(`/api/anchors/${anchorId}/instances`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(instanceData),
  });
  if (!res.ok) throw new Error(`Failed to create anchor instance: ${res.status}`);
  return await res.json();
}

export async function destroyAnchorInstance(token: string, anchorId: string, instanceId: string): Promise<void> {
  const res = await apiFetch(`/api/anchors/${anchorId}/instances/${instanceId}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Failed to destroy anchor instance: ${res.status}`);
}

export async function listAnchorEvents(token: string, anchorId: string): Promise<any[]> {
  const res = await apiFetch(`/api/anchors/${anchorId}/events`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Failed to list anchor events: ${res.status}`);
  const data = await res.json();
  return data.events || [];
}
