import { Canvas80x30 } from "../canvas.js";
import { packageGrid } from "../pack.js";
import { GridCanvasSpec } from "../types.js";

function eventSpatialRef(event: any): string | null {
  const ref = event?.placeRef || event?.locId || event?.location;
  if (!ref || typeof ref !== "string") return null;
  return ref.trim() || null;
}

function taskSpatialRef(task: any): string | null {
  const ref = task?.placeRef || task?.locId || task?.location;
  if (!ref || typeof ref !== "string") return null;
  return ref.trim() || null;
}

function compactSpatialRef(ref: string): string {
  const parts = ref.split(":");
  if (parts.length >= 3) return parts.slice(-2).join(":");
  return ref;
}

export function renderCalendarDay(spec: GridCanvasSpec, input: any) {
  const c = new Canvas80x30();
  c.clear(" ");
  c.box(0, 0, 80, 30, "single", spec.title);

  c.box(1, 1, 52, 28, "single", "Schedule");
  c.box(53, 1, 26, 28, "single", "Tasks");

  const spatialRefs = new Set<string>();

  let y = 2;
  for (const e of input.events || []) {
    const ref = eventSpatialRef(e);
    if (ref) spatialRefs.add(ref);
    const refHint = ref ? ` @${compactSpatialRef(ref)}` : "";
    c.write(2, y++, `${e.time} ${e.title}${refHint}`.slice(0, 50));
  }

  y = 2;
  for (const t of input.tasks || []) {
    const ref = taskSpatialRef(t);
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
