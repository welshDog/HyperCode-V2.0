import React from "react"

export default function Page() {
  const external = "/support/index.html"
  return (
    <main style={{ padding: 24, fontFamily: "system-ui, sans-serif" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
        <h1 style={{ margin: 0 }}>Support Hub</h1>
        <a href="/" style={{ display: "inline-block", padding: "6px 10px", border: "1px solid #ddd", borderRadius: 6, textDecoration: "none", color: "#111" }}>Back to Terminal</a>
      </div>

      <div style={{ marginBottom: 16, color: "#374151" }}>
        <p>Support the Hyperfocus Empire. External hub opens below; quick actions available if the embed is blocked.</p>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <a href="https://ko-fi.com/hyperfocuszone" target="_blank" rel="noopener noreferrer" style={{ padding: "6px 10px", border: "1px solid #ddd", borderRadius: 6, textDecoration: "none", background: "#fff", color: "#111" }}>Buy Coffee</a>
          <a href="https://patreon.com/hyperfocuszone" target="_blank" rel="noopener noreferrer" style={{ padding: "6px 10px", border: "1px solid #ddd", borderRadius: 6, textDecoration: "none", background: "#fff", color: "#111" }}>Patreon</a>
          <a href="mailto:business@hyperfocuszone.com" style={{ padding: "6px 10px", border: "1px solid #ddd", borderRadius: 6, textDecoration: "none", background: "#fff", color: "#111" }}>Business Inquiry</a>
        </div>
      </div>

      <div style={{ border: "1px solid #e5e7eb", borderRadius: 8, overflow: "hidden" }}>
        <iframe title="Support Hub" src={external} style={{ width: "100%", height: 700, border: 0 }} />
      </div>

      <div style={{ marginTop: 12, fontSize: 13 }}>
        <a href={external} target="_blank" rel="noopener noreferrer" style={{ color: "#2563eb", textDecoration: "underline" }}>Open full Support Hub in new tab</a>
      </div>
    </main>
  )
}
