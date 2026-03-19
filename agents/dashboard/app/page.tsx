"use client";

import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { 
  Activity, 
  Terminal, 
  Shield, 
  Zap, 
  Database, 
  Send,
  CheckCircle,
  Clock as ClockIcon,
  Server,
  Wifi,
  WifiOff
} from "lucide-react";
import clsx from "clsx";
import { fetchAgents, fetchLogs, fetchTasks, checkHealth, sendCommand, API_BASE_URL, login, type Task } from "@/lib/api";
import { Clock } from "@/components/Clock";
import { ApprovalModal } from "@/components/ApprovalModal";
import { SystemHealth } from "@/components/SystemHealth";
import { MetricsPanel } from "@/components/MetricsPanel";
import { BroskiWalletWidget } from "@/components/BroskiWalletWidget";
import { CognitiveLoadMeter } from "@/components/CognitiveLoadMeter";
import { HyperfocusTimer } from "@/components/HyperfocusTimer";
import NeuralViz from "@/components/NeuralViz";
import CognitiveUplink from "@/components/CognitiveUplink";
import { HyperCanvas } from "@/components/canvas/HyperCanvas";
import { SensoryThemeSwitcher } from "@/app/themes/SensoryThemeSwitcher";
import { LiveRegion } from "@/components/a11y/LiveRegion";
import { diffAgentStatusAnnouncements, type AgentSnapshot } from "@/lib/a11y";

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

// --- Components ---

