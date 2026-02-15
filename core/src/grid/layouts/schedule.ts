import { Canvas80x30 } from "../canvas.js";
import { packageGrid } from "../pack.js";
import { GridCanvasSpec, TableColumn } from "../types.js";

function scheduleSpatialRef(event: any): string | null {
  const ref = event?.placeRef || event?.locId || event?.location;
  if (!ref || typeof ref !== "string") return null;
  return ref.trim() || null;
}

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
  const spatialRefs = new Set<string>();
  const events = (input.events || []).sort((a: any, b: any) => {
    const timeA = a.time || "";
    const timeB = b.time || "";
    return timeA.localeCompare(timeB);
  }).map((event: any) => {
    const ref = scheduleSpatialRef(event);
    if (ref) spatialRefs.add(ref);
    return {
      ...event,
      location: ref || event.location || "",
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
