
'use client';

import React from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../store/store';
import { DashboardConnection } from '../components/DashboardConnection';
import { AgentCard } from '../components/dashboard/AgentCard';
import MissionFlow from '../components/dashboard/MissionFlow';
import MemoryStats from '../components/dashboard/MemoryStats';
import SwarmStatus from '../components/dashboard/SwarmStatus';
import { Activity, RefreshCw, Wifi, WifiOff, Network, Database, Layers } from 'lucide-react';

export default function DashboardPage() {
  const { agents, system_status, connected } = useSelector((state: RootState) => state.dashboard);

  return (
    <div className="min-h-screen bg-[#0B0418] text-gray-100 p-8">
      <DashboardConnection />
      
      {/* Header */}
      <header className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-black bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-500 tracking-tighter mb-2">
            MISSION CONTROL
          </h1>
          <p className="text-gray-400 font-mono text-sm">HYPERCODE SWARM // V2.1.0</p>
        </div>
        
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-gray-900 border border-gray-800">
            {connected ? <Wifi size={18} className="text-green-500" /> : <WifiOff size={18} className="text-red-500" />}
            <span className={`text-sm font-bold ${connected ? 'text-green-400' : 'text-red-400'}`}>
              {connected ? 'CONNECTED' : 'OFFLINE'}
            </span>
          </div>
          
          <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-gray-900 border border-gray-800">
            <Activity size={18} className="text-cyan-500" />
            <span className="text-sm font-bold text-cyan-400">
              SYSTEM: {system_status.toUpperCase()}
            </span>
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <main className="space-y-8">
        
        {/* Top Row: Mission Flow & Memory Stats */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
            <div className="xl:col-span-2 space-y-4">
                <h2 className="text-xl font-bold flex items-center gap-2 text-cyan-400">
                    <Network size={20} /> MISSION ROUTING VISUALIZATION
                </h2>
                <MissionFlow />
            </div>
            <div className="space-y-4">
                <h2 className="text-xl font-bold flex items-center gap-2 text-purple-400">
                    <Database size={20} /> SWARM MEMORY
                </h2>
                <div className="h-[250px]">
                    <MemoryStats />
                </div>
                <h2 className="text-xl font-bold flex items-center gap-2 text-blue-400 mt-4">
                    <Layers size={20} /> SWARM STATUS
                </h2>
                <div className="h-[250px]">
                    <SwarmStatus />
                </div>
            </div>
        </div>

        {/* Bottom Row: Agents Grid */}
        <section>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold flex items-center gap-3">
              <span className="w-2 h-8 bg-purple-500 rounded-full" />
              Active Agents
              <span className="text-sm font-normal text-gray-500 bg-gray-900 px-2 py-1 rounded border border-gray-800">
                {agents.length} Online
              </span>
            </h2>
          </div>

          {agents.length === 0 && connected ? (
             <div className="flex flex-col items-center justify-center h-64 border border-dashed border-gray-800 rounded-2xl bg-gray-900/30">
                <RefreshCw className="animate-spin text-gray-600 mb-4" size={32} />
                <p className="text-gray-500">Scanning for agents...</p>
             </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {agents.map((agent: any) => (
                <AgentCard
                  key={agent.id}
                  name={agent.name}
                  role={agent.role}
                  status={agent.status}
                  version={agent.version}
                  load={agent.load}
                  lastHeartbeat={agent.lastHeartbeat}
                />
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
