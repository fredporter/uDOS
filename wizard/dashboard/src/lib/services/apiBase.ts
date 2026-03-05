/**
 * API Base - Centralized HTTP client for the Wizard dashboard
 */

export interface ApiRequestOptions extends RequestInit {
  timeout?: number;
}

/**
 * Type for apiFetch function
 */
export type ApiFetch = typeof apiFetch;

/**
 * fetch wrapper with auth header injection
 */
export async function apiFetch(
  url: string,
  options: ApiRequestOptions = {}
): Promise<Response> {
  const { timeout = 30000, ...fetchOptions } = options;

  // Auto-inject authorization header if token exists
  const token = typeof localStorage !== "undefined" ? localStorage.getItem("wizardAdminToken") : null;
  if (token) {
    fetchOptions.headers = {
      ...(fetchOptions.headers || {}),
      Authorization: `Bearer ${token}`,
    };
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      signal: controller.signal,
    });
    return response;
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * Helper for JSON POST requests
 */
export async function apiPost<T>(url: string, body: unknown, options?: ApiRequestOptions): Promise<T> {
  const response = await apiFetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

/**
 * Helper for JSON GET requests
 */
export async function apiGet<T>(url: string, options?: ApiRequestOptions): Promise<T> {
  const response = await apiFetch(url, {
    method: "GET",
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

/**
 * Helper for DELETE requests
 */
export async function apiDelete<T>(url: string, options?: ApiRequestOptions): Promise<T> {
  const response = await apiFetch(url, {
    method: "DELETE",
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

/**
 * Helper for PATCH requests
 */
export async function apiPatch<T>(url: string, body: unknown, options?: ApiRequestOptions): Promise<T> {
  const response = await apiFetch(url, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

/**
 * Resolve API base URL (for dynamic hosts)
 */
export function resolveApiBase(): string {
  const env = (import.meta as { env?: Record<string, string | undefined> }).env ?? {};
  const configuredBase = (env.VITE_WIZARD_BASE_URL || "").trim();
  if (configuredBase) {
    return configuredBase.replace(/\/+$/, "");
  }
  const configuredPort = (env.VITE_WIZARD_PORT || "8765").trim() || "8765";

  if (typeof window === "undefined") return `http://127.0.0.1:${configuredPort}`;

  // If we're on localhost, use localhost API
  if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
    return `${window.location.protocol}//127.0.0.1:${configuredPort}`;
  }

  // Otherwise use same origin
  return window.location.origin;
}
