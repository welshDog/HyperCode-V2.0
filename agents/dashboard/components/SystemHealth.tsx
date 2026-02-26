"use client";

import { useEffect, useState } from "react";
import { fetchSystemHealth } from "@/lib/api";
import { Activity, AlertTriangle, CheckCircle, ServerCrash } from "lucide-react";

interface AgentHealth {
  status: "healthy" | "unhealthy" | "down";
  latency_ms?: number;
  error?: string;
  last_checked: string;
}

export function SystemHealth() {
  const [healthData, setHealthData] = useState<Record<string, AgentHealth> | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHealth = async () => {
      const data = await fetchSystemHealth();
      setHealthData(data);
      setLoading(false);
    };

    fetchHealth();
    const interval = setInterval(fetchHealth, 30000); // Update every 30s

    return () => clearInterval(interval);
  }, []);

  if (loading || !healthData) {
    return (
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 w-full">
            <div className="flex items-center gap-2 mb-4">
                <Activity className="w-5 h-5 text-zinc-400" />
                <h3 className="font-semibold text-zinc-200">System Health</h3>
            </div>
            <div className="animate-pulse space-y-2">
                <div className="h-8 bg-zinc-800 rounded w-full"></div>
                <div className="h-8 bg-zinc-800 rounded w-full"></div>
                <div className="h-8 bg-zinc-800 rounded w-full"></div>
            </div>
        </div>
    );
  }

  const failedCount = Object.values(healthData).filter(
    (a) => a.status === "down" || a.status === "unhealthy"
  ).length;

  return (
    <div className={`bg-zinc-900 border rounded-lg p-4 w-full transition-colors ${
        failedCount >= 4 ? "border-red-500 shadow-[0_0_20px_rgba(239,68,68,0.2)]" : "border-zinc-800"
    }`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Activity className={`w-5 h-5 ${failedCount >= 4 ? "text-red-500" : "text-green-500"}`} />
          <h3 className="font-semibold text-zinc-200">System Health</h3>
        </div>
        {failedCount >= 4 && (
            <span className="flex items-center gap-1 text-xs font-bold text-red-500 bg-red-500/10 px-2 py-1 rounded-full animate-pulse">
                <AlertTriangle className="w-3 h-3" /> CRITICAL
            </span>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-60 overflow-y-auto pr-2 custom-scrollbar">
        {Object.entries(healthData).map(([name, status]) => (
          <div 
            key={name} 
            className={`flex items-center justify-between p-2 rounded border text-xs ${
                status.status === "healthy" 
                    ? "bg-green-500/5 border-green-500/20 text-green-200" 
                    : "bg-red-500/5 border-red-500/20 text-red-200"
            }`}
          >
            <div className="flex items-center gap-2">
                {status.status === "healthy" ? (
                    <CheckCircle className="w-3 h-3 text-green-500" />
                ) : (
                    <ServerCrash className="w-3 h-3 text-red-500" />
                )}
                <span className="capitalize truncate max-w-[120px]" title={name}>
                    {name.replace(/_/g, " ")}
                </span>
            </div>
            
            <div className="text-right">
                {status.status === "healthy" ? (
                    <span className="text-zinc-500">{Math.round(status.latency_ms || 0)}ms</span>
                ) : (
                    <span className="text-red-400 font-medium">DOWN</span>
                )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
