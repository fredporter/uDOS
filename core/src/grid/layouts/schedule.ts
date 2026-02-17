import { Canvas80x30 } from "../canvas.js";
import { packageGrid } from "../pack.js";
import { GridCanvasSpec, ScheduleInput, TableColumn } from "../types.js";
import { normalizeScheduleRows } from "./shared.js";

export function renderSchedule(spec: GridCanvasSpec, input: ScheduleInput) {
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

  // Normalize and sort schedule rows by time/title/location
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

  c.table(1, 2, 78, 26, columns, events, {
    header: true,
    rowSep: true,
  });

  // Footer: filter/spatial-link info
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
    c.write(2, 29, footerParts.join(" | ").slice(0, 76));
  }

  const lines = c.toLines();
  return packageGrid({ ...spec, mode: "schedule" }, lines);
}
