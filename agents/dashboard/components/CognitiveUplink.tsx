import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Send, Cpu, Wifi, Radio } from 'lucide-react';

export default function CognitiveUplink() {
  const [status, setStatus] = useState('IDLE');

  return (
    <div className="flex flex-col items-center justify-center h-full w-full p-8 text-cyan-500">
      <motion.div 
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="max-w-2xl w-full bg-black/40 border border-cyan-500/30 p-8 rounded-lg backdrop-blur-xl relative overflow-hidden"
      >
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-cyan-500 to-transparent opacity-50" />
        
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-cyan-900/20 rounded border border-cyan-500/30">
              <Radio className="animate-pulse" size={24} />
            </div>
            <div>
              <h2 className="text-xl font-bold tracking-[0.2em]">COGNITIVE UPLINK</h2>
              <div className="text-[10px] text-cyan-700 font-mono">SECURE CHANNEL ESTABLISHED</div>
            </div>
          </div>
          <div className="text-right font-mono text-xs">
            <div className="text-emerald-500">SIGNAL: STRONG</div>
            <div className="text-cyan-700">LATENCY: 12ms</div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="h-32 border border-cyan-900/30 bg-black/50 rounded p-4 font-mono text-sm text-cyan-300/80 overflow-y-auto">
            <div className="mb-2 text-cyan-700">// SYSTEM MESSAGE</div>
            <div className="mb-1">Wait for user directive...</div>
            <div className="mb-1 text-emerald-500/80">Neural interface ready.</div>
            <motion.div 
              animate={{ opacity: [0, 1, 0] }}
              transition={{ duration: 1, repeat: Infinity }}
              className="inline-block w-2 h-4 bg-cyan-500 ml-1 align-middle"
            />
          </div>

          <div className="grid grid-cols-3 gap-4">
             {['LOGIC', 'CREATIVE', 'MEMORY'].map((module) => (
               <div key={module} className="border border-cyan-900/30 bg-cyan-950/10 p-3 rounded text-center">
                 <div className="text-[10px] text-cyan-600 mb-1">{module} CORE</div>
                 <div className="h-1 w-full bg-cyan-900/30 rounded-full overflow-hidden">
                   <motion.div 
                     className="h-full bg-cyan-500/50"
                     initial={{ width: '0%' }}
                     animate={{ width: `${Math.random() * 60 + 40}%` }}
                     transition={{ duration: 2, repeat: Infinity, repeatType: "reverse" }}
                   />
                 </div>
               </div>
             ))}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
