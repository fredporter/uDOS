import { Canvas80x30 } from "../canvas.js";
import { packageGrid } from "../pack.js";
import { GridCanvasSpec, TableColumn } from "../types.js";

export function renderSchedule(spec: GridCanvasSpec, input: any) {
  const c = new Canvas80x30();
  c.clear(" ");

  // Main header
  c.box(0, 0, 80, 30, "single", spec.title);

  // Schedule table area
  const columns: TableColumn[] = [
    { key: "time", title: "Time", width: 10 },
    { key: "item", title: "Item", width: 40 },
    { key: "location", title: "Location/LocId", width: 26 },
  ];

  // Sort events by time
  const events = (input.events || []).sort((a: any, b: any) => {
    const timeA = a.time || "";
    const timeB = b.time || "";
    return timeA.localeCompare(timeB);
  });

  c.table(1, 2, 78, 26, columns, events, {
    header: true,
    rowSep: true,
  });

  // Footer: filter info
  if (input.filters) {
    const filterStr = Object.entries(input.filters)
      .map(([k, v]) => `${k}:${v}`)
      .join(" | ")
      .slice(0, 76);
    c.write(2, 29, `Filters: ${filterStr}`);
  }

  const lines = c.toLines();
  return packageGrid({ ...spec, mode: "schedule" }, lines);
}
