import { useState, useEffect, useRef } from "react";

const AGENTS = [
  {
    id: "cortex",
    name: "CORTEX",
    subtitle: "The Thinking Core",
    icon: "⬡",
    color: "#00FFD1",
    glow: "rgba(0,255,209,0.4)",
    ring: "#00FFD1",
    description: "The central intelligence that models HOW you think, not just what you want. Learns your cognitive fingerprint over time — your peak hours, your pattern-jumps, your hyperfocus triggers.",
    powers: [
      "Cognitive fingerprint mapping",
      "Adaptive reasoning style",
      "Predicts next thought before you type it",
      "Learns your unique mental model language"
    ],
    nd_feature: "Speaks YOUR internal language — visual, spatial, metaphorical, or abstract",
    position: { top: "50%", left: "50%", transform: "translate(-50%, -50%)" }
  },
  {
    id: "hyperfocus",
    name: "FLOW",
    subtitle: "Hyperfocus Guardian",
    icon: "◈",
    color: "#FF6B35",
    glow: "rgba(255,107,53,0.4)",
    ring: "#FF6B35",
    description: "Detects when you enter flow state and builds a fortress around it. Filters all inputs, batches interruptions, and queues everything for when you surface.",
    powers: [
      "Flow state detection via typing rhythm",
      "Interrupt batching & scheduling",
      "Deep work session memory",
      "Auto-resumes exactly where you left off"
    ],
    nd_feature: "ADHD's hyperfocus is a superpower — FLOW weaponizes it",
    position: { top: "15%", left: "50%", transform: "translateX(-50%)" }
  },
  {
    id: "pattern",
    name: "WEAVER",
    subtitle: "Pattern Intelligence",
    icon: "✦",
    color: "#BD00FF",
    glow: "rgba(189,0,255,0.4)",
    ring: "#BD00FF",
    description: "Spots connections between everything — your code, notes, conversations, ideas from 3 months ago. The ND brain sees patterns others miss. WEAVER amplifies that gift.",
    powers: [
      "Cross-domain pattern recognition",
      "Connects ideas across time & context",
      "Visual knowledge graph in real-time",
      "Surfaces forgotten relevant insights"
    ],
    nd_feature: "Built for divergent thinkers who connect unrelated things brilliantly",
    position: { top: "28%", left: "82%", transform: "translate(-50%, -50%)" }
  },
  {
    id: "context",
    name: "ANCHOR",
    subtitle: "Context Preserver",
    icon: "⊕",
    color: "#FFD700",
    glow: "rgba(255,215,0,0.4)",
    ring: "#FFD700",
    description: "Never loses where you were. Context switching is a massive ND pain point — ANCHOR snapshots your entire mental state and restores it perfectly when you return.",
    powers: [
      "Full mental state snapshots",
      "Multi-thread context switching",
      "Restores work state in < 2 seconds",
      "Tracks all open thought threads"
    ],
    nd_feature: "For brains that run 12 tabs simultaneously — every tab is saved",
    position: { top: "28%", left: "18%", transform: "translate(-50%, -50%)" }
  },
  {
    id: "energy",
    name: "PULSE",
    subtitle: "Cognitive Energy Governor",
    icon: "◉",
    color: "#00FF88",
    glow: "rgba(0,255,136,0.4)",
    ring: "#00FF88",
    description: "Matches task complexity to your current cognitive energy. When you're dysregulated or exhausted, PULSE routes simpler tasks. When you're firing on all cylinders, it brings the hardest problems.",
    powers: [
      "Real-time energy state detection",
      "Dynamic task complexity routing",
      "Suggests breaks before burnout",
      "Tracks energy patterns over weeks"
    ],
    nd_feature: "ND brains have variable energy — this system respects and works WITH that",
    position: { top: "72%", left: "18%", transform: "translate(-50%, -50%)" }
  },
  {
    id: "translator",
    name: "BRIDGE",
    subtitle: "Output Translator",
    icon: "⟁",
    color: "#FF0080",
    glow: "rgba(255,0,128,0.4)",
    ring: "#FF0080",
    description: "Translates your ND thinking style into whatever the world needs — formal emails, reports, documentation, presentations. Think messy, output polished. Never lose your voice.",
    powers: [
      "ND thought → professional output",
      "Preserves your authentic voice",
      "Multiple output format adapters",
      "Tone calibration for any audience"
    ],
    nd_feature: "Think in your natural way. We handle the translation.",
    position: { top: "72%", left: "82%", transform: "translate(-50%, -50%)" }
  },
  {
    id: "safety",
    name: "GUARDIAN",
    subtitle: "Safety & Ethics Layer",
    icon: "⬔",
    color: "#4FC3F7",
    glow: "rgba(79,195,247,0.4)",
    ring: "#4FC3F7",
    description: "Every action reviewed before execution. Tiered permission levels, rollback on every change, human-in-the-loop checkpoints. Autonomous but never reckless.",
    powers: [
      "Pre-execution action review",
      "Full rollback capability",
      "Configurable autonomy levels",
      "Transparent reasoning logs"
    ],
    nd_feature: "Clarity & predictability — no surprise behaviours, ever",
    position: { top: "85%", left: "50%", transform: "translateX(-50%)" }
  }
];

