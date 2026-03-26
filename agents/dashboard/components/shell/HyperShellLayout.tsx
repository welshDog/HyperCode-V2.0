'use client'

import React, { useState, useCallback } from 'react'
import { Pane } from './Pane'
import { ViewModeToggle } from './ViewModeToggle'
import { NDToggle } from '../ui/NDToggle'
import { AgentSwarmView } from '../views/AgentSwarmView'
import { TimelineView } from '../views/TimelineView'
import { MetricsView } from '../views/MetricsView'
import { BROskiPulseView } from '../views/BROskiPulseView'
import { useViewMode } from '@/hooks/useViewMode'

// ── View Registry — register new views here, zero core changes needed
export const VIEW_REGISTRY: Record<string, React.ComponentType> = {
  'agent-swarm':  AgentSwarmView,
  'timeline':     TimelineView,
  'metrics':      MetricsView,
  'broski-pulse': BROskiPulseView,
}

export interface PaneConfig {
  id:         string
  title:      string
  viewId:     string
  gridArea:   string
}

const DEFAULT_PANES: PaneConfig[] = [
  { id: 'agents',  title: '\uD83E\uDD16 Agent Swarm',    viewId: 'agent-swarm',  gridArea: 'agents'  },
  { id: 'timeline',title: '\uD83D\uDCE1 Event Timeline', viewId: 'timeline',     gridArea: 'timeline' },
  { id: 'metrics', title: '\uD83D\uDCCA Metrics',        viewId: 'metrics',      gridArea: 'metrics'  },
  { id: 'pulse',   title: '\uD83E\uDD85 BROski Pulse',   viewId: 'broski-pulse', gridArea: 'pulse'    },
]

export function HyperShellLayout(): React.JSX.Element {
  const { viewMode, setViewMode } = useViewMode()
  const [focusedPaneId, setFocusedPaneId] = useState<string | null>(null)
  const [ndMode, setNdMode] = useState<string>('default')

  const handleNdChange = useCallback((mode: string) => {
    setNdMode(mode)
    document.documentElement.setAttribute('data-nd-mode', mode)
  }, [])

  const gridTemplate = viewMode === 'focus' && focusedPaneId
    ? `"${focusedPaneId} ${focusedPaneId}" 1fr / 1fr 1fr`
    : `
        "topbar   topbar   topbar"  44px
        "agents   timeline metrics" 1fr
        "agents   timeline pulse"   200px
        / 1fr     1fr      1fr
      `

  return (
    <div
      className="hyper-shell"
      style={{ gridTemplate }}
      data-testid="hyper-shell"
    >
      {/* ── Top Bar ─────────────────────────────── */}
      <div
        style={{
          gridArea:       'topbar',
          display:        'flex',
          alignItems:     'center',
          justifyContent: 'space-between',
          padding:        '0 16px',
          background:     'var(--pane-header)',
          borderBottom:   '1px solid var(--pane-border)',
        }}
      >
        <span style={{ color: 'var(--accent-cyan)', fontWeight: 700, fontSize: 14 }}>
          \uD83E\uDD85 HyperCode Mission Control
        </span>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <NDToggle value={ndMode} onChange={handleNdChange} />
          <ViewModeToggle value={viewMode} onChange={setViewMode} />
        </div>
      </div>

      {/* ── Panes ───────────────────────────────── */}
      {DEFAULT_PANES.map((pane) => {
        const ViewComponent = VIEW_REGISTRY[pane.viewId]
        const isFocused = focusedPaneId === pane.id
        return (
          <Pane
            key={pane.id}
            id={pane.id}
            title={pane.title}
            gridArea={pane.gridArea}
            focused={isFocused}
            onFocusToggle={() => setFocusedPaneId(isFocused ? null : pane.id)}
          >
            {ViewComponent && <ViewComponent />}
          </Pane>
        )
      })}
    </div>
  )
}
