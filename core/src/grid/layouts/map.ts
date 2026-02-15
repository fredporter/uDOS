import { Canvas80x30 } from "../canvas.js";
import { packageGrid } from "../pack.js";
import {
  GridCanvasSpec,
  MapViewportOptions,
  MinimapCell,
  LocIdOverlay,
} from "../types.js";

function parseLocIdZ(locId: string | undefined): number {
  if (!locId || typeof locId !== "string") return 0;
  const match = /-Z(-?\d{1,2})$/.exec(locId);
  if (!match) return 0;
  const z = Number(match[1]);
  if (!Number.isFinite(z)) return 0;
  return z;
}

export function renderMap(spec: GridCanvasSpec, input: any) {
  const c = new Canvas80x30();
  c.clear(" ");

  // Main header with focus location
  const focusLocId = input.focusLocId || "EARTH:SUR:L305-DA11";
  c.box(0, 0, 80, 30, "single", `${spec.title} — Focus: ${focusLocId}`);

  // Parse LocId format: WORLD:REALM:L###-CC##[-Zz]
  const parsed = focusLocId.match(/^([^:]+):([^:]+):(.+)$/);
  const world = parsed?.[1] || "EARTH";
  const realm = parsed?.[2] || "SUR";
  const locGrid = parsed?.[3] || "L305-DA11";
  const focusZ = parseLocIdZ(focusLocId);

  const viewport: MapViewportOptions = input.viewport || {};
  const zRange =
    typeof viewport.zRange === "number" && viewport.zRange >= 0
      ? Math.floor(viewport.zRange)
      : 1;

  // Display location info
  c.write(
    2,
    1,
    `World: ${world} | Realm: ${realm} | Grid: ${locGrid} | Focus Z: ${focusZ}`,
  );

  // Build minimap cells from overlays using z-aware viewport filtering.
  const cells = new Map<string, MinimapCell>();
  const overlays = input.overlays || [];
  const visibleOverlays: LocIdOverlay[] = [];
  let onPlaneCount = 0;
  let nearbyCount = 0;
  let hiddenCount = 0;

  overlays.forEach((overlay: LocIdOverlay, idx: number) => {
    const locId = overlay.locId || `CELL-${idx}`;
    const overlayZ =
      typeof overlay.z === "number" ? overlay.z : parseLocIdZ(overlay.locId);
    const dz = Math.abs(overlayZ - focusZ);
    const onPlane = dz === 0;
    const nearby = dz <= zRange;
    if (onPlane) onPlaneCount += 1;
    if (!onPlane && nearby) nearbyCount += 1;
    if (!nearby) {
      hiddenCount += 1;
      return;
    }

    visibleOverlays.push(overlay);
    cells.set(locId, {
      type: overlay.locId === focusLocId ? "selected" : "tagged",
      overlay,
    });
  });

  // Draw minimap
  c.minimap(1, 3, 50, 24, cells, {
    showLabels: true,
    focusCell: { x: 0, y: 0 },
  });

  // Legend pane on right
  c.box(52, 3, 27, 24, "single", "Legend");

  const iconMap: Record<string, string> = {
    T: "Tasks",
    N: "Notes",
    E: "Events",
    "!": "Alerts",
    "*": "Markers",
  };

  let legY = 4;
  for (const [icon, label] of Object.entries(iconMap)) {
    if (legY < 25) {
      c.write(54, legY++, `${icon} = ${label}`);
    }
  }

  if (legY + 5 < 25) {
    legY += 1;
    c.write(54, legY++, "Z Viewport");
    c.write(54, legY++, `Focus: z=${focusZ}`);
    c.write(54, legY++, `Range: +/-${zRange}`);
    c.write(54, legY++, `On-plane: ${onPlaneCount}`);
    c.write(54, legY++, `Nearby: ${nearbyCount}`);
    c.write(54, legY++, `Hidden: ${hiddenCount}`);
  }

  // Summary stats
  if (legY + 2 < 25) {
    legY += 2;
    const taskCount = visibleOverlays.filter(
      (o: LocIdOverlay) => o.icon === "T",
    ).length;
    const noteCount = visibleOverlays.filter(
      (o: LocIdOverlay) => o.icon === "N",
    ).length;
    const eventCount = visibleOverlays.filter(
      (o: LocIdOverlay) => o.icon === "E",
    ).length;
    const alertCount = visibleOverlays.filter(
      (o: LocIdOverlay) => o.icon === "!",
    ).length;

    if (legY < 25) c.write(54, legY++, `Tasks: ${taskCount}`);
    if (legY < 25) c.write(54, legY++, `Notes: ${noteCount}`);
    if (legY < 25) c.write(54, legY++, `Events: ${eventCount}`);
    if (legY < 25) c.write(54, legY++, `Alerts: ${alertCount}`);
  }

  const lines = c.toLines();
  return packageGrid({ ...spec, mode: "map" }, lines);
}
