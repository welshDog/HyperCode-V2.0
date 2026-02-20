"use client"
import React, { useEffect, useMemo, useState } from "react"
import Link from "next/link"
import { Agent } from "./types/dashboard"

type EventItem = { ts: number; data: string }

export default function Page() {
  const [events, setEvents] = useState<EventItem[]>([])
  const [p95, setP95] = useState<number | null>(null)
  const [lastStatus, setLastStatus] = useState<string | null>(null)
  const [agents, setAgents] = useState<Agent[]>([])
  
  const core = process.env.NEXT_PUBLIC_CORE_URL || "http://localhost:8000"
  const agentsBase = process.env.NEXT_PUBLIC_AGENTS_URL || `${core}/agents`

  useEffect(() => {
    fetch(`${agentsBase}/`)
      .then(r => r.json())
      .then(data => setAgents(Array.isArray(data) ? data : []))
      .catch(e => console.error("Failed to fetch agents", e))
  }, [agentsBase])

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
        
        <TaskInterface core={core} agents={agents} />
      </div>
    </main>
  )
}

function TaskInterface({ core, agents }: { core: string, agents: Agent[] }) {
  const [task, setTask] = useState("")
  const [agentId, setAgentId] = useState("auto")
  const [sending, setSending] = useState(false)
  const [status, setStatus] = useState<{type: 'success'|'error', msg: string} | null>(null)

  const handleSend = async () => {
    if (!task.trim()) return
    setSending(true)
    setStatus(null)
    
    try {
      const orchestratorUrl = "http://localhost:8080"

      if (agentId === 'auto') {
        // Swarm/Orchestrator Mode
        const res = await fetch(`${orchestratorUrl}/plan`, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            // 'X-API-Key': 'dev-master-key' // Orchestrator might not check this yet, but good to have
          },
          body: JSON.stringify({
            task: task,
            context: {},
            priority: "high"
          })
        })
        if (!res.ok) throw new Error(await res.text())
        const data = await res.json()
        setStatus({ type: 'success', msg: `Mission dispatched! ID: ${data.task_id} 🚀` })
      } else {
        // Single Agent Mode
        const agent = agents.find(a => a.id === agentId)
        const agentName = agent?.name.toLowerCase().replace(/\s+/g, '-') || agentId
        
        // Map generic names to specific service names if needed
        // e.g. "project-strategist" -> "project_strategist" depending on orchestrator map
        // The orchestrator uses keys like "project_strategist" in AGENTS dict, 
        // but the route /agent/{agent_name}/execute checks keys.
        // Let's assume the IDs match or we need to normalize.
        // The AGENTS dict keys in orchestrator are snake_case: "project_strategist"
        const normalizedAgentName = agentName.replace(/-/g, '_')

        const res = await fetch(`${orchestratorUrl}/agent/${normalizedAgentName}/execute`, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            agent: normalizedAgentName,
            message: task,
            context: {}
          })
        })
        if (!res.ok) throw new Error(await res.text())
        setStatus({ type: 'success', msg: `Task sent to ${agent?.name} 🤖` })
      }
      setTask("")
    } catch (e: any) {
      setStatus({ type: 'error', msg: `Failed: ${e.message}` })
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="hc-panel-content" style={{ marginTop: 'auto', borderTop: '1px solid var(--color-secondary)', paddingTop: 15 }}>
      <div style={{ marginBottom: 10 }}>
        <label style={{ fontSize: 11, color: '#999', textTransform: 'uppercase', marginBottom: 4, display: 'block' }}>New Mission / Task</label>
        <textarea
          value={task}
          onChange={e => setTask(e.target.value)}
          placeholder="Describe your task... (e.g., 'Create a Python function to sort lists')"
          className="hc-input"
          style={{ 
            width: '100%', 
            minHeight: 80, 
            background: 'rgba(0,0,0,0.3)', 
            border: '1px solid var(--color-secondary)', 
            borderRadius: 4, 
            color: '#fff', 
            padding: 8,
            fontFamily: 'var(--font-mono)',
            fontSize: 13,
            marginBottom: 10
          }}
        />
      </div>
      
      <div style={{ display: 'flex', gap: 10 }}>
        <select 
          value={agentId}
          onChange={e => setAgentId(e.target.value)}
          className="hc-input"
          style={{ 
            flex: 1, 
            background: 'rgba(0,0,0,0.3)', 
            border: '1px solid var(--color-secondary)', 
            borderRadius: 4, 
            color: '#fff', 
            padding: '0 8px',
            height: 40
          }}
        >
          <option value="auto">✨ ORCHESTRATOR (Auto-Swarm)</option>
          <option disabled>──────────</option>
          {agents.map(a => (
            <option key={a.id} value={a.id}>{a.name} ({a.role})</option>
          ))}
        </select>
        
        <button
          onClick={handleSend}
          disabled={sending || !task.trim()}
          className="hc-button"
          style={{
            flex: '0 0 120px',
            opacity: (sending || !task.trim()) ? 0.5 : 1,
            cursor: (sending || !task.trim()) ? 'not-allowed' : 'pointer',
            height: 40,
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center'
          }}
        >
          {sending ? "SENDING..." : "INITIALIZE"}
        </button>
      </div>

      {status && (
        <div style={{ 
          marginTop: 10, 
          padding: 8, 
          borderRadius: 4, 
          background: status.type === 'success' ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)', 
          border: `1px solid ${status.type === 'success' ? '#22c55e' : '#ef4444'}`,
          color: status.type === 'success' ? '#22c55e' : '#ef4444',
          fontSize: 13
        }}>
          {status.msg}
        </div>
      )}
    </div>
  )
}
