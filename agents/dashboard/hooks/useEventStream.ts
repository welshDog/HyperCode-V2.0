'use client'

import { useState, useEffect } from 'react'
import type { AgentEvent } from '@/types/event'

const MAX_EVENTS = 200

export function useEventStream() {
  const [events, setEvents]       = useState<AgentEvent[]>([])
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    const es = new EventSource('/api/events')

    es.onopen = () => setConnected(true)
    es.onerror = () => setConnected(false)

    es.addEventListener('agent_event', (e: MessageEvent) => {
      try {
        const ev: AgentEvent = JSON.parse(e.data)
        setEvents((prev) => [...prev.slice(-MAX_EVENTS + 1), ev])
      } catch {
        // malformed event — skip
      }
    })

    return () => es.close()
  }, [])

  return { events, connected }
}
