/**
 * Viewport + Renderer Tests
 * 
 * Tests for Phase 2 implementation
 */

import { ViewportManager } from "../src/viewport";
import { TeletextRenderer, RenderPipeline, GraphicsModeSupport } from "../src/renderer";
import { GraphicsMode, VIEWPORT_STANDARD, VIEWPORT_MINI } from "../src/geometry";
import { parseCell, CanonicalAddress } from "../src/address";

describe("ViewportManager", () => {
  let viewport: ViewportManager;

  beforeEach(() => {
    viewport = new ViewportManager({ col: 40, row: 15 });
  });

  test("should initialize with center cell", () => {
    expect(viewport).toBeDefined();
  });

  test("should get viewport bounds (center at 40,15)", () => {
    const bounds = viewport.getViewBounds();
    expect(bounds.minCol).toBe(40 - 40);
    expect(bounds.maxCol).toBe(40 + 40);
    expect(bounds.minRow).toBe(15 - 15);
    expect(bounds.maxRow).toBe(15 + 15);
  });

  test("should clamp bounds to grid edges", () => {
    const edgeViewport = new ViewportManager({ col: 0, row: 0 });
    const bounds = edgeViewport.getViewBounds();
    expect(bounds.minCol).toBeGreaterThanOrEqual(0);
    expect(bounds.minRow).toBeGreaterThanOrEqual(0);
  });

  test("should set visible layers", () => {
    viewport.setViewLayers(300, 299);
    // Should not throw
    expect(viewport).toBeDefined();
  });

  test("should switch render modes", () => {
    viewport.setRenderMode(GraphicsMode.Teletext);
    viewport.setRenderMode(GraphicsMode.AsciiBlock);
    viewport.setRenderMode(GraphicsMode.Shade);
    viewport.setRenderMode(GraphicsMode.ASCII);
    // Should not throw
    expect(viewport).toBeDefined();
  });

  test("should render character with fallback (teletext)", () => {
    viewport.setRenderMode(GraphicsMode.Teletext);
    const char = viewport.renderCharacter(5);
    expect(char).toBeTruthy();
    expect(char.length).toBe(1);
  });

  test("should render character with fallback (ASCII)", () => {
    viewport.setRenderMode(GraphicsMode.ASCII);
    const char = viewport.renderCharacter(15);
    expect(char).toMatch(/[.:#@]/);
  });

  test("should compose viewport to 2D array", () => {
    viewport.setViewLayers(300);
    const rendered = viewport.compose();
    expect(Array.isArray(rendered)).toBe(true);
    expect(rendered.length).toBe(VIEWPORT_STANDARD.rows);
    expect(rendered[0].length).toBe(VIEWPORT_STANDARD.cols);
  });

  test("should render viewport as string", () => {
    viewport.setViewLayers(300);
    const str = viewport.toString();
    expect(typeof str).toBe("string");
    const lines = str.split("\n");
    expect(lines.length).toBe(VIEWPORT_STANDARD.rows);
  });
});

describe("RenderPipeline", () => {
  let pipeline: RenderPipeline;

  beforeEach(() => {
    pipeline = new RenderPipeline(GraphicsMode.Teletext);
  });

  test("should initialize with default mode", () => {
    expect(pipeline).toBeDefined();
  });

  test("should switch render modes", () => {
    pipeline.setRenderMode(GraphicsMode.AsciiBlock);
    pipeline.setRenderMode(GraphicsMode.Shade);
    pipeline.setRenderMode(GraphicsMode.ASCII);
    expect(pipeline).toBeDefined();
  });

  test("should render character with teletext mode", () => {
    pipeline.setRenderMode(GraphicsMode.Teletext);
    const char = pipeline.renderCharacterWithFallback(5);
    expect(char).toBeTruthy();
  });

  test("should render character with asciiBlock fallback", () => {
    pipeline.setRenderMode(GraphicsMode.AsciiBlock);
    const char = pipeline.renderCharacterWithFallback(5);
    expect(char).toBeTruthy();
  });

  test("should render character with shade fallback", () => {
    pipeline.setRenderMode(GraphicsMode.Shade);
    const char = pipeline.renderCharacterWithFallback(5);
    expect(char).toMatch(/[░▒▓█]/);
  });

  test("should render character with ASCII fallback", () => {
    pipeline.setRenderMode(GraphicsMode.ASCII);
    const char = pipeline.renderCharacterWithFallback(5);
    expect(char).toMatch(/[.:#@]/);
  });

  test("should render tile with color", () => {
    const mockTile = { id: "tile1", type: "object" as const, static: true };
    const result = pipeline.renderTile(mockTile, 5);
    expect(result).toHaveProperty("char");
    expect(result).toHaveProperty("color");
    expect(result).toHaveProperty("priority");
  });

  test("should compose layers to canvas", () => {
    const layers = [
      {
        tiles: new Map([["00", "5"]]),
        colors: new Map([["00", 5]]),
        priorities: new Map([["00", 10]])
      }
    ];
    const canvas = pipeline.composeLayers(layers, 10, 10);
    expect(canvas.length).toBe(10);
    expect(canvas[0].length).toBe(10);
  });

  test("should convert canvas to string", () => {
    const layers = [
      {
        tiles: new Map(),
        colors: new Map(),
        priorities: new Map()
      }
    ];
    const canvas = pipeline.composeLayers(layers, 5, 5);
    const str = pipeline.canvasToString(canvas);
    expect(typeof str).toBe("string");
    const lines = str.split("\n");
    expect(lines.length).toBe(5);
  });

  test("should get color for tile", () => {
    const color = pipeline.getColorForTile({ id: "1", type: "object", static: true }, 5);
    expect(color).toBeTruthy();
    expect(color).toMatch(/^#[0-9A-F]{6}$/i);
  });
});

describe("TeletextCharacterSet", () => {
  test("should get character for sprite", () => {
    const mockSprite = { id: "sp1", type: "sprite" as const, static: false };
    const char = TeletextCharacterSet.getCharacter(mockSprite);
    expect(char).toBeTruthy();
  });

  test("should get character for marker", () => {
    const mockMarker = { id: "m1", type: "marker" as const, static: false };
    const char = TeletextCharacterSet.getCharacter(mockMarker);
    expect(char).toBeTruthy();
  });

  test("should get character for object", () => {
    const mockObject = { id: "obj1", type: "object" as const, static: true };
    const char = TeletextCharacterSet.getCharacter(mockObject);
    expect(char).toBeTruthy();
  });
});

describe("GraphicsModeSupport", () => {
  test("should get fallback chain for teletext", () => {
    const chain = GraphicsModeSupport.getFallbackChain(GraphicsMode.Teletext);
    expect(chain[0]).toBe(GraphicsMode.Teletext);
    expect(chain[chain.length - 1]).toBe(GraphicsMode.ASCII);
  });

  test("should get fallback chain for ASCII", () => {
    const chain = GraphicsModeSupport.getFallbackChain(GraphicsMode.ASCII);
    expect(chain).toContain(GraphicsMode.ASCII);
  });

  test("should detect terminal mode", () => {
    const mode = GraphicsModeSupport.detectTerminalMode();
    expect([GraphicsMode.Teletext, GraphicsMode.AsciiBlock, GraphicsMode.Shade, GraphicsMode.ASCII]).toContain(mode);
  });
});

describe("Fallback Rendering", () => {
  test("should gracefully fallback teletext → ASCII", () => {
    const pipeline = new RenderPipeline();

    const teletextChar = (() => {
      pipeline.setRenderMode(GraphicsMode.Teletext);
      return pipeline.renderCharacterWithFallback(5);
    })();

    const asciiChar = (() => {
      pipeline.setRenderMode(GraphicsMode.ASCII);
      return pipeline.renderCharacterWithFallback(5);
    })();

    expect(teletextChar).toBeTruthy();
    expect(asciiChar).toMatch(/[.:#@]/);
  });
});

describe("Performance", () => {
  test("should compose 80x30 viewport in reasonable time", () => {
    const pipeline = new RenderPipeline();
    const layers = Array(3)
      .fill(null)
      .map(() => ({
        tiles: new Map(),
        colors: new Map(),
        priorities: new Map()
      }));

    const start = performance.now();
    const canvas = pipeline.composeLayers(layers, 80, 30);
    const elapsed = performance.now() - start;

    expect(canvas.length).toBe(30);
    expect(canvas[0].length).toBe(80);
    expect(elapsed).toBeLessThan(100); // Should complete in <100ms
  });
});
