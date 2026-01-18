/**
 * CodeBlockParser - Parse teletext, grid, and tiles code blocks
 * Phase 3: Code Block Parser component
 *
 * Supports three block types:
 * 1. teletext - Raw text/ASCII art storage
 * 2. grid - YAML location definition with cell data
 * 3. tiles - YAML array of tile manifests
 */

import { ExpressionEvaluator } from "./expression-evaluator";

/**
 * Raw code block from markdown
 */
export interface CodeBlock {
  type: "teletext" | "grid" | "tiles";
  content: string;
  metadata?: Record<string, string>;
}

/**
 * Parsed teletext block (raw text)
 */
export interface TeletextBlock {
  type: "teletext";
  lines: string[];
  width: number;
  height: number;
}

/**
 * Grid block content - location definition
 */
export interface GridLocation {
  name: string;
  layer: number;
  startCell: string;
  cells: Array<{
    address: string;
    objects?: Array<{ type: string; props?: Record<string, any> }>;
    sprites?: Array<{ id: string; props?: Record<string, any> }>;
    terrain?: string;
  }>;
}

/**
 * Parsed grid block
 */
export interface GridBlock {
  type: "grid";
  location: GridLocation;
}

/**
 * Tile definition
 */
export interface TileDefinition {
  id: string;
  character: string;
  color: string;
  layer: number;
  props?: Record<string, any>;
}

/**
 * Parsed tiles block
 */
export interface TilesBlock {
  type: "tiles";
  tiles: TileDefinition[];
}

/**
 * CodeBlockParser: Parse markdown code blocks into structured data
 */
export class CodeBlockParser {
  private evaluator: ExpressionEvaluator;

  /**
   * Constructor with optional expression evaluator
   * @param evaluator - ExpressionEvaluator for interpolation in blocks
   */
  constructor(evaluator?: ExpressionEvaluator) {
    this.evaluator = evaluator || new ExpressionEvaluator();
  }

  /**
   * Parse a code block based on its type
   * @param block - Code block to parse
   * @returns Parsed block data
   */
  public parse(block: CodeBlock): TeletextBlock | GridBlock | TilesBlock {
    switch (block.type) {
      case "teletext":
        return this.parseTeletextBlock(block);
      case "grid":
        return this.parseGridBlock(block);
      case "tiles":
        return this.parseTilesBlock(block);
      default:
        throw new Error(`Unknown code block type: ${(block as any).type}`);
    }
  }

  /**
   * Parse teletext block (raw text/ASCII art)
   * Lines are preserved as-is, with interpolation
   * @param block - Code block
   * @returns Parsed teletext block
   */
  private parseTeletextBlock(block: CodeBlock): TeletextBlock {
    const lines = block.content
      .split("\n")
      .map((line) => this.evaluator.interpolate(line));

    // Remove trailing empty lines
    while (lines.length > 0 && lines[lines.length - 1] === "") {
      lines.pop();
    }

    const width = Math.max(...lines.map((line) => line.length), 0);
    const height = lines.length;

    return {
      type: "teletext",
      lines,
      width,
      height,
    };
  }

  /**
   * Parse grid block (YAML location definition)
   * @param block - Code block
   * @returns Parsed grid block
   */
  private parseGridBlock(block: CodeBlock): GridBlock {
    const yaml = this.parseYAML(block.content);

    // Validate required fields
    if (!yaml.name) {
      throw new Error("Grid block missing required 'name' field");
    }
    if (yaml.layer === undefined) {
      throw new Error("Grid block missing required 'layer' field");
    }
    if (!yaml.startCell) {
      throw new Error("Grid block missing required 'startCell' field");
    }

    const location: GridLocation = {
      name: String(yaml.name),
      layer: Number(yaml.layer),
      startCell: String(yaml.startCell),
      cells: [],
    };

    // Parse cells array
    if (Array.isArray(yaml.cells)) {
      for (const cellData of yaml.cells) {
        if (cellData && cellData.address) {
          const cell = {
            address: String(cellData.address),
            objects: cellData.objects as any[] | undefined,
            sprites: cellData.sprites as any[] | undefined,
            terrain: cellData.terrain ? String(cellData.terrain) : undefined,
          };

          // Remove undefined fields
          if (!cell.objects) delete cell.objects;
          if (!cell.sprites) delete cell.sprites;
          if (!cell.terrain) delete cell.terrain;

          location.cells.push(cell);
        }
      }
    }

    return {
      type: "grid",
      location,
    };
  }

