'use client'

import React from 'react'
import { useAgentSwarm } from '@/hooks/useAgentSwarm'

export function BROskiPulseView(): React.JSX.Element {
  const { agents } = useAgentSwarm()

  const totalXP     = agents.reduce((s, a) => s + a.xp, 0)
  const totalCoins  = agents.reduce((s, a) => s + (a.coins ?? 0), 0)
  const topAgent    = [...agents].sort((a, b) => b.xp - a.xp)[0]
  const healthyCount = agents.filter((a) => a.status === 'healthy').length

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, height: '100%' }} data-testid="broski-pulse">
      {[
        { label: '\uD83D\uDCB0 BROski$',   value: totalCoins, colour: 'var(--accent-amber)'  },
        { label: '\uD83E\uDDEB Total XP',   value: totalXP,    colour: 'var(--accent-purple)' },
        { label: '\uD83D\uDFE2 Healthy',    value: `${healthyCount}/${agents.length}`, colour: 'var(--status-healthy)' },
        { label: '\uD83E\uDD47 Top Agent',  value: topAgent?.name ?? '—', colour: 'var(--accent-cyan)' },
      ].map((stat) => (
        <div
          key={stat.label}
          style={{
            background:   'rgba(255,255,255,0.03)',
            border:       '1px solid var(--pane-border)',
            borderRadius: 6,
            padding:      '8px 10px',
            display:      'flex',
            flexDirection: 'column',
            gap:          4,
          }}
        >
          <span style={{ fontSize: 10, color: 'var(--text-secondary)' }}>{stat.label}</span>
          <span style={{ fontSize: 18, fontWeight: 700, color: stat.colour, fontFamily: 'var(--font-mono)' }}>
            {stat.value}
          </span>
        </div>
      ))}
    </div>
  )
}
