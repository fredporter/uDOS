import { Canvas80x30 } from "../canvas.js";
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

export function renderWorkflow(spec: GridCanvasSpec, input: WorkflowInput) {
  const c = new Canvas80x30();
  c.clear(" ");
  c.box(0, 0, 80, 30, "single", spec.title);

  c.box(1, 1, 26, 28, "single", "Tasks");
  c.box(27, 1, 26, 28, "single", "Schedule");
  c.box(53, 1, 26, 28, "single", "Workflow");

  const tasks = normalizeTaskRows(input.tasks || []);
  const schedule = normalizeScheduleRows(input.scheduleItems || []);
  const workflow = normalizeWorkflowRows(input.workflowSteps || []);

  let y = 2;
  for (const task of tasks) {
    if (y >= 28) break;
    const ref = spatialRef(task);
    const hint = ref ? ` @${compactSpatialRef(ref)}` : "";
    c.write(2, y++, `${task.status} ${task.text}${hint}`.slice(0, 24));
  }

  y = 2;
  for (const event of schedule) {
    if (y >= 28) break;
    const hint = event._ref ? ` @${compactSpatialRef(event._ref)}` : "";
    c.write(28, y++, `${event.time} ${event.item}${hint}`.slice(0, 24));
  }

  y = 2;
  for (const step of workflow) {
    if (y >= 28) break;
    const dep = step.dependsOn && step.dependsOn.length > 0 ? ` <-${step.dependsOn[0]}` : "";
    c.write(54, y++, `${workflowStateGlyph(step.state)} ${step.title}${dep}`.slice(0, 24));
  }

  // Footer counters for parity assertions.
  c.write(2, 28, `Counts T:${tasks.length} S:${schedule.length} W:${workflow.length}`.slice(0, 76));

  const lines = c.toLines();
  return packageGrid({ ...spec, mode: "workflow" }, lines);
}
