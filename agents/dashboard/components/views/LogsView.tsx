'use client'

import React, { useRef, useEffect } from 'react'
import { useLogs, levelColour } from '@/hooks/useLogs'

export function LogsView(): React.JSX.Element {
  const { logs, loading } = useLogs(80)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (bottomRef.current && typeof bottomRef.current.scrollIntoView === 'function') {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [logs])

  if (loading) return (
    <div style={{ color: 'var(--text-secondary)', padding: 16 }}>⏳ Loading logs...</div>
  )

  return (
    <div
      style={{
        display:        'flex',
        flexDirection:  'column',
        gap:            2,
        height:         '100%',
        overflowY:      'auto',
        fontFamily:     'var(--font-mono)',
        fontSize:       10,
      }}
      data-testid="logs-view"
    >
      {logs.length === 0 && (
        <div style={{ color: 'var(--text-secondary)', padding: 12 }}>
          No log entries yet — system warming up…
        </div>
      )}
      {logs.map((entry, i) => (
        <div
          key={entry.id ?? i}
          style={{
            display:    'flex',
            gap:        8,
            padding:    '1px 0',
            borderBottom: '1px solid rgba(255,255,255,0.03)',
          }}
        >
          <span style={{ color: 'var(--text-secondary)', flexShrink: 0, width: 52 }}>
            {entry.time}
          </span>
          <span style={{
            color: levelColour(entry.level),
            flexShrink: 0,
            width: 48,
            fontWeight: 700,
            textTransform: 'uppercase',
          }}>
            {entry.level}
          </span>
          <span style={{ color: 'var(--accent-cyan)', flexShrink: 0, width: 96, overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {entry.agent}
          </span>
          <span style={{ color: 'var(--text-primary)', flex: 1 }}>
            {entry.msg}
          </span>
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  )
}
