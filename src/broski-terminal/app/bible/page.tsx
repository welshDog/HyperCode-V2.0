import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function extractMeta(src: string) {
  const versionMatch = src.match(/\*\*Version:\*\*\s*([^\n]+)/i);
  const updatedMatch = src.match(/\*\*(?:Last\s*Updated|Updated):\*\*\s*([^\n]+)/i);
  const version = versionMatch ? versionMatch[1].trim() : "Unknown";
  const updatedRaw = updatedMatch ? updatedMatch[1].trim() : "Unknown";
  return { version, updated: updatedRaw };
}

export default async function Page() {
  const core = process.env.NEXT_PUBLIC_CORE_URL || "http://hypercode-core:8000";
  let text = "";
  try {
      // In server components running in Docker, localhost refers to the container itself.
      // We need to use the service name 'hypercode-core' for internal communication.
      // However, NEXT_PUBLIC_CORE_URL is usually for client-side.
      // We should use an internal URL if running on server.
      const internalCoreUrl = process.env.INTERNAL_CORE_URL || "http://hypercode-core:8000";
      console.log(`Fetching Bible from: ${internalCoreUrl}/agents/bible`);
      
      const res = await fetch(`${internalCoreUrl}/agents/bible`, { cache: "no-store" });
      if (res.ok) {
        text = await res.text();
      } else {
        console.error(`Failed to fetch Bible: ${res.status} ${res.statusText}`);
        text = `# Error fetching Bible\nCould not connect to Core service. Status: ${res.status}`;
      }
  } catch (e) {
      console.error("Error fetching Bible:", e);
      text = `# Error fetching Bible\nCould not connect to Core service. Error: ${e}`;
  }
  
  const meta = extractMeta(text);
  
  return (
    <main className="p-8 max-w-5xl mx-auto font-sans bg-[#0B0418] text-gray-200 min-h-screen">
      <div className="sticky top-0 z-10 bg-[#0B0418]/90 backdrop-blur-md border-b border-gray-800 py-4 mb-8">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-500">Hyper Agent Bible</h1>
          <a href="/dashboard" className="px-4 py-2 border border-gray-700 rounded-lg text-sm hover:bg-gray-800 transition-colors">Back to Terminal</a>
        </div>
        <div className="mt-2 flex gap-4 text-xs text-gray-400 font-mono">
          <span>VERSION: <strong className="text-cyan-400">{meta.version}</strong></span>
          <span>UPDATED: <strong className="text-purple-400">{meta.updated}</strong></span>
        </div>
      </div>

      <div className="border border-gray-800 bg-[#13111C] rounded-xl p-8 shadow-2xl">
        <div className="prose prose-invert max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
        </div>
      </div>
    </main>
  );
}
