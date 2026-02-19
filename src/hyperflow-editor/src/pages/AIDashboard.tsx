import React, { useEffect } from 'react';
import AgentWorkflow from '../components/ai-visualization/AgentWorkflow';
import BudgetGauge from '../components/ai-visualization/BudgetGauge';
import TaskQueue from '../components/ai-visualization/TaskQueue';
import { Activity, Cpu, Wifi, WifiOff } from 'lucide-react';
import { useAIStore } from '../stores/aiStore';
import { useAgentUpdates } from '../hooks/useAgentUpdates';

export default function AIDashboard() {
  const { fetchAgents, fetchBudget, isConnected } = useAIStore();
  
  // Enable real-time updates
  useAgentUpdates();

  // Initial Data Fetch
  useEffect(() => {
    fetchAgents();
    fetchBudget();
  }, [fetchAgents, fetchBudget]);

  return (
    <div className="h-full w-full p-4 flex flex-col gap-4 bg-[var(--color-bg)] text-[var(--color-text)] overflow-hidden">
      {/* Header */}
      <div className="flex justify-between items-center px-2">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-[rgba(124,58,237,0.1)] rounded-lg border border-[var(--color-primary)]">
            <Cpu size={24} className="text-[var(--color-primary)]" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white">VISUAL CORTEX</h1>
            <div className="text-xs text-[var(--color-secondary)] font-mono flex items-center gap-2">
              <Activity size={10} className="animate-pulse" />
              NEURAL INTERFACE ACTIVE
            </div>
          </div>
        </div>
        
        <div className="flex gap-4 text-xs font-mono text-gray-400 items-center">
          <div className="bg-[var(--color-panel)] px-3 py-1 rounded border border-[rgba(255,255,255,0.1)] flex items-center gap-2">
            {isConnected ? (
              <>
                <Wifi size={12} className="text-green-500" />
                <span className="text-green-500">LIVE</span>
              </>
            ) : (
              <>
                <WifiOff size={12} className="text-red-500" />
                <span className="text-red-500">OFFLINE</span>
              </>
            )}
          </div>
          <div className="bg-[var(--color-panel)] px-3 py-1 rounded border border-[rgba(255,255,255,0.1)]">
            UPTIME: 42h 12m
          </div>
        </div>
      </div>

      {/* Main Grid */}
      <div className="flex-1 grid grid-cols-12 gap-4 min-h-0">
        
        {/* Left Panel: Workflow (60%) */}
        <div className="col-span-12 lg:col-span-8 h-full min-h-[400px]">
          <AgentWorkflow />
        </div>

        {/* Right Panel: Metrics & Queue (40%) */}
        <div className="col-span-12 lg:col-span-4 flex flex-col gap-4 h-full">
          
          {/* Top Right: Budget */}
          <div className="h-[40%] min-h-[200px]">
            <BudgetGauge />
          </div>

          {/* Bottom Right: Task Queue */}
          <div className="h-[60%] min-h-[300px]">
            <TaskQueue />
          </div>
          
        </div>
      </div>
    </div>
  );
}
