/**
 * Tests for lean TypeScript runtime
 * Using example-script.md as test case
 */

jest.mock('marked', () => ({
  marked: jest.fn(() => ''),
}))

import { Runtime, MarkdownParser, StateManager } from '../src/index'

describe('StateManager', () => {
  let state: StateManager

  beforeEach(() => {
    state = new StateManager()
  })

  test('set and get simple values', () => {
    state.set('name', 'Alice')
    expect(state.get('name')).toBe('Alice')
  })

  test('set and get nested values', () => {
    state.set('player', { name: 'Alice', pos: { x: 10, y: 20 } })
    expect(state.get('player.name')).toBe('Alice')
    expect(state.get('player.pos.x')).toBe(10)
  })

  test('set and get array values', () => {
    state.set('items', [{ id: 1, name: 'sword' }, { id: 2, name: 'shield' }])
    expect(state.get('items[0].name')).toBe('sword')
    expect(state.get('items[1].id')).toBe(2)
  })

  test('increment numeric values', () => {
    state.set('count', 5)
    state.increment('count', 3)
    expect(state.get('count')).toBe(8)
  })

  test('decrement numeric values', () => {
    state.set('count', 10)
    state.decrement('count', 2)
    expect(state.get('count')).toBe(8)
  })

  test('toggle boolean values', () => {
    state.set('flag', false)
    state.toggle('flag')
    expect(state.get('flag')).toBe(true)
    state.toggle('flag')
    expect(state.get('flag')).toBe(false)
  })

  test('interpolate simple variables', () => {
    state.set('name', 'Alice')
    const result = state.interpolate('Hello $name!')
    expect(result).toBe('Hello Alice!')
  })

  test('interpolate nested variables', () => {
    state.set('player', { name: 'Alice', pos: { tile: 42 } })
    const result = state.interpolate('You are at $player.pos.tile as $player.name')
    expect(result).toBe('You are at 42 as Alice')
  })

  test('interpolate array access', () => {
    state.set('items', ['sword', 'shield', 'potion'])
    const result = state.interpolate('First item: $items[0]')
    expect(result).toBe('First item: sword')
  })

  test('watch for changes', () => {
    const callback = jest.fn()
    state.watch('count', callback)
    state.set('count', 5)
    expect(callback).toHaveBeenCalledWith(5)
  })

  test('merge partial state', () => {
    state.setAll({ a: 1, b: 2 })
    state.merge({ b: 20, c: 30 })
    expect(state.getAll()).toEqual({ a: 1, b: 20, c: 30 })
  })
})

describe('MarkdownParser', () => {
  test('parse basic markdown with frontmatter', () => {
    const markdown = `---
title: Test Script
id: test-script
---

## Section 1
Content here

\`\`\`state
$player = { "name": "Alice" }
\`\`\`
`
    const doc = MarkdownParser.parse(markdown)
    expect(doc.frontmatter.title).toBe('Test Script')
    expect(doc.sections.length).toBeGreaterThan(0)
  })

  test('identify runtime blocks', () => {
    const markdown = `---
title: Test
---

## Test
\`\`\`state
$x = 1
\`\`\`

\`\`\`form
field: name
\`\`\`

\`\`\`nav
choice: "Option 1"
\`\`\`
`
    const doc = MarkdownParser.parse(markdown)
    const section = doc.sections[0]
    const blockTypes = section.blocks.map(b => b.type)
    expect(blockTypes).toContain('state')
    expect(blockTypes).toContain('form')
    expect(blockTypes).toContain('nav')
  })

  test('parse multiple sections', () => {
    const markdown = `---
title: Test
---

## First Section
Content 1

## Second Section
Content 2

## Third Section
Content 3
`
    const doc = MarkdownParser.parse(markdown)
    expect(doc.sections.length).toBe(3)
    expect(doc.sections[0].title).toBe('First Section')
    expect(doc.sections[2].title).toBe('Third Section')
  })
})

