'use client';

import React, { useState, useRef, useId } from 'react';
import {
  parseBrainDump,
  MicroTask,
  EFFORT_LABELS,
  PRIORITY_COLOURS,
} from '../lib/brainDump';

// ── Types ─────────────────────────────────────────────────────────────────────

type ViewState = 'input' | 'results';

// ── Component ─────────────────────────────────────────────────────────────────

export default function BrainDumpChunker() {
  const [view, setView]       = useState<ViewState>('input');
  const [raw, setRaw]         = useState('');
  const [tasks, setTasks]     = useState<MicroTask[]>([]);
  const [loading, setLoading] = useState(false);
  const [announce, setAnnounce] = useState('');

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const labelId     = useId();
  const liveId      = useId();

  function chunk() {
    if (!raw.trim()) return;
    setLoading(true);
    // Async tick so the loading state renders before heavy parse
    setTimeout(() => {
      const result = parseBrainDump(raw);
      setTasks(result);
      setView('results');
      setLoading(false);
      setAnnounce(
        `Brain dump chunked into ${result.length} micro-task${
          result.length !== 1 ? 's' : ''
        }. ${
          result.filter(t => t.priority === 'critical').length
        } critical.`
      );
    }, 0);
  }

  function reset() {
    setView('input');
    setRaw('');
    setTasks([]);
    setAnnounce('Brain dump cleared. Ready for a new dump.');
    setTimeout(() => textareaRef.current?.focus(), 50);
  }

  function toggleDone(id: string) {
    setTasks(prev => prev.map(t => t.id === id ? { ...t, done: !t.done } : t));
  }

  const remaining = tasks.filter(t => !t.done).length;
  const total     = tasks.length;

  return (
    <section
      aria-labelledby={labelId}
      style={{
        background: 'var(--hc-color-surface, #1a1a2e)',
        border:     '1px solid var(--hc-color-border, #333)',
        borderRadius: 12,
        padding: '1.25rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.75rem',
      }}
    >
      {/* Live region */}
      <div
        id={liveId}
        role="status"
        aria-live="assertive"
        aria-atomic="true"
        style={{ position: 'absolute', width: 1, height: 1, overflow: 'hidden', clip: 'rect(0,0,0,0)' }}
      >
        {announce}
      </div>

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 id={labelId} style={{ margin: 0, fontSize: '1rem', fontWeight: 700 }}>
          📋 Brain Dump
        </h2>
        {view === 'results' && (
          <span style={{ fontSize: '0.75rem', color: 'var(--hc-color-muted, #888)' }}>
            {remaining}/{total} remaining
          </span>
        )}
      </div>

      {/* Input view */}
      {view === 'input' && (
        <>
          <label
            htmlFor={`${labelId}-textarea`}
            style={{ fontSize: '0.8rem', color: 'var(--hc-color-muted, #888)' }}
          >
            Dump everything in your brain. One thought per line, bullet points, or total chaos — it's fine.
          </label>
          <textarea
            id={`${labelId}-textarea`}
            ref={textareaRef}
            value={raw}
            onChange={e => setRaw(e.target.value)}
            placeholder={
              `- fix the auth bug urgently\n` +
              `- refactor the agent polling logic\n` +
              `- maybe explore chroma embeddings\n` +
              `- write up docs for the plugin SDK\n` +
              `- quick update to README`
            }
            rows={7}
            style={{
              width: '100%',
              background: 'var(--hc-color-bg, #0f0f1a)',
              color: 'var(--hc-color-text, #e0e0e0)',
              border: '1px solid var(--hc-color-border, #444)',
              borderRadius: 8,
              padding: '0.6rem 0.75rem',
              fontSize: '0.85rem',
              fontFamily: 'inherit',
              resize: 'vertical',
              boxSizing: 'border-box',
            }}
          />
          <button
            onClick={chunk}
            disabled={!raw.trim() || loading}
            aria-busy={loading}
            style={{
              alignSelf: 'flex-start',
              background: raw.trim() ? 'var(--hc-color-accent, #4a9eff)' : 'var(--hc-color-muted, #555)',
              color: '#fff',
              border: 'none',
              borderRadius: 8,
              padding: '0.5rem 1.2rem',
              fontSize: '0.9rem',
              fontWeight: 700,
              cursor: raw.trim() ? 'pointer' : 'not-allowed',
            }}
          >
            {loading ? 'Chunking…' : '⚡ Chunk It'}
          </button>
        </>
      )}

      {/* Results view */}
      {view === 'results' && (
        <>
          <ul
            aria-label={`${total} micro-tasks generated`}
            style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}
          >
            {tasks.map(task => (
              <li
                key={task.id}
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '0.6rem',
                  background: 'var(--hc-color-bg, #0f0f1a)',
                  borderRadius: 8,
                  padding: '0.6rem 0.75rem',
                  borderLeft: `3px solid ${PRIORITY_COLOURS[task.priority]}`,
                  opacity: task.done ? 0.45 : 1,
                }}
              >
                <input
                  type="checkbox"
                  id={`task-${task.id}`}
                  checked={task.done}
                  onChange={() => toggleDone(task.id)}
                  style={{ marginTop: 3, accentColor: 'var(--hc-color-accent, #4a9eff)', flexShrink: 0 }}
                  aria-label={`Mark done: ${task.text}`}
                />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <label
                    htmlFor={`task-${task.id}`}
                    style={{
                      fontSize: '0.85rem',
                      textDecoration: task.done ? 'line-through' : 'none',
                      cursor: 'pointer',
                      display: 'block',
                      wordBreak: 'break-word',
                    }}
                  >
                    {task.text}
                  </label>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.3rem', marginTop: '0.3rem' }}>
                    {/* Effort badge */}
                    <span style={{
                      fontSize: '0.7rem',
                      background: 'var(--hc-color-surface, #1a1a2e)',
                      border: '1px solid var(--hc-color-border, #444)',
                      borderRadius: 4,
                      padding: '0 0.4rem',
                    }}>
                      ⏱ {EFFORT_LABELS[task.effort]}
                    </span>
                    {/* Priority badge */}
                    <span style={{
                      fontSize: '0.7rem',
                      color: PRIORITY_COLOURS[task.priority],
                      border: `1px solid ${PRIORITY_COLOURS[task.priority]}`,
                      borderRadius: 4,
                      padding: '0 0.4rem',
                    }}>
                      {task.priority}
                    </span>
                    {/* Tag badges */}
                    {task.tags.map(tag => (
                      <span key={tag} style={{
                        fontSize: '0.7rem',
                        background: 'var(--hc-color-surface, #1a1a2e)',
                        border: '1px solid var(--hc-color-border, #555)',
                        borderRadius: 4,
                        padding: '0 0.4rem',
                        color: 'var(--hc-color-muted, #aaa)',
                      }}>
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </li>
            ))}
          </ul>

          <button
            onClick={reset}
            style={{
              alignSelf: 'flex-start',
              background: 'transparent',
              color: 'var(--hc-color-muted, #888)',
              border: '1px solid var(--hc-color-border, #444)',
              borderRadius: 8,
              padding: '0.4rem 0.9rem',
              fontSize: '0.8rem',
              cursor: 'pointer',
            }}
          >
            🔄 New Dump
          </button>
        </>
      )}
    </section>
  );
}
