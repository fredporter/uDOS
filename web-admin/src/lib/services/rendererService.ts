const API_BASE = import.meta.env.VITE_WIZARD_API_URL ?? "http://localhost:8765";

async function fetchJson<T>(fetcher: typeof window.fetch, path: string): Promise<T | null> {
  try {
    const response = await fetcher(`${API_BASE}${path}`);
    if (!response.ok) {
      console.warn(`Renderer API ${path} failed: ${response.status}`);
      return null;
    }
    return (await response.json()) as T;
  } catch (error) {
    console.error(`Renderer API ${path} error`, error);
    return null;
  }
}

export async function getThemes(fetcher: typeof window.fetch) {
  return fetchJson<{ themes: unknown[] }>(fetcher, "/api/renderer/themes");
}

export async function getSiteSummary(fetcher: typeof window.fetch) {
  return fetchJson<{ exports: { theme: string; files: number; lastModified: string | null }[] }>(fetcher, "/api/renderer/site");
}

export async function getSiteFiles(fetcher: typeof window.fetch, theme: string) {
  return fetchJson<{ theme: string; files: { path: string; size: number; updatedAt: string | null }[] }>(fetcher, `/api/renderer/site/${theme}/files`);
}

export async function getMissions(fetcher: typeof window.fetch) {
  return fetchJson<{ missions: any[] }>(fetcher, "/api/renderer/missions");
}

export async function getContributions(fetcher: typeof window.fetch, status?: string) {
  const query = status ? `?status=${encodeURIComponent(status)}` : "";
  return fetchJson<{ contributions: unknown[] }>(fetcher, `/api/renderer/contributions${query}`);
}

export async function updateContributionStatus(
  fetcher: typeof window.fetch,
  contributionId: string,
  status: string,
  reviewer?: string,
  note?: string,
) {
  const response = await fetcher(
    `${API_BASE}/api/renderer/contributions/${contributionId}/status`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-UDOS-Role": "maintainer",
      },
      body: JSON.stringify({ status, reviewer, note }),
    },
  );
  if (!response.ok) {
    console.warn(`Contribution status update failed: ${response.status}`);
    return null;
  }
  return (await response.json()) as { contribution: unknown };
}
