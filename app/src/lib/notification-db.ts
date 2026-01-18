/**
 * Notification Database Utility
 * ==============================
 *
 * Provides async interface to notification history service via Tauri IPC.
 * Integrates with notification store for auto-save on new toasts.
 */

import { writable, type Readable } from 'svelte/store';

export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error' | 'progress';
  title?: string;
  message: string;
  timestamp: string;
  duration_ms: number;
  sticky: boolean;
  action_count: number;
  dismissed_at?: string;
}

export interface HistoryState {
  notifications: Notification[];
  total: number;
  page: number;
  pageSize: number;
  loading: boolean;
  error?: string;
}

export interface ExportResult {
  format: 'json' | 'csv' | 'markdown';
  content: string;
  filename: string;
}

export interface SearchFilters {
  query?: string;
  type?: string;
  startDate?: string;
  endDate?: string;
  limit?: number;
}

/**
 * Create notification history store.
 */
export function createHistoryStore() {
  const initialState: HistoryState = {
    notifications: [],
    total: 0,
    page: 0,
    pageSize: 20,
    loading: false,
    error: undefined,
  };

  const { subscribe, set, update } = writable<HistoryState>(initialState);

  return {
    subscribe,

    async load(page: number = 0) {
      update((s) => ({ ...s, loading: true, page }));
      try {
        const offset = page * this.getPageSize();
        const response = await fetch('http://localhost:8765/api/v1/notification-history/list', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ limit: 20, offset }),
        });

        if (!response.ok) throw new Error('Failed to load history');

        const { data } = await response.json();
        update((s) => ({
          ...s,
          notifications: data.notifications,
          total: data.total,
          loading: false,
        }));
      } catch (e) {
        update((s) => ({
          ...s,
          error: String(e),
          loading: false,
        }));
      }
    },

    async search(filters: SearchFilters) {
      update((s) => ({ ...s, loading: true }));
      try {
        const response = await fetch('http://localhost:8765/api/v1/notification-history/search', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(filters),
        });

        if (!response.ok) throw new Error('Search failed');

        const { data } = await response.json();
        update((s) => ({
          ...s,
          notifications: data,
          loading: false,
        }));
      } catch (e) {
        update((s) => ({
          ...s,
          error: String(e),
          loading: false,
        }));
      }
    },

    async delete(id: string) {
      try {
        const response = await fetch(`http://localhost:8765/api/v1/notification-history/${id}`, {
          method: 'DELETE',
        });

        if (!response.ok) throw new Error('Delete failed');

        update((s) => ({
          ...s,
          notifications: s.notifications.filter((n) => n.id !== id),
        }));
      } catch (e) {
        update((s) => ({ ...s, error: String(e) }));
      }
    },

    async clearOld(days: number = 30) {
      try {
        const response = await fetch('http://localhost:8765/api/v1/notification-history/clear', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ days }),
        });

        if (!response.ok) throw new Error('Clear failed');

        const { data } = await response.json();
        await this.load(0); // Reload
      } catch (e) {
        update((s) => ({ ...s, error: String(e) }));
      }
    },

    async export(format: 'json' | 'csv' | 'markdown', filters?: SearchFilters): Promise<ExportResult | null> {
      try {
        const response = await fetch('http://localhost:8765/api/v1/notification-history/export', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ format, ...filters }),
        });

        if (!response.ok) throw new Error('Export failed');

        return await response.json();
      } catch (e) {
        update((s) => ({ ...s, error: String(e) }));
        return null;
      }
    },

    async getStats() {
      try {
        const response = await fetch('http://localhost:8765/api/v1/notification-history/stats', {
          method: 'GET',
        });

        if (!response.ok) throw new Error('Stats failed');

        return await response.json();
      } catch (e) {
        update((s) => ({ ...s, error: String(e) }));
        return null;
      }
    },

    getPageSize(): number {
      let size = 20;
      let state: HistoryState;
      subscribe((s) => {
        state = s;
      })();
      return state!.pageSize;
    },

    reset() {
      set(initialState);
    },
  };
}

/**
 * Auto-save integration function.
 *
 * Call this when a new toast is added to persist to history.
 */
export async function saveToHistory(
  type: 'info' | 'success' | 'warning' | 'error' | 'progress',
  title: string | undefined,
  message: string,
  durationMs: number = 5000,
  sticky: boolean = false
): Promise<string | null> {
  try {
    const response = await fetch('http://localhost:8765/api/v1/notification-history/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type,
        title,
        message,
        duration_ms: durationMs,
        sticky,
      }),
    });

    if (!response.ok) throw new Error('Save failed');

    const { data } = await response.json();
    return data.id;
  } catch (e) {
    console.error('[NotificationHistory] Save failed:', e);
    return null;
  }
}

/**
 * Download file from export result.
 */
export function downloadExport(result: ExportResult) {
  const blob = new Blob([result.content], {
    type: result.format === 'json' ? 'application/json' : 'text/plain',
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = result.filename;
  a.click();
  URL.revokeObjectURL(url);
}
