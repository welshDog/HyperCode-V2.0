'use client'

import React, { useState } from 'react'
import { useTasks } from '@/hooks/useTasks'

const STATUS_COLOUR: Record<string, string> = {
  completed:   'var(--status-healthy)',
  in_progress: 'var(--accent-cyan)',
  pending:     'var(--accent-amber)',
  error:       'var(--status-error)',
}

function ProgressBar({ value }: { value: number }) {
  return (
    <div style={{ height: 4, background: 'rgba(255,255,255,0.08)', borderRadius: 2, marginTop: 4 }}>
      <div style={{
        width: `${Math.min(100, Math.max(0, value))}%`,
        height: '100%',
        background: value >= 100 ? 'var(--status-healthy)' : 'var(--accent-cyan)',
        borderRadius: 2,
        transition: 'width 0.4s ease',
      }} />
    </div>
  )
}

export function TasksView(): React.JSX.Element {
  const { tasks, loading, error, refetch } = useTasks()
  const [creating, setCreating] = useState(false)
  const [newDesc, setNewDesc]   = useState('')

  const handleCreate = async () => {
    if (!newDesc.trim()) return
    setCreating(true)
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('token') ?? '' : ''
      await fetch('/api/tasks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          title: newDesc.trim().slice(0, 60),
          description: newDesc.trim(),
          priority: 'normal',
          type: 'user_command',
          project_id: 1,
        }),
      })
      setNewDesc('')
      refetch()
    } catch {
      // silently fail — task will appear on next poll
    } finally {
      setCreating(false)
    }
  }

  if (loading) return (
    <div style={{ color: 'var(--text-secondary)', padding: 16 }}>⏳ Loading tasks...</div>
  )
  if (error) return (
    <div style={{ color: 'var(--status-error)', padding: 16 }}>⚠️ {error}</div>
  )

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6, height: '100%', overflow: 'hidden' }}>
      {/* Quick-create bar */}
      <div style={{ display: 'flex', gap: 6 }}>
        <input
          value={newDesc}
          onChange={(e) => setNewDesc(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
          placeholder="New task… (Enter to submit)"
          style={{
            flex: 1,
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid var(--pane-border)',
            borderRadius: 4,
            color: 'var(--text-primary)',
            padding: '4px 8px',
            fontSize: 11,
            outline: 'none',
          }}
        />
        <button
          onClick={handleCreate}
          disabled={creating || !newDesc.trim()}
          style={{
            background: 'var(--accent-cyan)',
            color: '#000',
            border: 'none',
            borderRadius: 4,
            padding: '4px 10px',
            fontSize: 11,
            fontWeight: 700,
            cursor: creating ? 'wait' : 'pointer',
            opacity: creating || !newDesc.trim() ? 0.5 : 1,
          }}
        >
          {creating ? '…' : '+'}
        </button>
      </div>

      {/* Task list */}
      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 4 }}
           data-testid="tasks-view">
        {tasks.length === 0 && (
          <div style={{ color: 'var(--text-secondary)', textAlign: 'center', padding: 20, fontSize: 12 }}>
            No tasks yet — create one above
          </div>
        )}
        {tasks.map((task) => (
          <div
            key={task.id}
            style={{
              background: 'rgba(255,255,255,0.03)',
              border: '1px solid var(--pane-border)',
              borderRadius: 5,
              padding: '6px 8px',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <span style={{ fontSize: 11, fontWeight: 600, flex: 1, marginRight: 8, wordBreak: 'break-word' }}>
                {task.title || task.description?.slice(0, 60) || `Task #${task.id}`}
              </span>
              <span style={{
                fontSize: 9,
                fontWeight: 700,
                color: STATUS_COLOUR[task.status] ?? 'var(--text-secondary)',
                textTransform: 'uppercase',
                flexShrink: 0,
              }}>
                {task.status}
              </span>
            </div>
            <ProgressBar value={task.progress ?? 0} />
          </div>
        ))}
      </div>
    </div>
  )
}
