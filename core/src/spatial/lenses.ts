/**
 * World Lenses (Engine Adapters)
 *
 * Provides a minimal adapter surface for engine integrations (Godot/O3DE).
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
import { AnchorRuntimeGateway } from "./runtime.js";

export type EngineId = "godot" | "o3de" | "terminal";

export interface WorldLensConfig {
  engineId: EngineId;
  anchorId: AnchorId;
  mode?: "2d" | "2.5d" | "3d";
  options?: Record<string, unknown>;
}

export interface WorldLensAdapter {
  readonly config: WorldLensConfig;
  connect(): Promise<void>;
  disconnect(): Promise<void>;

  meta(): Promise<AnchorMeta | null>;
  transform(): Promise<AnchorTransform | null>;

  createInstance(params?: {
    seed?: string;
    profileId?: string;
    space?: "SUR" | "SUB" | "UDN";
    initialLocId?: string;
  }): Promise<AnchorInstance>;

  destroyInstance(instanceId: string): Promise<void>;
  input(instanceId: string, event: InputEvent): Promise<void>;
  tick(instanceId: string, dtMs: number): Promise<void>;
  render(instanceId: string): Promise<RenderFrame>;

  saveState(instanceId: string): Promise<SaveStateRef | null>;
  loadState(instanceId: string, state: SaveStateRef): Promise<void>;
  pollEvents(instanceId: string, sinceTs: number): Promise<AnchorEvent[] | null>;
}

class BaseLensAdapter implements WorldLensAdapter {
  readonly config: WorldLensConfig;
  private readonly gateway: AnchorRuntimeGateway;

  constructor(config: WorldLensConfig, gateway?: AnchorRuntimeGateway) {
    this.config = config;
    this.gateway = gateway || new AnchorRuntimeGateway();
  }

  async connect(): Promise<void> {
    // No-op for now; concrete adapters can override to handshake with engine.
  }

  async disconnect(): Promise<void> {
    // No-op for now; concrete adapters can override to teardown connections.
  }

  async meta(): Promise<AnchorMeta | null> {
    return this.gateway.meta(this.config.anchorId);
  }

  async transform(): Promise<AnchorTransform | null> {
    return this.gateway.transform(this.config.anchorId);
  }

  async createInstance(params?: {
    seed?: string;
    profileId?: string;
  }): Promise<AnchorInstance> {
    return this.gateway.createInstance(this.config.anchorId, params);
  }

  async destroyInstance(instanceId: string): Promise<void> {
    await this.gateway.destroyInstance(this.config.anchorId, instanceId);
  }

  async input(instanceId: string, event: InputEvent): Promise<void> {
    await this.gateway.input(this.config.anchorId, instanceId, event);
  }

  async tick(instanceId: string, dtMs: number): Promise<void> {
    await this.gateway.tick(this.config.anchorId, instanceId, dtMs);
  }

  async render(instanceId: string): Promise<RenderFrame> {
    return this.gateway.render(this.config.anchorId, instanceId);
  }

  async saveState(instanceId: string): Promise<SaveStateRef | null> {
    return this.gateway.saveState(this.config.anchorId, instanceId);
  }

  async loadState(instanceId: string, state: SaveStateRef): Promise<void> {
    await this.gateway.loadState(this.config.anchorId, instanceId, state);
  }

  async pollEvents(
    instanceId: string,
    sinceTs: number,
  ): Promise<AnchorEvent[] | null> {
    return this.gateway.pollEvents(this.config.anchorId, instanceId, sinceTs);
  }
}

export class GodotLensAdapter extends BaseLensAdapter {
  constructor(anchorId: AnchorId, gateway?: AnchorRuntimeGateway) {
    super({ engineId: "godot", anchorId, mode: "2d" }, gateway);
  }
}

export class O3DELensAdapter extends BaseLensAdapter {
  constructor(anchorId: AnchorId, gateway?: AnchorRuntimeGateway) {
    super({ engineId: "o3de", anchorId, mode: "3d" }, gateway);
  }
}

export function createLensAdapter(
  config: WorldLensConfig,
  gateway?: AnchorRuntimeGateway,
): WorldLensAdapter {
  switch (config.engineId) {
    case "godot":
      return new GodotLensAdapter(config.anchorId, gateway);
    case "o3de":
      return new O3DELensAdapter(config.anchorId, gateway);
    default:
      return new BaseLensAdapter(config, gateway);
  }
}
