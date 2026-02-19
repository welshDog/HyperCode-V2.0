"use client"
import React, { useEffect, useMemo, useState } from "react"
import Link from "next/link"

type EventItem = { ts: number; data: string }

export default function Page() {
  const [events, setEvents] = useState<EventItem[]>([])
  const [p95, setP95] = useState<number | null>(null)
  const [lastStatus, setLastStatus] = useState<string | null>(null)
  const core = process.env.NEXT_PUBLIC_CORE_URL || "http://localhost:8000"
  const agentsBase = process.env.NEXT_PUBLIC_AGENTS_URL || `${core}/agents`
  const [sending, setSending] = useState(false)
  const [toast, setToast] = useState<{ type: 'success' | 'error'; msg: string } | null>(null)

  useEffect(() => {
    const es = new EventSource(`${core}/agents/stream`)
    es.onmessage = e => {
      setEvents(prev => [{ ts: Date.now(), data: e.data }, ...prev].slice(0, 200))
    }
    es.onerror = () => {}
    return () => es.close()
  }, [core])

  useEffect(() => {
    let active = true
    async function poll() {
      try {
        const r = await fetch(`${core}/metrics/agent_stream_summary`)
        const j = await r.json()
        if (active) setP95(typeof j.p95_ms === "number" ? j.p95_ms : null)
      } catch {}
      try {
        const r2 = await fetch(`${core}/execution/last`)
        if (r2.ok) {
          const j2 = await r2.json()
          if (active) setLastStatus(j2.status)
        }
      } catch {}
    }
    poll()
    const id = setInterval(poll, 10000)
    return () => {
      active = false
      clearInterval(id)
    }
  }, [core])

  const metrics = useMemo(() => {
    const now = Date.now()
    const lastTs = events.length ? events[0].ts : 0
    const ageMs = lastTs ? now - lastTs : Infinity
    const lastMin = events.filter(e => now - e.ts <= 60_000).length
    const ratePerSec = lastMin / 60
    const healthy = ageMs < 5_000
    return { ageMs, ratePerSec, healthy }
  }, [events])

  return (
    <main className="hc-main">
      <div className="hc-panel" style={{ gridColumn: '1 / -1' }}>
        <div className="hc-panel-header" style={{ justifyContent: 'space-between' }}>
          <h2 className="hc-panel-title">/ BROSKI TERMINAL</h2>
          <nav>
            <Link href="/bible" className="hc-button" style={{ marginRight: 8, textDecoration: "none", display: 'inline-block' }}>Hyper Agent Bible</Link>
            <Link href="/support" className="hc-button" style={{ textDecoration: "none", display: 'inline-block' }}>Support Hub</Link>
          </nav>
        </div>
      </div>

      <div className="hc-panel primary">
        <div className="hc-panel-header">
          <h2 className="hc-panel-title">/ NETWORK STATUS</h2>
          <div style={{ width: 10, height: 10, background: metrics.healthy ? "#22c55e" : "#ef4444", borderRadius: '50%', marginLeft: 'auto', boxShadow: `0 0 10px ${metrics.healthy ? "#22c55e" : "#ef4444"}` }} />
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10 }}>
          <div style={{ background: 'rgba(6, 182, 212, 0.05)', padding: 10, borderRadius: 4, borderLeft: '2px solid var(--color-secondary)' }}>
            <div style={{ fontSize: 11, color: '#999', textTransform: 'uppercase' }}>Stream Health</div>
            <div style={{ fontSize: 14, fontWeight: 'bold' }}>{metrics.ageMs === Infinity ? "—" : `${Math.round(metrics.ageMs)}ms`}</div>
          </div>
          <div style={{ background: 'rgba(124, 58, 237, 0.05)', padding: 10, borderRadius: 4, borderLeft: '2px solid var(--color-primary)' }}>
            <div style={{ fontSize: 11, color: '#999', textTransform: 'uppercase' }}>Events/min</div>
            <div style={{ fontSize: 14, fontWeight: 'bold' }}>{(metrics.ratePerSec * 60).toFixed(0)}</div>
          </div>
          <div style={{ background: 'rgba(6, 182, 212, 0.05)', padding: 10, borderRadius: 4, borderLeft: '2px solid var(--color-secondary)' }}>
            <div style={{ fontSize: 11, color: '#999', textTransform: 'uppercase' }}>p95 latency</div>
            <div style={{ fontSize: 14, fontWeight: 'bold' }}>{p95 == null ? "—" : `${p95.toFixed(0)}ms`}</div>
          </div>
        </div>
      </div>

      <div className="hc-panel" style={{ gridColumn: '1 / -1', minHeight: 400, display: 'flex', flexDirection: 'column' }}>
        <div className="hc-panel-header">
          <h2 className="hc-panel-title">/ AGENT STREAM</h2>
        </div>
        <div style={{ flex: 1, border: "1px solid var(--color-secondary)", borderRadius: 4, padding: 10, background: 'rgba(0,0,0,0.3)', overflow: "auto", fontFamily: 'var(--font-mono)', fontSize: 13, marginBottom: 15 }}>
          {events.map((e, i) => (
            <div key={i} style={{ padding: "4px 0", borderBottom: '1px dashed rgba(6,182,212,0.1)' }}>
              <span style={{ color: "var(--color-secondary)", marginRight: 10 }}>[{new Date(e.ts).toLocaleTimeString()}]</span>
              <span style={{ color: "#fff" }}>{e.data}</span>
            </div>
          ))}
        </div>
        
        <AdminButton 
          sending={sending}
          toast={toast}
          onSend={async () => {
            setSending(true)
            setToast(null)
            const payload = { prompt: "Write a Python function add(a,b) that returns sum" }
            const maxRetries = 5
            let attempt = 0
            let delay = 500
            const backoff = () => new Promise(res => setTimeout(res, delay))
            try {
              // Discover Coder agent id
              const listResp = await fetch(`${agentsBase}/`)
              const agents = await listResp.json()
              const coder = (agents as any[]).find(a => a.name === 'Coder')
              if (!coder) throw new Error('Coder agent not found')
              const target = `${agentsBase}/${coder.id}/send`
              while (attempt < maxRetries) {
                try {
                  const resp = await fetch(target, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                  })
                  if (resp.status === 202) {
                    setToast({ type: 'success', msg: 'Task dispatched to Coder Agent' })
                    setSending(false)
                    return
                  }
                  const text = await resp.text()
                  throw new Error(`HTTP ${resp.status}: ${text}`)
                } catch (err: any) {
                  attempt++
                  if (attempt >= maxRetries) {
                    setToast({ type: 'error', msg: `Failed: ${err?.message || 'Unknown error'}` })
                    setSending(false)
                    return
                  }
                  await backoff()
                  delay = Math.min(delay * 2, 8000)
                }
              }
            } catch (e: any) {
              setToast({ type: 'error', msg: e?.message || 'Dispatch failed' })
              setSending(false)
            }
          }}
        />
        {toast && (
          <div role="status" aria-live="polite" style={{ marginTop: 8, padding: 8, borderRadius: 6, border: '1px solid var(--color-secondary)', background: toast.type === 'success' ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)', color: toast.type === 'success' ? '#22c55e' : '#ef4444' }}>
            {toast.msg}
          </div>
        )}
      </div>
    </main>
  )
}

function AdminButton({ sending, toast, onSend }: { sending: boolean; toast: { type: 'success' | 'error'; msg: string } | null; onSend: () => Promise<void> }) {
  return (
    <button
      onClick={onSend}
      aria-busy={sending}
      aria-disabled={sending}
      className="hc-button"
      style={{
        width: '100%',
        cursor: sending ? "not-allowed" : "pointer",
        opacity: sending ? 0.7 : 1
      }}
    >
      {sending ? "DISPATCHING..." : "SEND TEST TASK TO CODER"}
    </button>
  )
}