  /**
   * Parse tiles block (YAML array of tile definitions)
   * @param block - Code block
   * @returns Parsed tiles block
   */
  private parseTilesBlock(block: CodeBlock): TilesBlock {
    const yaml = this.parseYAML(block.content);

    if (!Array.isArray(yaml)) {
      throw new Error("Tiles block must contain a YAML array");
    }

    const tiles: TileDefinition[] = [];

    for (const tileData of yaml) {
      if (tileData && tileData.id && tileData.character) {
        const tile: TileDefinition = {
          id: String(tileData.id),
          character: String(tileData.character),
          color: String(tileData.color || "white"),
          layer: Number(tileData.layer || 299),
          props: tileData.props as Record<string, any> | undefined,
        };

        if (!tile.props) delete tile.props;

        tiles.push(tile);
      }
    }

    return {
      type: "tiles",
      tiles,
    };
  }

  /**
   * Simple YAML parser for grid/tiles blocks
   * Supports basic structure: key: value, arrays, nested objects
   * @param content - YAML content as string
   * @returns Parsed object or array
   */
  private parseYAML(content: string): any {
    const lines = content.split("\n").filter((line) => line.trim());

    // Check if it's an array (starts with -)
    if (lines.some((line) => line.trim().startsWith("-"))) {
      return this.parseYAMLArray(lines);
    }

    // Parse as object
    return this.parseYAMLObject(lines);
  }

  /**
   * Parse YAML object (key: value pairs)
   */
  private parseYAMLObject(lines: string[]): Record<string, any> {
    const result: Record<string, any> = {};
    let currentKey = "";
    let currentValue = "";
    let indentStack: number[] = [];

    for (const line of lines) {
      if (!line.trim()) continue;

      const indent = line.search(/\S/);
      const trimmed = line.trim();

      // Simple key: value parsing
      if (trimmed.includes(":")) {
        const [key, ...valueParts] = trimmed.split(":");
        const value = valueParts.join(":").trim();

        // Handle nested structures
        if (value === "") {
          currentKey = key.trim();
        } else {
          // Try to parse value as number, boolean, or string
          result[key.trim()] = this.parseYAMLValue(value);
        }
      } else if (trimmed.startsWith("-") && indent > (indentStack[0] || 0)) {
        // Array item
        if (!result[currentKey]) {
          result[currentKey] = [];
        }
        const item = trimmed.slice(1).trim();
        result[currentKey].push(this.parseYAMLValue(item));
      }
    }

    return result;
  }

  /**
   * Parse YAML array (list of items)
   */
  private parseYAMLArray(lines: string[]): any[] {
    const result: any[] = [];
    let currentItem: Record<string, any> | null = null;

    for (const line of lines) {
      if (!line.trim()) continue;

      const trimmed = line.trim();

      if (trimmed.startsWith("-")) {
        // New array item
        if (currentItem) {
          result.push(currentItem);
        }
        currentItem = {};

        // Check if value is inline
        const value = trimmed.slice(1).trim();
        if (value.includes(":")) {
          const [key, ...valueParts] = value.split(":");
          currentItem[key.trim()] = this.parseYAMLValue(valueParts.join(":").trim());
        }
      } else if (currentItem && trimmed.includes(":")) {
        // Property of current item
        const [key, ...valueParts] = trimmed.split(":");
        const value = valueParts.join(":").trim();

        if (value.startsWith("[")) {
          // Array value
          currentItem[key.trim()] = this.parseYAMLArrayValue(value);
        } else if (value.startsWith("{")) {
          // Object value
          currentItem[key.trim()] = JSON.parse(value);
        } else {
          currentItem[key.trim()] = this.parseYAMLValue(value);
        }
      }
    }

    if (currentItem) {
      result.push(currentItem);
    }

    return result;
  }

  /**
   * Parse a YAML array value [1, 2, 3]
   */
  private parseYAMLArrayValue(value: string): any[] {
    try {
      return JSON.parse(value);
    } catch {
      // Fallback: split by comma
      return value
        .slice(1, -1) // Remove [ ]
        .split(",")
        .map((v) => this.parseYAMLValue(v.trim()));
    }
  }

  /**
   * Parse YAML value (number, boolean, string)
   */
  private parseYAMLValue(value: string): any {
    if (value === "true") return true;
    if (value === "false") return false;
    if (value === "null" || value === "") return null;

    // Try to parse as number
    const num = Number(value);
    if (!isNaN(num) && value !== "") return num;

    // String
    return value;
  }
}
