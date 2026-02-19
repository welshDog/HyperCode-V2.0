import React from 'react';
import ReactFlow, { 
  Node, 
  Handle, 
  Position, 
  Background, 
  Controls,
  MiniMap,
  applyNodeChanges,
  applyEdgeChanges
} from 'reactflow';
import 'reactflow/dist/style.css';
import { useAIStore, AgentNodeData } from '../../stores/aiStore';
import clsx from 'clsx';
import { Brain, Code, CheckCircle2, AlertCircle } from 'lucide-react';

const AgentNode = ({ data }: { data: AgentNodeData }) => {
  const statusColors = {
    idle: 'bg-gray-600 border-gray-500',
    working: 'bg-blue-600 border-blue-400 animate-pulse',
    completed: 'bg-green-600 border-green-400',
    failed: 'bg-red-600 border-red-400'
  };

  const StatusIcon = {
    idle: Brain,
    working: Code,
    completed: CheckCircle2,
    failed: AlertCircle
  }[data.status];

  return (
    <div className={clsx(
      "px-4 py-3 rounded-lg border-2 shadow-lg min-w-[180px] transition-all duration-300",
      statusColors[data.status]
    )}>
      <Handle type="target" position={Position.Top} className="!bg-[var(--color-text)]" />
      
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-full bg-[rgba(255,255,255,0.2)]">
          <StatusIcon size={20} className="text-white" />
        </div>
        <div>
          <div className="text-sm font-bold text-white">{data.label}</div>
          <div className="text-xs text-gray-200 capitalize">{data.status}</div>
        </div>
      </div>

      <Handle type="source" position={Position.Bottom} className="!bg-[var(--color-text)]" />
    </div>
  );
};

export const nodeTypes = {
  agent: AgentNode,
};

export default function AgentWorkflow() {
  const { nodes, edges, setNodes, setEdges } = useAIStore();

  return (
    <div className="h-full w-full bg-[var(--color-bg)] rounded-xl border border-[var(--color-primary)] overflow-hidden shadow-[0_0_30px_rgba(124,58,237,0.1)]">
      <div className="p-3 border-b border-[var(--color-primary)] bg-[rgba(124,58,237,0.1)] flex justify-between items-center">
        <h3 className="font-mono text-sm font-bold text-[var(--color-secondary)]">/ AGENT WORKFLOW VISUALIZER</h3>
        <span className="text-xs text-[var(--color-text)] animate-pulse">● LIVE</span>
      </div>
      <div className="h-[calc(100%-45px)]">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={(changes) => setNodes(applyNodeChanges(changes, nodes))}
          onEdgesChange={(changes) => setEdges(applyEdgeChanges(changes, edges))}
          nodeTypes={nodeTypes}
          fitView
          attributionPosition="bottom-right"
        >
          <Background color="#7c3aed" gap={20} size={1} className="opacity-20" />
          <Controls className="!bg-[var(--color-panel)] !border-[var(--color-primary)] !fill-[var(--color-text)]" />
          <MiniMap 
            nodeColor={(n) => {
              if (n.type === 'agent') return '#06b6d4';
              return '#eee';
            }}
            className="!bg-[var(--color-panel)] border border-[var(--color-secondary)]"
          />
        </ReactFlow>
      </div>
    </div>
  );
}
