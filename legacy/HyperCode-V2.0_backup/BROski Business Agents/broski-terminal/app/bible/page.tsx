import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function extractMeta(src: string) {
  const versionMatch = src.match(/\*\*Version:\*\*\s*([^\n]+)/i);
  const updatedMatch = src.match(/\*\*(?:Last\s*Updated|Updated):\*\*\s*([^\n]+)/i);
  const version = versionMatch ? versionMatch[1].trim() : "Unknown";
  const updatedRaw = updatedMatch ? updatedMatch[1].trim() : "Unknown";
  return { version, updated: updatedRaw };
}

export default async function Page() {
  const core = process.env.NEXT_PUBLIC_CORE_URL || "http://localhost:8000";
  const res = await fetch(`${core}/agents/bible`, { cache: "no-store" });
  const text = await res.text();
  const meta = extractMeta(text);
  return (
    <main style={{ padding: 24, maxWidth: 1000, margin: "0 auto", fontFamily: "system-ui, sans-serif" }}>
      <div style={{ position: "sticky", top: 0, zIndex: 10, background: "rgba(255,255,255,0.9)", backdropFilter: "saturate(180%) blur(6px)", borderBottom: "1px solid #e5e7eb", padding: "10px 0", marginBottom: 12 }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <h1 style={{ margin: 0 }}>Hyper Agent Bible</h1>
          <a href="/" style={{ display: "inline-block", padding: "6px 10px", border: "1px solid #ddd", borderRadius: 6, textDecoration: "none", color: "#111" }}>Back to Terminal</a>
        </div>
        <div style={{ marginTop: 8, display: "flex", gap: 12, fontSize: 13, color: "#374151" }}>
          <span>Version: <strong>{meta.version}</strong></span>
          <span>Updated: <strong>{meta.updated}</strong></span>
        </div>
      </div>

      <div style={{ border: "1px solid #e5e7eb", background: "#fafafa", borderRadius: 8, padding: 16 }}>
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            h1: ({ children }) => <h1 style={{ fontSize: 24, margin: "18px 0" }}>{children}</h1>,
            h2: ({ children }) => <h2 style={{ fontSize: 20, margin: "16px 0" }}>{children}</h2>,
            h3: ({ children }) => <h3 style={{ fontSize: 18, margin: "14px 0" }}>{children}</h3>,
            p: ({ children }) => <p style={{ lineHeight: 1.7, margin: "10px 0", color: "#111" }}>{children}</p>,
            li: ({ children }) => <li style={{ lineHeight: 1.6 }}>{children}</li>,
            code: ({ children }) => (
              <code style={{ background: "#f3f4f6", border: "1px solid #e5e7eb", borderRadius: 4, padding: "2px 5px" }}>{children}</code>
            ),
            a: ({ href, children }) => (
              <a href={href as string} style={{ color: "#2563eb", textDecoration: "underline" }}>{children}</a>
            ),
          }}
        >
          {text}
        </ReactMarkdown>
      </div>
    </main>
  );
}