describe('Runtime', () => {
  let runtime: Runtime

  beforeEach(() => {
    runtime = new Runtime({ allowScripts: false })
  })

  test('load and parse markdown', () => {
    const markdown = `---
title: Test Script
---

## Start
Hello world
`
    runtime.load(markdown)
    const doc = runtime.getDocument()
    expect(doc).not.toBeNull()
    expect(doc?.frontmatter.title).toBe('Test Script')
  })

  test('execute state initialization', async () => {
    const markdown = `---
title: Test
---

## Start
\`\`\`state
$player = { "name": "Alice", "coins": 10 }
$world = { "time": "morning" }
\`\`\`
`
    runtime.load(markdown)
    const doc = runtime.getDocument()
    if (doc) {
      await runtime.execute(doc.sections[0].id)
      const state = runtime.getState()
      expect(state.player.name).toBe('Alice')
      expect(state.player.coins).toBe(10)
      expect(state.world.time).toBe('morning')
    }
  })

  test('execute set operations', async () => {
    const markdown = `---
title: Test
---

## Start
\`\`\`state
$count = 0
\`\`\`

\`\`\`set
inc $count 5
\`\`\`
`
    runtime.load(markdown)
    const doc = runtime.getDocument()
    if (doc) {
      await runtime.execute(doc.sections[0].id)
      const state = runtime.getState()
      expect(state.count).toBe(5)
    }
  })

  test('execute panel with interpolation', async () => {
    const markdown = `---
title: Test
---

## Start
\`\`\`state
$player = { "name": "Alice" }
\`\`\`

\`\`\`panel
Welcome, $player.name!
\`\`\`
`
    runtime.load(markdown)
    const doc = runtime.getDocument()
    if (doc) {
      const result = await runtime.execute(doc.sections[0].id)
      expect(result.output).toContain('Welcome, Alice!')
    }
  })

  test('execute script block when enabled', async () => {
    runtime = new Runtime({ allowScripts: true })
    const markdown = `---
title: Script Test
---

## Start
\`\`\`script
helper.setState('game.score', 10)
return 'score:' + helper.getState('game.score')
\`\`\`
`
    runtime.load(markdown)
    const doc = runtime.getDocument()
    if (doc) {
      const result = await runtime.execute(doc.sections[0].id)
      expect(result.success).toBe(true)
      expect(result.output?.trim()).toBe('score:10')
      const state = runtime.getState()
      expect(state.game.score).toBe(10)
    }
  })

  test('script block rejected when disabled', async () => {
    runtime = new Runtime({ allowScripts: false })
    const markdown = `---
title: Script Fail
---

## Start
\`\`\`script
helper.setState('game.score', 5)
\`\`\`
`
    runtime.load(markdown)
    const doc = runtime.getDocument()
    if (doc) {
      const result = await runtime.execute(doc.sections[0].id)
      expect(result.success).toBe(false)
      expect(result.error).toContain('Script blocks are disabled')
    }
  })

  test('get and set state directly', () => {
    runtime.setState({ x: 1, y: 2 })
    const state = runtime.getState()
    expect(state.x).toBe(1)
    expect(state.y).toBe(2)
  })
})

describe('Integration: Example Script Features', () => {
  test('complete script with state, form, nav, panels', async () => {
    const markdown = `---
title: Example Script
id: example
---

## Start
\`\`\`state
$player = { "name": "Traveller", "coins": 100, "inventory": [] }
$world = { "time": "morning", "location": "village" }
\`\`\`

Welcome to the world!

## Village
You are in the village. Time: \\\`$world.time\\\`

\`\`\`nav
choice: "Go to forest"
  when: $player.coins >= 50
choice: "Rest"
\`\`\`
`

    const runtime = new Runtime()
    runtime.load(markdown)
    const doc = runtime.getDocument()

    expect(doc).not.toBeNull()
    if (doc) {
      expect(doc.sections.length).toBeGreaterThanOrEqual(2)
      // Execute the first section to initialize state
      await runtime.execute(doc.sections[0].id)
      const state = runtime.getState()
      expect(state.player.coins).toBe(100)
      expect(state.world.time).toBe('morning')
    }
  })
})

