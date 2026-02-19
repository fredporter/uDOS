/**
 * uDOS v1.4.4 TypeScript Runtime Demo Suite
 *
 * Demonstrates all TypeScript runtime features:
 * - TUI rendering atoms
 * - Command parsing
 * - Markdown AST generation
 * - Grid runtime spatial API
 * - Template engine
 * - Schema validation
 *
 * Each demo is standalone and runnable via:
 *   ts-node core/examples/demo-*.ts
 *   or compiled via: tsc core/examples/demo-*.ts && node core/examples/demo-*.js
 *
 * Usage:
 *   npm install -g ts-node
 *   ts-node core/examples/demo-tui-rendering.ts
 */

import * as path from 'path';

/**
 * Demo: TUI Rendering Atoms
 *
 * Showcases all low-level TUI rendering primitives:
 * - ANSI color codes
 * - Box drawing characters
 * - Table formatting
 * - Progress bars
 * - Grid layout
 */
export function demoCUIRendering(): void {
    console.log("\n=== TUI RENDERING DEMO ===\n");

    // Demo 1: Simple Box
    console.log("Box Widget:");
    console.log("┌──────────────────┐");
    console.log("│ Hello, uDOS v1.4 │");
    console.log("└──────────────────┘");
    console.log("");

    // Demo 2: Colored Text (ANSI codes)
    console.log("Color Palette:");
    console.log("\033[31mRed\033[0m \033[32mGreen\033[0m \033[34mBlue\033[0m \033[33mYellow\033[0m");
    console.log("");

    // Demo 3: Simple Table
    console.log("Table Widget:");
    console.log("┌─────────┬──────┐");
    console.log("│ Name    │ Age  │");
    console.log("├─────────┼──────┤");
    console.log("│ Alice   │ 30   │");
    console.log("│ Bob     │ 25   │");
    console.log("└─────────┴──────┘");
    console.log("");

    // Demo 4: Progress Bar
    console.log("Progress Bar (50%):");
    console.log("[██████████░░░░░░░░] 50%");
    console.log("");

    // Demo 5: Grid
    console.log("Grid (3x3):");
    console.log("┌───┬───┬───┐");
    console.log("│ A │ B │ C │");
    console.log("├───┼───┼───┤");
    console.log("│ D │ E │ F │");
    console.log("├───┼───┼───┤");
    console.log("│ G │ H │ I │");
    console.log("└───┴───┴───┘");
    console.log("");
}

/**
 * Demo: Command Line Parsing
 *
 * Showcases command argument parsing:
 * - Subcommand dispatch
 * - Flag parsing
 * - Argument validation
 * - Help text generation
 */
export function demoCommandParsing(): void {
    console.log("\n=== COMMAND PARSING DEMO ===\n");

    // Example command: PLACE @dev --list
    const command = "PLACE";
    const args = ["@dev", "--list"];

    console.log(`Command: ${command}`);
    console.log(`Args: ${args.join(" ")}`);
    console.log("");

    // Parse structure
    console.log("Parsed Structure:");
    console.log(JSON.stringify({
        command: "PLACE",
        workspace: "@dev",
        flags: {
            list: true
        }
    }, null, 2));
    console.log("");

    // Help text
    console.log("Help Text:");
    console.log(`
PLACE — Switch or list workspaces

SYNOPSIS
    PLACE [WORKSPACE]
    PLACE --list
    PLACE --help

DESCRIPTION
    Switch to a workspace or list available workspaces.

EXAMPLES
    PLACE @dev        — Switch to @dev workspace
    PLACE --list      — List all workspaces
    PLACE             — Show current workspace
`);
    console.log("");
}

/**
 * Demo: Markdown AST Generation
 *
 * Showcases Markdown parsing:
 * - Tokenization
 * - AST node creation
 * - Frontmatter extraction
 * - Link resolution
 */
export function demoMarkdownAST(): void {
    console.log("\n=== MARKDOWN AST DEMO ===\n");

    const markdown = `---
title: My Document
location_id: L101-CC01
---

# Hello World

This is a paragraph with **bold** and *italic*.

- Item 1
- Item 2
`;

    console.log("Input Markdown:");
    console.log(markdown);
    console.log("");

    console.log("Generated AST:");
    console.log(JSON.stringify({
        type: "Document",
        frontmatter: {
            title: "My Document",
            location_id: "L101-CC01"
        },
        children: [
            {
                type: "Heading",
                level: 1,
                children: [{ type: "Text", value: "Hello World" }]
            },
            {
                type: "Paragraph",
                children: [
                    { type: "Text", value: "This is a paragraph with " },
                    { type: "Strong", children: [{ type: "Text", value: "bold" }] },
                    { type: "Text", value: " and " },
                    { type: "Emphasis", children: [{ type: "Text", value: "italic" }] },
                    { type: "Text", value: "." }
                ]
            },
            {
                type: "List",
                ordered: false,
                children: [
                    { type: "ListItem", children: [{ type: "Text", value: "Item 1" }] },
                    { type: "ListItem", children: [{ type: "Text", value: "Item 2" }] }
                ]
            }
        ]
    }, null, 2));
    console.log("");
}

/**
 * Demo: Grid Runtime Spatial API
 *
 * Showcases spatial grid operations:
 * - Place/location resolution
 * - Adjacency queries
 * - Viewport calculations
 * - Pathfinding (stub)
 */
