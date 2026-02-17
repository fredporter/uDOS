import { Canvas80x30 } from "../canvas.js";
import { packageGrid } from "../pack.js";
import {
  GridCanvasSpec,
  MapInput,
  MapViewportOptions,
  MinimapCell,
  LocIdOverlay,
  TerrainCell,
  MapObject,
  WorkflowMarker,
  MapLayerSpec,
  MapLayerKind,
} from "../types.js";

function parseLocIdZ(locId: string | undefined): number {
  if (!locId || typeof locId !== "string") return 0;
  const match = /-Z(-?\d{1,2})$/.exec(locId);
  if (!match) return 0;
  const z = Number(match[1]);
  if (!Number.isFinite(z)) return 0;
  return z;
}

function inZRange(itemZ: number, focusZ: number, zRange: number): boolean {
  return Math.abs(itemZ - focusZ) <= zRange;
}

// Default layer stack order (bottom → top)
const DEFAULT_LAYER_ORDER: MapLayerKind[] = [
  "terrain",
  "objects",
  "overlays",
  "workflow",
];

function resolveLayerStack(layers: MapLayerSpec[] | undefined): MapLayerSpec[] {
  if (layers && layers.length > 0) return layers;
  return DEFAULT_LAYER_ORDER.map((kind) => ({ kind, visible: true }));
}

// Glyphs for workflow marker states
const WORKFLOW_STATE_GLYPH: Record<WorkflowMarker["state"], string> = {
  todo: "[ ]",
  in_progress: "[>]",
  blocked: "[!]",
  done: "[x]",
};

export function renderMap(spec: GridCanvasSpec, input: MapInput) {
  const c = new Canvas80x30();
  c.clear(" ");

  const focusLocId = input.focusLocId || "EARTH:SUR:L305-DA11";
  c.box(0, 0, 80, 30, "single", `${spec.title} — Focus: ${focusLocId}`);

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

  c.write(
    2,
    1,
    `World: ${world} | Realm: ${realm} | Grid: ${locGrid} | Focus Z: ${focusZ}`,
  );

  // Resolve layer stack
  const layerStack = resolveLayerStack(input.layers);
  const visibleLayers = layerStack.filter((l) => l.visible !== false);

  // Build minimap cells from all visible layers in order
  const cells = new Map<string, MinimapCell>();

  // Count stats per layer for legend
  const stats: Record<MapLayerKind, number> = {
    terrain: 0,
    objects: 0,
    overlays: 0,
    workflow: 0,
  };

  let onPlaneCount = 0;
  let nearbyCount = 0;
  let hiddenCount = 0;

  // Layer rendering helpers

  function applyTerrain(terrain: TerrainCell[] = []) {
    terrain.forEach((cell) => {
      const z = typeof cell.z === "number" ? cell.z : parseLocIdZ(cell.locId);
      if (!inZRange(z, focusZ, zRange)) return;
      const key = cell.locId;
      // Terrain is the base; only set if no existing cell
      if (!cells.has(key)) {
        cells.set(key, { type: "occupied", content: cell.glyph });
      }
      stats.terrain++;
    });
  }

  function applyObjects(objects: MapObject[] = []) {
    objects.forEach((obj) => {
      const z = typeof obj.z === "number" ? obj.z : parseLocIdZ(obj.locId);
      if (!inZRange(z, focusZ, zRange)) return;
      cells.set(obj.locId, { type: "occupied", content: obj.sprite });
      stats.objects++;
    });
  }

  function applyOverlays(overlays: LocIdOverlay[] = []) {
    overlays.forEach((overlay, idx) => {
      const locId = overlay.locId || `CELL-${idx}`;
      const overlayZ =
        typeof overlay.z === "number" ? overlay.z : parseLocIdZ(overlay.locId);
      const dz = Math.abs(overlayZ - focusZ);
      const onPlane = dz === 0;
      const nearby = dz <= zRange;
      if (onPlane) onPlaneCount++;
      if (!onPlane && nearby) nearbyCount++;
      if (!nearby) {
        hiddenCount++;
        return;
      }
      cells.set(locId, {
        type: overlay.locId === focusLocId ? "selected" : "tagged",
        overlay,
      });
      stats.overlays++;
    });
  }

  function applyWorkflowMarkers(markers: WorkflowMarker[] = []) {
    markers.forEach((marker) => {
      const z = typeof marker.z === "number" ? marker.z : parseLocIdZ(marker.locId);
      if (!inZRange(z, focusZ, zRange)) return;
      const glyph = WORKFLOW_STATE_GLYPH[marker.state] || "[ ]";
      cells.set(marker.locId, {
        type: "tagged",
        content: glyph[1] ?? "W",
      });
      stats.workflow++;
    });
  }

  // Apply layers in stack order
  for (const layer of visibleLayers) {
    switch (layer.kind) {
      case "terrain":
        applyTerrain(input.terrain);
        break;
      case "objects":
        applyObjects(input.objects);
        break;
      case "overlays":
        applyOverlays(input.overlays);
        break;
      case "workflow":
        applyWorkflowMarkers(input.workflowMarkers);
        break;
    }
  }

  // Draw minimap
  c.minimap(1, 3, 50, 24, cells, {
    showLabels: true,
    focusCell: { x: 0, y: 0 },
  });

  // Legend pane on right
  c.box(52, 3, 27, 24, "single", "Legend");

  let legY = 4;

  // Layer stack section
  c.write(54, legY++, "Layers (b→t):");
  for (const layer of layerStack) {
    if (legY >= 12) break;
    const vis = layer.visible !== false ? "+" : "-";
    const name = (layer.label || layer.kind).slice(0, 16);
    c.write(54, legY++, `${vis} ${name}`);
  }

  legY++;

  // Z Viewport section
  if (legY + 3 < 22) {
    c.write(54, legY++, "Z Viewport");
    c.write(54, legY++, `Focus: z=${focusZ}`);
    c.write(54, legY++, `Range: +/-${zRange}`);
    c.write(54, legY++, `On-plane: ${onPlaneCount}`);
    c.write(54, legY++, `Nearby: ${nearbyCount}`);
    c.write(54, legY++, `Hidden: ${hiddenCount}`);
  }

  legY++;

  // Layer counts
  if (legY + 4 < 26) {
    c.write(54, legY++, "Counts:");
    const countLine = `T:${stats.terrain} O:${stats.objects} OV:${stats.overlays} W:${stats.workflow}`;
    c.write(54, legY++, countLine.slice(0, 24));
  }

  // Icon legend for overlays
  const iconMap: Record<string, string> = {
    T: "Tasks",
    N: "Notes",
    E: "Events",
    "!": "Alerts",
    "*": "Markers",
  };
  legY++;
  if (legY + 1 < 26) {
    c.write(54, legY++, "Icons:");
    for (const [icon, label] of Object.entries(iconMap)) {
      if (legY >= 26) break;
      c.write(54, legY++, `${icon} = ${label}`);
    }
  }

  const lines = c.toLines();
  return packageGrid({ ...spec, mode: "map" }, lines);
}
