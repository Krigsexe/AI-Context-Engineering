import initSqlJs, { Database as SqlJsDatabase } from 'sql.js'
import path from 'path'
import fs from 'fs-extra'

export interface MemoryEntry {
  id?: number
  key: string
  value: string
  category: string
  timestamp: number
  confidence: number
}

export interface IndexEntry {
  id?: number
  filePath: string
  content: string
  embedding?: string
  lastModified: number
}

/**
 * SQLite database using sql.js (pure JavaScript, no native compilation)
 */
export class OdinDatabase {
  private db: SqlJsDatabase | null = null
  private dbPath: string
  private initialized: boolean = false

  constructor(dbPath: string) {
    this.dbPath = dbPath
    // Ensure directory exists
    fs.ensureDirSync(path.dirname(dbPath))
  }

  /**
   * Initialize the database (must be called before use)
   */
  async init(): Promise<void> {
    if (this.initialized) return

    const SQL = await initSqlJs()

    // Load existing database or create new one
    if (fs.existsSync(this.dbPath)) {
      const buffer = fs.readFileSync(this.dbPath)
      this.db = new SQL.Database(buffer)
    } else {
      this.db = new SQL.Database()
    }

    this.initTables()
    this.save()
    this.initialized = true
  }

  private initTables(): void {
    if (!this.db) throw new Error('Database not initialized')

    // Memory bank table
    this.db.run(`
      CREATE TABLE IF NOT EXISTS memory_bank (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT NOT NULL UNIQUE,
        value TEXT NOT NULL,
        category TEXT NOT NULL DEFAULT 'general',
        timestamp INTEGER NOT NULL,
        confidence REAL NOT NULL DEFAULT 1.0
      )
    `)

    // Semantic index table
    this.db.run(`
      CREATE TABLE IF NOT EXISTS semantic_index (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT NOT NULL UNIQUE,
        content TEXT NOT NULL,
        embedding TEXT,
        last_modified INTEGER NOT NULL
      )
    `)

    // Archives/sessions table
    this.db.run(`
      CREATE TABLE IF NOT EXISTS archives (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        data TEXT NOT NULL,
        timestamp INTEGER NOT NULL
      )
    `)

    // Create indices
    this.db.run('CREATE INDEX IF NOT EXISTS idx_memory_category ON memory_bank(category)')
    this.db.run('CREATE INDEX IF NOT EXISTS idx_memory_timestamp ON memory_bank(timestamp)')
    this.db.run('CREATE INDEX IF NOT EXISTS idx_index_path ON semantic_index(file_path)')
    this.db.run('CREATE INDEX IF NOT EXISTS idx_archive_session ON archives(session_id)')
  }

  /**
   * Save database to disk
   */
  private save(): void {
    if (!this.db) return
    const data = this.db.export()
    fs.writeFileSync(this.dbPath, Buffer.from(data))
  }

  /**
   * Store a memory entry
   */
  storeMemory(entry: Omit<MemoryEntry, 'id'>): void {
    if (!this.db) throw new Error('Database not initialized - call init() first')

    this.db.run(
      `INSERT OR REPLACE INTO memory_bank (key, value, category, timestamp, confidence)
       VALUES (?, ?, ?, ?, ?)`,
      [entry.key, entry.value, entry.category, entry.timestamp, entry.confidence]
    )
    this.save()
  }

  /**
   * Retrieve memory by key
   */
  getMemory(key: string): MemoryEntry | null {
    if (!this.db) throw new Error('Database not initialized - call init() first')

    const result = this.db.exec('SELECT * FROM memory_bank WHERE key = ?', [key])

    if (result.length === 0 || result[0].values.length === 0) {
      return null
    }

    const row = result[0].values[0]
    return {
      id: row[0] as number,
      key: row[1] as string,
      value: row[2] as string,
      category: row[3] as string,
      timestamp: row[4] as number,
      confidence: row[5] as number
    }
  }

  /**
   * Get all memories by category
   */
  getMemoriesByCategory(category: string): MemoryEntry[] {
    if (!this.db) throw new Error('Database not initialized - call init() first')

    const result = this.db.exec(
      'SELECT * FROM memory_bank WHERE category = ? ORDER BY timestamp DESC',
      [category]
    )

    if (result.length === 0) return []

    return result[0].values.map(row => ({
      id: row[0] as number,
      key: row[1] as string,
      value: row[2] as string,
      category: row[3] as string,
      timestamp: row[4] as number,
      confidence: row[5] as number
    }))
  }

  /**
   * Index a file for semantic search
   */
  indexFile(filePath: string, content: string, lastModified: number): void {
    if (!this.db) throw new Error('Database not initialized - call init() first')

    this.db.run(
      `INSERT OR REPLACE INTO semantic_index (file_path, content, last_modified)
       VALUES (?, ?, ?)`,
      [filePath, content, lastModified]
    )
    this.save()
  }

  /**
   * Archive a session event
   */
  archiveEvent(sessionId: string, eventType: string, eventData: any): void {
    if (!this.db) throw new Error('Database not initialized - call init() first')

    this.db.run(
      `INSERT INTO archives (session_id, event_type, data, timestamp)
       VALUES (?, ?, ?, ?)`,
      [sessionId, eventType, JSON.stringify(eventData), Date.now()]
    )
    this.save()
  }

  /**
   * Get session history
   */
  getSessionHistory(sessionId: string): any[] {
    if (!this.db) throw new Error('Database not initialized - call init() first')

    const result = this.db.exec(
      'SELECT * FROM archives WHERE session_id = ? ORDER BY timestamp ASC',
      [sessionId]
    )

    if (result.length === 0) return []

    return result[0].values.map(row => ({
      id: row[0],
      session_id: row[1],
      event_type: row[2],
      data: JSON.parse(row[3] as string),
      timestamp: row[4]
    }))
  }

  /**
   * Close database connection
   */
  close(): void {
    if (this.db) {
      this.save()
      this.db.close()
      this.db = null
      this.initialized = false
    }
  }

  /**
   * Get database statistics
   */
  getStats(): {
    memories: number
    indexed: number
    archives: number
  } {
    if (!this.db) throw new Error('Database not initialized - call init() first')

    const getCount = (table: string): number => {
      const result = this.db!.exec(`SELECT COUNT(*) as count FROM ${table}`)
      return result.length > 0 ? (result[0].values[0][0] as number) : 0
    }

    return {
      memories: getCount('memory_bank'),
      indexed: getCount('semantic_index'),
      archives: getCount('archives')
    }
  }
}

/**
 * Helper to create and initialize a database
 */
export async function createDatabase(dbPath: string): Promise<OdinDatabase> {
  const db = new OdinDatabase(dbPath)
  await db.init()
  return db
}
