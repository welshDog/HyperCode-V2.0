import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Send, Radio, Terminal } from 'lucide-react';

import { formatTime } from '@/lib/format';

interface AgentMessage {
  id: string;
  timestamp: string;
  type: 'command' | 'thought' | 'response' | 'error' | 'presence' | 'system';
  source: string;
  target: string;
  payload: unknown;
  metadata?: unknown;
}

interface MessageUI {
  role: 'user' | 'system' | 'agent';
  content: string;
  timestamp: number;
}

export default function CognitiveUplink() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<MessageUI[]>([]); // Initialize empty to avoid hydration mismatch
  const [isConnected, setIsConnected] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // Hydration fix: Set initial message on mount
  useEffect(() => {
    setMessages([
        { role: 'system', content: 'Neural interface ready. Establishing uplink...', timestamp: Date.now() }
    ]);
  }, []);

  const connect = useCallback(() => {
    // In production, this URL should come from env vars
    // Use 127.0.0.1 to avoid localhost resolution issues with CORS
    const wsUrl = 'ws://127.0.0.1:8081/ws/uplink'; 
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setIsConnected(true);
      setMessages(prev => [...prev, { 
        role: 'system', 
        content: 'SECURE CHANNEL ESTABLISHED. NEURAL NET ONLINE.', 
        timestamp: Date.now() 
      }]);
    };

    ws.onclose = () => {
      setIsConnected(false);
      setMessages(prev => [...prev, { 
        role: 'system', 
        content: 'CONNECTION INTERRUPTED. Re-establishing link to Neural Net...', 
        timestamp: Date.now() 
      }]);
    };

    ws.onmessage = (event) => {
      try {
        const data: AgentMessage = JSON.parse(event.data);
        if (data.type === 'response') {
          setMessages(prev => [...prev, { 
            role: 'agent', 
            content: JSON.stringify(data.payload, null, 2), 
            timestamp: Date.now() 
          }]);
          setIsTyping(false);
        }
      } catch (e) {
        console.error("Failed to parse message", e);
      }
    };

    wsRef.current = ws;
  }, []);

  useEffect(() => {
    connect();
    const interval = setInterval(() => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.CLOSED) {
            connect();
        }
    }, 3000);
    return () => {
      if (wsRef.current) wsRef.current.close();
      clearInterval(interval);
    };
  }, [connect]);

  // Auto-scroll
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = () => {
    if (!input.trim() || !isConnected) return;

    const content = input;
    setInput('');
    
    // Optimistic update
    setMessages(prev => [...prev, { role: 'user', content: content, timestamp: Date.now() }]);
    setIsTyping(true);

    const message: AgentMessage = {
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      type: 'command',
      source: 'user',
      target: 'orchestrator',
      payload: { command: content }
    };

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      setMessages(prev => [...prev, { role: 'system', content: 'Error: Uplink offline.', timestamp: Date.now() }]);
      setIsTyping(false);
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
            <div className={`p-2 rounded border border-cyan-500/30 transition-colors ${isConnected ? 'bg-cyan-900/20' : 'bg-red-900/20'}`}>
              <Radio className={isConnected ? "animate-pulse text-cyan-500" : "text-red-500"} size={24} />
            </div>
            <div>
              <h2 className="text-xl font-bold tracking-[0.2em]">COGNITIVE UPLINK</h2>
              <div className={`text-[10px] font-mono ${isConnected ? 'text-cyan-700' : 'text-red-700'}`}>
                {isConnected ? 'SECURE CHANNEL ESTABLISHED' : 'SEARCHING FOR CARRIER...'}
              </div>
            </div>
          </div>
          <div className="text-right font-mono text-xs">
            <div className={isConnected ? "text-emerald-500" : "text-red-500"}>
              SIGNAL: {isConnected ? 'STRONG' : 'LOST'}
            </div>
            <div className="text-cyan-700">LATENCY: {isConnected ? '12ms' : '--'}</div>
          </div>
        </div>

        <div className="space-y-6">
          <div 
            ref={scrollRef}
            className="h-64 border border-cyan-900/30 bg-black/50 rounded p-4 font-mono text-sm text-cyan-300/80 overflow-y-auto scrollbar-thin scrollbar-thumb-cyan-900/50"
          >
            {messages.map((msg, i) => (
              <div key={i} className={`mb-2 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                <span className={`text-[10px] uppercase ${msg.role === 'user' ? 'text-emerald-700' : 'text-cyan-700'} block mb-1`}>
                  [{formatTime(msg.timestamp)}] {msg.role === 'user' ? 'OPERATOR' : msg.role === 'agent' ? 'SWARM' : 'SYSTEM'}
                </span>
                <div className={`${msg.role === 'user' ? 'text-emerald-400' : msg.role === 'system' ? 'text-zinc-500 italic' : 'text-cyan-300'}`}>
                  {msg.role === 'system' && '// '}
                  {msg.content}
                </div>
              </div>
            ))}
            {isTyping && (
              <div className="text-left animate-pulse">
                <span className="text-[10px] text-cyan-700 block mb-1">SWARM</span>
                <div className="flex gap-1 items-center h-4">
                  <div className="w-1 h-1 bg-cyan-500 rounded-full"></div>
                  <div className="w-1 h-1 bg-cyan-500 rounded-full animation-delay-200"></div>
                  <div className="w-1 h-1 bg-cyan-500 rounded-full animation-delay-400"></div>
                </div>
              </div>
            )}
          </div>

          <form 
            onSubmit={(e) => { e.preventDefault(); handleSend(); }}
            className="flex gap-2"
          >
            <div className="flex items-center justify-center w-10 bg-zinc-900 border border-zinc-700 text-cyan-500">
              <Terminal size={18} />
            </div>
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={isConnected ? "Enter directive (e.g., 'run: build a spaceship UI')..." : "Connecting..."}
              disabled={!isConnected}
              className="flex-1 bg-transparent border-b border-zinc-700 text-cyan-400 font-mono focus:outline-none focus:border-cyan-500 transition-colors placeholder:text-zinc-700 disabled:opacity-50"
            />
            <button 
              type="submit"
              disabled={!isConnected}
              className="px-6 bg-cyan-900/20 border border-cyan-800 text-cyan-400 hover:bg-cyan-500 hover:text-black transition-all font-bold uppercase text-xs tracking-wider flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Execute <Send size={14} />
            </button>
          </form>
        </div>
      </motion.div>
    </div>
  );
}
