import fs from 'fs'
import path from 'path'
import { RuntimeBlock, ExecutionContext, ExecutorResult, RuntimeValue } from '../types'
import { BaseExecutor } from './base'

type SqlValue = string | number | Uint8Array | null

export class SqlExecutor extends BaseExecutor {
  private betterSqliteModule?: any | null

  async execute(block: RuntimeBlock, context: ExecutionContext): Promise<ExecutorResult> {
    const config = this.parseKeyValues(block.content)
    const rawQuery = config.query

    if (!rawQuery) {
      return {
        success: false,
        error: 'SqlExecutor error: missing "query" definition',
      }
    }

    const query = this.interpolate(rawQuery, context.state).trim()
    if (!query) {
      return {
        success: false,
        error: 'SqlExecutor error: query resolved to an empty string',
      }
    }

    if (!/^(select|pragma)/i.test(query)) {
      return {
        success: false,
        error: 'SqlExecutor error: only read-only SELECT/PRAGMA statements are allowed',
      }
    }

    const rawPath = config.path || config.db || ':memory:'
    const dbPath = this.interpolate(rawPath, context.state)
    const params = this.parseParams(config.params, context.state)
    const alias = config.as || '__sqlResult'

    try {
      const rows = await this.executeQuery(dbPath, query, params)
      context.state[alias] = rows
      return {
        success: true,
        output: `SQL query returned ${rows.length} row(s)`,
        stateChanges: { [alias]: rows },
        rows,
      }
    } catch (error) {
      return {
        success: false,
        error: `SqlExecutor error: ${error instanceof Error ? error.message : String(error)}`,
      }
    }
  }

  private async executeQuery(dbPath: string, query: string, params: RuntimeValue[]): Promise<any[]> {
    const better = await this.loadBetterSqlite()
    if (better) {
      return this.runBetterSqlite(better, dbPath, query, params)
    }
    return this.runSqlJs(dbPath, query, params)
  }

  private async loadBetterSqlite(): Promise<any | null> {
    if (this.betterSqliteModule !== undefined) {
      return this.betterSqliteModule
    }

    try {
      const mod = await import('better-sqlite3')
      this.betterSqliteModule = mod.default ?? mod
    } catch {
      this.betterSqliteModule = null
    }

    return this.betterSqliteModule
  }

  private runBetterSqlite(Database: any, dbPath: string, query: string, params: RuntimeValue[]): any[] {
    const db = new Database(dbPath, { readonly: true })
    try {
      const statement = db.prepare(query)
      const rows = params.length ? statement.all(...params) : statement.all()
      return rows
    } finally {
      db.close()
    }
  }

  private async runSqlJs(dbPath: string, query: string, params: RuntimeValue[]): Promise<any[]> {
    const initSqlJs = (await import('sql.js')).default
    const distDir = path.join(process.cwd(), 'node_modules', 'sql.js', 'dist')
    const SQL = await initSqlJs({
      locateFile: (filename: string) => path.join(distDir, filename),
    })

    const buffer = dbPath === ':memory:' ? undefined : fs.readFileSync(dbPath)
    const db = buffer ? new SQL.Database(buffer) : new SQL.Database()
    try {
      const statement = db.prepare(query)
      if (params.length) {
      const normalized = this.normalizeSqlJsParams(params)
      if (normalized.length) {
        statement.bind(normalized)
      }
      }

      const rows: any[] = []
      while (statement.step()) {
        rows.push(statement.getAsObject())
      }

      statement.free()
      return rows
    } finally {
      db.close()
    }
  }

  private normalizeSqlJsParams(params: RuntimeValue[]): SqlValue[] {
    return params.map(value => {
      if (value === null || value === undefined) {
        return null
      }
      if (typeof value === 'boolean') {
        return value ? 1 : 0
      }
      return value
    })
  }
}
