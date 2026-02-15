import { Canvas80x30 } from "../canvas.js";
import { packageGrid } from "../pack.js";
import { GridCanvasSpec, MinimapCell, LocIdOverlay } from "../types.js";

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

  // Display location info
  c.write(2, 1, `World: ${world} | Realm: ${realm} | Grid: ${locGrid}`);

  // Build minimap cells from overlays
  const cells = new Map<string, MinimapCell>();
  const overlays = input.overlays || [];

  overlays.forEach((overlay: LocIdOverlay, idx: number) => {
    const locId = overlay.locId || `CELL-${idx}`;
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

  // Summary stats
  if (legY + 2 < 25) {
    legY += 2;
    const taskCount = overlays.filter(
      (o: LocIdOverlay) => o.icon === "T",
    ).length;
    const noteCount = overlays.filter(
      (o: LocIdOverlay) => o.icon === "N",
    ).length;
    const eventCount = overlays.filter(
      (o: LocIdOverlay) => o.icon === "E",
    ).length;
    const alertCount = overlays.filter(
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
