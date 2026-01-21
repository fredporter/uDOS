/**
 * Phase 3 Integration Examples
 * Demonstrates ExpressionEvaluator, CodeBlockParser, and MarkdownCodeBlockExtractor working together
 */

import {
  ExpressionEvaluator,
  CodeBlockParser,
  MarkdownCodeBlockExtractor,
} from "../src/index";

/**
 * Example 1: Parse Location Definition
 * Load a markdown file with a grid block and parse it
 */
function exampleParseLocation() {
  const locationMarkdown = `
# Enchanted Forest

A mystical forest full of magic and mystery.

\`\`\`grid forest-location
name: Enchanted Forest
layer: 300
startCell: AA10
cells:
  - address: AA10
    terrain: grass
    sprites:
      - id: player-start
  - address: AB10
    terrain: tree
    objects:
      - type: ancient_oak
        props:
          age: 1000
  - address: AA11
    terrain: water
    objects:
      - type: fountain
        props:
          magical: true
\`\`\`

## Tile Definitions

\`\`\`tiles
- id: grass
  character: "."
  color: green
  layer: 299
- id: tree
  character: "T"
  color: darkgreen
  layer: 300
- id: water
  character: "~"
  color: blue
  layer: 298
\`\`\`
`;

  // Step 1: Extract blocks
  const extractor = new MarkdownCodeBlockExtractor();
  const blocks = extractor.extractBlocks(locationMarkdown);
  console.log(`Found ${blocks.length} code blocks`);

  // Step 2: Parse grid block
  const gridBlock = blocks.find((b) => b.type === "grid");
  if (gridBlock) {
    const parser = new CodeBlockParser();
    const gridData = parser.parse(gridBlock);
    console.log("Grid location:", (gridData as any).location.name);
    console.log("Cells:", (gridData as any).location.cells.length);
  }

  // Step 3: Parse tiles block
  const tilesBlock = blocks.find((b) => b.type === "tiles");
  if (tilesBlock) {
    const parser = new CodeBlockParser();
    const tilesData = parser.parse(tilesBlock);
    console.log("Tiles defined:", (tilesData as any).tiles.length);
  }
}

/**
 * Example 2: Variable Interpolation in Game Text
 * Use ExpressionEvaluator to substitute game variables
 */
function exampleVariableInterpolation() {
  // Create evaluator with game state
  const evaluator = new ExpressionEvaluator({
    player: {
      name: "Aragorn",
      pos: {
        tile: "AB11",
        layer: 300,
      },
      stats: {
        health: 85,
        mana: 50,
      },
    },
    world: {
      time: "sunset",
      location: "Enchanted Forest",
    },
  });

  // Interpolate text with variables
  const text1 = "Welcome, #{$player.name}!";
  const result1 = evaluator.interpolate(text1);
  console.log(result1); // "Welcome, Aragorn!"

  const text2 =
    "You are at #{$world.location} (#{$player.pos.tile}) at #{$world.time}";
  const result2 = evaluator.interpolate(text2);
  console.log(result2); // "You are at Enchanted Forest (AB11) at sunset"

  const text3 = "Health: #{$player.stats.health}/100, Mana: #{$player.stats.mana}";
  const result3 = evaluator.interpolate(text3);
  console.log(result3); // "Health: 85/100, Mana: 50"
}

/**
 * Example 3: Parse Teletext ASCII Art with Interpolation
 * Extract and display ASCII art blocks
 */
function exampleTeletextArt() {
  const artMarkdown = `
# Map Preview

\`\`\`teletext
╔════════════════════╗
║  #{$world.name}    ║
╠════════════════════╣
║  Start: #{$player.pos.tile}   ║
║  Layer: #{$player.pos.layer}   ║
╚════════════════════╝
\`\`\`
`;

  const evaluator = new ExpressionEvaluator({
    world: { name: "Enchanted Forest" },
    player: {
      pos: {
        tile: "AA10",
        layer: 300,
      },
    },
  });

  const extractor = new MarkdownCodeBlockExtractor();
  const blocks = extractor.extractBlocks(artMarkdown);

  for (const block of blocks) {
    if (block.type === "teletext") {
      const interpolated = evaluator.interpolate(block.content);
      console.log("Rendered ASCII art:");
      console.log(interpolated);
    }
  }
}

/**
 * Example 4: Multi-Block Processing Pipeline
 * Load complex markdown with all three block types
 */
function exampleCompleteWorkflow() {
  const complexMarkdown = `
# Complete Location Definition

## Forest Zone
Desc: A beautiful forest with ancient trees

\`\`\`grid forest
name: Ancient Forest
layer: 300
startCell: AA10
cells:
  - address: AA10
    terrain: grass
  - address: AB10
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

## Location Description

\`\`\`teletext
Welcome to #{$location.name}
Starting at #{$location.startCell}
\`\`\`
`;

  // Setup evaluator with context
  const evaluator = new ExpressionEvaluator({
    location: {
      name: "Ancient Forest",
      startCell: "AA10",
    },
  });

  // Extract all blocks
  const extractor = new MarkdownCodeBlockExtractor();
  const allBlocks = extractor.extractBlocks(complexMarkdown);

  // Process each block
  const parser = new CodeBlockParser();
  const results = allBlocks.map((block) => {
    if (block.type === "teletext") {
      // For teletext, interpolate the content
      return {
        type: block.type,
        content: evaluator.interpolate(block.content),
      };
    } else {
      // For grid/tiles, parse directly
      return parser.parse(block);
    }
  });

  console.log("Processed", results.length, "blocks");
  console.log("Types:", results.map((r) => r.type).join(", "));
}

/**
 * Example 5: Error Handling
 * Demonstrate graceful error handling
 */
function exampleErrorHandling() {
  const evaluator = new ExpressionEvaluator({
    exists: "value",
  });

  // Non-existent variable returns undefined
  const result1 = evaluator.evaluateVariable("$nonexistent");
  console.log("Undefined variable:", result1.value); // undefined

  // Interpolation with undefined becomes empty string
  const text = "Value: #{$nonexistent}";
  const result2 = evaluator.interpolate(text);
  console.log("Interpolated undefined:", `"${result2}"`); // "Value: "

  // Parser error handling
  const parser = new CodeBlockParser();
  try {
    parser.parse({
      type: "grid",
      content: "invalid: yaml",
    });
  } catch (e) {
    console.log("Parser error caught:", (e as Error).message);
  }
}

// Export examples for testing/documentation
export {
  exampleParseLocation,
  exampleVariableInterpolation,
  exampleTeletextArt,
  exampleCompleteWorkflow,
  exampleErrorHandling,
};
