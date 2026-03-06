import { Canvas } from "../canvas.js";
import { packageGrid } from "../pack.js";
import { DashboardInput, GridCanvasSpec } from "../types.js";
import { normalizeScheduleRows, normalizeTaskRows, normalizeWorkflowRows, workflowStateGlyph } from "./shared.js";

function clamp(v: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, v));
}

export function renderDashboard(spec: GridCanvasSpec, input: DashboardInput) {
  const width = clamp(Math.floor(spec.width || 80), 48, 220);
  const height = clamp(Math.floor(spec.height || 30), 20, 120);

  const c = new Canvas(width, height);
  c.clear(" ");

  c.write(2, 0, `${spec.title || "Boss Dashboard"}`.slice(0, Math.max(1, width - 20)));
  const now = new Date().toLocaleTimeString();
  c.write(Math.max(2, width - now.length - 2), 0, now);

  const topY = 2;
  const topH = Math.max(8, Math.floor((height - 3) * 0.45));
  const bottomY = topY + topH;
  const bottomH = height - bottomY;

  const splitX = Math.floor(width / 2);
  const leftW = splitX;
  const rightW = width - splitX;

  c.box(0, topY, leftW, topH, "single", "Mission Queue");
  c.box(splitX, topY, rightW, topH, "single", "Stats");

  let y = topY + 1;
  for (const mission of input.missions || []) {
    if (y >= topY + topH - 1) break;
    c.write(2, y++, `[${mission.status}] ${mission.title}`.slice(0, Math.max(1, leftW - 4)));
  }

  y = topY + 1;
  if (input.stats) {
    for (const [key, value] of Object.entries(input.stats)) {
      if (y >= topY + topH - 1) break;
      const line = `${key}: ${value}`;
      c.write(splitX + 2, y++, line.slice(0, Math.max(1, rightW - 4)));
    }
  }

  const taskRows = normalizeTaskRows(input.tasks || []);
  const schedRows = normalizeScheduleRows(input.scheduleItems || []);
  const wfRows = normalizeWorkflowRows(input.workflowSteps || []);
  if (taskRows.length || schedRows.length || wfRows.length) {
    if (y < topY + topH - 1) c.write(splitX + 2, y++, "Panels:");
    if (y < topY + topH - 1) c.write(splitX + 2, y++, `Tasks: ${taskRows.length}`);
    if (y < topY + topH - 1) c.write(splitX + 2, y++, `Schedule: ${schedRows.length}`);
    if (y < topY + topH - 1) c.write(splitX + 2, y++, `Workflow: ${wfRows.length}`);
    const inProgress = wfRows.filter((step) => step.state === "in_progress");
    if (y < topY + topH - 1 && inProgress.length > 0) {
      const head = inProgress[0];
      c.write(splitX + 2, y++, `Now ${workflowStateGlyph(head.state)} ${head.title}`.slice(0, Math.max(1, rightW - 4)));
    }
  }

  c.box(0, bottomY, width, bottomH, "single", "Recent Activity");
  y = bottomY + 1;
  for (const log of input.logs || []) {
    if (y >= bottomY + bottomH - 1) break;
    const msg = `[${log.time || ""}] ${log.level || "INFO"}: ${log.message || ""}`;
    c.write(2, y++, msg.slice(0, Math.max(1, width - 4)));
  }

  const lines = c.toLines();
  return packageGrid({ ...spec, mode: "dashboard", width, height }, lines);
}
