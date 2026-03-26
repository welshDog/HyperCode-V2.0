/**
 * Unit Tests — HyperShellLayout
 * Validates: render, pane presence, focus toggle, ND modes, view modes
 */
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { HyperShellLayout } from '../components/shell/HyperShellLayout'

vi.mock('../hooks/useAgentSwarm', () => ({
  useAgentSwarm: () => ({
    agents: [
      { id: '1', name: 'Healer Agent', status: 'healthy', xp: 150, xpToNextLevel: 500, level: 2, coins: 75 },
      { id: '2', name: 'Agent X',      status: 'warning', xp:  50, xpToNextLevel: 500, level: 1, coins: 20 },
    ],
    loading: false,
    error: null,
  })
}))

vi.mock('../hooks/useEventStream', () => ({
  useEventStream: () => ({ events: [], connected: true })
}))

vi.mock('../hooks/useMetrics', () => ({
  useMetrics: () => ({ metrics: null, loading: false })
}))

describe('HyperShellLayout', () => {
  it('renders without crashing', () => {
    render(<HyperShellLayout />)
    expect(screen.getByTestId('hyper-shell')).toBeInTheDocument()
  })

  it('renders all 4 panes', () => {
    render(<HyperShellLayout />)
    expect(screen.getByTestId('pane-agents')).toBeInTheDocument()
    expect(screen.getByTestId('pane-timeline')).toBeInTheDocument()
    expect(screen.getByTestId('pane-metrics')).toBeInTheDocument()
    expect(screen.getByTestId('pane-pulse')).toBeInTheDocument()
  })

  it('shows Mission Control header', () => {
    render(<HyperShellLayout />)
    expect(screen.getByText(/Mission Control/i)).toBeInTheDocument()
  })

  it('focuses a pane on click', () => {
    render(<HyperShellLayout />)
    const focusBtn = screen.getAllByText(/Focus/i)[0]
    fireEvent.click(focusBtn)
    expect(screen.getByText(/Exit Focus/i)).toBeInTheDocument()
  })

  it('renders view mode toggles', () => {
    render(<HyperShellLayout />)
    expect(screen.getByText(/Grid/i)).toBeInTheDocument()
    expect(screen.getByText(/Focus/i)).toBeInTheDocument()
    expect(screen.getByText(/Present/i)).toBeInTheDocument()
  })

  it('renders ND mode toggles', () => {
    render(<HyperShellLayout />)
    expect(screen.getByText(/Default/i)).toBeInTheDocument()
    expect(screen.getByText(/Dyslexia/i)).toBeInTheDocument()
    expect(screen.getByText(/High-C/i)).toBeInTheDocument()
  })
})
