/**
 * Anchor Runtime Gateway
 *
 * Provides a minimal adapter surface for game/engine runtimes.
 */

import {
  AnchorId,
  AnchorMeta,
  AnchorRuntime,
  AnchorTransform,
  AnchorInstance,
  InputEvent,
  RenderFrame,
  SaveStateRef,
  AnchorEvent,
} from "./anchors.js";
import { AnchorRegistry, getGlobalRegistry } from "./registry.js";

export class AnchorRuntimeGateway {
  private registry: AnchorRegistry;
  private runtimes: Map<AnchorId, AnchorRuntime> = new Map();

  constructor(registry?: AnchorRegistry) {
    this.registry = registry || getGlobalRegistry();
  }

  registerRuntime(anchorId: AnchorId, runtime: AnchorRuntime): void {
    this.runtimes.set(anchorId, runtime);
  }

  getRuntime(anchorId: AnchorId): AnchorRuntime | null {
    return this.runtimes.get(anchorId) || null;
  }

  listRuntimes(): AnchorId[] {
    return Array.from(this.runtimes.keys());
  }

  async meta(anchorId: AnchorId): Promise<AnchorMeta | null> {
    const runtime = this.getRuntime(anchorId);
    if (!runtime) return null;
    return runtime.meta();
  }

  async transform(anchorId: AnchorId): Promise<AnchorTransform | null> {
    const runtime = this.getRuntime(anchorId);
    if (!runtime) return null;
    return runtime.transform();
  }

  async createInstance(
    anchorId: AnchorId,
    params?: {
      seed?: string;
      profileId?: string;
    },
  ): Promise<AnchorInstance> {
    const runtime = this._requireRuntime(anchorId);
    return runtime.createInstance(params);
  }

  async destroyInstance(anchorId: AnchorId, instanceId: string): Promise<void> {
    const runtime = this._requireRuntime(anchorId);
    await runtime.destroyInstance(instanceId);
  }

  async input(
    anchorId: AnchorId,
    instanceId: string,
    event: InputEvent,
  ): Promise<void> {
    const runtime = this._requireRuntime(anchorId);
    await runtime.input(instanceId, event);
  }

  async tick(anchorId: AnchorId, instanceId: string, dtMs: number): Promise<void> {
    const runtime = this._requireRuntime(anchorId);
    await runtime.tick(instanceId, dtMs);
  }

  async render(anchorId: AnchorId, instanceId: string): Promise<RenderFrame> {
    const runtime = this._requireRuntime(anchorId);
    return runtime.render(instanceId);
  }

  async saveState(
    anchorId: AnchorId,
    instanceId: string,
  ): Promise<SaveStateRef | null> {
    const runtime = this._requireRuntime(anchorId);
    if (!runtime.saveState) return null;
    return runtime.saveState(instanceId);
  }

  async loadState(
    anchorId: AnchorId,
    instanceId: string,
    state: SaveStateRef,
  ): Promise<void> {
    const runtime = this._requireRuntime(anchorId);
    if (!runtime.loadState) return;
    await runtime.loadState(instanceId, state);
  }

  async pollEvents(
    anchorId: AnchorId,
    instanceId: string,
    sinceTs: number,
  ): Promise<AnchorEvent[] | null> {
    const runtime = this._requireRuntime(anchorId);
    if (!runtime.pollEvents) return null;
    return runtime.pollEvents(instanceId, sinceTs);
  }

  private _requireRuntime(anchorId: AnchorId): AnchorRuntime {
    const runtime = this.getRuntime(anchorId);
    if (!runtime) {
      throw new Error(`Anchor runtime not registered: ${anchorId}`);
    }
    if (!this.registry.hasAnchor(anchorId)) {
      // Runtime can exist without registry entry; allow but make it explicit.
      this.registry.registerAnchor({ id: anchorId, title: anchorId });
    }
    return runtime;
  }
}
