import { apiFetch } from "$lib/services/apiBase";

export type NotionBlockMap = {
  queue_id?: number;
  notion_block_id: string;
  block_type?: string;
  runtime_type?: string;
  action?: string;
  status?: string;
  payload_preview?: string;
  created_at?: string;
  processed_at?: string;
  local_file_path?: string;
  last_synced?: string;
};

export type NotionPendingItem = {
  queue_id?: number;
  notion_block_id?: string;
  block_type?: string;
  runtime_type?: string;
  action?: string;
  status?: string;
  payload?: string;
  created_at?: string;
};

const API_BASE = "/api/notion";

async function handleResponse(response: Response) {
  if (response.ok) {
    return response.json();
  }
  const errorText = await response.text();
  throw new Error(errorText || response.statusText);
}

export async function fetchNotionBlockMaps(options: {
  limit?: number;
  signal?: AbortSignal | null;
} = {}): Promise<NotionBlockMap[]> {
  const { limit = 12, signal = null } = options;
  const response = await apiFetch(`${API_BASE}/sync/maps?limit=${limit}`, {
    signal: signal || undefined,
  });
  const data = await handleResponse(response);
  if (Array.isArray(data)) {
    return data;
  }
  return data.blocks ?? [];
}

export async function fetchNotionPendingSyncs(options: {
  limit?: number;
  signal?: AbortSignal | null;
} = {}): Promise<NotionPendingItem[]> {
  const { limit = 12, signal = null } = options;
  const response = await apiFetch(`${API_BASE}/sync/pending?limit=${limit}`, {
    signal: signal || undefined,
  });
  const data = await handleResponse(response);
  if (Array.isArray(data)) {
    return data;
  }
  return [];
}

export async function triggerNotionManualSync(): Promise<{ result: string }> {
  const response = await apiFetch(`${API_BASE}/sync/manual`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  });
  return handleResponse(response);
}

export async function fetchNotionSyncStatus() {
  const response = await apiFetch(`${API_BASE}/sync/status`);
  return handleResponse(response);
}
