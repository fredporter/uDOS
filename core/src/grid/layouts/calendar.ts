import { Canvas80x30 } from "../canvas.js";
import { packageGrid } from "../pack.js";
import { GridCanvasSpec } from "../types.js";

export function renderCalendarDay(spec: GridCanvasSpec, input: any) {
  const c = new Canvas80x30();
  c.clear(" ");
  c.box(0, 0, 80, 30, "single", spec.title);

  c.box(1, 1, 52, 28, "single", "Schedule");
  c.box(53, 1, 26, 28, "single", "Tasks");

  let y = 2;
  for (const e of input.events || []) {
    c.write(2, y++, `${e.time} ${e.title}`.slice(0, 50));
  }

  y = 2;
  for (const t of input.tasks || []) {
    c.write(54, y++, `${t.status} ${t.text}`.slice(0, 24));
  }

  const lines = c.toLines();
  return packageGrid({ ...spec, mode: "calendar" }, lines);
}
