import { Canvas } from "../canvas.js";
import { packageGrid } from "../pack.js";
import { GridCanvasSpec, ScheduleInput, TableColumn } from "../types.js";
import { normalizeScheduleRows } from "./shared.js";

function clamp(v: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, v));
}

export function renderSchedule(spec: GridCanvasSpec, input: ScheduleInput) {
  const width = clamp(Math.floor(spec.width || 80), 40, 220);
  const height = clamp(Math.floor(spec.height || 30), 16, 120);

  const c = new Canvas(width, height);
  c.clear(" ");

  c.box(0, 0, width, height, "single", (spec.title || "Schedule").slice(0, Math.max(0, width - 4)));

  const columns: TableColumn[] = [
    { key: "time", title: "Time", width: Math.max(8, Math.floor((width - 6) * 0.16)) },
    { key: "item", title: "Item", width: Math.max(12, Math.floor((width - 6) * 0.50)) },
    { key: "location", title: "Location/LocId", width: Math.max(10, Math.floor((width - 6) * 0.30)) },
  ];

  const spatialRefs = new Set<string>();
  const sourceRows = input.scheduleItems && input.scheduleItems.length > 0
    ? input.scheduleItems
    : input.events || [];
  const events = normalizeScheduleRows(sourceRows).map((event) => {
    if (event._ref) spatialRefs.add(event._ref);
    return {
      time: event.time,
      item: event.item,
      location: event.location,
    };
  });

  const tableY = 2;
  const tableH = Math.max(6, height - 4);
  c.table(1, tableY, width - 2, tableH, columns, events, {
    header: true,
    rowSep: true,
  });

  const footerParts: string[] = [];
  if (input.filters) {
    const filterStr = Object.entries(input.filters)
      .map(([k, v]) => `${k}:${v}`)
      .join(" ");
    footerParts.push(`Filters ${filterStr}`);
  }
  if (spatialRefs.size > 0) {
    footerParts.push(`Spatial ${Array.from(spatialRefs).join(", ")}`);
  }
  if (footerParts.length > 0) {
    c.write(2, height - 1, footerParts.join(" | ").slice(0, Math.max(1, width - 4)));
  }

  const lines = c.toLines();
  return packageGrid({ ...spec, mode: "schedule", width, height }, lines);
}
