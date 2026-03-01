import { create } from 'zustand';
import { 
  Node, 
  Edge, 
  Connection, 
  addEdge, 
  NodeChange, 
  EdgeChange, 
  applyNodeChanges, 
  applyEdgeChanges 
} from 'reactflow';

interface FlowState {
  nodes: Node[];
  edges: Edge[];
  onNodesChange: (changes: NodeChange[]) => void;
  onEdgesChange: (changes: EdgeChange[]) => void;
  onConnect: (connection: Connection) => void;
  addNode: (node: Node) => void;
  deleteNode: (id: string) => void;
  updateNodeStatus: (id: string, status: any) => void;
}

const initialNodes: Node[] = [
  { 
    id: 'agent-frontend', 
    type: 'agent', 
    position: { x: 250, y: 100 }, 
    data: { 
      name: 'Frontend Ace', 
      role: 'frontend', 
      status: 'idle', 
      health: 100,
      tools: ['react', 'nextjs'],
      avatar: '🎨'
    } 
  },
  { 
    id: 'agent-backend', 
    type: 'agent', 
    position: { x: 600, y: 100 }, 
    data: { 
      name: 'Backend Beast', 
      role: 'backend', 
      status: 'working', 
      health: 98,
      tools: ['fastapi', 'postgres'],
      avatar: '⚙️'
    } 
  }
];

const initialEdges: Edge[] = [
  { id: 'e1-2', source: 'agent-frontend', target: 'agent-backend', animated: true, style: { stroke: '#00F0FF' } }
];

export const useFlowStore = create<FlowState>((set, get) => ({
  nodes: initialNodes,
  edges: initialEdges,

  onNodesChange: (changes) => {
    set({
      nodes: applyNodeChanges(changes, get().nodes),
    });
  },

  onEdgesChange: (changes) => {
    set({
      edges: applyEdgeChanges(changes, get().edges),
    });
  },

  onConnect: (connection) => {
    set({
      edges: addEdge(connection, get().edges),
    });
  },

  addNode: (node) => {
    set({ nodes: [...get().nodes, node] });
  },

  deleteNode: (id) => {
    set({ 
      nodes: get().nodes.filter(n => n.id !== id),
      edges: get().edges.filter(e => e.source !== id && e.target !== id)
    });
  },

  updateNodeStatus: (id, status) => {
    set({
      nodes: get().nodes.map((node) => {
        if (node.id === id) {
          return { ...node, data: { ...node.data, ...status } };
        }
        return node;
      }),
    });
  },
}));
