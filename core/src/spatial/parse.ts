import { AddressPath, LocId, PlaceKey, Space } from "./types.js";

/**
 * uDOS grid constraints (current spec):
 * - Cell is two letters + two digits.
 * - Rows are 10..39 (80x30 grid).
 * - Optional vertical axis suffix: -Z{z} where z is -99..99.
 */
export function isValidRow(row: number): boolean {
  return row >= 10 && row <= 39;
}

export function isValidCell(cell: string): boolean {
  if (!/^[A-Z]{2}\d{2}$/.test(cell)) return false;
  const row = Number(cell.slice(2, 4));
  return Number.isFinite(row) && isValidRow(row);
}

export function isValidZ(z: number): boolean {
  return Number.isInteger(z) && z >= -99 && z <= 99;
}

/** LocId: L###-Cell[-Zz] */
export function parseLocId(s: string): LocId | null {
  const m = /^L(\d{3})-([A-Z]{2}\d{2})(?:-Z(-?\d{1,2}))?$/.exec(s);
  if (!m) return null;
  const layer = Number(m[1]);
  const cell = m[2];
  const z = m[3] !== undefined ? Number(m[3]) : undefined;
  if (!isValidCell(cell)) return null;
  if (z !== undefined && !isValidZ(z)) return null;
  return { locId: s, effectiveLayer: layer, finalCell: cell, z };
}

/**
 * Narrative address path:
 *   L{BaseLayer}-{Cell}(-{Cell})*[-Z{z}]
 * Canonical compressed identity:
 *   L{BaseLayer + Depth}-{FinalCell}[-Z{z}]
 */
export function parseAddressPath(s: string): AddressPath | null {
  const m = /^L(\d{3})-([A-Z]{2}\d{2}(?:-[A-Z]{2}\d{2})*)(?:-Z(-?\d{1,2}))?$/.exec(s);
  if (!m) return null;

  const baseLayer = Number(m[1]);
  const cells = m[2].split("-");
  const z = m[3] !== undefined ? Number(m[3]) : undefined;
  if (cells.length < 1 || !cells.every(isValidCell)) return null;
  if (z !== undefined && !isValidZ(z)) return null;

  const effectiveLayer = baseLayer + (cells.length - 1);
  const finalCell = cells[cells.length - 1];
  const canonicalLocId = `L${String(effectiveLayer).padStart(3, "0")}-${finalCell}${z !== undefined ? `-Z${z}` : ""}`;

  return { baseLayer, cells, effectiveLayer, canonicalLocId, z };
}

/**
 * PlaceRef string:
 *   <ANCHOR_ID>:<SPACE>:<LOCID>[:D<depth>][:I<instance>]
 */
export function parsePlaceRef(s: string): PlaceKey | null {
  const parts = s.split(":");
  if (parts.length < 3) return null;

  const head = parts[0];
  let anchorId = parts[0];
  let idx = 1;

  if (head === "BODY" || head === "GAME" || head === "CATALOG") {
    if (parts.length < 4) return null;
    anchorId = `${parts[0]}:${parts[1]}`;
    idx = 2;
  }

  const space = parts[idx] as Space;
  if (space !== "SUR" && space !== "UDN" && space !== "SUB") return null;

  const locId = parts[idx + 1];
  if (!parseLocId(locId)) return null;

  let depth: number | undefined;
  let instance: string | undefined;

  for (const t of parts.slice(idx + 2)) {
    if (/^D\d+$/.test(t)) depth = Number(t.slice(1));
    else if (/^I.+$/.test(t)) instance = t.slice(1);
  }

  return { anchorId, space, locId, depth, instance };
}

/**
 * Frontmatter migration helper:
 * - legacy grid_locations entries ("L305-DA11") become "EARTH:SUR:L305-DA11"
 */
export function normaliseFrontmatterPlaces(fm: { grid_locations?: string[]; places?: string[] }): string[] {
  const out: string[] = [];

  if (Array.isArray(fm.places)) {
    for (const p of fm.places) if (parsePlaceRef(p)) out.push(p);
  }

  if (Array.isArray(fm.grid_locations)) {
    for (const l of fm.grid_locations) {
      if (parseLocId(l)) out.push(`EARTH:SUR:${l}`);
    }
  }

  return Array.from(new Set(out));
}
