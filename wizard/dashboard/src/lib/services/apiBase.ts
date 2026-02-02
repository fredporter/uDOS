export function resolveApiBase(): string | null {
  const envBase =
    typeof import.meta !== "undefined" && import.meta.env
      ? import.meta.env.VITE_WIZARD_API_BASE
      : undefined;
  if (envBase && envBase.trim()) {
    return envBase.trim().replace(/\/$/, "");
  }

  if (typeof window !== "undefined") {
    const stored = window.localStorage?.getItem("wizardApiBase");
    if (stored && stored.trim()) {
      return stored.trim().replace(/\/$/, "");
    }
    if (window.location?.origin && window.location.origin !== "null") {
      return window.location.origin.replace(/\/$/, "");
    }
  }

  return null;
}

export function buildApiUrl(path: string): string {
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  const base = resolveApiBase();
  if (!base) {
    return path;
  }
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${base}${normalized}`;
}

export async function apiFetch(
  path: string,
  options?: RequestInit,
): Promise<Response> {
  return fetch(buildApiUrl(path), options);
}
