'use client';

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { Network, Cpu, Share2, Activity, Shield, Code, Server, Database, Eye } from 'lucide-react';

// Agent Roles mapped to icons
const AGENT_ICONS: Record<string, any> = {
  'Project Strategist': Network,
  'Frontend Specialist': Eye,
  'Backend Specialist': Server,
  'Database Architect': Database,
  'QA Engineer': Shield,
  'DevOps Engineer': Cpu,
  'Security Engineer': Shield,
  'System Architect': Share2,
  'Coder Agent': Code,
};

const AGENTS = [
  { id: 'strategist', name: 'Project Strategist', x: 50, y: 10 },
  { id: 'frontend', name: 'Frontend Specialist', x: 20, y: 30 },
  { id: 'backend', name: 'Backend Specialist', x: 80, y: 30 },
  { id: 'db', name: 'Database Architect', x: 80, y: 70 },
  { id: 'qa', name: 'QA Engineer', x: 35, y: 90 },
  { id: 'devops', name: 'DevOps Engineer', x: 65, y: 90 },
  { id: 'security', name: 'Security Engineer', x: 50, y: 50 },
  { id: 'sysarch', name: 'System Architect', x: 50, y: 30 },
  { id: 'coder', name: 'Coder Agent', x: 20, y: 70 },
];

const CONNECTIONS = [
  ['strategist', 'sysarch'],
  ['sysarch', 'frontend'],
  ['sysarch', 'backend'],
  ['sysarch', 'security'],
  ['backend', 'db'],
  ['frontend', 'coder'],
  ['backend', 'coder'],
  ['coder', 'qa'],
  ['qa', 'devops'],
  ['devops', 'security'],
];

export default function NeuralViz() {
  const [activeSignals, setActiveSignals] = useState<{ id: string; from: string; to: string }[]>([]);

  // Simulate random data flow
  useEffect(() => {
    const interval = setInterval(() => {
      const randomConnection = CONNECTIONS[Math.floor(Math.random() * CONNECTIONS.length)];
      const signalId = Math.random().toString(36).substring(7);
      
      setActiveSignals(prev => [...prev, { id: signalId, from: randomConnection[0], to: randomConnection[1] }]);

      // Remove signal after animation
      setTimeout(() => {
        setActiveSignals(prev => prev.filter(s => s.id !== signalId));
      }, 2000);
    }, 1500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="relative w-full h-full bg-zinc-900/20 rounded-lg overflow-hidden border border-zinc-800">
      <div className="absolute inset-0 grid grid-cols-[repeat(20,minmax(0,1fr))] grid-rows-[repeat(20,minmax(0,1fr))] opacity-10 pointer-events-none">
        {Array.from({ length: 400 }).map((_, i) => (
          <div key={i} className="border-[0.5px] border-cyan-500/20" />
        ))}
      </div>

      <svg className="absolute inset-0 w-full h-full pointer-events-none">
        {CONNECTIONS.map(([startId, endId], i) => {
          const start = AGENTS.find(a => a.id === startId);
          const end = AGENTS.find(a => a.id === endId);
          if (!start || !end) return null;

          return (
            <g key={i}>
              <line
                x1={`${start.x}%`}
                y1={`${start.y}%`}
                x2={`${end.x}%`}
                y2={`${end.y}%`}
                stroke="#3f3f46"
                strokeWidth="2"
              />
              {/* Animated Signals */}
              {activeSignals.filter(s => s.from === startId && s.to === endId).map(signal => (
                <motion.circle
                  key={signal.id}
                  r="4"
                  fill="#06b6d4"
                  initial={{ cx: `${start.x}%`, cy: `${start.y}%` }}
                  animate={{ cx: `${end.x}%`, cy: `${end.y}%` }}
                  transition={{ duration: 1.5, ease: "linear" }}
                />
              ))}
            </g>
          );
        })}
      </svg>

      {AGENTS.map(agent => {
        const Icon = AGENT_ICONS[agent.name] || Activity;
        return (
          <div
            key={agent.id}
            className="absolute -translate-x-1/2 -translate-y-1/2 flex flex-col items-center gap-2"
            style={{ left: `${agent.x}%`, top: `${agent.y}%` }}
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              whileHover={{ scale: 1.1 }}
              className="w-12 h-12 rounded-full bg-zinc-900 border-2 border-cyan-500/50 flex items-center justify-center shadow-[0_0_15px_rgba(6,182,212,0.3)] z-10"
            >
              <Icon className="w-6 h-6 text-cyan-400" />
            </motion.div>
            <span className="text-[10px] font-mono text-zinc-400 bg-black/50 px-2 py-0.5 rounded backdrop-blur-sm whitespace-nowrap">
              {agent.name}
            </span>
          </div>
        );
      })}

      <div className="absolute bottom-4 right-4 flex items-center gap-2 text-xs text-cyan-500 font-mono">
        <Activity className="w-4 h-4 animate-pulse" />
        <span>NEURAL LINK ACTIVE</span>
      </div>
    </div>
  );
}
