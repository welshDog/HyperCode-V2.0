import React from 'react';
import { Activity, Cpu, Database, Server, Terminal, Shield, Eye, Settings, Briefcase } from 'lucide-react';

interface AgentCardProps {
  name: string;
  role?: string;
  status: string;
  version: string;
  load?: number;
  lastHeartbeat?: string;
}

const getIcon = (name: string) => {
  if (name.includes('frontend')) return <Terminal className="w-6 h-6 text-pink-400" />;
  if (name.includes('backend')) return <Server className="w-6 h-6 text-blue-400" />;
  if (name.includes('database')) return <Database className="w-6 h-6 text-green-400" />;
  if (name.includes('security')) return <Shield className="w-6 h-6 text-red-400" />;
  if (name.includes('qa')) return <Eye className="w-6 h-6 text-purple-400" />;
  if (name.includes('devops')) return <Settings className="w-6 h-6 text-orange-400" />;
  if (name.includes('project')) return <Briefcase className="w-6 h-6 text-yellow-400" />;
  return <Activity className="w-6 h-6 text-gray-400" />;
};

export const AgentCard: React.FC<AgentCardProps> = ({ name, role, status, version, load, lastHeartbeat }) => {
  const isOnline = status === 'active';
  const statusColor = isOnline ? 'bg-green-500' : 'bg-red-500';
  const borderColor = isOnline ? 'border-cyan-500/50' : 'border-gray-700';
  const glow = isOnline ? 'shadow-[0_0_15px_rgba(6,182,212,0.3)]' : '';

  return (
    <div className={`relative p-4 rounded-xl border ${borderColor} bg-gray-900/80 backdrop-blur-sm transition-all duration-300 ${glow} hover:scale-[1.02]`}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-gray-800/50 border border-gray-700">
            {getIcon(name)}
          </div>
          <div>
            <h3 className="font-bold text-gray-100 capitalize">{name.replace('-', ' ')}</h3>
            <p className="text-xs text-gray-400">{role || 'Specialist'}</p>
          </div>
        </div>
        <div className={`w-3 h-3 rounded-full ${statusColor} animate-pulse`} />
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500">Status</span>
          <span className={`font-mono ${isOnline ? 'text-green-400' : 'text-red-400'}`}>{status.toUpperCase()}</span>
        </div>
        
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500">Version</span>
          <span className="font-mono text-gray-300">v{version}</span>
        </div>

        {load !== undefined && (
          <div className="space-y-1">
            <div className="flex justify-between text-xs text-gray-400">
              <span className="flex items-center gap-1"><Cpu size={12} /> Load</span>
              <span>{Math.round(load * 100)}%</span>
            </div>
            <div className="h-1.5 w-full bg-gray-800 rounded-full overflow-hidden">
              <div 
                className="h-full bg-cyan-500 transition-all duration-500"
                style={{ width: `${Math.min(load * 100, 100)}%` }}
              />
            </div>
          </div>
        )}
      </div>

      <div className="mt-4 pt-3 border-t border-gray-800 flex justify-between items-center text-xs text-gray-600 font-mono">
        <span>ID: {name.substring(0, 8)}...</span>
        <span>{lastHeartbeat ? new Date(lastHeartbeat).toLocaleTimeString() : 'N/A'}</span>
      </div>
    </div>
  );
};
