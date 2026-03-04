import { describe, expect, it, vi, beforeEach } from "vitest";

const apiFetch = vi.fn();
const buildAuthHeaders = vi.fn();

vi.mock("./apiBase", () => ({
  apiFetch,
}));

vi.mock("./auth", () => ({
  buildAuthHeaders,
}));

describe("ucodeService endpoint wiring", () => {
  beforeEach(() => {
    apiFetch.mockReset();
    buildAuthHeaders.mockReset();
    buildAuthHeaders.mockImplementation((token?: string) =>
      token ? { Authorization: `Bearer ${token}` } : {}
    );
    apiFetch.mockResolvedValue({
      ok: true,
      json: async () => ({}),
      text: async () => "",
    });
  });

  it("activates @dev via /api/dev/activate", async () => {
    const { toggleDevMode } = await import("./ucodeService.js");

    await toggleDevMode("test-token", true);

    expect(apiFetch).toHaveBeenCalledWith("/api/dev/activate", {
      method: "POST",
      headers: { Authorization: "Bearer test-token" },
    });
  });

  it("deactivates @dev via /api/dev/deactivate", async () => {
    const { toggleDevMode } = await import("./ucodeService.js");

    await toggleDevMode("", false);

    expect(apiFetch).toHaveBeenCalledWith("/api/dev/deactivate", {
      method: "POST",
      headers: {},
    });
  });
});
