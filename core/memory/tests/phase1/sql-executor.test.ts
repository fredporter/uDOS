import fs from 'fs'
import os from 'os'
import path from 'path'
import { DocumentRunner } from '../../../src/runtime/document-runner'

describe('Phase 1D SQLite executor', () => {
  let dbPath: string
  let tempDir: string

  beforeAll(async () => {
    tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'udos-phase1-'))
    dbPath = path.join(tempDir, 'phase1-sqlite.db')

    const initSqlJs = (await import('sql.js')).default
    const distDir = path.join(process.cwd(), 'node_modules', 'sql.js', 'dist')
    const SQL = await initSqlJs({
      locateFile: (filename: string) => path.join(distDir, filename),
    })

    const db = new SQL.Database()
    db.exec(`
      CREATE TABLE heroes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        power INTEGER NOT NULL
      )
    `)
    const insert = db.prepare('INSERT INTO heroes (name, power) VALUES (?, ?)')
    insert.run(['Nova', 9001])
    insert.free()

    const data = db.export()
    fs.writeFileSync(dbPath, Buffer.from(data))
    db.close()
  })

  afterAll(() => {
    try {
      fs.rmSync(tempDir, { recursive: true, force: true })
    } catch {
      // ignore cleanup errors
    }
  })

  it('runs a read-only query and saves the rows into state', async () => {
    const markdown = `
---
title: Hero lookup
id: hero-lookup
---
## Hero lookup
\`\`\`sql
path = ${dbPath}
query = SELECT name, power FROM heroes WHERE id = 1
as = heroQuery
\`\`\`
\`\`\`panel
Hero: $heroQuery.0.name ($heroQuery.0.power)
\`\`\`
`

    const runner = new DocumentRunner()
    const result = await runner.run(markdown)

    expect(result.success).toBe(true)
    expect(runner.getState().heroQuery?.[0]?.name).toBe('Nova')
    expect(runner.getState().heroQuery?.[0]?.power).toBe(9001)
    expect(result.aggregatedOutput).toContain('Hero:')
  })
})
