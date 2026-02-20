import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Node, Edge } from 'reactflow';
import { hypercodeCoreClient, AgentDto } from '../services/hypercodeCoreClient';

export type AgentStatus = 'idle' | 'working' | 'completed' | 'failed';
export type TaskPriority = 'low' | 'medium' | 'high';

export interface AgentNodeData {
  label: string;
  status: AgentStatus;
  role: string;
}

export interface Task {
  id: string;
  title: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  priority: TaskPriority;
  progress: number;
  }

interface AIState {
  // Actions
  generateAgent: (prompt: string) => Promise<void>;
  
  // Workflow State
  nodes: Node<AgentNodeData>[];
  edges: Edge[];
  setNodes: (nodes: Node<AgentNodeData>[]) => void;
  setEdges: (edges: Edge[]) => void;
  updateAgentStatus: (nodeId: string, status: AgentStatus) => void;
  fetchAgents: () => Promise<void>;

  // Budget State
  totalBudget: number;
  spentBudget: number;
  setBudget: (total: number) => void;
  addExpense: (amount: number) => void;
  fetchBudget: () => Promise<void>;

  // Task Queue State
  tasks: Task[];
  addTask: (task: Task) => void;
  updateTaskStatus: (taskId: string, status: Task['status'], progress?: number) => void;
  removeTask: (taskId: string) => void;
  
  // Real-time
  isConnected: boolean;
  setConnected: (status: boolean) => void;
}

export const useAIStore = create<AIState>()(
  persist(
    (set, get) => ({
      // Workflow Initial State
      nodes: [],
      edges: [
        { id: 'e1-2', source: '1', target: '2', animated: true },
        { id: 'e2-3', source: '2', target: '3', animated: true },
      ],
      setNodes: (nodes) => set({ nodes }),
      setEdges: (edges) => set({ edges }),
      updateAgentStatus: (nodeId, status) =>
        set((state) => ({
          nodes: state.nodes.map((node) =>
            node.id === nodeId ? { ...node, data: { ...node.data, status } } : node
          ),
        })),
      fetchAgents: async () => {
        try {
          const agents = await hypercodeCoreClient.getAgents();
          const nodes: Node<AgentNodeData>[] = agents.map((agent: AgentDto, index: number) => ({
            id: agent.id,
            type: 'agent',
            position: { x: 250, y: 50 + index * 150 },
            data: { label: agent.name, status: agent.status, role: agent.role }
          }));
          set({ nodes });
        } catch (error) {
          console.error("Failed to fetch agents", error);
        }
      },

      generateAgent: async (prompt) => {
        try {
          const agent = await hypercodeCoreClient.generateAgent(prompt);
          // Add to task queue immediately
          get().addTask({
            id: agent.id,
            title: `Agent: ${agent.name}`,
            status: 'pending',
            priority: 'high',
            progress: 0
          });
          // Refresh agents list to update graph
          get().fetchAgents();
        } catch (error) {
          console.error("Failed to generate agent", error);
        }
      },

      // Budget Initial State
      totalBudget: 10.0,
      spentBudget: 0.0,
      setBudget: (total) => set({ totalBudget: total }),
      addExpense: (amount) => set((state) => ({ spentBudget: state.spentBudget + amount })),
      fetchBudget: async () => {
        try {
          const { total, spent } = await hypercodeCoreClient.getBudgetStatus();
          set({ totalBudget: total, spentBudget: spent });
        } catch (error) {
           console.error("Failed to fetch budget", error);
        }
      },

      // Task Queue Initial State
      tasks: [],
      addTask: (task) => set((state) => ({ tasks: [...state.tasks, task] })),
      updateTaskStatus: (taskId, status, progress) =>
        set((state) => ({
          tasks: state.tasks.map((t) =>
            t.id === taskId ? { ...t, status, progress: progress ?? t.progress } : t
          ),
        })),
      removeTask: (taskId) => set((state) => ({ tasks: state.tasks.filter((t) => t.id !== taskId) })),
      
      // Real-time
      isConnected: false,
      setConnected: (status) => set({ isConnected: status }),
    }),
    {
      name: 'hypercode-ai-store',
    }
  )
);
