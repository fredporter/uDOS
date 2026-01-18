/**
 * Sync Status Store
 * 
 * Reactive Svelte store for tracking Notion sync state
 * Used by SyncIndicator component and app header
 */

import { writable } from 'svelte/store';

export interface SyncStatus {
  isConnected: boolean;
  isHealthy: boolean;
  pendingCount: number;
  errorCount: number;
  conflictCount: number;
  lastSync?: string;
  mode: 'publish' | 'bidirectional';
  message?: string;
}

const initialState: SyncStatus = {
  isConnected: false,
  isHealthy: false,
  pendingCount: 0,
  errorCount: 0,
  conflictCount: 0,
  mode: 'publish',
  message: 'Initializing...',
};

export const syncStatus = writable<SyncStatus>(initialState);

/**
 * Fetch sync status from Dev Server
 */
export async function refreshSyncStatus(): Promise<void> {
  try {
    const devServerUrl = import.meta.env.VITE_DEV_SERVER_URL || 'http://localhost:8766';
    const response = await fetch(`${devServerUrl}/api/v0/notion/sync/status`, {
      headers: { 'Content-Type': 'application/json' },
      mode: 'cors',
    });

    if (!response.ok) {
      syncStatus.set({
        ...initialState,
        isConnected: false,
        message: `Server error: ${response.status}`,
      });
      return;
    }

    const data = await response.json();
    syncStatus.set({
      isConnected: true,
      isHealthy: data.status === 'healthy',
      pendingCount: data.pendingCount || 0,
      errorCount: data.errorCount || 0,
      conflictCount: data.conflictCount || 0,
      lastSync: data.lastSync,
      mode: data.mode || 'publish',
      message: `${data.pendingCount} pending`,
    });
  } catch (error) {
    console.error('[SYNC] Error fetching status:', error);
    syncStatus.set({
      ...initialState,
      isConnected: false,
      message: `Connection error: ${error instanceof Error ? error.message : 'Unknown'}`,
    });
  }
}

/**
 * Initialize sync monitor
 * Polls Dev Server health every 5 seconds
 */
export function initSyncMonitor(intervalMs: number = 5000): () => void {
  // Initial status check
  refreshSyncStatus();

  // Poll for updates
  const interval = setInterval(refreshSyncStatus, intervalMs);

  // Return cleanup function
  return () => clearInterval(interval);
}

/**
 * Report local change to sync system
 */
export async function notifyLocalChange(
  operation: 'insert' | 'update' | 'delete',
  localType: 'document' | 'task' | 'resource',
  localId: string,
  payload?: Record<string, unknown>
): Promise<string | null> {
  try {
    const devServerUrl = import.meta.env.VITE_DEV_SERVER_URL || 'http://localhost:8766';
    const response = await fetch(`${devServerUrl}/api/v0/notion/sync/queue`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      mode: 'cors',
      body: JSON.stringify({
        operation,
        localType,
        localId,
        payload,
      }),
    });

    if (!response.ok) {
      console.error(`[SYNC] Failed to queue operation: ${response.status}`);
      return null;
    }

    const data = await response.json();
    refreshSyncStatus(); // Update status after change
    return data.queue_id || null;
  } catch (error) {
    console.error('[SYNC] Error notifying local change:', error);
    return null;
  }
}
