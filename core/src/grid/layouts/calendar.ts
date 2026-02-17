import { Canvas80x30 } from "../canvas.js";
import { packageGrid } from "../pack.js";
import { CalendarInput, GridCanvasSpec } from "../types.js";
import { compactSpatialRef, normalizeScheduleRows, normalizeTaskRows, spatialRef } from "./shared.js";

export function renderCalendarDay(spec: GridCanvasSpec, input: CalendarInput) {
  const c = new Canvas80x30();
  c.clear(" ");
  c.box(0, 0, 80, 30, "single", spec.title);

  c.box(1, 1, 52, 28, "single", "Schedule");
  c.box(53, 1, 26, 28, "single", "Tasks");

  const spatialRefs = new Set<string>();

  const scheduleRows = normalizeScheduleRows(input.events || []);
  const taskRows = normalizeTaskRows(input.tasks || []);

  let y = 2;
  for (const e of scheduleRows) {
    const ref = e._ref || null;
    if (ref) spatialRefs.add(ref);
    const refHint = ref ? ` @${compactSpatialRef(ref)}` : "";
    c.write(2, y++, `${e.time} ${e.item}${refHint}`.slice(0, 50));
  }

  y = 2;
  for (const t of taskRows) {
    const ref = spatialRef(t);
    if (ref) spatialRefs.add(ref);
    const refHint = ref ? ` @${compactSpatialRef(ref)}` : "";
    c.write(54, y++, `${t.status} ${t.text}${refHint}`.slice(0, 24));
  }

  if (spatialRefs.size > 0) {
    const refs = Array.from(spatialRefs);
    c.write(2, 28, `Spatial: ${refs.join(", ")}`.slice(0, 76));
  }

  const lines = c.toLines();
  return packageGrid({ ...spec, mode: "calendar" }, lines);
}
