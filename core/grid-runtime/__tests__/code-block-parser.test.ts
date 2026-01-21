/**
 * Phase 3 Test Suite: Code Block Parser
 * Tests for ExpressionEvaluator, CodeBlockParser, MarkdownCodeBlockExtractor
 * Total: 18+ test cases
 */

import { ExpressionEvaluator } from "../src/expression-evaluator";
import { CodeBlockParser, CodeBlock } from "../src/code-block-parser";
import { MarkdownCodeBlockExtractor } from "../src/markdown-extractor";

describe("Phase 3: Code Block Parser", () => {
  describe("ExpressionEvaluator", () => {
    let evaluator: ExpressionEvaluator;

    beforeEach(() => {
      evaluator = new ExpressionEvaluator({
        player: {
          name: "Hero",
          pos: {
            tile: "AA10",
          },
        },
        inventory: ["sword", "shield", "potion"],
        stats: {
          health: 100,
          mana: 50,
        },
      });
    });

    test("should evaluate simple variable reference", () => {
      const result = evaluator.evaluateVariable("$player.name");
      expect(result.type).toBe("variable");
      expect(result.value).toBe("Hero");
    });

    test("should evaluate nested object access", () => {
      const result = evaluator.evaluateVariable("$player.pos.tile");
      expect(result.type).toBe("variable");
      expect(result.value).toBe("AA10");
    });

    test("should evaluate array element access", () => {
      const result = evaluator.evaluateVariable("$inventory[0]");
      expect(result.type).toBe("variable");
      expect(result.value).toBe("sword");
    });

    test("should handle undefined variables", () => {
      const result = evaluator.evaluateVariable("$nonexistent");
      expect(result.type).toBe("variable");
      expect(result.value).toBeUndefined();
    });

    test("should interpolate text with variable substitution", () => {
      const text = "Player #{$player.name} is at #{$player.pos.tile}";
      const result = evaluator.interpolate(text);
      expect(result).toBe("Player Hero is at AA10");
    });

    test("should interpolate multiple variables in text", () => {
      const text =
        "Health: #{$stats.health}, Mana: #{$stats.mana}";
      const result = evaluator.interpolate(text);
      expect(result).toBe("Health: 100, Mana: 50");
    });

    test("should handle undefined variables in interpolation", () => {
      const text = "Location: #{$undefined}";
      const result = evaluator.interpolate(text);
      expect(result).toBe("Location: ");
    });

    test("should set and retrieve state", () => {
      evaluator.setState("newVar", "newValue");
      const result = evaluator.evaluateVariable("$newVar");
      expect(result.value).toBe("newValue");
    });
  });

  describe("CodeBlockParser", () => {
    let parser: CodeBlockParser;

    beforeEach(() => {
      parser = new CodeBlockParser();
    });

    test("should parse teletext block", () => {
      const block: CodeBlock = {
        type: "teletext",
        content: "🬀🬁🬂🬃\n████████\n🬪🬫🬬🬭",
      };

      const result = parser.parse(block);
      expect(result.type).toBe("teletext");
      expect((result as any).lines).toHaveLength(3);
      expect((result as any).width).toBeGreaterThan(0);
    });

    test("should parse grid block with location data", () => {
      const gridYAML = `
name: Enchanted Forest
layer: 300
startCell: AA10
cells:
  - address: AA10
    terrain: grass
  - address: AA11
    terrain: tree
`;

      const block: CodeBlock = {
        type: "grid",
        content: gridYAML,
      };

      const result = parser.parse(block);
      expect(result.type).toBe("grid");
      expect((result as any).location.name).toBe("Enchanted Forest");
      expect((result as any).location.layer).toBe(300);
      expect((result as any).location.startCell).toBe("AA10");
    });

    test("should parse tiles block with array of tile definitions", () => {
      const tilesYAML = `
- id: grass
  character: "."
  color: green
  layer: 299
- id: tree
  character: "T"
  color: darkgreen
  layer: 300
`;

      const block: CodeBlock = {
        type: "tiles",
        content: tilesYAML,
      };

      const result = parser.parse(block);
      expect(result.type).toBe("tiles");
      expect((result as any).tiles).toHaveLength(2);
      expect((result as any).tiles[0].id).toBe("grass");
    });

    test("should throw error for missing required fields in grid", () => {
      const block: CodeBlock = {
        type: "grid",
        content: "layer: 300",
      };

      expect(() => parser.parse(block)).toThrow("missing required 'name' field");
    });

    test("should throw error for non-array tiles block", () => {
      const block: CodeBlock = {
        type: "tiles",
        content: "key: value",
      };

      expect(() => parser.parse(block)).toThrow("must contain a YAML array");
    });

    test("should handle empty cells in grid", () => {
      const gridYAML = `
name: Test
layer: 300
startCell: AA10
cells: []
`;

      const block: CodeBlock = {
        type: "grid",
        content: gridYAML,
      };

      const result = parser.parse(block);
      expect((result as any).location.cells).toHaveLength(0);
    });

    test("should parse YAML numbers and booleans correctly", () => {
      const tilesYAML = `
- id: test
  character: "#"
  layer: 301
  color: red
`;

      const block: CodeBlock = {
        type: "tiles",
        content: tilesYAML,
      };

      const result = parser.parse(block);
      const tile = (result as any).tiles[0];
      expect(tile.layer).toBe(301);
      expect(typeof tile.layer).toBe("number");
    });
  });

  describe("MarkdownCodeBlockExtractor", () => {
    let extractor: MarkdownCodeBlockExtractor;

    beforeEach(() => {
      extractor = new MarkdownCodeBlockExtractor();
    });

    test("should extract all code blocks from markdown", () => {
      const markdown = `
# Test Document

\`\`\`teletext
Hello World
\`\`\`

Some text here.

\`\`\`grid location-name
name: Test
layer: 300
startCell: AA10
cells: []
\`\`\`

\`\`\`tiles
- id: test
  character: "#"
  color: red
  layer: 300
\`\`\`
`;

      const blocks = extractor.extractBlocks(markdown);
      expect(blocks).toHaveLength(3);
      expect(blocks[0].type).toBe("teletext");
      expect(blocks[1].type).toBe("grid");
      expect(blocks[2].type).toBe("tiles");
    });

    test("should extract blocks by type", () => {
      const markdown = `
\`\`\`teletext
Art 1
\`\`\`

\`\`\`teletext
Art 2
\`\`\`

\`\`\`grid
name: Test
layer: 300
startCell: AA10
cells: []
\`\`\`
`;

      const teletextBlocks = extractor.extractBlocksByType(markdown, "teletext");
      expect(teletextBlocks).toHaveLength(2);

      const gridBlocks = extractor.extractBlocksByType(markdown, "grid");
      expect(gridBlocks).toHaveLength(1);
    });

    test("should find first block of type", () => {
      const markdown = `
\`\`\`teletext
Content 1
\`\`\`

\`\`\`teletext
Content 2
\`\`\`
`;

      const block = extractor.extractFirstBlock(markdown, "teletext");
      expect(block).toBeDefined();
      expect(block?.content).toContain("Content 1");
    });

    test("should count blocks by type", () => {
      const markdown = `
\`\`\`teletext
Art
\`\`\`

\`\`\`grid
name: Test
layer: 300
startCell: AA10
cells: []
\`\`\`

\`\`\`tiles
- id: test
  character: "#"
  color: red
  layer: 300
\`\`\`
`;

      const counts = extractor.countBlocks(markdown);
      expect(counts.teletext).toBe(1);
      expect(counts.grid).toBe(1);
      expect(counts.tiles).toBe(1);
      expect(counts.total).toBe(3);
    });

    test("should validate required block types", () => {
      const markdown = `
\`\`\`teletext
Art
\`\`\`

\`\`\`grid
name: Test
layer: 300
startCell: AA10
cells: []
\`\`\`
`;

      const hasRequired = extractor.hasAllBlockTypes(markdown, [
        "teletext",
        "grid",
      ]);
      expect(hasRequired).toBe(true);

      const hasAll = extractor.hasAllBlockTypes(markdown, [
        "teletext",
        "grid",
        "tiles",
      ]);
      expect(hasAll).toBe(false);
    });

    test("should get block statistics", () => {
      const markdown = `
\`\`\`teletext
Short
\`\`\`

\`\`\`grid
name: Test
layer: 300
startCell: AA10
cells: []
\`\`\`

\`\`\`tiles
- id: test
  character: "#"
  color: red
  layer: 300
\`\`\`
`;

      const stats = extractor.getStatistics(markdown);
      expect(stats.totalBlocks).toBe(3);
      expect(stats.types.teletext).toBe(1);
      expect(stats.types.grid).toBe(1);
      expect(stats.types.tiles).toBe(1);
    });
  });

  describe("Integration Tests", () => {
    test("should parse example markdown with all components", () => {
      const markdown = `
# Game Location

\`\`\`grid location-forest
name: Enchanted Forest
layer: 300
startCell: AA10
cells:
  - address: AA10
    terrain: grass
  - address: AA11
    terrain: tree
\`\`\`

\`\`\`tiles
- id: grass
  character: "."
  color: green
  layer: 299
- id: tree
  character: "T"
  color: darkgreen
  layer: 300
\`\`\`

\`\`\`teletext
Welcome to the forest!
Beware of the trees.
\`\`\`
`;

      const extractor = new MarkdownCodeBlockExtractor();
      const blocks = extractor.extractBlocks(markdown);

      const parser = new CodeBlockParser();
      const parsed = blocks.map((b) => parser.parse(b));

      expect(parsed).toHaveLength(3);
      expect(parsed[0].type).toBe("grid");
      expect(parsed[1].type).toBe("tiles");
      expect(parsed[2].type).toBe("teletext");
    });

    test("should interpolate variables in extracted content", () => {
      const markdown = `
\`\`\`teletext
You are at #{$location}
Health: #{$health}
\`\`\`
`;

      const extractor = new MarkdownCodeBlockExtractor();
      const blocks = extractor.extractBlocks(markdown);

      const evaluator = new ExpressionEvaluator({
        location: "AA10",
        health: 100,
      });

      const result = evaluator.interpolate(blocks[0].content);
      expect(result).toContain("You are at AA10");
      expect(result).toContain("Health: 100");
    });
  });
});
