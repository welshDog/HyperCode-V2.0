"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Activity, 
  Terminal, 
  Cpu, 
  Shield, 
  Zap, 
  Database, 
  Layout, 
  Send,
  AlertTriangle,
  CheckCircle,
  Clock,
  Server
} from "lucide-react";
import clsx from "clsx";

// --- Mock Data ---
const MOCK_AGENTS = [
  { id: "orchestrator", name: "Crew Orchestrator", role: "Commander", status: "online", cpu: 12, ram: 45 },
  { id: "backend", name: "Backend Specialist", role: "Engineer", status: "thinking", cpu: 65, ram: 60 },
  { id: "frontend", name: "Frontend Specialist", role: "Designer", status: "idle", cpu: 5, ram: 20 },
  { id: "db-architect", name: "DB Architect", role: "Engineer", status: "idle", cpu: 2, ram: 15 },
  { id: "coder", name: "Coder Agent", role: "Builder", status: "coding", cpu: 88, ram: 75 },
];

const MOCK_LOGS = [
  { id: 1, agent: "orchestrator", level: "info", msg: "Received new mission: Test 3 Protocol", time: "16:13:26" },
  { id: 2, agent: "db-architect", level: "info", msg: "Analyzing schema requirements for 'todos' table...", time: "16:13:27" },
  { id: 3, agent: "db-architect", level: "success", msg: "Schema plan approved. Generating migrations.", time: "16:13:28" },
  { id: 4, agent: "backend", level: "info", msg: "Drafting API routes for CRUD operations.", time: "16:13:29" },
  { id: 5, agent: "frontend", level: "warn", msg: "Detected missing 'framer-motion' dependency. Adding to plan.", time: "16:13:30" },
  { id: 6, agent: "coder", level: "info", msg: "Writing file: components/TodoList.tsx", time: "16:13:31" },
];

const MOCK_TASKS = [
  { id: "t-003", title: "Build Todo App", status: "in_progress", progress: 75, steps: ["Schema", "API", "UI", "Integration"] },
  { id: "t-002", title: "User Profile", status: "completed", progress: 100, steps: ["Backend", "Frontend"] },
];

// --- Components ---

const AgentCard = ({ agent }: { agent: any }) => (
  <motion.div 
    layout
    initial={{ opacity: 0, x: -20 }}
    animate={{ opacity: 1, x: 0 }}
    className={clsx(
      "relative p-4 rounded-sm border-l-4 bg-zinc-900/50 backdrop-blur-sm transition-all hover:bg-zinc-800/50 group",
      agent.status === "online" ? "border-emerald-500" : 
      agent.status === "thinking" ? "border-cyan-500" :
      agent.status === "coding" ? "border-purple-500" :
      agent.status === "error" ? "border-red-500" : "border-zinc-700"
    )}
  >
    <div className="flex justify-between items-start">
      <div>
        <h3 className="font-bold text-sm tracking-wider uppercase text-zinc-300 group-hover:text-white">{agent.name}</h3>
        <p className="text-xs text-zinc-500 uppercase">{agent.role}</p>
      </div>
      <div className={clsx(
        "h-2 w-2 rounded-full animate-pulse",
        agent.status === "online" ? "bg-emerald-500" : 
        agent.status === "thinking" ? "bg-cyan-500 shadow-[0_0_10px_#00f0ff]" :
        agent.status === "coding" ? "bg-purple-500 shadow-[0_0_10px_#a855f7]" :
        agent.status === "error" ? "bg-red-500" : "bg-zinc-500"
      )} />
    </div>
    
    <div className="mt-4 space-y-2">
      <div className="flex justify-between text-[10px] text-zinc-400">
        <span>CPU</span>
        <span>{agent.cpu}%</span>
      </div>
      <div className="h-1 w-full bg-zinc-800 rounded-full overflow-hidden">
        <div 
          className="h-full bg-cyan-500/50 transition-all duration-500" 
          style={{ width: `${agent.cpu}%` }}
        />
      </div>
      
      <div className="flex justify-between text-[10px] text-zinc-400">
        <span>RAM</span>
        <span>{agent.ram}%</span>
      </div>
      <div className="h-1 w-full bg-zinc-800 rounded-full overflow-hidden">
        <div 
          className="h-full bg-purple-500/50 transition-all duration-500" 
          style={{ width: `${agent.ram}%` }}
        />
      </div>
    </div>
  </motion.div>
);

