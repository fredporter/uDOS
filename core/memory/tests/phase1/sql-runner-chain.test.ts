import { DocumentRunner } from '../../../src/runtime/document-runner'
import { createHeroDb } from './db-utils'

describe('Phase 1 SQL → runner mutation chain', () => {
  it('runs SQL, stores rows, and surfaces alias via aggregated output/state', async () => {
    const { dbPath, cleanup } = await createHeroDb()
    const markdown = `
---
title: Runner SQL chain
id: runner-sql-chain
---
## Runner SQL chain
\`\`\`state
$player.level = 5
\`\`\`
\`\`\`sql
path = ${dbPath}
query = SELECT name, power, level FROM heroes WHERE level >= $player.level
as = heroStack
\`\`\`
\`\`\`panel
Consumed hero: $heroStack.0.name ($heroStack.0.power)
\`\`\`
`

    const runner = new DocumentRunner()
    const result = await runner.run(markdown)
    cleanup()

    expect(result.success).toBe(true)
    expect(result.aggregatedOutput).toContain('Consumed hero')
    expect(result.history.length).toBeGreaterThan(0)
    expect(result.history[0].output).toContain('SQL query returned')
    expect(runner.getState().heroStack?.length).toBeGreaterThan(0)
    expect(runner.getState().heroStack?.[0]?.name).toBe('Nova')
  })
})
