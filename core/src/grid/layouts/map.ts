import { Canvas } from "../canvas.js";
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

const WORKFLOW_STATE_GLYPH: Record<WorkflowMarker["state"], string> = {
  todo: "[ ]",
  in_progress: "[>]",
  blocked: "[!]",
  done: "[x]",
};

function clamp(v: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, v));
}

function hashLocId(value: string): number {
  let hash = 2166136261;
  for (let i = 0; i < value.length; i++) {
    hash ^= value.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

function locIdToCoord(locId: string, cols: number, rows: number): { x: number; y: number } {
  const match = /:L(\d+)-([A-Z]{1,2})(\d{1,2})(?:-Z-?\d{1,2})?$/.exec(locId);
  if (match) {
    const gridNum = Number(match[1]) || 0;
    const letters = match[2];
    const subNum = Number(match[3]) || 0;
    let lettersVal = 0;
    for (let i = 0; i < letters.length; i++) {
      lettersVal = lettersVal * 26 + (letters.charCodeAt(i) - 64);
    }
    const x = Math.abs((lettersVal + subNum + gridNum) % cols);
    const y = Math.abs((subNum + gridNum) % rows);
    return { x, y };
  }
  const hash = hashLocId(locId);
  const x = hash % cols;
  const y = Math.floor(hash / cols) % rows;
  return { x, y };
}

function writeClamped(canvas: Canvas, x: number, y: number, text: string, width: number) {
  if (width <= 0) return;
  canvas.write(x, y, text.slice(0, width));
}

export function renderMap(spec: GridCanvasSpec, input: MapInput) {
  const width = clamp(Math.floor(spec.width || 80), 40, 180);
  const height = clamp(Math.floor(spec.height || 30), 20, 90);

  const c = new Canvas(width, height);
  c.clear(" ");

  const focusLocId = input.focusLocId || "EARTH:SUR:L305-DA11";
  const title = `${spec.title || "Map"} — Focus: ${focusLocId}`;
  c.box(0, 0, width, height, "single", title.slice(0, Math.max(0, width - 4)));

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

  writeClamped(
    c,
    2,
    1,
    `World:${world} Realm:${realm} Grid:${locGrid} FocusZ:${focusZ}`,
    width - 4,
  );

  const layerStack = resolveLayerStack(input.layers);
  const visibleLayers = layerStack.filter((l) => l.visible !== false);

  const sideBySide = width >= 72;
  const mapX = 1;
  const mapY = 3;
  const mapW = sideBySide ? width - Math.max(24, Math.floor(width * 0.33)) - 2 : width - 2;
  const mapH = sideBySide ? height - 4 : Math.max(8, height - 12);

  const legendX = sideBySide ? mapX + mapW : 1;
  const legendY = sideBySide ? 3 : mapY + mapH;
  const legendW = sideBySide ? width - legendX - 1 : width - 2;
  const legendH = sideBySide ? height - 4 : height - legendY - 1;

  const cellCols = Math.max(1, Math.floor((mapW - 2) / 2));
  const cellRows = Math.max(1, Math.floor((mapH - 2) / 2));

  const cells = new Map<string, MinimapCell>();

  const stats: Record<MapLayerKind, number> = {
    terrain: 0,
    objects: 0,
    overlays: 0,
    workflow: 0,
  };

  let onPlaneCount = 0;
  let nearbyCount = 0;
  let hiddenCount = 0;

  function upsertCell(locId: string, cell: MinimapCell, overwrite = true) {
    const coord = locIdToCoord(locId, cellCols, cellRows);
    const key = `${coord.x},${coord.y}`;
    if (!overwrite && cells.has(key)) return;
    cells.set(key, { ...cell, coord });
  }

  function applyTerrain(terrain: TerrainCell[] = []) {
    terrain.forEach((cell) => {
      const z = typeof cell.z === "number" ? cell.z : parseLocIdZ(cell.locId);
      if (!inZRange(z, focusZ, zRange)) return;
      upsertCell(cell.locId, { type: "occupied", content: cell.glyph }, false);
      stats.terrain++;
    });
  }

  function applyObjects(objects: MapObject[] = []) {
    objects.forEach((obj) => {
      const z = typeof obj.z === "number" ? obj.z : parseLocIdZ(obj.locId);
      if (!inZRange(z, focusZ, zRange)) return;
      upsertCell(obj.locId, { type: "occupied", content: obj.sprite }, true);
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
      upsertCell(
        locId,
        {
          type: locId === focusLocId ? "selected" : "tagged",
          overlay,
        },
        true,
      );
      stats.overlays++;
    });
  }

  function applyWorkflowMarkers(markers: WorkflowMarker[] = []) {
    markers.forEach((marker) => {
      const z = typeof marker.z === "number" ? marker.z : parseLocIdZ(marker.locId);
      if (!inZRange(z, focusZ, zRange)) return;
      const glyph = WORKFLOW_STATE_GLYPH[marker.state] || "[ ]";
      upsertCell(marker.locId, { type: "tagged", content: glyph[1] ?? "W" }, true);
      stats.workflow++;
    });
  }

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

  c.minimap(mapX, mapY, mapW, mapH, cells, {
    showLabels: true,
    focusCell: { x: 0, y: 0 },
  });

  if (legendW >= 12 && legendH >= 6) {
    c.box(legendX, legendY, legendW, legendH, "single", "Legend");
    let y = legendY + 1;
    const textW = Math.max(1, legendW - 2);

    writeClamped(c, legendX + 1, y++, "Layers (b->t):", textW);
    for (const layer of layerStack) {
      if (y >= legendY + legendH - 1) break;
      const vis = layer.visible !== false ? "+" : "-";
      const name = (layer.label || layer.kind).slice(0, Math.max(1, textW - 3));
      writeClamped(c, legendX + 1, y++, `${vis} ${name}`, textW);
    }

    if (y < legendY + legendH - 2) {
      y++;
      writeClamped(c, legendX + 1, y++, `Focus z=${focusZ}`, textW);
      writeClamped(c, legendX + 1, y++, `Range +/-${zRange}`, textW);
      writeClamped(c, legendX + 1, y++, `On:${onPlaneCount} Near:${nearbyCount}`, textW);
      writeClamped(c, legendX + 1, y++, `Hidden:${hiddenCount}`, textW);
    }

    if (y < legendY + legendH - 2) {
      y++;
      writeClamped(
        c,
        legendX + 1,
        y++,
        `T:${stats.terrain} O:${stats.objects} OV:${stats.overlays} W:${stats.workflow}`,
        textW,
      );
    }
  }

  const lines = c.toLines();
  return packageGrid({ ...spec, mode: "map" }, lines);
}
