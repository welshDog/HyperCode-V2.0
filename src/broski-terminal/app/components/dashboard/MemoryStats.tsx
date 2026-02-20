
'use client';

import React from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../../store/store';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Database, Activity } from 'lucide-react';

const MemoryStats = () => {
  const { memory, memoryHistory } = useSelector((state: RootState) => state.dashboard);

  const data = memoryHistory.map(h => ({
      time: new Date(h.timestamp * 1000).toLocaleTimeString(),
      memories: h.count
  }));

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 h-full">
        {/* Stats Card */}
        <div className="bg-[#1a1a2e] border border-cyan-500/30 rounded-xl p-6 flex flex-col justify-between">
            <div className="flex items-center gap-4">
                <div className="p-3 bg-cyan-500/20 rounded-lg">
                    <Database className="text-cyan-400 w-8 h-8" />
                </div>
                <div>
                    <h3 className="text-gray-400 text-sm font-mono">TOTAL MEMORIES</h3>
                    <p className="text-3xl font-bold text-gray-100">{memory.total_memories}</p>
                </div>
            </div>
            
            <div className="mt-6">
                <div className="flex items-center gap-2 mb-2">
                    <Activity className="text-purple-400 w-4 h-4" />
                    <span className="text-gray-400 text-xs font-mono">SYNC STATUS</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    <span className="text-green-400 text-sm font-bold">SYNCHRONIZED</span>
                </div>
                <p className="text-xs text-gray-600 mt-1">Last update: {new Date(memory.last_updated * 1000).toLocaleTimeString()}</p>
            </div>
        </div>

        {/* Chart */}
        <div className="bg-[#1a1a2e] border border-cyan-500/30 rounded-xl p-4">
            <h3 className="text-gray-400 text-xs font-mono mb-4">MEMORY GROWTH</h3>
            <div className="h-32 w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={data}>
                        <defs>
                            <linearGradient id="colorMem" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#00ccff" stopOpacity={0.3}/>
                                <stop offset="95%" stopColor="#00ccff" stopOpacity={0}/>
                            </linearGradient>
                        </defs>
                        <XAxis dataKey="time" hide />
                        <YAxis hide domain={['auto', 'auto']} />
                        <Tooltip 
                            contentStyle={{ backgroundColor: '#000', border: '1px solid #333' }}
                            itemStyle={{ color: '#00ccff' }}
                        />
                        <Area type="monotone" dataKey="memories" stroke="#00ccff" fillOpacity={1} fill="url(#colorMem)" />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    </div>
  );
};

export default MemoryStats;
