import fs from 'fs'
import os from 'os'
import path from 'path'

export interface HeroRecord {
  name: string
  power: number
  level: number
}

export interface TestDatabase {
  dbPath: string
  cleanup(): void
}

export async function createHeroDb(records: HeroRecord[] = createDefaultHeroes()): Promise<TestDatabase> {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'udos-phase1-'))
  const dbPath = path.join(tempDir, 'phase1-heroes.db')
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
      power INTEGER NOT NULL,
      level INTEGER NOT NULL
    )
  `)
  const insert = db.prepare('INSERT INTO heroes (name, power, level) VALUES (?, ?, ?)')
  for (const record of records) {
    insert.run([record.name, record.power, record.level])
  }
  insert.free()

  const data = db.export()
  fs.writeFileSync(dbPath, Buffer.from(data))
  db.close()

  return {
    dbPath,
    cleanup: () => {
      try {
        fs.rmSync(tempDir, { recursive: true, force: true })
      } catch {
        // best effort cleanup
      }
    },
  }
}

function createDefaultHeroes(): HeroRecord[] {
  return [
    { name: 'Nova', power: 9001, level: 10 },
    { name: 'Echo', power: 4200, level: 3 },
    { name: 'Riven', power: 11111, level: 12 },
  ]
}
