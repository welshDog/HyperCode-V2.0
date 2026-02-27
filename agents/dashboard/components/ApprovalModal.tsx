"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, CheckCircle, XCircle } from "lucide-react";
import { API_BASE_URL, respondToApproval } from "@/lib/api";

interface ApprovalRequest {
  id: string;
  task_id: string;
  description: string;
  agent?: string;
  plan?: string;
  risk_level?: string;
  estimated_time?: string;
}

export function ApprovalModal() {
  const [requests, setRequests] = useState<ApprovalRequest[]>([]);
  
  useEffect(() => {
    // Construct WS URL
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // Use API_BASE_URL but replace http/https with ws/wss
    // If API_BASE_URL is "http://localhost:8080", we want "ws://localhost:8080"
    // Handle the case where API_BASE_URL might be undefined or empty
    const baseUrl = API_BASE_URL || "http://localhost:8080";
    let wsUrl = baseUrl.replace(/^http/, 'ws');
    
    // Fallback if replace didn't work (e.g. relative path)
    if (wsUrl.startsWith('/')) {
        wsUrl = `${protocol}//${window.location.host}${wsUrl}`;
    }
    
    // Append endpoint
    wsUrl = `${wsUrl}/ws/approvals`;
    
    console.log("Connecting to Approval Stream:", wsUrl);
    
    let socket: WebSocket | null = null;
    let retryTimeout: NodeJS.Timeout;

    const connect = () => {
        socket = new WebSocket(wsUrl);

        socket.onopen = () => {
            console.log("Approval Stream Connected");
        };

        socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log("WS Message Received:", data);
                
                // Validate payload: Must have task_id to be an approval request
                if (data && data.task_id && data.description) {
                    setRequests(prev => {
                        // Prevent duplicates
                        if (prev.some(r => r.id === data.id)) return prev;
                        return [...prev, data];
                    });
                } else {
                    console.log("Ignored non-approval message:", data);
                }
            } catch (e) {
                console.error("Failed to parse approval message", e);
            }
        };

        socket.onclose = () => {
            console.log("Approval Stream Disconnected. Retrying...");
            retryTimeout = setTimeout(connect, 3000);
        };
        
        socket.onerror = (err) => {
            console.error("WebSocket Error:", err);
            socket?.close();
        };
    };

    connect();

    return () => {
        if (socket) socket.close();
        clearTimeout(retryTimeout);
    };
  }, []);

  const handleRespond = async (id: string, status: "approved" | "rejected") => {
      // Optimistically remove
      setRequests(prev => prev.filter(r => r.id !== id));
      
      await respondToApproval(id, status);
  };

  if (requests.length === 0) return null;

  const currentRequest = requests[0];

  return (
    <AnimatePresence>
      <motion.div 
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
      >
        <div className="bg-zinc-900 border border-yellow-500/50 w-full max-w-lg rounded-lg shadow-[0_0_50px_rgba(234,179,8,0.2)] overflow-hidden">
          
          {/* Header */}
          <div className="bg-yellow-500/10 border-b border-yellow-500/20 p-4 flex items-center gap-3">
             <div className="p-2 bg-yellow-500/20 rounded-full animate-pulse">
                <AlertTriangle className="text-yellow-500" size={24} />
             </div>
             <div>
                <h3 className="text-yellow-500 font-bold tracking-widest uppercase text-sm">Authorization Required</h3>
                <p className="text-zinc-400 text-xs">Awaiting human oversight protocol</p>
             </div>
          </div>
          
          {/* Content */}
          <div className="p-6 space-y-4 font-mono text-sm">
             <div className="grid grid-cols-[100px_1fr] gap-2">
                <span className="text-zinc-500 uppercase text-xs">Task ID</span>
                <span className="text-zinc-300">{currentRequest.task_id}</span>
                
                <span className="text-zinc-500 uppercase text-xs">Agent</span>
                <span className="text-cyan-400 font-bold">{currentRequest.agent || "Orchestrator"}</span>
                
                <span className="text-zinc-500 uppercase text-xs">Risk Level</span>
                <span className="text-emerald-400">{currentRequest.risk_level || "Unknown"}</span>
             </div>
             
             <div className="bg-black/40 border border-zinc-800 p-3 rounded text-zinc-300">
                <p className="text-xs text-zinc-500 mb-1 uppercase">Description</p>
                {currentRequest.description}
             </div>
             
             {currentRequest.plan && (
                 <div className="bg-black/40 border border-zinc-800 p-3 rounded text-zinc-300 max-h-32 overflow-y-auto">
                    <p className="text-xs text-zinc-500 mb-1 uppercase">Proposed Plan</p>
                    {currentRequest.plan}
                 </div>
             )}
          </div>
          
          {/* Actions */}
          <div className="p-4 bg-zinc-900/50 border-t border-zinc-800 flex gap-3">
             <button 
               onClick={() => handleRespond(currentRequest.id, "rejected")}
               className="flex-1 py-3 bg-red-900/20 border border-red-900/50 text-red-500 hover:bg-red-500 hover:text-white transition-all rounded font-bold uppercase tracking-wider flex items-center justify-center gap-2"
             >
                <XCircle size={18} /> Abort
             </button>
             <button 
               onClick={() => handleRespond(currentRequest.id, "approved")}
               className="flex-1 py-3 bg-emerald-900/20 border border-emerald-900/50 text-emerald-500 hover:bg-emerald-500 hover:text-white transition-all rounded font-bold uppercase tracking-wider flex items-center justify-center gap-2"
             >
                <CheckCircle size={18} /> Authorize
             </button>
          </div>
          
          {requests.length > 1 && (
             <div className="bg-zinc-950 text-center py-1 text-xs text-zinc-600 border-t border-zinc-900">
                +{requests.length - 1} more pending requests
             </div>
          )}
          
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
