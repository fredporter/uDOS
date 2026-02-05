import { Canvas80x30 } from "../canvas.js";
import { packageGrid } from "../pack.js";
import { GridCanvasSpec } from "../types.js";

export function renderDashboard(spec: GridCanvasSpec, input: any) {
  const c = new Canvas80x30();
  c.clear(" ");

  // Top banner with title and clock
  c.box(0, 0, 80, 2, "none");
  c.write(2, 0, `${spec.title || "Boss Dashboard"}`);

  const now = new Date().toLocaleTimeString();
  c.write(70, 0, now);

  // Left pane: Mission Queue
  c.box(0, 2, 40, 14, "single", "Mission Queue");
  let y = 3;
  for (const mission of input.missions || []) {
    if (y < 15) {
      c.write(2, y++, `[${mission.status}] ${mission.title}`.slice(0, 36));
    }
  }

  // Right pane: Stats
  c.box(40, 2, 40, 14, "single", "Stats");
  y = 3;

  if (input.stats) {
    for (const [key, value] of Object.entries(input.stats)) {
      if (y < 15) {
        const line = `${key}: ${value}`;
        c.write(42, y++, line.slice(0, 36));
      }
    }
  }

  // Alternative API quota display if provided
  if (input.apiQuota) {
    if (y < 10) {
      c.write(42, y++, `API: ${input.apiQuota.used}/${input.apiQuota.limit}`);
    }
  }

  // Node state if provided
  if (input.nodeState) {
    if (y < 15) {
      c.write(42, y++, `Node: ${input.nodeState.status}`);
    }
  }

  // Bottom pane: Recent logs
  c.box(0, 16, 80, 14, "single", "Recent Activity");
  y = 17;
  for (const log of input.logs || []) {
    if (y < 29) {
      const msg = `[${log.time || ""}] ${log.level || "INFO"}: ${log.message || ""}`;
      c.write(2, y++, msg.slice(0, 76));
    }
  }

  const lines = c.toLines();
  return packageGrid({ ...spec, mode: "dashboard" }, lines);
}
