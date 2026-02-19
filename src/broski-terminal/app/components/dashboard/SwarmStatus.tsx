import React, { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../store/store';
import { Layers, Users, Zap } from 'lucide-react';

const SwarmStatus: React.FC = () => {
  const { phase, activeCrew, system_status } = useSelector((state: RootState) => state.dashboard);
  
  // Phase color mapping
  const getPhaseColor = (p: string) => {
    switch(p?.toLowerCase()) {
      case 'planning': return 'text-blue-400 border-blue-500/30 bg-blue-500/10';
      case 'architecture': return 'text-purple-400 border-purple-500/30 bg-purple-500/10';
      case 'development': return 'text-green-400 border-green-500/30 bg-green-500/10';
      case 'testing': return 'text-yellow-400 border-yellow-500/30 bg-yellow-500/10';
      case 'deployment': return 'text-red-400 border-red-500/30 bg-red-500/10';
      default: return 'text-gray-400 border-gray-500/30 bg-gray-500/10';
    }
  };

  const phaseStyle = getPhaseColor(phase);

  return (
    <div className="bg-[#13111C] border border-gray-800 rounded-xl p-6 shadow-xl">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-xl font-bold flex items-center gap-2 text-cyan-400">
            <Layers size={20} /> SWARM PHASE CONTROL
          </h2>
          <p className="text-gray-500 text-sm mt-1">Real-time orchestration status</p>
        </div>
        <div className={`px-3 py-1 rounded-full text-xs font-mono border ${phaseStyle}`}>
          {phase?.toUpperCase() || 'UNKNOWN'}
        </div>
      </div>

      <div className="space-y-6">
        {/* Active Crew */}
        <div>
          <h3 className="text-sm font-semibold text-gray-400 flex items-center gap-2 mb-3">
            <Users size={16} /> ACTIVE CREW
          </h3>
          <div className="flex flex-wrap gap-2">
            {activeCrew && activeCrew.length > 0 ? (
              activeCrew.map((agent, idx) => (
                <span 
                  key={idx} 
                  className="px-3 py-1.5 bg-gray-800/50 border border-gray-700 rounded-lg text-xs font-mono text-gray-300 hover:border-cyan-500/50 transition-colors"
                >
                  {agent}
                </span>
              ))
            ) : (
              <span className="text-gray-600 text-sm italic">No active agents detected</span>
            )}
          </div>
        </div>

        {/* System Status */}
        <div className="pt-4 border-t border-gray-800">
          <div className="flex justify-between items-center">
            <span className="text-sm font-semibold text-gray-400 flex items-center gap-2">
              <Zap size={16} /> SYSTEM LOAD
            </span>
            <span className={`text-sm font-mono ${system_status === 'operational' ? 'text-green-400' : 'text-yellow-400'}`}>
              {system_status?.toUpperCase()}
            </span>
          </div>
          <div className="w-full bg-gray-800 h-1.5 mt-2 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-cyan-500 to-purple-500 transition-all duration-1000"
              style={{ width: system_status === 'operational' ? '30%' : '80%' }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default SwarmStatus;
