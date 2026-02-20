import React from 'react';
import { useAIStore, Task } from '../../stores/aiStore';
import { List, CheckCircle, Circle, Clock, AlertTriangle, Plus, Download } from 'lucide-react';
import clsx from 'clsx';
import { hypercodeCoreClient } from '../../services/hypercodeCoreClient';

export default function TaskQueue() {
  const { tasks, addTask, generateAgent } = useAIStore();
  const [isAdding, setIsAdding] = React.useState(false);
  const [prompt, setPrompt] = React.useState('');

  const handleAddTask = () => {
    setIsAdding(!isAdding);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    
    await generateAgent(prompt);
    setPrompt('');
    setIsAdding(false);
  };

  const StatusIcon = ({ status }: { status: Task['status'] }) => {
    switch (status) {
      case 'completed': return <CheckCircle size={16} className="text-green-500" />;
      case 'running': return <Clock size={16} className="text-blue-500 animate-spin-slow" />;
      case 'failed': return <AlertTriangle size={16} className="text-red-500" />;
      default: return <Circle size={16} className="text-gray-500" />;
    }
  };

  const PriorityBadge = ({ priority }: { priority: Task['priority'] }) => {
    const colors = {
      low: 'bg-gray-800 text-gray-300 border-gray-600',
      medium: 'bg-blue-900/30 text-blue-300 border-blue-800',
      high: 'bg-red-900/30 text-red-300 border-red-800'
    };
    return (
      <span className={clsx("text-[10px] px-2 py-0.5 rounded border uppercase font-bold", colors[priority])}>
        {priority}
      </span>
    );
  };

  return (
    <div className="bg-[var(--color-panel)] border border-[var(--color-primary)] rounded-xl p-4 h-full flex flex-col shadow-[0_0_20px_rgba(6,182,212,0.1)]">
      <div className="flex justify-between items-center mb-4 border-b border-[rgba(255,255,255,0.1)] pb-2">
        <div className="flex items-center gap-2">
          <List size={18} className="text-[var(--color-secondary)]" />
          <h3 className="font-mono text-sm font-bold text-[var(--color-secondary)]">/ TASK QUEUE</h3>
        </div>
        <button 
          onClick={handleAddTask}
          className="p-1 hover:bg-[rgba(255,255,255,0.1)] rounded transition-colors text-[var(--color-text)]"
          title="Create New Agent"
          data-cy="create-agent-button"
        >
          <Plus size={16} />
        </button>
      </div>

      {isAdding && (
        <form onSubmit={handleSubmit} className="mb-4 p-3 bg-[rgba(124,58,237,0.1)] rounded border border-[var(--color-primary)] animate-in fade-in slide-in-from-top-2">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe agent task..."
            className="w-full bg-transparent border-none outline-none text-sm text-[var(--color-text)] placeholder-gray-500 mb-2"
            autoFocus
          />
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setIsAdding(false)}
              className="px-2 py-1 text-xs text-gray-400 hover:text-white"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-2 py-1 text-xs bg-[var(--color-primary)] text-white rounded hover:bg-opacity-80"
            >
              Generate
            </button>
          </div>
        </form>
      )}

      <div className="flex-1 overflow-y-auto space-y-2 pr-2 custom-scrollbar">
        {tasks.length === 0 ? (
          <div className="text-center text-gray-500 py-8 text-sm italic">
            No active tasks in queue.
          </div>
        ) : (
          tasks.map((task) => (
            <div 
              key={task.id}
              data-cy="task-item"
              data-status={task.status}
              className="bg-[rgba(0,0,0,0.2)] p-3 rounded border border-[rgba(255,255,255,0.05)] hover:border-[var(--color-secondary)] transition-all group"
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                  <StatusIcon status={task.status} />
                  <span className={clsx("font-medium text-sm", task.status === 'completed' && "line-through text-gray-500")}>
                    {task.title}
                  </span>
                </div>
                <PriorityBadge priority={task.priority} />
              </div>
              
              {task.status === 'running' && (
                <div className="w-full bg-gray-800 h-1.5 rounded-full mt-2 overflow-hidden">
                  <div 
                    className="bg-[var(--color-primary)] h-full transition-all duration-500"
                    style={{ width: `${task.progress}%` }}
                  />
                </div>
              )}

              {task.status === 'completed' && (
                <a 
                  href={hypercodeCoreClient.getArtifactUrl(task.id)}
                  download
                  className="flex items-center gap-1 mt-2 text-xs text-[var(--color-secondary)] hover:underline"
                  target="_blank" rel="noopener noreferrer"
                  data-cy="download-artifact-link"
                >
                  <Download size={12} />
                  Download Artifact
                </a>
              )}
              
              <div className="flex justify-between text-[10px] text-gray-500 mt-2 font-mono">
                <span>ID: {task.id.slice(-4)}</span>
                <span className="capitalize">{task.status}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