const CONNECTIONS = [
  { from: "cortex", to: "hyperfocus" },
  { from: "cortex", to: "pattern" },
  { from: "cortex", to: "context" },
  { from: "cortex", to: "energy" },
  { from: "cortex", to: "translator" },
  { from: "cortex", to: "safety" },
  { from: "hyperfocus", to: "pattern" },
  { from: "hyperfocus", to: "context" },
  { from: "energy", to: "safety" },
  { from: "translator", to: "safety" },
];

const PRINCIPLES = [
  { icon: "🧠", title: "Cognitive Respect", text: "The system adapts to YOUR brain — you never adapt to it" },
  { icon: "🔥", title: "Superpower First", text: "ND traits are features, not bugs — hyperfocus, pattern-thinking, creativity are amplified" },
  { icon: "🛡️", title: "Safe Autonomy", text: "Agents act — but never without your awareness and the ability to undo" },
  { icon: "👁️", title: "Visual Everything", text: "Every process, every state, every decision visualized — no hidden black boxes" },
  { icon: "⚡", title: "Zero Friction", text: "One thought → action. The system removes every barrier between idea and execution" },
  { icon: "🔄", title: "Never Lost", text: "Infinite context, infinite undo, infinite patience — pick up exactly where you left" },
];

function Particle({ x, y, color }) {
  return (
    <div
      style={{
        position: "absolute",
        left: x + "%",
        top: y + "%",
        width: 2,
        height: 2,
        borderRadius: "50%",
        background: color,
        opacity: 0.6,
        animation: `float ${3 + Math.random() * 4}s ease-in-out infinite alternate`,
        animationDelay: Math.random() * 3 + "s"
      }}
    />
  );
}

