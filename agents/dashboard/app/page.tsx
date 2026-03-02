"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Activity, 
  Terminal, 
  Shield, 
  Zap, 
  Database, 
  Send,
  AlertTriangle,
  CheckCircle,
  Clock as ClockIcon,
  Server,
  Wifi,
  WifiOff
} from "lucide-react";
import clsx from "clsx";
import { fetchAgents, fetchLogs, fetchTasks, checkHealth, sendCommand, API_BASE_URL } from "@/lib/api";
import { Clock } from "@/components/Clock";
import { ApprovalModal } from "@/components/ApprovalModal";
import { SystemHealth } from "@/components/SystemHealth";
import NeuralViz from "@/components/NeuralViz";
import CognitiveUplink from "@/components/CognitiveUplink";
import { HyperCanvas } from "@/components/canvas/HyperCanvas";

// --- Type Definitions ---
interface Agent {
  id: number | string;
  name: string;
  role: string;
  status: 'online' | 'working' | 'thinking' | 'coding' | 'error' | 'offline';
  cpu: number;
  ram: number;
}

interface Log {
  id: number | string;
  time: string;
  agent: string;
  level: 'info' | 'warn' | 'error' | 'success';
  msg: string;
}

interface Task {
  id: number | string;
  description: string;
  title: string;
  status: string;
  progress: number;
}


// --- Components ---