const LogEntry = ({ log }: { log: any }) => (
  <motion.div 
    initial={{ opacity: 0, x: -10 }}
    animate={{ opacity: 1, x: 0 }}
    className="flex gap-3 text-xs font-mono py-1 border-b border-zinc-900/50 hover:bg-zinc-900/30 px-2"
  >
    <span className="text-zinc-600 shrink-0">[{log.time}]</span>
    <span className={clsx(
      "font-bold w-24 shrink-0 truncate",
      log.agent === "orchestrator" ? "text-emerald-400" :
      log.agent === "coder" ? "text-purple-400" : "text-cyan-400"
    )}>{log.agent}</span>
    <span className={clsx(
      "truncate",
      log.level === "warn" ? "text-yellow-500" :
      log.level === "error" ? "text-red-500" :
      log.level === "success" ? "text-emerald-500" : "text-zinc-400"
    )}>{log.msg}</span>
  </motion.div>
);

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("live");
  const [input, setInput] = useState("");
  const [logs, setLogs] = useState(MOCK_LOGS);
  
  // Simulate live data
  useEffect(() => {
    const interval = setInterval(() => {
      // Randomly update CPU stats
      // In a real app, this would fetch from an API
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleCommand = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    const newLog = {
      id: Date.now(),
      agent: "USER",
      level: "info",
      msg: `Command issued: ${input}`,
      time: new Date().toLocaleTimeString([], { hour12: false })
    };
    
    setLogs(prev => [newLog, ...prev]);
    setInput("");
  };

  return (
    <div className="flex flex-col h-full scanline">
      {/* Header */}
      <header className="h-14 border-b border-zinc-800 bg-black/50 flex items-center justify-between px-6 shrink-0">
        <div className="flex items-center gap-4">
          <Activity className="text-cyan-500 animate-pulse" size={20} />
          <h1 className="text-lg font-bold tracking-[0.2em] text-cyan-500 glow-text">
            HYPERSTATION <span className="text-zinc-600 text-xs tracking-normal">ALPHA</span>
          </h1>
        </div>
        <div className="flex items-center gap-6 text-xs font-mono text-zinc-500">
          <div className="flex items-center gap-2">
            <Server size={14} />
            <span className="text-emerald-500">SYSTEM OPTIMAL</span>
          </div>
          <div className="flex items-center gap-2">
            <Clock size={14} />
            <span>STARDATE {new Date().toISOString().split('T')[0]}</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex overflow-hidden">
        
        {/* Left Panel: The Crew */}
        <aside className="w-64 border-r border-zinc-800 bg-black/20 flex flex-col p-4 gap-4 overflow-y-auto shrink-0">
          <h2 className="text-xs font-bold text-zinc-600 uppercase tracking-widest mb-2 flex items-center gap-2">
            <Shield size={12} /> Active Agents
          </h2>
          <div className="space-y-3">
            {MOCK_AGENTS.map(agent => (
              <AgentCard key={agent.id} agent={agent} />
            ))}
          </div>
        </aside>

        {/* Center Panel: Viewport */}
        <section className="flex-1 flex flex-col min-w-0 bg-black/40 relative">
          
          {/* Tabs */}
          <div className="flex border-b border-zinc-800">
            {['live', 'neural', 'tasks'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={clsx(
                  "px-6 py-3 text-xs font-bold uppercase tracking-wider transition-colors border-r border-zinc-800",
                  activeTab === tab 
                    ? "bg-cyan-950/30 text-cyan-400 border-b-2 border-b-cyan-500" 
                    : "text-zinc-600 hover:text-zinc-300 hover:bg-zinc-900"
                )}
              >
                {tab === 'live' ? 'Live Ops' : tab === 'neural' ? 'Neural Net' : 'Mission Log'}
              </button>
            ))}
          </div>

          {/* Viewport Content */}
          <div className="flex-1 overflow-y-auto p-4 font-mono relative">
            {activeTab === 'live' && (
              <div className="space-y-1">
                <div className="sticky top-0 bg-black/80 backdrop-blur-md border-b border-zinc-800 p-2 mb-4 text-xs text-cyan-600 font-bold flex justify-between">
                  <span>// SYSTEM_LOGS_STREAM_V2.0</span>
                  <span className="animate-pulse">● LIVE</span>
                </div>
                <div className="flex flex-col-reverse gap-1 min-h-0">
                   {logs.map(log => <LogEntry key={log.id} log={log} />)}
                </div>
              </div>
            )}
            
            {activeTab === 'neural' && (
              <div className="h-full flex items-center justify-center text-zinc-700 flex-col gap-4">
                 <Layout size={64} className="animate-spin-slow opacity-20" />
                 <p className="text-xs tracking-widest">NEURAL LINK VISUALIZATION OFFLINE</p>
                 <p className="text-[10px]">Connecting to agent swarm...</p>
              </div>
            )}

            {activeTab === 'tasks' && (
               <div className="space-y-4">
                 {MOCK_TASKS.map(task => (
                   <div key={task.id} className="border border-zinc-800 bg-zinc-900/20 p-4 rounded-sm">
                      <div className="flex justify-between mb-2">
                        <h3 className="font-bold text-cyan-400">{task.title}</h3>
                        <span className="text-xs px-2 py-0.5 rounded bg-zinc-800 text-zinc-400 uppercase">{task.status}</span>
                      </div>
                      <div className="h-1 bg-zinc-800 w-full rounded-full overflow-hidden">
                        <div className="h-full bg-emerald-500 transition-all" style={{ width: `${task.progress}%` }} />
                      </div>
                      <div className="flex gap-2 mt-3">
                        {task.steps.map((step, i) => (
                           <div key={i} className="text-[10px] bg-zinc-900 border border-zinc-700 px-2 py-1 rounded text-zinc-500">
                             {step}
                           </div>
                        ))}
                      </div>
                   </div>
                 ))}
               </div>
            )}
          </div>

          {/* Command Input */}
          <div className="h-16 border-t border-zinc-800 bg-black/60 backdrop-blur p-3">
             <form onSubmit={handleCommand} className="flex gap-2 h-full">
                <div className="flex items-center justify-center w-10 bg-zinc-900 border border-zinc-700 text-cyan-500">
                  <Terminal size={18} />
                </div>
                <input 
                  type="text" 
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Enter directive..."
                  className="flex-1 bg-transparent border-b border-zinc-700 text-cyan-400 font-mono focus:outline-none focus:border-cyan-500 transition-colors placeholder:text-zinc-700"
                />
                <button 
                  type="submit"
                  className="px-6 bg-cyan-900/20 border border-cyan-800 text-cyan-400 hover:bg-cyan-500 hover:text-black transition-all font-bold uppercase text-xs tracking-wider flex items-center gap-2"
                >
                  Execute <Send size={14} />
                </button>
             </form>
          </div>
        </section>

        {/* Right Panel: Telemetry */}
        <aside className="w-72 border-l border-zinc-800 bg-black/20 p-4 flex flex-col gap-6 overflow-y-auto shrink-0 hidden xl:flex">
          
          <div>
            <h2 className="text-xs font-bold text-zinc-600 uppercase tracking-widest mb-4 flex items-center gap-2">
               <Zap size={12} /> Resource Usage
            </h2>
            <div className="space-y-4">
               {/* Mock Charts */}
               <div className="h-32 border border-zinc-800 bg-zinc-900/30 relative overflow-hidden flex items-end gap-1 p-2">
                  {[40, 60, 30, 80, 50, 90, 70, 40, 60, 50].map((h, i) => (
                    <div key={i} className="flex-1 bg-cyan-500/20 hover:bg-cyan-500/50 transition-colors" style={{ height: `${h}%` }} />
                  ))}
                  <div className="absolute top-2 left-2 text-[10px] text-zinc-500">CPU LOAD</div>
               </div>
               
               <div className="h-32 border border-zinc-800 bg-zinc-900/30 relative overflow-hidden flex items-end gap-1 p-2">
                  {[20, 30, 25, 40, 35, 30, 45, 50, 60, 55].map((h, i) => (
                    <div key={i} className="flex-1 bg-purple-500/20 hover:bg-purple-500/50 transition-colors" style={{ height: `${h}%` }} />
                  ))}
                  <div className="absolute top-2 left-2 text-[10px] text-zinc-500">MEMORY ALLOCATION</div>
               </div>
            </div>
          </div>

          <div>
            <h2 className="text-xs font-bold text-zinc-600 uppercase tracking-widest mb-4 flex items-center gap-2">
               <Database size={12} /> Database Health
            </h2>
            <div className="grid grid-cols-2 gap-2">
               <div className="bg-zinc-900/50 p-3 border border-zinc-800 rounded flex flex-col items-center">
                  <span className="text-2xl font-bold text-emerald-500">98%</span>
                  <span className="text-[10px] text-zinc-500 uppercase">Uptime</span>
               </div>
               <div className="bg-zinc-900/50 p-3 border border-zinc-800 rounded flex flex-col items-center">
                  <span className="text-2xl font-bold text-cyan-500">42ms</span>
                  <span className="text-[10px] text-zinc-500 uppercase">Latency</span>
               </div>
            </div>
          </div>

          <div className="mt-auto border-t border-zinc-800 pt-4">
             <div className="flex items-center gap-3 text-xs text-zinc-500">
               <AlertTriangle size={14} className="text-yellow-600" />
               <span>2 Warnings in last hour</span>
             </div>
             <div className="flex items-center gap-3 text-xs text-zinc-500 mt-2">
               <CheckCircle size={14} className="text-emerald-600" />
               <span>System Integrity Verified</span>
             </div>
          </div>

        </aside>
      </main>
    </div>
  );
}
