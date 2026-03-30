'use client'

import { useState, useEffect, useCallback } from 'react'
import type { Agent } from '@/types/agent'

const POLL_MS = 5_000

export function useAgentSwarm() {
  const [agents, setAgents]   = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState<string | null>(null)

  const fetchAgents = useCallback(async () => {
    try {
      const res = await fetch('/api/agents', { next: { revalidate: 0 } })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setAgents(data.agents ?? [])
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchAgents()
    const timer = setInterval(fetchAgents, POLL_MS)
    return () => clearInterval(timer)
  }, [fetchAgents])

  return { agents, loading, error, refetch: fetchAgents }
}