const AgentCard = ({ agent }: { agent: Agent }) => (
  <motion.div 
    layout
    initial={{ opacity: 0, x: -20 }}
    animate={{ opacity: 1, x: 0 }}
    className={clsx(
      "relative p-4 rounded-sm border-l-4 bg-zinc-900/50 backdrop-blur-sm transition-all cursor-default",
      agent.status === "online" || agent.status === "working" ? "border-emerald-500" : 
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
        agent.status === "online" || agent.status === "working" ? "bg-emerald-500" : 
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

const LogEntry = ({ log }: { log: Log }) => (
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
  const [activeTab, setActiveTab] = useState("uplink");
  const [input, setInput] = useState("");
  
  // Data State
  const [agents, setAgents] = useState<Agent[]>([]);
  const [logs, setLogs] = useState<Log[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [connected, setConnected] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  // Poll for data
  useEffect(() => {
    const poll = async () => {
      const isHealthy = await checkHealth();
      setConnected(isHealthy);
      
      if (isHealthy) {
        const [agentsData, logsData, tasksData] = await Promise.all([
          fetchAgents(),
          fetchLogs(),
          fetchTasks()
        ]);
        
        if (agentsData.length > 0) setAgents(agentsData);
        if (logsData.length > 0) setLogs(logsData);
        if (tasksData.length > 0) setTasks(tasksData);
        setLastUpdated(new Date());
      }
    };

    poll(); // Initial call
    const interval = setInterval(poll, 2000); // Poll every 2s
    return () => clearInterval(interval);
  }, []);

  const handleCommand = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    // Optimistic log
    const newLog = {
      id: Date.now(),
      agent: "USER",
      level: "info",
      msg: `Command issued: ${input}`,
      time: new Date().toLocaleTimeString([], { hour12: false })
    };
    setLogs(prev => [newLog, ...prev]);
    
    // Send to API
    const res = await sendCommand(input);
    
    if (res.status === "error") {
         setLogs(prev => [{
            id: Date.now() + 1,
            agent: "SYSTEM",
            level: "error",
            msg: `Command failed: ${res.message}`,
            time: new Date().toLocaleTimeString([], { hour12: false })
         }, ...prev]);
    } else if (res.status === "ignored") {
         setLogs(prev => [{
            id: Date.now() + 1,
            agent: "SYSTEM",
            level: "warn",
            msg: res.message,
            time: new Date().toLocaleTimeString([], { hour12: false })
         }, ...prev]);
    }

    setInput("");
  };

  return (
    <div className="flex flex-col h-full scanline">
      <ApprovalModal />
      {/* Header */}
      <header className="h-14 border-b border-zinc-800 bg-black/50 flex items-center justify-between px-6 shrink-0">
        <div className="flex items-center gap-4">
          <Activity className="text-cyan-500 animate-pulse" size={20} />
          <h1 className="text-lg font-bold tracking-[0.2em] text-cyan-500 glow-text">
            HYPERSTATION <span className="text-zinc-600 text-xs tracking-normal">BETA</span>
          </h1>
        </div>
        <div className="flex items-center gap-6 text-xs font-mono text-zinc-500">
           <div className="flex items-center gap-2" title={`API: ${API_BASE_URL}`}>
            {connected ? <Wifi size={14} className="text-emerald-500" /> : <WifiOff size={14} className="text-red-500" />}
            <span className={connected ? "text-emerald-500" : "text-red-500"}>
                {connected ? "CONNECTED" : "OFFLINE"}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Server size={14} />
            <span className="text-emerald-500">SYSTEM OPTIMAL</span>
          </div>
          <div className="flex items-center gap-2">
            <ClockIcon size={14} />
            <Clock />
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
            {agents.length === 0 && !connected && (
                <div className="text-xs text-zinc-500 text-center py-4">Connecting to Neural Net...</div>
            )}
            {agents.map(agent => (
              <AgentCard key={agent.id} agent={agent} />
            ))}
          </div>
        </aside>

        {/* Center Panel: Viewport */}
        <section className="flex-1 flex flex-col min-w-0 bg-black/40 relative">
          
          {/* Tabs */}
          <div className="flex border-b border-zinc-800">
            {['uplink', 'hyperflow', 'live', 'neural', 'tasks'].map(tab => (
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
                {tab === 'uplink' ? 'Mission Control' : 
                 tab === 'hyperflow' ? 'HyperFlow' : 
                 tab === 'live' ? 'Live Ops' : 
                 tab === 'neural' ? 'Neural Net' : 'Mission Log'}
              </button>
            ))}
          </div>

          {/* Viewport Content */}
          <div className="flex-1 overflow-y-auto p-4 font-mono relative">
            {activeTab === 'uplink' && (
              <div className="h-full flex items-center justify-center">
                 <CognitiveUplink />
              </div>
            )}

            {activeTab === 'hyperflow' && (
              <div className="h-full w-full rounded-lg overflow-hidden border border-zinc-800 relative">
                 <div className="absolute top-2 left-2 z-10 text-[10px] text-cyan-500 bg-black/50 px-2 py-1 rounded border border-cyan-900/50">
                   HYPERFLOW EDITOR v1.0
                 </div>
                 <HyperCanvas />
              </div>
            )}

            {activeTab === 'live' && (
              <div className="space-y-1">
                <div className="sticky top-0 bg-black/80 backdrop-blur-md border-b border-zinc-800 p-2 mb-4 text-xs text-cyan-600 font-bold flex justify-between">
                  <span>{/* SYSTEM_LOGS_STREAM_V2.0 */}</span>
                  <span className="animate-pulse">● LIVE</span>
                </div>
                <div className="flex flex-col-reverse gap-1 min-h-0">
                   {logs.map((log, i) => <LogEntry key={log.id || i} log={log} />)}
                </div>
              </div>
            )}
            
            {activeTab === 'neural' && (
              <div className="h-full flex items-center justify-center text-zinc-700 flex-col gap-4">
                 <NeuralViz />
              </div>
            )}

            {activeTab === 'tasks' && (
               <div className="space-y-4">
                 {tasks.map(task => (
                   <div key={task.id} className="border border-zinc-800 bg-zinc-900/20 p-4 rounded-sm">
                      <div className="flex justify-between mb-2">
                        <h3 className="font-bold text-cyan-400">{task.description || task.title}</h3>
                        <span className="text-xs px-2 py-0.5 rounded bg-zinc-800 text-zinc-400 uppercase">{task.status}</span>
                      </div>
                      <div className="h-1 bg-zinc-800 w-full rounded-full overflow-hidden">
                        <div className="h-full bg-emerald-500 transition-all" style={{ width: `${task.progress || 0}%` }} />
                      </div>
                      <div className="flex gap-2 mt-3">
                         <div className="text-[10px] bg-zinc-900 border border-zinc-700 px-2 py-1 rounded text-zinc-500">
                             ID: {task.id}
                         </div>
                      </div>
                   </div>
                 ))}
                 {tasks.length === 0 && (
                     <div className="text-center text-zinc-600 py-10">No active missions. Standby.</div>
                 )}
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
                  placeholder="Enter directive (e.g., 'run: build a spaceship UI')..."
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
          
          <SystemHealth />

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
