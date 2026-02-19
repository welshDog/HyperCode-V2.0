
'use client';

import React, { useEffect } from 'react';
import ReactFlow, { 
  Node, 
  Edge, 
  Background, 
  Controls, 
  useNodesState, 
  useEdgesState,
  MarkerType
} from 'reactflow';
import 'reactflow/dist/style.css';
import { useSelector } from 'react-redux';
import { RootState } from '../../store/store';

const MissionFlow = () => {
  const { missions, agents } = useSelector((state: RootState) => state.dashboard);
  
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  useEffect(() => {
     const newNodes: Node[] = [];
     const newEdges: Edge[] = [];
     
     // 1. Orchestrator Node
     newNodes.push({
       id: 'orchestrator',
       type: 'input',
       data: { label: 'Mission Control' },
       position: { x: 400, y: 0 },
       style: { 
         background: '#1a1a2e', 
         color: '#00ff88', 
         border: '1px solid #00ff88', 
         width: 180,
         borderRadius: '8px',
         fontWeight: 'bold',
         textAlign: 'center'
       }
     });

     // 2. Agent Nodes (Bottom Layer)
     const agentMap = new Map();
     agents.forEach((a, idx) => {
       const x = 50 + idx * 200;
       const y = 400;
       agentMap.set(a.id, { x, y });
       
       newNodes.push({
         id: `agent-${a.id}`,
         data: { label: `${a.name}\n[${a.status.toUpperCase()}]` },
         position: { x, y },
         style: { 
             background: '#0f0f1a', 
             color: '#ccc', 
             border: a.status === 'active' ? '1px solid #00ccff' : '1px solid #555',
             width: 160,
             fontSize: '12px',
             borderRadius: '4px'
         }
       });
     });

     // 3. Mission Nodes (Middle Layer)
     missions.forEach((m, idx) => {
        const isAssigned = !!m.agentId;
        const x = 100 + (idx % 4) * 220;
        const y = 150 + Math.floor(idx / 4) * 100;
        
        let statusColor = '#fff';
        if (m.status === 'queued') statusColor = '#ffd700';
        if (m.status === 'assigned') statusColor = '#00ccff';
        if (m.status === 'completed') statusColor = '#00ff88';
        if (m.status === 'failed') statusColor = '#ff0055';

        newNodes.push({
          id: `mission-${m.id}`,
          data: { label: `${m.title.substring(0, 20)}...` },
          position: { x, y },
          style: { 
            background: '#1e1e2f',
            color: statusColor,
            border: `1px solid ${statusColor}`,
            fontSize: '11px',
            width: 150,
            borderRadius: '15px'
          }
        });
        
        // Edge: Orchestrator -> Mission
        newEdges.push({
          id: `e-orch-${m.id}`,
          source: 'orchestrator',
          target: `mission-${m.id}`,
          animated: m.status === 'queued' || m.status === 'assigned',
          style: { stroke: '#555' }
        });
        
        // Edge: Mission -> Agent
        if (m.agentId) {
           newEdges.push({
             id: `e-${m.id}-${m.agentId}`,
             source: `mission-${m.id}`,
             target: `agent-${m.agentId}`,
             animated: m.status === 'assigned' || m.status === 'in_progress',
             style: { stroke: statusColor, strokeWidth: 2 },
             markerEnd: { type: MarkerType.ArrowClosed, color: statusColor },
           });
        }
     });

     setNodes(newNodes);
     setEdges(newEdges);
  }, [missions, agents, setNodes, setEdges]);

  return (
    <div style={{ height: '500px', width: '100%', border: '1px solid #333', borderRadius: '12px', overflow: 'hidden', background: '#050505' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      >
        <Background color="#222" gap={20} />
        <Controls />
      </ReactFlow>
    </div>
  );
};

export default MissionFlow;