describe('Executors: Block Execution', () => {
  let runtime: Runtime

  beforeEach(() => {
    runtime = new Runtime()
  })

  test('StateExecutor initializes state', async () => {
    const markdown = `---
title: Test
---

## Start
\`\`\`state
$x = 10
$name = "Alice"
$obj = { "key": "value" }
\`\`\`
`
    runtime.load(markdown)
    const doc = runtime.getDocument()
    if (doc) {
      await runtime.execute(doc.sections[0].id)
      const state = runtime.getState()
      expect(state.x).toBe(10)
      expect(state.name).toBe('Alice')
      expect(state.obj.key).toBe('value')
    }
  })

  test('SetExecutor mutates state', async () => {
    const markdown = `---
title: Test
---

## Start
\`\`\`state
$coins = 0
$active = false
\`\`\`

\`\`\`set
set $coins 50
toggle $active
\`\`\`
`
    runtime.load(markdown)
    const doc = runtime.getDocument()
    if (doc) {
      await runtime.execute(doc.sections[0].id)
      const state = runtime.getState()
      expect(state.coins).toBe(50)
      expect(state.active).toBe(true)
    }
  })

  test('PanelExecutor renders with interpolation', async () => {
    const markdown = `---
title: Test
---

## Start
\`\`\`state
$player = { "name": "Hero", "level": 5 }
\`\`\`

\`\`\`panel
Player: $player.name
Level: $player.level
\`\`\`
`
    runtime.load(markdown)
    const doc = runtime.getDocument()
    if (doc) {
      const result = await runtime.execute(doc.sections[0].id)
      expect(result.output).toContain('Player: Hero')
      expect(result.output).toContain('Level: 5')
    }
  })

  test('FormExecutor parses form fields', async () => {
    const markdown = `---
title: Test
---

## Start
\`\`\`form
username: "Enter your name"
  type: text
  required: true
password: "Enter password"
  type: password
\`\`\`
`
    runtime.load(markdown)
    const doc = runtime.getDocument()
    if (doc) {
      const result = await runtime.execute(doc.sections[0].id)
      expect(result.formFields).toBeDefined()
      expect(result.formFields?.length).toBeGreaterThan(0)
    }
  })

  test('NavigationExecutor parses choices with conditions', async () => {
    const markdown = `---
title: Test
---

## Start
\`\`\`state
$has_key = true
$coins = 100
\`\`\`

\`\`\`nav
choice: "Unlock door"
  when: $has_key == true
choice: "Buy key"
  when: $coins >= 50
choice: "Leave"
\`\`\`
`
    runtime.load(markdown)
    const doc = runtime.getDocument()
    if (doc) {
      const result = await runtime.execute(doc.sections[0].id)
      expect(result.choices).toBeDefined()
      if (result.choices) {
        // First choice should be available
        expect(result.choices[0].available).toBe(true)
        // Second choice should be available
        expect(result.choices[1].available).toBe(true)
      }
    }
  })

  test('MapExecutor renders viewport with sprites', async () => {
    const markdown = `---
title: Test
---

## Start
\`\`\`state
$player = { "x": 5, "y": 3 }
\`\`\`

\`\`\`map
width: 10
height: 8
sprite: "@"
  x: $player.x
  y: $player.y
\`\`\`
`
    runtime.load(markdown)
    const doc = runtime.getDocument()
    if (doc) {
      const result = await runtime.execute(doc.sections[0].id)
      expect(result.output).toBeDefined()
      expect(result.mapConfig).toBeDefined()
    }
  })

  test('Increment and decrement operations', async () => {
    const markdown = `---
title: Test
---

## Start
\`\`\`state
$count = 0
$health = 100
\`\`\`

\`\`\`set
inc $count 5
dec $health 10
inc $count 3
\`\`\`
`
    runtime.load(markdown)
    const doc = runtime.getDocument()
    if (doc) {
      await runtime.execute(doc.sections[0].id)
      const state = runtime.getState()
      expect(state.count).toBe(8)
      expect(state.health).toBe(90)
    }
  })

  test('Nested state mutations', async () => {
    const markdown = `---
title: Test
---

## Start
\`\`\`state
$player = { "inventory": { "gold": 0 } }
\`\`\`

\`\`\`set
set $player.inventory.gold 100
\`\`\`
`
    runtime.load(markdown)
    const doc = runtime.getDocument()
    if (doc) {
      await runtime.execute(doc.sections[0].id)
      const state = runtime.getState()
      expect(state.player.inventory.gold).toBe(100)
    }
  })
})
