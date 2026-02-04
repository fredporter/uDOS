/**
 * uDOS v1.3 Spatial Types
 *
 * Canonical identity:
 *   LocId := L{EffectiveLayer}-{FinalCell}
 *
 * Place identity (recommended string form for frontmatter + APIs):
 *   PlaceRef := <ANCHOR_ID>:<SPACE>:<LOCID>[:D<depth>][:I<instance>]
 */

export type Space = "SUR" | "UDN" | "SUB";
export type AnchorKind = "earth" | "body" | "game" | "catalog";

export interface Anchor {
  anchorId: string; // "EARTH", "BODY:MOON", "GAME:skyrim"
  kind: AnchorKind;
  title: string;
  status: "active" | "deprecated";
  config: Record<string, unknown>;
  createdAt: number;
  updatedAt: number;
}

export interface LocId {
  locId: string;            // "L305-DA11"
  effectiveLayer: number;   // 305
  finalCell: string;        // "DA11"
}

export interface AddressPath {
  baseLayer: number;        // e.g. 300
  cells: string[];          // ["AC10","EA12","BB21","AB32","DA11"]
  effectiveLayer: number;   // baseLayer + (cells.length - 1)
  canonicalLocId: string;   // "L305-DA11"
}

export interface PlaceKey {
  anchorId: string;
  space: Space;
  locId: string;
  depth?: number;
  instance?: string;
}

export interface PlaceRow extends PlaceKey {
  placeId: string;
  label?: string;
  createdAt: number;
  updatedAt: number;
}

/** Frontmatter compatibility */
export interface FileFrontmatter {
  title?: string;

  /** Legacy: implicit EARTH:SUR */
  grid_locations?: string[];

  /** v1.3 preferred */
  places?: string[];
}
