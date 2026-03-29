'use client'

import { useState, useEffect, useCallback } from 'react'

export interface LogEntry {
  id?: string | number
  time: string
  agent: string
  level: 'info' | 'warn' | 'error' | 'success'
  msg: string
}

const POLL_MS = 5_000

const LEVEL_COLOUR: Record<string, string> = {
  info:    'var(--accent-cyan)',
  warn:    'var(--accent-amber)',
  error:   'var(--status-error)',
  success: 'var(--status-healthy)',
}

export function levelColour(level: string): string {
  return LEVEL_COLOUR[level] ?? 'var(--text-secondary)'
}

export function useLogs(maxEntries = 50) {
  const [logs, setLogs]     = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(true)

  const fetchLogs = useCallback(async () => {
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('token') ?? '' : ''
      const res = await fetch('/api/logs', {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        cache: 'no-store',
      })
      if (!res.ok) return
      const data = await res.json()
      const entries: LogEntry[] = Array.isArray(data) ? data : []
      setLogs(entries.slice(0, maxEntries))
    } catch {
      // keep stale data
    } finally {
      setLoading(false)
    }
  }, [maxEntries])

  useEffect(() => {
    fetchLogs()
    const t = setInterval(fetchLogs, POLL_MS)
    return () => clearInterval(t)
  }, [fetchLogs])

  return { logs, loading }
}
