/**
 * Anchor Registry Implementation
 *
 * Manages coordinate frame definitions, validation, and transforms.
 * Implements the AnchorRegistry interface from anchors.ts.
 *
 * @module spatial/registry
 */

import {
  AnchorId,
  AnchorMeta,
  AnchorCapabilities,
  AnchorCoord,
  AnchorTransform,
  QuantiseOptions,
} from "./anchors.js";
import { parseLocId } from "./parse.js";

/**
 * Anchor metadata with full config
 */
export interface AnchorEntry extends AnchorMeta {
  createdAt: number;
  updatedAt: number;
  config?: Record<string, unknown>;
}

/**
 * In-memory registry of anchors
 */
export class AnchorRegistry {
  private anchors: Map<AnchorId, AnchorEntry> = new Map();
  private transforms: Map<AnchorId, AnchorTransform> = new Map();

  /**
   * Register an anchor with metadata
   */
  registerAnchor(meta: AnchorMeta, config?: Record<string, unknown>): void {
    const entry: AnchorEntry = {
      ...meta,
      id: meta.id,
      title: meta.title,
      version: meta.version,
      description: meta.description,
      capabilities: meta.capabilities,
      config: config || {},
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };
    this.anchors.set(meta.id, entry);
  }

  /**
   * Register a transform for coordinate conversion
   */
  registerTransform(anchorId: AnchorId, transform: AnchorTransform): void {
    this.transforms.set(anchorId, transform);
  }

  /**
   * Get anchor metadata by ID
   */
  getAnchor(id: AnchorId): AnchorMeta | null {
    return this.anchors.get(id) || null;
  }

  /**
   * Get anchor with full configuration
   */
  getAnchorEntry(id: AnchorId): AnchorEntry | null {
    return this.anchors.get(id) || null;
  }

  /**
   * List all registered anchors
   */
  listAnchors(): AnchorMeta[] {
    return Array.from(this.anchors.values());
  }

  /**
   * Get transform for an anchor (if registered)
   */
  getTransform(anchorId: AnchorId): AnchorTransform | null {
    return this.transforms.get(anchorId) || null;
  }

  /**
   * Check if anchor exists
   */
  hasAnchor(id: AnchorId): boolean {
    return this.anchors.has(id);
  }

  /**
   * Get anchor by specific kind
   */
  getAnchorsByKind(kind: string): AnchorMeta[] {
    return Array.from(this.anchors.values()).filter((a) => {
      const config = a.config as Record<string, unknown> | undefined;
      return config?.["kind"] === kind;
    });
  }

  /**
   * Validate anchor existence
   */
  validateAnchor(anchorId: string): boolean {
    return this.hasAnchor(anchorId as AnchorId);
  }

  /**
   * Count registered anchors
   */
  count(): number {
    return this.anchors.size;
  }

  /**
   * Clear all anchors and transforms
   */
  clear(): void {
    this.anchors.clear();
    this.transforms.clear();
  }
}

/**
 * Global singleton registry instance
 */
let globalRegistry: AnchorRegistry | null = null;

/**
 * Get the global registry (lazy init)
 */
export function getGlobalRegistry(): AnchorRegistry {
  if (!globalRegistry) {
    globalRegistry = new AnchorRegistry();
  }
  return globalRegistry;
}

/**
 * Set the global registry (for testing or custom initialization)
 */
export function setGlobalRegistry(registry: AnchorRegistry): void {
  globalRegistry = registry;
}

/**
 * Load anchors from JSON data into a registry
 *
 * Expected format:
 * {
 *   "version": "1.3.0",
 *   "anchors": [
 *     {
 *       "anchorId": "EARTH",
 *       "kind": "earth",
 *       "title": "...",
 *       "status": "active",
 *       "config": { ... }
 *     },
 *     ...
 *   ]
 * }
 */
export function loadAnchorsFromJSON(
  data: Record<string, unknown>,
  registry?: AnchorRegistry,
): AnchorRegistry {
  const reg = registry || new AnchorRegistry();

  if (!data.anchors || !Array.isArray(data.anchors)) {
    throw new Error("Invalid anchor metadata: anchors array not found");
  }

  for (const item of data.anchors) {
    const anchor = item as Record<string, unknown>;

    const id = anchor.anchorId as string | undefined;
    const title = anchor.title as string | undefined;

    if (!id || !title) {
      throw new Error(
        `Invalid anchor entry: missing anchorId or title in ${JSON.stringify(anchor)}`,
      );
    }

    const meta: AnchorMeta = {
      id: id as AnchorId,
      title,
      version: (anchor.version as string) || undefined,
      description: (anchor.description as string) || undefined,
      capabilities: (anchor.capabilities as AnchorCapabilities) || undefined,
    };

    reg.registerAnchor(meta, anchor.config as Record<string, unknown>);
  }

  return reg;
}

/**
 * Load anchors from a JSON file path (Node.js environment)
 * Returns a function that can load the JSON dynamically
 */
export function createFileLoader(
  filePath: string,
): (registry?: AnchorRegistry) => Promise<AnchorRegistry> {
  return async (registry?: AnchorRegistry) => {
    const fs = await import("fs/promises");
    const data = await fs.readFile(filePath, "utf-8");
    const parsed = JSON.parse(data);
    return loadAnchorsFromJSON(parsed, registry);
  };
}
