import { Canvas } from "../canvas.js";
import { packageGrid } from "../pack.js";
import { CalendarInput, GridCanvasSpec } from "../types.js";
import { compactSpatialRef, normalizeScheduleRows, normalizeTaskRows, spatialRef } from "./shared.js";

function clamp(v: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, v));
}

export function renderCalendarDay(spec: GridCanvasSpec, input: CalendarInput) {
  const width = clamp(Math.floor(spec.width || 80), 40, 180);
  const height = clamp(Math.floor(spec.height || 30), 18, 90);

  const c = new Canvas(width, height);
  c.clear(" ");
  c.box(0, 0, width, height, "single", (spec.title || "Calendar").slice(0, Math.max(0, width - 4)));

  const scheduleRows = normalizeScheduleRows(input.events || []);
  const taskRows = normalizeTaskRows(input.tasks || []);
  const spatialRefs = new Set<string>();

  const sideBySide = width >= 72;
  const scheduleX = 1;
  const scheduleY = 1;
  const scheduleW = sideBySide ? Math.floor((width - 2) * 0.67) : width - 2;
  const scheduleH = sideBySide ? height - 3 : Math.max(8, Math.floor((height - 3) * 0.62));

  const tasksX = sideBySide ? scheduleX + scheduleW : 1;
  const tasksY = sideBySide ? 1 : scheduleY + scheduleH;
  const tasksW = sideBySide ? width - tasksX - 1 : width - 2;
  const tasksH = sideBySide ? height - 3 : height - tasksY - 1;

  c.box(scheduleX, scheduleY, scheduleW, scheduleH, "single", "Schedule");
  c.box(tasksX, tasksY, tasksW, tasksH, "single", "Tasks");

  let y = scheduleY + 1;
  const scheduleMaxY = scheduleY + scheduleH - 1;
  const scheduleTextW = Math.max(1, scheduleW - 2);
  for (const e of scheduleRows) {
    if (y >= scheduleMaxY) break;
    const ref = e._ref || null;
    if (ref) spatialRefs.add(ref);
    const refHint = ref ? ` @${compactSpatialRef(ref)}` : "";
    c.write(scheduleX + 1, y++, `${e.time} ${e.item}${refHint}`.slice(0, scheduleTextW));
  }

  y = tasksY + 1;
  const taskMaxY = tasksY + tasksH - 1;
  const taskTextW = Math.max(1, tasksW - 2);
  for (const t of taskRows) {
    if (y >= taskMaxY) break;
    const ref = spatialRef(t);
    if (ref) spatialRefs.add(ref);
    const refHint = ref ? ` @${compactSpatialRef(ref)}` : "";
    c.write(tasksX + 1, y++, `${t.status} ${t.text}${refHint}`.slice(0, taskTextW));
  }

  if (spatialRefs.size > 0 && height >= 4) {
    const refs = Array.from(spatialRefs);
    c.write(2, height - 2, `Spatial: ${refs.join(", ")}`.slice(0, Math.max(1, width - 4)));
  }

  const lines = c.toLines();
  return packageGrid({ ...spec, mode: "calendar", width, height }, lines);
}
