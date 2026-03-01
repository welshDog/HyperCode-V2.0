import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Send, Radio } from 'lucide-react';
import { createTask, getTask } from '../lib/api'; 

interface Message {
  role: 'user' | 'system' | 'agent';
  content: string;
  timestamp: number;
}

export default function CognitiveUplink() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    { role: 'system', content: 'Neural interface ready. Awaiting command.', timestamp: Date.now() }
  ]);
  const [isProcessing, setIsProcessing] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isProcessing) return;

    const userMsg: Message = { role: 'user', content: input, timestamp: Date.now() };
    setMessages(prev => [...prev, userMsg]);
    const currentInput = input;
    setInput('');
    setIsProcessing(true);

    try {
      const taskPayload = {
        title: currentInput.slice(0, 50),
        description: currentInput,
        type: "general",
        project_id: 1, 
        priority: "high"
      };

      const task = await createTask(taskPayload);
      
      // Poll
      let attempts = 0;
      const maxAttempts = 30; // 60s timeout
      while (attempts < maxAttempts) {
        await new Promise(r => setTimeout(r, 2000));
        const updatedTask = await getTask(task.id);
        
        if (updatedTask.status === 'done') {
           const output = updatedTask.output || "Task completed.";
           setMessages(prev => [...prev, { role: 'agent', content: output, timestamp: Date.now() }]);
           setIsProcessing(false);
           return;
        }
        if (updatedTask.status === 'failed') {
           setMessages(prev => [...prev, { role: 'system', content: "Task failed.", timestamp: Date.now() }]);
           setIsProcessing(false);
           return;
        }
        attempts++;
      }
      setMessages(prev => [...prev, { role: 'system', content: "Task timed out.", timestamp: Date.now() }]);
      setIsProcessing(false);

    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { role: 'system', content: "Error sending command.", timestamp: Date.now() }]);
      setIsProcessing(false);
    }
  };

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
          <div 
            ref={scrollRef}
            className="h-64 border border-cyan-900/30 bg-black/50 rounded p-4 font-mono text-sm text-cyan-300/80 overflow-y-auto"
          >
             {messages.map((msg, i) => (
               <div key={i} className={`mb-2 whitespace-pre-wrap ${msg.role === 'user' ? 'text-right text-emerald-400' : msg.role === 'system' ? 'text-cyan-700' : 'text-cyan-300'}`}>
                 <span className="text-[10px] opacity-50 block mb-1">{msg.role.toUpperCase()}</span>
                 {msg.content}
               </div>
             ))}
             {isProcessing && (
               <div className="text-cyan-500 animate-pulse mt-2">
                 Processing... <motion.div className="inline-block w-2 h-4 bg-cyan-500 ml-1" />
               </div>
             )}
          </div>

          <div className="flex gap-2">
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              className="flex-1 bg-black/50 border border-cyan-900/30 rounded p-2 text-cyan-300 focus:outline-none focus:border-cyan-500 font-mono"
              placeholder="Enter directive..."
              disabled={isProcessing}
            />
            <button 
              onClick={handleSend}
              disabled={isProcessing}
              className="bg-cyan-900/20 border border-cyan-500/30 p-2 rounded hover:bg-cyan-500/20 disabled:opacity-50 text-cyan-500"
            >
              <Send size={20} />
            </button>
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