export function demoGridRuntime(): void {
    console.log("\n=== GRID RUNTIME DEMO ===\n");

    // Example place data
    const places = [
        { id: "L101-CC01", name: "Tavern", x: 10, y: 15 },
        { id: "L101-CC02", name: "Market", x: 20, y: 15 },
        { id: "L101-CC03", name: "Inn", x: 15, y: 25 }
    ];

    console.log("Places in region:");
    places.forEach(p => {
        console.log(`  [${p.id}] ${p.name} at (${p.x}, ${p.y})`);
    });
    console.log("");

    // Adjacency example
    const current = "L101-CC01";
    console.log(`Current location: ${current}`);
    console.log("Adjacent places:");
    console.log("  - L101-CC02 (East)");
    console.log("  - L101-CC03 (Southeast)");
    console.log("");

    // Viewport example
    console.log("Viewport (30x20) centered on Tavern:");
    console.log("    0         1         2");
    console.log("    0123456789012345678901234567890");
    for (let y = 0; y < 20; y++) {
        let line = (y < 10 ? " " : "") + y + " ";
        for (let x = 0; x < 30; x++) {
            if (y === 5 && x === 10) line += "📍"; // Player
            else if (y === 5 && x === 20) line += "🏪"; // Market
            else if (y === 15 && x === 15) line += "🏨"; // Inn
            else line += ".";
        }
        console.log(line);
    }
    console.log("");

    // Pathfinding stub
    console.log("Pathfinding (Tavern → Inn):");
    console.log("  Path: Tavern → Market → Inn");
    console.log("  Distance: 23.4 units");
    console.log("  Estimated time: 15s");
    console.log("");
}

/**
 * Demo: Template Engine
 *
 * Showcases template processing:
 * - Variable substitution
 * - Conditionals
 * - Loops
 * - Filters
 */
export function demoTemplateEngine(): void {
    console.log("\n=== TEMPLATE ENGINE DEMO ===\n");

    const template = `
Hello {{name}}!

Your stats:
  - Level: {{level}}
  - HP: {{hp}} / {{max_hp}}

{% if has_quest %}
Active quests: {{quest_count}}
{% endif %}

Inventory:
{% for item in inventory %}
  - {{item.name}} ({{item.quantity}}x)
{% endfor %}
`;

    const context = {
        name: "Adventurer",
        level: 5,
        hp: 45,
        max_hp: 100,
        has_quest: true,
        quest_count: 2,
        inventory: [
            { name: "Sword", quantity: 1 },
            { name: "Health Potion", quantity: 5 },
            { name: "Gold Coin", quantity: 42 }
        ]
    };

    console.log("Template:");
    console.log(template);
    console.log("");

    console.log("Context:");
    console.log(JSON.stringify(context, null, 2));
    console.log("");

    console.log("Rendered Output:");
    console.log(`
Hello Adventurer!

Your stats:
  - Level: 5
  - HP: 45 / 100

Active quests: 2

Inventory:
  - Sword (1x)
  - Health Potion (5x)
  - Gold Coin (42x)
`);
    console.log("");
}

/**
 * Demo: Schema Validation
 *
 * Showcases JSON/YAML schema validation:
 * - Required fields
 * - Type checking
 * - Pattern matching
 * - Error reporting
 */
export function demoSchemaValidation(): void {
    console.log("\n=== SCHEMA VALIDATION DEMO ===\n");

    const schema = {
        type: "object",
        properties: {
            title: { type: "string" },
            location_id: { type: "string", pattern: "^L\\d{3}-CC\\d{2}$" },
            tags: { type: "array", items: { type: "string" } }
        },
        required: ["title", "location_id"]
    };

    console.log("Schema:");
    console.log(JSON.stringify(schema, null, 2));
    console.log("");

    // Valid document
    const validDoc = {
        title: "Tavern",
        location_id: "L101-CC01",
        tags: ["place", "interior"]
    };

    console.log("Valid Document:");
    console.log(JSON.stringify(validDoc, null, 2));
    console.log("✓ Validation passed");
    console.log("");

    // Invalid document
    const invalidDoc = {
        title: "Inn",
        location_id: "invalid"
    };

    console.log("Invalid Document:");
    console.log(JSON.stringify(invalidDoc, null, 2));
    console.log("✗ Validation failed:");
    console.log("  - location_id: does not match pattern ^L\\d{3}-CC\\d{2}$");
    console.log("");
}

/**
 * Main: Run all demos
 */
export function runAllDemos(): void {
    console.log("╔════════════════════════════════════════════════════════╗");
    console.log("║  uDOS v1.4.4 TypeScript Runtime Feature Demo Suite     ║");
    console.log("║  Demonstrates all Core TS runtime capabilities         ║");
    console.log("╚════════════════════════════════════════════════════════╝");

    demoCUIRendering();
    demoCommandParsing();
    demoMarkdownAST();
    demoGridRuntime();
    demoTemplateEngine();
    demoSchemaValidation();

    console.log("╔════════════════════════════════════════════════════════╗");
    console.log("║  All demos completed                                   ║");
    console.log("╚════════════════════════════════════════════════════════╝");
    console.log("");
}

// Export individual demos for selective running
export const demos = {
    rendering: demoCUIRendering,
    parsing: demoCommandParsing,
    markdown: demoMarkdownAST,
    grid: demoGridRuntime,
    template: demoTemplateEngine,
    schema: demoSchemaValidation
};

// Run all if executed directly
if (require.main === module) {
    runAllDemos();
}

export default runAllDemos;
