/**
 * API Client Library
 * 
 * Unified fetch wrapper for Dev Server endpoints
 * Handles error responses, CORS, and request logging
 */

const BASE_URL = import.meta.env.VITE_DEV_SERVER_URL || 'http://localhost:8766';

export interface ApiResponse<T = unknown> {
  status: string;
  data?: T;
  error?: string;
  message?: string;
}

export interface SyncStatusResponse {
  status: string;
  mode: 'publish' | 'bidirectional';
  queue: Record<string, number>;
  pendingCount: number;
  errorCount: number;
  successCount: number;
  processingCount: number;
  conflictCount: number;
  lastSync?: string;
  isConnected: boolean;
}

/**
 * Make fetch request with error handling
 */
async function apiCall<T = unknown>(
  endpoint: string,
  options?: RequestInit
): Promise<ApiResponse<T>> {
  try {
    const url = `${BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      mode: 'cors',
      ...options,
    });

    if (!response.ok) {
      return {
        status: 'error',
        error: `HTTP ${response.status}`,
        message: response.statusText,
      };
    }

    const data = await response.json();
    return {
      status: 'success',
      data: data as T,
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    console.error(`[API] ${endpoint} failed:`, message);
    return {
      status: 'error',
      error: 'NETWORK_ERROR',
      message,
    };
  }
}

/**
 * Health check endpoint
 */
export async function healthCheck(): Promise<boolean> {
  const result = await apiCall('/health');
  return result.status === 'success';
}

/**
 * Get Notion sync status
 */
export async function getNotionSyncStatus(): Promise<SyncStatusResponse | null> {
  const result = await apiCall<SyncStatusResponse>('/api/v0/notion/sync/status');
  return result.data || null;
}

/**
 * Get Notion sync queue
 */
export async function getNotionSyncQueue(limit: number = 10) {
  return apiCall(`/api/v0/notion/sync/queue?limit=${limit}`);
}

/**
 * Get Notion maps (local ↔ Notion ID mappings)
 */
export async function getNotionMaps() {
  return apiCall('/api/v0/notion/maps');
}

/**
 * Get TS runtime parse results
 */
export async function parseMarkdown(markdown: string) {
  return apiCall('/api/v0/runtime/parse', {
    method: 'POST',
    body: JSON.stringify({ markdown }),
  });
}

/**
 * Execute TS runtime block
 */
export async function executeBlock(blockId: string, blockType: string, code: string) {
  return apiCall('/api/v0/runtime/execute', {
    method: 'POST',
    body: JSON.stringify({
      blockId,
      blockType,
      code,
    }),
  });
}

/**
 * Get runtime state variables
 */
export async function getRuntimeState(sessionId: string) {
  return apiCall(`/api/v0/runtime/state/${sessionId}`);
}

/**
 * Set runtime state variable
 */
export async function setRuntimeState(sessionId: string, variables: Record<string, unknown>) {
  return apiCall(`/api/v0/runtime/state/${sessionId}`, {
    method: 'POST',
    body: JSON.stringify({ variables }),
  });
}

/**
 * Get task queue
 */
export async function getTaskQueue() {
  return apiCall('/api/v0/tasks/queue');
}

/**
 * Schedule a task
 */
export async function scheduleTask(
  title: string,
  description?: string,
  dueDate?: string,
  priority?: string
) {
  return apiCall('/api/v0/tasks/schedule', {
    method: 'POST',
    body: JSON.stringify({
      title,
      description,
      dueDate,
      priority,
    }),
  });
}

/**
 * Compile binder
 */
export async function compileBinder(projectId: string, format: string = 'markdown') {
  return apiCall('/api/v0/binder/compile', {
    method: 'POST',
    body: JSON.stringify({
      projectId,
      format,
    }),
  });
}
