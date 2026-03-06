import { Canvas } from "../canvas.js";
import { packageGrid } from "../pack.js";
import { GridCanvasSpec, WorkflowInput } from "../types.js";
import {
  compactSpatialRef,
  normalizeScheduleRows,
  normalizeTaskRows,
  normalizeWorkflowRows,
  spatialRef,
  workflowStateGlyph,
} from "./shared.js";

function clamp(v: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, v));
}

export function renderWorkflow(spec: GridCanvasSpec, input: WorkflowInput) {
  const width = clamp(Math.floor(spec.width || 80), 48, 220);
  const height = clamp(Math.floor(spec.height || 30), 18, 120);

  const c = new Canvas(width, height);
  c.clear(" ");
  c.box(0, 0, width, height, "single", (spec.title || "Workflow").slice(0, Math.max(0, width - 4)));

  const tasks = normalizeTaskRows(input.tasks || []);
  const schedule = normalizeScheduleRows(input.scheduleItems || []);
  const workflow = normalizeWorkflowRows(input.workflowSteps || []);

  const cols = width >= 96 ? 3 : 2;
  const panelTop = 1;
  const panelHeight = height - 2;

  if (cols === 3) {
    const w = Math.floor((width - 2) / 3);
    const x1 = 1;
    const x2 = x1 + w;
    const x3 = x2 + w;
    c.box(x1, panelTop, w, panelHeight, "single", "Tasks");
    c.box(x2, panelTop, w, panelHeight, "single", "Schedule");
    c.box(x3, panelTop, width - x3 - 1, panelHeight, "single", "Workflow");

    let y = panelTop + 1;
    for (const task of tasks) {
      if (y >= panelTop + panelHeight - 1) break;
      const ref = spatialRef(task);
      const hint = ref ? ` @${compactSpatialRef(ref)}` : "";
      c.write(x1 + 1, y++, `${task.status} ${task.text}${hint}`.slice(0, Math.max(1, w - 2)));
    }

    y = panelTop + 1;
    for (const event of schedule) {
      if (y >= panelTop + panelHeight - 1) break;
      const hint = event._ref ? ` @${compactSpatialRef(event._ref)}` : "";
      c.write(x2 + 1, y++, `${event.time} ${event.item}${hint}`.slice(0, Math.max(1, w - 2)));
    }

    y = panelTop + 1;
    const w3 = width - x3 - 2;
    for (const step of workflow) {
      if (y >= panelTop + panelHeight - 1) break;
      const dep = step.dependsOn && step.dependsOn.length > 0 ? ` <-${step.dependsOn[0]}` : "";
      c.write(x3 + 1, y++, `${workflowStateGlyph(step.state)} ${step.title}${dep}`.slice(0, Math.max(1, w3)));
    }
  } else {
    const topH = Math.max(7, Math.floor((height - 2) / 2));
    const bottomH = height - 2 - topH;
    const leftW = Math.floor((width - 2) / 2);
    const rightW = width - 2 - leftW;

    c.box(1, 1, leftW, topH, "single", "Tasks");
    c.box(1 + leftW, 1, rightW, topH, "single", "Schedule");
    c.box(1, 1 + topH, width - 2, bottomH, "single", "Workflow");

    let y = 2;
    for (const task of tasks) {
      if (y >= topH) break;
      const ref = spatialRef(task);
      const hint = ref ? ` @${compactSpatialRef(ref)}` : "";
      c.write(2, y++, `${task.status} ${task.text}${hint}`.slice(0, Math.max(1, leftW - 2)));
    }

    y = 2;
    for (const event of schedule) {
      if (y >= topH) break;
      const hint = event._ref ? ` @${compactSpatialRef(event._ref)}` : "";
      c.write(2 + leftW, y++, `${event.time} ${event.item}${hint}`.slice(0, Math.max(1, rightW - 2)));
    }

    y = 2 + topH;
    for (const step of workflow) {
      if (y >= height - 1) break;
      const dep = step.dependsOn && step.dependsOn.length > 0 ? ` <-${step.dependsOn[0]}` : "";
      c.write(2, y++, `${workflowStateGlyph(step.state)} ${step.title}${dep}`.slice(0, Math.max(1, width - 4)));
    }
  }

  c.write(2, height - 2, `Counts T:${tasks.length} S:${schedule.length} W:${workflow.length}`.slice(0, Math.max(1, width - 4)));

  const lines = c.toLines();
  return packageGrid({ ...spec, mode: "workflow", width, height }, lines);
}
