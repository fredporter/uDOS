/**
 * Phase 3B: Integration Test with Example Script
 * 
 * This test validates the runtime with a realistic markdown script
 * containing all 8 block types and complex state management.
 */

import { Runtime } from '../src/index';
import { readFileSync } from 'fs';
import { join } from 'path';

describe('Integration: Example Script', () => {
  let runtime: Runtime;

  beforeEach(() => {
    runtime = new Runtime();
  });

  // Helper to execute first section
  async function executeFirstSection(markdown: string) {
    runtime.load(markdown);
    const doc = runtime.getDocument();
    return runtime.execute(doc!.sections[0].id);
  }

  test('loads and parses example script with all features', () => {
    const scriptPath = join(__dirname, '../../dev/roadmap/example-script.md');
    const markdown = readFileSync(scriptPath, 'utf-8');

    runtime.load(markdown);
    const doc = runtime.getDocument();

    // Validate frontmatter
    expect(doc).toBeDefined();
    expect(doc!.frontmatter.title).toBe('Example Interactive Script');
    expect(doc!.frontmatter.id).toBe('example-script');
    expect(doc!.frontmatter.version).toBe('1.0');
    expect(doc!.frontmatter.runtime).toBe('udos-md-runtime');
    expect(doc!.frontmatter.mode).toBe('teletext');

    // Validate sections parsed
    expect(doc!.sections.length).toBeGreaterThan(0);
  });

  test('initializes complex state with objects and arrays', async () => {
    const markdown = `---
title: "State Test"
---

## State Test

\`\`\`state
$player = { name: "Hero", hp: 10, coins: 3 }
$inventory = [
  { id: "apple", label: "Apple", qty: 1 },
  { id: "sword", label: "Sword", qty: 1 }
]
$simple = 42
\`\`\`
`;

    runtime.load(markdown);
    const doc = runtime.getDocument();
    const result = await runtime.execute(doc!.sections[0].id);

    expect(result.success).toBe(true);
    const state = runtime.getState();
    expect(state.player).toEqual({ name: "Hero", hp: 10, coins: 3 });
    expect(state.inventory).toHaveLength(2);
    expect(state.simple).toBe(42);
  });

  test('executes set operations on nested state', async () => {
    const markdown = `---
title: "Mutation Test"
---

## Mutation Test

\`\`\`state
$player = { name: "Hero", hp: 10, coins: 3 }
\`\`\`

\`\`\`set
set $player.coins 50
inc $player.hp 5
\`\`\`
`;

    const result = await executeFirstSection(markdown);
    expect(result.success).toBe(true);

    const state = runtime.getState();
    expect(state.player.coins).toBe(50);
    expect(state.player.hp).toBe(15);
  });

  test('renders panel with variable interpolation', async () => {
    const markdown = `---
title: "Panel Test"
---

## Panel Test

\`\`\`state
$player = { name: "Hero", coins: 3 }
$location = "Village"
\`\`\`

\`\`\`panel
Welcome to $location, $player.name!
You have $player.coins coins.
\`\`\`
`;

    const result = await executeFirstSection(markdown);

    expect(result.success).toBe(true);
    expect(result.output).toContain('Welcome to Village, Hero!');
    expect(result.output).toContain('You have 3 coins.');
  });

  test('parses form with all field types', async () => {
    const markdown = `---
title: "Form Test"
---

## Form Test

\`\`\`form
field: text
var: $player.name
label: "Your name"
placeholder: "Enter name"
required: true

field: number
var: $player.age
label: "Your age"
default: 25

field: toggle
var: $settings.dark_mode
label: "Dark mode"

field: choice
var: $player.class
label: "Choose class"
options: ["Warrior", "Mage", "Rogue"]
\`\`\`
`;

    const result = await executeFirstSection(markdown);

    expect(result.success).toBe(true);
    expect(result.formFields).toBeDefined();
    expect(result.formFields).toHaveLength(4);
    
    // Validate field types
    const fields = result.formFields!;
    expect(fields[0].type).toBe('text');
    expect(fields[0].var).toBe('$player.name');
    expect(fields[0].required).toBe(true);
    
    expect(fields[1].type).toBe('number');
    expect(fields[1].default).toBe('25');
    
    expect(fields[2].type).toBe('toggle');
    expect(fields[3].type).toBe('choice');
  });

  test('parses navigation with conditional gates', async () => {
    const markdown = `---
title: "Nav Test"
---

## Nav Test

\`\`\`state
$player = { coins: 50, has_key: true }
\`\`\`

\`\`\`nav
choice: "Go to market"
target: "#market"

choice: "Buy potion (30 coins)"
target: "#buy-potion"
when: $player.coins >= 30

choice: "Locked door"
target: "#locked"
when: $player.has_key

choice: "Exit"
target: "#exit"
\`\`\`
`;

    const result = await executeFirstSection(markdown);

    expect(result.success).toBe(true);
    expect(result.choices).toBeDefined();
    expect(result.choices).toHaveLength(4);
    
    // All conditions should be met
    const choices = result.choices!;
    expect(choices[0].available).toBe(true);
    expect(choices[1].available).toBe(true); // has 50 coins
    expect(choices[2].available).toBe(true); // has key
    expect(choices[3].available).toBe(true);
  });

  test('evaluates if/else conditionals', async () => {
    const markdown = `---
title: "Conditional Test"
---

## Conditional Test

\`\`\`state
$player = { coins: 50 }
\`\`\`

\`\`\`if
$player.coins >= 30
\`\`\`

\`\`\`panel
You have enough coins!
\`\`\`

\`\`\`else
\`\`\`

\`\`\`panel
You need more coins.
\`\`\`
`;

    const result = await executeFirstSection(markdown);

    expect(result.success).toBe(true);
    expect(result.output).toContain('You have enough coins!');
    expect(result.output).not.toContain('You need more coins.');
  });

  test('renders map with viewport and sprites', async () => {
    const markdown = `---
title: "Map Test"
---

## Map Test

\`\`\`state
$player = { x: 5, y: 3 }
\`\`\`

\`\`\`map
width: 10
height: 8
viewport: true

sprite: player
ch: @
x: $player.x
y: $player.y

sprite: tree
ch: T
x: 3
y: 2

sprite: npc
ch: M
x: 7
y: 5
\`\`\`
`;

    const result = await executeFirstSection(markdown);

    expect(result.success).toBe(true);
    expect(result.mapConfig).toBeDefined();
    expect(result.mapConfig.width).toBe(10);
    expect(result.mapConfig.height).toBe(8);
    expect(result.mapConfig.sprites).toHaveLength(3);
    
    // Validate sprites
    const sprites = result.mapConfig.sprites;
    expect(sprites[0].ch).toBe('@');
    expect(sprites[0].x).toBe(5);
    expect(sprites[0].y).toBe(3);
  });

  test('full integration: state → mutations → conditionals → output', async () => {
    const markdown = `---
title: "Full Test"
---

## Game Start

\`\`\`state
$game = { score: 0, level: 1 }
$player = { name: "Hero", hp: 100 }
\`\`\`

\`\`\`set
inc $game.score 10
inc $player.hp 50
\`\`\`

\`\`\`if
$game.score >= 10
\`\`\`

\`\`\`panel
Great! $player.name scored $game.score points!
HP: $player.hp
\`\`\`

\`\`\`nav
choice: "Continue"
target: "#next"
when: $player.hp > 100

choice: "Rest"
target: "#rest"
\`\`\`
`;

    const result = await executeFirstSection(markdown);

    expect(result.success).toBe(true);
    
    // Validate state mutations
    const state = runtime.getState();
    expect(state.game).toEqual({ score: 10, level: 1 });
    expect(state.player.hp).toBe(150);
    
    // Validate output
    expect(result.output).toContain('Great! Hero scored 10 points!');
    expect(result.output).toContain('HP: 150');
    
    // Validate navigation
    expect(result.choices).toBeDefined();
    expect(result.choices![0].available).toBe(true); // hp > 100
  });

  test('handles empty sections gracefully', async () => {
    const markdown = `---
title: "Empty Test"
---

## Section 1

Some text here.

## Section 2

More text.
`;

    runtime.load(markdown);
    const doc = runtime.getDocument();
    const result = await runtime.execute(doc!.sections[0].id);

    expect(result.success).toBe(true);
    expect(doc!.sections).toHaveLength(2);
  });

  test('persists state across multiple sections', async () => {
    const markdown = `---
title: "Multi-Section Test"
---

## Section 1

\`\`\`state
$count = 0
\`\`\`

\`\`\`set
inc $count 5
\`\`\`

## Section 2

\`\`\`set
inc $count 10
\`\`\`

\`\`\`panel
Count is now: $count
\`\`\`
`;

    runtime.load(markdown);
    const doc = runtime.getDocument();
    
    // Execute section 1
    await runtime.execute(doc!.sections[0].id);
    // Execute section 2
    const result = await runtime.execute(doc!.sections[1].id);

    expect(result.success).toBe(true);
    const state = runtime.getState();
    expect(state.count).toBe(15); // 0 + 5 + 10
    expect(result.output).toContain('Count is now: 15');
  });
});
