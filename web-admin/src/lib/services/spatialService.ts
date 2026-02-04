import { buildAuthHeaders } from "$lib/services/auth";

const API_BASE = import.meta.env.VITE_WIZARD_API_URL ?? "http://localhost:8765";

async function fetchJson<T>(fetcher: typeof window.fetch, path: string): Promise<T | null> {
  try {
    const response = await fetcher(`${API_BASE}${path}`, {
      headers: buildAuthHeaders(),
    });
    if (!response.ok) {
      console.warn(`Spatial API ${path} failed:`, response.status);
      return null;
    }
    return (await response.json()) as T;
  } catch (error) {
    console.error(`Spatial API ${path} error`, error);
    return null;
  }
}

export async function getAnchors(fetcher: typeof window.fetch) {
  return fetchJson<{ anchors: unknown[] }>(fetcher, "/api/renderer/spatial/anchors");
}

export async function getPlaces(fetcher: typeof window.fetch) {
  return fetchJson<{ places: unknown[] }>(fetcher, "/api/renderer/spatial/places");
}

export async function getFileTags(fetcher: typeof window.fetch) {
  return fetchJson<{ file_tags: unknown[] }>(fetcher, "/api/renderer/spatial/file-tags");
}
