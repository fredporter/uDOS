function normalizeApiBase(candidate: string | null | undefined): string | null {
  if (!candidate) return null;
  const trimmed = candidate.trim().replace(/\/$/, "");
  if (!trimmed) return null;
  const lowered = trimmed.toLowerCase();
  if (lowered === "null" || lowered === "undefined") return null;

  if (/^https?:\/\//i.test(trimmed)) {
    try {
      // Validate URL format.
      new URL(trimmed);
      return trimmed;
    } catch {
      return null;
    }
  }

  if (typeof window !== "undefined") {
    if (/^\/\//.test(trimmed)) {
      const inferred = `${window.location.protocol}${trimmed}`;
      try {
        new URL(inferred);
        return inferred;
      } catch {
        return null;
      }
    }

    if (/^[a-z0-9.-]+:\d{2,5}$/i.test(trimmed)) {
      const inferred = `${window.location.protocol}//${trimmed}`;
      try {
        new URL(inferred);
        return inferred;
      } catch {
        return null;
      }
    }
  }

  return null;
}

export function resolveApiBase(): string | null {
  const envBase =
    typeof import.meta !== "undefined" && import.meta.env
      ? import.meta.env.VITE_WIZARD_API_BASE
      : undefined;
  const normalizedEnv = normalizeApiBase(envBase);
  if (normalizedEnv) return normalizedEnv;

  if (typeof window !== "undefined") {
    const stored = normalizeApiBase(
      window.localStorage?.getItem("wizardApiBase"),
    );
    if (stored) return stored;

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
  let base = resolveApiBase();
  if (!base) {
    return path;
  }
  const normalized = path.startsWith("/") ? path : `/${path}`;
  if (base.endsWith("/api") && normalized.startsWith("/api/")) {
    base = base.slice(0, -4);
  }
  return `${base}${normalized}`;
}

export type ApiFetchOptions = RequestInit & { timeoutMs?: number };

export async function apiFetch(
  path: string,
  options?: ApiFetchOptions,
): Promise<Response> {
  const timeoutMs =
    typeof options?.timeoutMs === "number" ? options.timeoutMs : 12000;

  if (options?.signal || timeoutMs <= 0) {
    return fetch(buildApiUrl(path), options);
  }

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const { timeoutMs: _ignored, ...rest } = options ?? {};
    return await fetch(buildApiUrl(path), { ...rest, signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
}