export default function NexusSystem() {
  const [selected, setSelected] = useState(null);
  const [hovered, setHovered] = useState(null);
  const [particles] = useState(() =>
    Array.from({ length: 40 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      color: ["#00FFD1", "#BD00FF", "#FF6B35", "#FFD700"][Math.floor(Math.random() * 4)]
    }))
  );
  const [pulse, setPulse] = useState(0);

  useEffect(() => {
    const t = setInterval(() => setPulse(p => (p + 1) % 100), 50);
    return () => clearInterval(t);
  }, []);

  const selectedAgent = AGENTS.find(a => a.id === selected);

  return (
    <div style={{
      minHeight: "100vh",
      background: "#030712",
      fontFamily: "'Courier New', monospace",
      color: "#E2E8F0",
      overflow: "hidden",
      position: "relative"
    }}>
      <style>{`
        @keyframes float {
          from { transform: translateY(0px) scale(1); opacity: 0.3; }
          to { transform: translateY(-20px) scale(1.5); opacity: 0.8; }
        }
        @keyframes spin-slow {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        @keyframes spin-reverse {
          from { transform: rotate(360deg); }
          to { transform: rotate(0deg); }
        }
        @keyframes pulse-ring {
          0% { transform: scale(1); opacity: 0.8; }
          50% { transform: scale(1.15); opacity: 0.3; }
          100% { transform: scale(1); opacity: 0.8; }
        }
        @keyframes data-flow {
          0% { stroke-dashoffset: 100; opacity: 0; }
          20% { opacity: 1; }
          80% { opacity: 1; }
          100% { stroke-dashoffset: 0; opacity: 0; }
        }
        @keyframes slide-in {
          from { transform: translateX(60px); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
        @keyframes fade-up {
          from { transform: translateY(20px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }
        @keyframes glow-pulse {
          0%, 100% { box-shadow: 0 0 20px currentColor; }
          50% { box-shadow: 0 0 50px currentColor, 0 0 80px currentColor; }
        }
        .agent-node:hover {
          transform: translate(-50%, -50%) scale(1.1) !important;
        }
        .agent-node {
          transition: transform 0.2s ease;
        }
        .principle-card {
          transition: all 0.2s ease;
          border: 1px solid rgba(255,255,255,0.05);
        }
        .principle-card:hover {
          border-color: rgba(0,255,209,0.3);
          background: rgba(0,255,209,0.05) !important;
          transform: translateY(-2px);
        }
      `}</style>

      {/* Background particles */}
      <div style={{ position: "fixed", inset: 0, pointerEvents: "none" }}>
        {particles.map(p => <Particle key={p.id} {...p} />)}
      </div>

      {/* Background grid */}
      <div style={{
        position: "fixed", inset: 0, pointerEvents: "none",
        backgroundImage: `
          linear-gradient(rgba(0,255,209,0.03) 1px, transparent 1px),
          linear-gradient(90deg, rgba(0,255,209,0.03) 1px, transparent 1px)
        `,
        backgroundSize: "60px 60px"
      }} />

      {/* Header */}
      <div style={{ textAlign: "center", padding: "40px 20px 20px", position: "relative", zIndex: 10 }}>
        <div style={{
          fontSize: 11, letterSpacing: 8, color: "#00FFD1",
          marginBottom: 12, opacity: 0.7
        }}>
          NEURODIVERGENT INTELLIGENCE FRAMEWORK
        </div>
        <h1 style={{
          fontSize: "clamp(48px, 8vw, 96px)",
          fontWeight: 900,
          margin: 0,
          letterSpacing: -2,
          background: "linear-gradient(135deg, #00FFD1 0%, #BD00FF 50%, #FF6B35 100%)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
          lineHeight: 1
        }}>
          NEXUS
        </h1>
        <div style={{ fontSize: 14, color: "#94A3B8", marginTop: 10, letterSpacing: 3 }}>
          THE AGENT SYSTEM THAT THINKS LIKE YOU
        </div>
      </div>

      {/* Main Architecture Diagram */}
      <div style={{
        position: "relative",
        width: "100%",
        maxWidth: 800,
        height: 600,
        margin: "0 auto",
        zIndex: 10
      }}>
        {/* SVG Connection Lines */}
        <svg style={{
          position: "absolute", inset: 0, width: "100%", height: "100%",
          pointerEvents: "none"
        }}>
          {CONNECTIONS.map(({ from, to }) => {
            const fromAgent = AGENTS.find(a => a.id === from);
            const toAgent = AGENTS.find(a => a.id === to);
            const isActive = selected === from || selected === to || hovered === from || hovered === to;
            const fromPos = fromAgent.position;
            const toPos = toAgent.position;

            // Parse positions to percentages
            const getX = (pos) => parseFloat(pos.left);
            const getY = (pos) => parseFloat(pos.top);

            const x1 = getX(fromPos);
            const y1 = getY(fromPos);
            const x2 = getX(toPos);
            const y2 = getY(toPos);

            return (
              <line
                key={`${from}-${to}`}
                x1={`${x1}%`} y1={`${y1}%`}
                x2={`${x2}%`} y2={`${y2}%`}
                stroke={isActive ? fromAgent.color : "rgba(255,255,255,0.06)"}
                strokeWidth={isActive ? 2 : 1}
                strokeDasharray={isActive ? "none" : "4 4"}
                style={{ transition: "all 0.3s ease" }}
              />
            );
          })}
        </svg>

        {/* Agent Nodes */}
        {AGENTS.map((agent) => {
          const isSelected = selected === agent.id;
          const isHovered = hovered === agent.id;
          const isActive = isSelected || isHovered;

          return (
            <div
              key={agent.id}
              className="agent-node"
              onClick={() => setSelected(selected === agent.id ? null : agent.id)}
              onMouseEnter={() => setHovered(agent.id)}
              onMouseLeave={() => setHovered(null)}
              style={{
                position: "absolute",
                ...agent.position,
                cursor: "pointer",
                zIndex: isSelected ? 20 : 10
              }}
            >
              {/* Outer pulse ring */}
              <div style={{
                position: "absolute",
                inset: -20,
                borderRadius: "50%",
                border: `1px solid ${agent.color}`,
                opacity: isActive ? 0.6 : 0.15,
                animation: isActive ? "pulse-ring 1.5s ease-in-out infinite" : "none",
                transition: "opacity 0.3s"
              }} />

              {/* Main node */}
              <div style={{
                width: agent.id === "cortex" ? 90 : 70,
                height: agent.id === "cortex" ? 90 : 70,
                borderRadius: "50%",
                background: isActive
                  ? `radial-gradient(circle, ${agent.color}33, ${agent.color}11)`
                  : "rgba(15,15,25,0.9)",
                border: `2px solid ${isActive ? agent.color : agent.color + "44"}`,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                boxShadow: isActive ? `0 0 30px ${agent.glow}, 0 0 60px ${agent.glow}` : `0 0 10px ${agent.glow}`,
                transition: "all 0.3s ease",
                transform: "translate(-50%, -50%)",
              }}>
                <div style={{
                  fontSize: agent.id === "cortex" ? 28 : 20,
                  color: agent.color,
                  lineHeight: 1
                }}>
                  {agent.icon}
                </div>
                <div style={{
                  fontSize: 8,
                  letterSpacing: 1.5,
                  color: agent.color,
                  fontWeight: 700,
                  marginTop: 3
                }}>
                  {agent.name}
                </div>
              </div>

              {/* Label below node */}
              <div style={{
                position: "absolute",
                top: "100%",
                left: "50%",
                transform: "translateX(-50%)",
                marginTop: agent.id === "cortex" ? 55 : 42,
                fontSize: 9,
                color: isActive ? agent.color : "#64748B",
                whiteSpace: "nowrap",
                letterSpacing: 1,
                transition: "color 0.3s",
                textAlign: "center"
              }}>
                {agent.subtitle}
              </div>
            </div>
          );
        })}
      </div>

      {/* Selected Agent Detail Panel */}
      {selectedAgent && (
        <div style={{
          maxWidth: 800,
          margin: "0 auto 40px",
          padding: "0 24px",
          animation: "slide-in 0.3s ease",
          zIndex: 10,
          position: "relative"
        }}>
          <div style={{
            background: `linear-gradient(135deg, ${selectedAgent.color}11, rgba(15,15,25,0.95))`,
            border: `1px solid ${selectedAgent.color}44`,
            borderRadius: 16,
            padding: 28,
            boxShadow: `0 0 40px ${selectedAgent.glow}`
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 20 }}>
              <div style={{
                fontSize: 36, color: selectedAgent.color,
                textShadow: `0 0 20px ${selectedAgent.color}`
              }}>
                {selectedAgent.icon}
              </div>
              <div>
                <div style={{ fontSize: 22, fontWeight: 700, color: selectedAgent.color, letterSpacing: 3 }}>
                  {selectedAgent.name}
                </div>
                <div style={{ fontSize: 11, color: "#94A3B8", letterSpacing: 2 }}>
                  {selectedAgent.subtitle}
                </div>
              </div>
            </div>

            <p style={{ color: "#CBD5E1", lineHeight: 1.8, marginBottom: 20, fontSize: 14 }}>
              {selectedAgent.description}
            </p>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 20 }}>
              {selectedAgent.powers.map((power, i) => (
                <div key={i} style={{
                  display: "flex", alignItems: "center", gap: 8,
                  background: "rgba(255,255,255,0.03)",
                  padding: "8px 12px",
                  borderRadius: 8,
                  border: `1px solid ${selectedAgent.color}22`,
                  fontSize: 12, color: "#94A3B8"
                }}>
                  <div style={{ width: 4, height: 4, borderRadius: "50%", background: selectedAgent.color, flexShrink: 0 }} />
                  {power}
                </div>
              ))}
            </div>

            <div style={{
              background: `${selectedAgent.color}11`,
              border: `1px solid ${selectedAgent.color}33`,
              borderRadius: 10,
              padding: "12px 16px",
              fontSize: 12,
              color: selectedAgent.color,
              display: "flex", gap: 10, alignItems: "center"
            }}>
              <span style={{ fontSize: 16 }}>🧠</span>
              <strong>ND Superpower:</strong> {selectedAgent.nd_feature}
            </div>
          </div>
        </div>
      )}

      {!selectedAgent && (
        <div style={{
          textAlign: "center", padding: "0 20px 20px",
          fontSize: 12, color: "#475569", letterSpacing: 1
        }}>
          ↑ TAP ANY AGENT TO EXPLORE ITS CAPABILITIES
        </div>
      )}

      {/* Core Principles */}
      <div style={{
        maxWidth: 800, margin: "0 auto 60px",
        padding: "0 24px", zIndex: 10, position: "relative"
      }}>
        <div style={{
          fontSize: 10, letterSpacing: 5, color: "#00FFD1",
          textAlign: "center", marginBottom: 24, opacity: 0.7
        }}>
          DESIGN PRINCIPLES
        </div>
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
          gap: 12
        }}>
          {PRINCIPLES.map((p, i) => (
            <div key={i} className="principle-card" style={{
              background: "rgba(255,255,255,0.02)",
              borderRadius: 12,
              padding: "16px 18px",
              cursor: "default"
            }}>
              <div style={{ fontSize: 24, marginBottom: 8 }}>{p.icon}</div>
              <div style={{ fontSize: 12, fontWeight: 700, color: "#E2E8F0", marginBottom: 6, letterSpacing: 1 }}>
                {p.title}
              </div>
              <div style={{ fontSize: 11, color: "#64748B", lineHeight: 1.7 }}>{p.text}</div>
            </div>
          ))}
        </div>
      </div>

      {/* What Makes NEXUS Different */}
      <div style={{
        maxWidth: 800, margin: "0 auto 60px",
        padding: "0 24px", zIndex: 10, position: "relative"
      }}>
        <div style={{
          background: "linear-gradient(135deg, rgba(189,0,255,0.08), rgba(0,255,209,0.08))",
          border: "1px solid rgba(189,0,255,0.2)",
          borderRadius: 20,
          padding: 32
        }}>
          <div style={{ fontSize: 10, letterSpacing: 5, color: "#BD00FF", marginBottom: 16, opacity: 0.8 }}>
            THE BIG IDEA
          </div>
          <div style={{
            fontSize: "clamp(20px, 4vw, 32px)",
            fontWeight: 700,
            lineHeight: 1.4,
            color: "#F1F5F9",
            marginBottom: 20
          }}>
            Every agent system ever built was designed for neurotypical, linear thinkers.
            <span style={{
              background: "linear-gradient(135deg, #00FFD1, #BD00FF)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent"
            }}> NEXUS is the first one built for the way ND brains actually work.</span>
          </div>
          <div style={{ color: "#94A3B8", fontSize: 13, lineHeight: 1.9 }}>
            Non-linear. Pattern-jumping. Hyperfocused. Variable-energy. Context-rich. 
            Creatively explosive. These aren't limitations — they're a completely different 
            cognitive architecture that current systems punish instead of serve. 
            NEXUS doesn't ask you to mask your thinking style. It meets you exactly where you are.
          </div>
        </div>
      </div>

      {/* Footer signal */}
      <div style={{
        textAlign: "center", paddingBottom: 40,
        fontSize: 10, letterSpacing: 4, color: "#1E293B"
      }}>
        NEXUS v1.0 — DESIGNED FOR DIFFERENTLY WIRED MINDS
      </div>
    </div>
  );
}
