/**
 * Container Actions Service
 *
 * Provides actions for launching, stopping, and opening containerized plugins
 */

import type { ApiFetch } from './apiBase';

export interface Container {
  id: string;
  name: string;
  port: number;
  browser_route: string;
  state: string;
  running: boolean;
  container_type?: string;
  git_cloned?: boolean;
}

/**
 * Launch a container (start the plugin service)
 */
export async function launchContainerAction(
  apiFetch: ApiFetch,
  authHeaders: () => Record<string, string>,
  containerId: string
): Promise<void> {
  const res = await apiFetch(`/api/containers/${containerId}/launch`, {
    method: 'POST',
    headers: authHeaders(),
  });

  if (!res.ok) {
    let detail = '';
    try {
      const data = await res.json();
      detail = data?.detail || data?.error || '';
    } catch {
      // ignore parsing errors
    }
    throw new Error(detail || `Failed to launch container (HTTP ${res.status})`);
  }
}

/**
 * Stop a running container
 */
export async function stopContainerAction(
  apiFetch: ApiFetch,
  authHeaders: () => Record<string, string>,
  containerId: string
): Promise<void> {
  const res = await apiFetch(`/api/containers/${containerId}/stop`, {
    method: 'POST',
    headers: authHeaders(),
  });

  if (!res.ok) {
    let detail = '';
    try {
      const data = await res.json();
      detail = data?.detail || data?.error || '';
    } catch {
      // ignore parsing errors
    }
    throw new Error(detail || `Failed to stop container (HTTP ${res.status})`);
  }
}

/**
 * Open a container's web interface in a new browser tab
 */
export function openContainerAction(container: Container): void {
  if (!container) {
    console.error('Cannot open container: container object is null or undefined');
    return;
  }

  const { port, browser_route, id, name } = container;

  if (!port) {
    console.error(`Cannot open container ${id}: port not defined`);
    alert(`⚠️ Cannot open ${name || id}: port not configured`);
    return;
  }

  // Construct a local loopback URL that matches current page protocol.
  const route = browser_route || '/';
  const protocol = window.location.protocol === "https:" ? "https:" : "http:";
  const host = window.location.hostname === "localhost" ? "127.0.0.1" : window.location.hostname;
  const url = `${protocol}//${host}:${port}${route}`;

  // Open in new tab
  const newWindow = window.open(url, '_blank');

  if (!newWindow) {
    // Popup blocked
    console.warn(`Failed to open ${url} - popup may be blocked`);
    alert(`⚠️ Could not open ${name || id}.\n\nPlease allow popups or manually navigate to:\n${url}`);
  }
}