const AgentCard = ({ agent }: { agent: Agent }) => (
  <motion.li 
    layout
    initial={{ opacity: 0, x: -20 }}
    animate={{ opacity: 1, x: 0 }}
    aria-label={`${agent.name} (${agent.role}) status ${agent.status}`}
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
      <div aria-hidden="true" className={clsx(
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
      <div
        className="h-1 w-full bg-zinc-800 rounded-full overflow-hidden"
        role="progressbar"
        aria-label={`${agent.name} CPU usage`}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={agent.cpu}
      >
        <div 
          className="h-full bg-cyan-500/50 transition-all duration-500" 
          style={{ width: `${agent.cpu}%` }}
        />
      </div>
      
      <div className="flex justify-between text-[10px] text-zinc-400">
        <span>RAM</span>
        <span>{agent.ram}%</span>
      </div>
      <div
        className="h-1 w-full bg-zinc-800 rounded-full overflow-hidden"
        role="progressbar"
        aria-label={`${agent.name} RAM usage`}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={agent.ram}
      >
        <div 
          className="h-full bg-purple-500/50 transition-all duration-500" 
          style={{ width: `${agent.ram}%` }}
        />
      </div>
    </div>
  </motion.li>
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
  const [token, setToken] = useState<string>(() => {
    if (typeof window === "undefined") return "";
    return localStorage.getItem("token") ?? "";
  });
  const [loginUsername, setLoginUsername] = useState("admin@hypercode.ai");
  const [loginPassword, setLoginPassword] = useState("adminpassword");
  const [loginError, setLoginError] = useState<string>("");
  
  // Data State
  const [agents, setAgents] = useState<Agent[]>([]);
  const [logs, setLogs] = useState<Log[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [connected, setConnected] = useState(false);
  const [logsBusy, setLogsBusy] = useState(false);
  const [srPolite, setSrPolite] = useState("");
  const [srAssertive, setSrAssertive] = useState("");
  const prevConnectedRef = useRef<boolean | null>(null);
  const prevAgentsRef = useRef<Map<string | number, AgentSnapshot>>(new Map());

  const announcePolite = (msg: string) => {
    if (!msg) return;
    window.setTimeout(() => {
      setSrPolite(msg);
      window.setTimeout(() => setSrPolite(""), 750);
    }, 0);
  };

  const announceAssertive = (msg: string) => {
    if (!msg) return;
    window.setTimeout(() => {
      setSrAssertive(msg);
      window.setTimeout(() => setSrAssertive(""), 750);
    }, 0);
  };

  // Poll for data
  useEffect(() => {
    const poll = async () => {
      const isHealthy = await checkHealth();
      setConnected(isHealthy);
      
      if (isHealthy && token) {
        setLogsBusy(true);
        const [agentsData, logsData, tasksData] = await Promise.all([
          fetchAgents(token),
          fetchLogs(token),
          fetchTasks(token)
        ]);
        
        if (agentsData.length > 0) setAgents(agentsData);
        if (logsData.length > 0) setLogs(logsData);
        if (tasksData.length > 0) setTasks(tasksData);
        setLogsBusy(false);
      }
    };

    poll(); // Initial call
    const interval = setInterval(poll, 2000); // Poll every 2s
    return () => clearInterval(interval);
  }, [token]);

  useEffect(() => {
    if (prevConnectedRef.current === null) {
      prevConnectedRef.current = connected;
      return;
    }
    if (prevConnectedRef.current !== connected) {
      announcePolite(`API ${connected ? "connected" : "offline"}`);
      prevConnectedRef.current = connected;
    }
  }, [connected]);

  useEffect(() => {
    const { polite, assertive, nextMap } = diffAgentStatusAnnouncements(prevAgentsRef.current, agents);
    prevAgentsRef.current = nextMap;
    if (assertive.length > 0) announceAssertive(assertive[0]);
    else if (polite.length > 0) announcePolite(polite[0]);
  }, [agents]);

  const handleLogin = async () => {
    setLoginError("");
    const result = await login(loginUsername, loginPassword);
    if (!result) {
      setLoginError("Login failed");
      return;
    }
    if (typeof window !== "undefined") {
      localStorage.setItem("token", result.access_token);
    }
    setToken(result.access_token);
  };

  const handleCommand = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    // Optimistic log
    const newLog: Log = {
      id: Date.now(),
      agent: "USER",
      level: "info",
      msg: `Command issued: ${input}`,
      time: new Date().toLocaleTimeString([], { hour12: false })
    };
    setLogs(prev => [newLog, ...prev]);
    
    // Send to API
    const res = await sendCommand(input, token);
    
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
      <LiveRegion message={srPolite} politeness="polite" atomic relevant="additions text" />
      <LiveRegion message={srAssertive} politeness="assertive" atomic relevant="additions text" />
      <ApprovalModal />
      {/* Header */}
      <header className="h-14 border-b border-zinc-800 bg-black/50 flex items-center justify-between px-6 shrink-0">
        <div className="flex items-center gap-4">
          <Activity className="text-cyan-500 animate-pulse" size={20} aria-hidden="true" />
          <h1 className="text-lg font-bold tracking-[0.2em] text-cyan-500 glow-text">
            HYPERSTATION <span className="text-zinc-600 text-xs tracking-normal">BETA</span>
          </h1>
        </div>
        <div className="flex items-center gap-6 text-xs font-mono text-zinc-500">
          <SensoryThemeSwitcher />
           <div className="flex items-center gap-2" title={`API: ${API_BASE_URL}`} role="status" aria-live="polite" aria-label={`API status: ${connected ? "connected" : "offline"}`}>
            {connected ? <Wifi size={14} className="text-emerald-500" aria-hidden="true" /> : <WifiOff size={14} className="text-red-500" aria-hidden="true" />}
            <span className={connected ? "text-emerald-500" : "text-red-500"}>
                {connected ? "CONNECTED" : "OFFLINE"}
            </span>
          </div>
          <div className="flex items-center gap-2" role="status" aria-live="polite">
            <Server size={14} aria-hidden="true" />
            <span className="text-emerald-500">SYSTEM OPTIMAL</span>
          </div>
          <div className="flex items-center gap-2">
            <ClockIcon size={14} aria-hidden="true" />
            <Clock />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* Left Panel: The Crew */}
        <aside className="w-64 border-r border-zinc-800 bg-black/20 flex flex-col p-4 gap-4 overflow-y-auto shrink-0" aria-label="Active agents">
          <h2 className="text-xs font-bold text-zinc-600 uppercase tracking-widest mb-2 flex items-center gap-2">
            <Shield size={12} aria-hidden="true" /> Active Agents
          </h2>
          <ul className="space-y-3" aria-label="Agent list">
            {agents.length === 0 && !connected && (
                <li className="text-xs text-zinc-500 text-center py-4" aria-live="polite">Connecting to Neural Net...</li>
            )}
            {agents.map(agent => (
              <AgentCard key={agent.id} agent={agent} />
            ))}
          </ul>
        </aside>

        {/* Center Panel: Viewport */}
        <section className="flex-1 flex flex-col min-w-0 bg-black/40 relative">
          
          {/* Tabs */}
          <div className="flex border-b border-zinc-800" role="tablist" aria-label="Dashboard views">
            {['uplink', 'hyperflow', 'live', 'neural', 'tasks'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                role="tab"
                aria-selected={activeTab === tab}
                aria-controls={`panel-${tab}`}
                id={`tab-${tab}`}
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
          <div className="flex-1 overflow-y-auto p-0 font-mono relative bg-black">
            {activeTab === 'uplink' && (
               <div className="flex flex-col h-full" role="tabpanel" id="panel-uplink" aria-labelledby="tab-uplink" tabIndex={0}>
                  <div className="p-6 pb-0">
                     <div className="grid grid-cols-1 xl:grid-cols-5 gap-4 items-start">
                       <div className="xl:col-span-2">
                         <MetricsPanel />
                       </div>
                       <BroskiWalletWidget />
                       <CognitiveLoadMeter connected={connected} agents={agents} tasks={tasks} logs={logs} />
                       <HyperfocusTimer />
                     </div>
                  </div>
                  <div className="flex-1 min-h-0">
                     <CognitiveUplink />
                  </div>
               </div>
            )}

            {activeTab === 'hyperflow' && (
              <div className="h-full w-full rounded-lg overflow-hidden border border-zinc-800 relative" role="tabpanel" id="panel-hyperflow" aria-labelledby="tab-hyperflow" tabIndex={0} aria-label="HyperFlow editor">
                 <div className="absolute top-2 left-2 z-10 text-[10px] text-cyan-500 bg-black/50 px-2 py-1 rounded border border-cyan-900/50" aria-hidden="true">
                   HYPERFLOW EDITOR v1.0
                 </div>
                 <HyperCanvas />
              </div>
            )}

            {activeTab === 'live' && (
              <div className="space-y-1" role="tabpanel" id="panel-live" aria-labelledby="tab-live" tabIndex={0} aria-label="Live operations logs">
                <div className="sticky top-0 bg-black/80 backdrop-blur-md border-b border-zinc-800 p-2 mb-4 text-xs text-cyan-600 font-bold flex justify-between">
                  <span>{/* SYSTEM_LOGS_STREAM_V2.0 */}</span>
                  <span className="animate-pulse" aria-hidden="true">● LIVE</span>
                </div>
                <div className="flex flex-col-reverse gap-1 min-h-0" aria-live="off" aria-label="Log stream" aria-busy={logsBusy}>
                   {logs.map((log, i) => <LogEntry key={log.id || i} log={log} />)}
                </div>
              </div>
            )}
            
            {activeTab === 'neural' && (
              <div className="h-full flex items-center justify-center text-zinc-700 flex-col gap-4" role="tabpanel" id="panel-neural" aria-labelledby="tab-neural" tabIndex={0} aria-label="Neural network view">
                 <NeuralViz />
              </div>
            )}

            {activeTab === 'tasks' && (
               <div className="space-y-4" role="tabpanel" id="panel-tasks" aria-labelledby="tab-tasks" tabIndex={0} aria-label="Mission log">
                 {tasks.map(task => (
                   <div key={task.id} className="border border-zinc-800 bg-zinc-900/20 p-4 rounded-sm">
                      <div className="flex justify-between mb-2">
                        <h3 className="font-bold text-cyan-400">{task.description || task.title}</h3>
                        <span className="text-xs px-2 py-0.5 rounded bg-zinc-800 text-zinc-400 uppercase">{task.status}</span>
                      </div>
                      <div className="h-1 bg-zinc-800 w-full rounded-full overflow-hidden" role="progressbar" aria-label={`Task progress: ${task.description || task.title || task.id}`} aria-valuemin={0} aria-valuemax={100} aria-valuenow={task.progress || 0}>
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
                <div className="flex items-center justify-center w-10 bg-zinc-900 border border-zinc-700 text-cyan-500" aria-hidden="true">
                  <Terminal size={18} aria-hidden="true" />
                </div>
                <label className="sr-only" htmlFor="command-input">Command</label>
                <input 
                  id="command-input"
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
                  Execute <Send size={14} aria-hidden="true" />
                </button>
             </form>
          </div>
        </section>

        {/* Right Panel: Telemetry */}
        <aside className="w-72 border-l border-zinc-800 bg-black/20 p-4 flex flex-col gap-6 overflow-y-auto shrink-0 hidden xl:flex">
          
          <SystemHealth />

          <div>
            <h2 className="text-xs font-bold text-zinc-600 uppercase tracking-widest mb-4 flex items-center gap-2">
               <Zap size={12} aria-hidden="true" /> Resource Usage
            </h2>
            <div className="space-y-4">
               {/* Mock Charts */}
               <div className="h-32 border border-zinc-800 bg-zinc-900/30 relative overflow-hidden flex items-end gap-1 p-2">
                  {[40, 60, 30, 80, 50, 90, 70, 40, 60, 50].map((h, i) => (
                    <div key={i} className="flex-1 bg-cyan-500/20 hover:bg-cyan-500/50 transition-colors" style={{ height: `${h}%` }} aria-hidden="true" />
                  ))}
                  <div className="absolute top-2 left-2 text-[10px] text-zinc-500">CPU LOAD</div>
               </div>
               
               <div className="h-32 border border-zinc-800 bg-zinc-900/30 relative overflow-hidden flex items-end gap-1 p-2">
                  {[20, 30, 25, 40, 35, 30, 45, 50, 60, 55].map((h, i) => (
                    <div key={i} className="flex-1 bg-purple-500/20 hover:bg-purple-500/50 transition-colors" style={{ height: `${h}%` }} aria-hidden="true" />
                  ))}
                  <div className="absolute top-2 left-2 text-[10px] text-zinc-500">MEMORY ALLOCATION</div>
               </div>
            </div>
          </div>

          <div>
            <h2 className="text-xs font-bold text-zinc-600 uppercase tracking-widest mb-4 flex items-center gap-2">
               <Database size={12} aria-hidden="true" /> Database Health
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
               <AlertTriangle size={14} className="text-yellow-600" aria-hidden="true" />
               <span>2 Warnings in last hour</span>
             </div>
             <div className="flex items-center gap-3 text-xs text-zinc-500 mt-2">
               <CheckCircle size={14} className="text-emerald-600" aria-hidden="true" />
               <span>System Integrity Verified</span>
             </div>
          </div>

        </aside>
      </div>

      {!token && (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4" role="dialog" aria-modal="true" aria-labelledby="auth-title">
          <div className="w-full max-w-md bg-zinc-900 border border-zinc-700 rounded-lg p-6">
            <h2 id="auth-title" className="text-cyan-400 font-bold tracking-widest uppercase text-sm mb-4">Authenticate</h2>
            <label className="block text-xs text-zinc-500 uppercase mb-1" htmlFor="login-email">Email</label>
            <input
              id="login-email"
              className="w-full bg-black/40 border border-zinc-700 rounded p-2 mb-4 text-sm"
              value={loginUsername}
              onChange={(e) => setLoginUsername(e.target.value)}
              placeholder="admin@hypercode.ai"
            />
            <label className="block text-xs text-zinc-500 uppercase mb-1" htmlFor="login-password">Password</label>
            <input
              id="login-password"
              type="password"
              className="w-full bg-black/40 border border-zinc-700 rounded p-2 mb-4 text-sm"
              value={loginPassword}
              onChange={(e) => setLoginPassword(e.target.value)}
              placeholder="adminpassword"
            />
            {loginError && <div className="text-red-400 text-xs mb-3">{loginError}</div>}
            <button
              onClick={handleLogin}
              className="w-full py-2 bg-cyan-700 hover:bg-cyan-600 rounded font-bold text-sm"
            >
              SIGN IN
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
