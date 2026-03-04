import { fireEvent, render, screen, waitFor } from "@testing-library/svelte";
import { describe, expect, it, vi, beforeEach } from "vitest";

const { apiFetch } = vi.hoisted(() => ({
  apiFetch: vi.fn(),
}));

vi.mock("$lib/services/apiBase", () => ({
  apiFetch,
}));

vi.mock("$lib/services/auth", () => ({
  buildAuthHeaders: () => ({ Authorization: "Bearer test-token" }),
  getAdminToken: () => "test-token",
}));

function jsonResponse(payload: unknown) {
  return {
    ok: true,
    json: async () => payload,
  };
}

describe("DevMode route", () => {
  beforeEach(() => {
    apiFetch.mockReset();
    apiFetch.mockImplementation((url: string) => {
      if (url === "/api/dev/status") {
        return Promise.resolve(
          jsonResponse({
            active: false,
            workspace_alias: "@dev",
            requirements: {
              workspace_alias: "@dev",
              dev_root: "/repo/dev",
              dev_root_present: true,
              dev_template_present: true,
              framework_ready: true,
              tracked_sync_paths: {
                ops: "/repo/dev/ops",
                docs: "/repo/dev/docs",
                roadmap: "/repo/dev/docs/roadmap/ROADMAP.md",
                tasks_json: "/repo/dev/ops/tasks.json",
                workspace: "/repo/dev/ops/templates/uDOS-dev.code-workspace",
                copilot: "/repo/dev/ops/templates/copilot-instructions.md",
                goblin: "/repo/dev/goblin",
                goblin_tests: "/repo/dev/goblin/tests",
              },
              script_count: 2,
              test_count: 3,
              framework_manifest_present: true,
            },
          })
        );
      }
      if (url === "/api/dev/ops") {
        return Promise.resolve(
          jsonResponse({
            workspace_alias: "@dev",
            active: false,
            ops: {
              root: "/repo/dev/ops",
              files: {
                tasks_json: { path: "/repo/dev/ops/tasks.json", present: true },
                workspace: {
                  path: "/repo/dev/ops/templates/uDOS-dev.code-workspace",
                  present: true,
                },
                copilot: {
                  path: "/repo/dev/ops/templates/copilot-instructions.md",
                  present: true,
                },
              },
            },
          })
        );
      }
      if (url === "/api/dev/logs?lines=100") {
        return Promise.resolve(jsonResponse({ logs: ["dev log line"] }));
      }
      if (url === "/api/dev/ops/files?area=ops") {
        return Promise.resolve(
          jsonResponse({
            entries: [
              { name: "AGENTS.md", path: "AGENTS.md", type: "file" },
              { name: "templates", type: "dir" },
            ],
          })
        );
      }
      if (url === "/api/dev/ops/files?area=docs") {
        return Promise.resolve(
          jsonResponse({
            entries: [
              { name: "README.md", path: "README.md", type: "file" },
              { name: "roadmap", type: "dir" },
            ],
          })
        );
      }
      if (url === "/api/dev/ops/files?area=goblin") {
        return Promise.resolve(
          jsonResponse({
            entries: [
              { name: "README.md", path: "README.md", type: "file" },
              { name: "tests", type: "dir" },
            ],
          })
        );
      }
      if (url === "/api/dev/ops/read?area=ops&path=AGENTS.md") {
        return Promise.resolve(
          jsonResponse({
            area: "ops",
            path: "AGENTS.md",
            content: "# ops agents",
          })
        );
      }
      if (url === "/api/dev/scripts") {
        return Promise.resolve(jsonResponse({ scripts: ["dev-work/scripts/check.sh"] }));
      }
      if (url === "/api/dev/tests") {
        return Promise.resolve(jsonResponse({ tests: ["goblin/test_dev_workspace_contract.py"] }));
      }
      if (url === "/api/dev/github/pat-status") {
        return Promise.resolve(jsonResponse({ configured: false }));
      }
      if (url === "/api/dev/webhook/github-secret-status") {
        return Promise.resolve(jsonResponse({ configured: false }));
      }
      return Promise.resolve(jsonResponse({}));
    });
  });

  it("renders @dev workspace and Goblin status text", async () => {
    const { default: DevMode } = await import("./DevMode.svelte");

    render(DevMode);

    await waitFor(() => {
      expect(screen.getByText("@dev Workspace Status")).toBeInTheDocument();
    });

    expect(screen.getByText("@dev Dev Mode")).toBeInTheDocument();
    expect(screen.getByText("Manage the contributor workspace, tracked payload, Goblin scaffold, and Wizard-gated tooling lane.")).toBeInTheDocument();
    expect(screen.getByText("@dev")).toBeInTheDocument();
    expect(screen.getByText("/repo/dev/ops")).toBeInTheDocument();
    expect(screen.getByText("/repo/dev/docs")).toBeInTheDocument();
    expect(screen.getByText("/repo/dev/docs/roadmap/ROADMAP.md")).toBeInTheDocument();
    expect(screen.getByText("/repo/dev/ops/tasks.json")).toBeInTheDocument();
    expect(screen.getByText("/repo/dev/ops/templates/uDOS-dev.code-workspace")).toBeInTheDocument();
    expect(screen.getByText("/repo/dev/ops/templates/copilot-instructions.md")).toBeInTheDocument();
    expect(screen.getByText("/repo/dev/goblin")).toBeInTheDocument();
    expect(screen.getByText("/repo/dev/goblin/tests")).toBeInTheDocument();
    expect(screen.getByText("Tracked Payload Browser")).toBeInTheDocument();
    expect(screen.getByText("file · AGENTS.md")).toBeInTheDocument();
    expect(screen.getByText("dir · roadmap")).toBeInTheDocument();
    expect(screen.getByText("dir · tests")).toBeInTheDocument();
    expect(screen.getByText("@dev present: yes · templates ok: yes · framework manifest: yes")).toBeInTheDocument();

    await fireEvent.click(screen.getByRole("button", { name: "file · AGENTS.md" }));

    await waitFor(() => {
      expect(screen.getByText("# ops agents")).toBeInTheDocument();
    });
    expect(screen.getByText("ops · AGENTS.md")).toBeInTheDocument();
  });
});
