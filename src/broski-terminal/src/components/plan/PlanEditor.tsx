import React, { useState } from 'react';
import { ProjectPlan, Phase, Task } from './types';
import { planService } from '../../services/PlanService';
import { useRouter } from 'next/navigation';
import { Save, Plus, Trash2, GripVertical } from 'lucide-react';

interface PlanEditorProps {
  initialPlan?: ProjectPlan;
  mode: 'create' | 'edit';
}

export const PlanEditor: React.FC<PlanEditorProps> = ({ initialPlan, mode }) => {
  const router = useRouter();
  const [plan, setPlan] = useState<Partial<ProjectPlan>>(initialPlan || {
    title: '',
    description: '',
    phases: [],
    isPublic: false,
    userId: 'user-1'
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Drag and Drop State
  const [draggedPhaseIdx, setDraggedPhaseIdx] = useState<number | null>(null);

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      // Re-index orders before saving to ensure consistency
      const planToSave = {
          ...plan,
          phases: plan.phases?.map((p, i) => ({
              ...p,
              order: i,
              tasks: p.tasks.map((t, j) => ({ ...t, order: j }))
          }))
      };

      if (mode === 'create') {
        const newPlan = await planService.createPlan(planToSave as any);
        router.push(`/plans/${newPlan.id}`);
      } else {
        if (!plan.id) throw new Error("Plan ID missing for update");
        await planService.updatePlan(plan.id, planToSave);
      }
    } catch (e: any) {
      console.error(e);
      setError(e.message || "Failed to save plan");
    } finally {
      setSaving(false);
    }
  };

  const handlePhaseDrop = (targetIdx: number) => {
      if (draggedPhaseIdx === null || draggedPhaseIdx === targetIdx) return;
      
      const newPhases = [...(plan.phases || [])];
      const [removed] = newPhases.splice(draggedPhaseIdx, 1);
      newPhases.splice(targetIdx, 0, removed);
      
      setPlan({...plan, phases: newPhases});
      setDraggedPhaseIdx(null);
  };

  return (
    <div className="p-6 max-w-4xl mx-auto bg-[#0f172a] text-white rounded-lg shadow-xl font-sans">
        {/* Header */}
        <div className="flex justify-between items-center mb-6 border-b border-gray-700 pb-4">
            <h1 className="text-2xl font-bold text-[#818cf8]">
                {mode === 'create' ? 'Create New Plan' : 'Edit Plan'}
            </h1>
            <button 
                onClick={handleSave}
                disabled={saving}
                className="flex items-center gap-2 px-4 py-2 bg-[#22d3ee] text-black font-semibold rounded hover:bg-[#06b6d4] disabled:opacity-50 transition-colors"
            >
                <Save size={18} />
                {saving ? 'Saving...' : 'Save Plan'}
            </button>
        </div>

        {error && (
            <div className="mb-4 p-3 bg-red-900/50 border border-red-500 rounded text-red-200">
                {error}
            </div>
        )}

        {/* Basic Info */}
        <div className="space-y-4 mb-8">
            <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Plan Title</label>
                <input 
                    type="text" 
                    value={plan.title}
                    onChange={e => setPlan({...plan, title: e.target.value})}
                    className="w-full bg-[#1e293b] border border-gray-600 rounded p-2 text-white focus:ring-2 focus:ring-[#818cf8] outline-none transition-all"
                    placeholder="e.g. Project Phoenix"
                />
            </div>
            <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Description (Markdown supported)</label>
                <textarea 
                    value={plan.description || ''}
                    onChange={e => setPlan({...plan, description: e.target.value})}
                    className="w-full bg-[#1e293b] border border-gray-600 rounded p-2 text-white h-32 focus:ring-2 focus:ring-[#818cf8] outline-none font-mono transition-all"
                    placeholder="Describe the project goals..."
                />
            </div>
        </div>

        {/* Phases Editor */}
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-200">Phases</h2>
                <button 
                    onClick={() => {
                        const newPhase: Phase = {
                            id: crypto.randomUUID(),
                            title: 'New Phase',
                            status: 'pending',
                            order: (plan.phases?.length || 0),
                            tasks: []
                        };
                        setPlan({...plan, phases: [...(plan.phases || []), newPhase]});
                    }}
                    className="flex items-center gap-1 text-sm text-[#22d3ee] hover:text-[#06b6d4] transition-colors"
                >
                    <Plus size={16} /> Add Phase
                </button>
            </div>
            
            {plan.phases?.length === 0 && (
                <div className="text-center p-8 border border-dashed border-gray-700 rounded text-gray-500">
                    No phases added yet. Click "Add Phase" to start.
                </div>
            )}

            {plan.phases?.map((phase, idx) => (
                <div 
                    key={phase.id} 
                    className={`bg-[#1e293b] rounded border border-gray-700 p-4 transition-all hover:border-gray-600 ${draggedPhaseIdx === idx ? 'opacity-50 border-dashed border-[#22d3ee]' : ''}`}
                    draggable
                    onDragStart={() => setDraggedPhaseIdx(idx)}
                    onDragOver={(e) => e.preventDefault()}
                    onDrop={(e) => {
                        e.preventDefault();
                        handlePhaseDrop(idx);
                    }}
                >
                    <div className="flex gap-4 mb-4">
                        <div className="pt-2 text-gray-500 cursor-grab hover:text-gray-300 active:cursor-grabbing"><GripVertical size={20} /></div>
                        <div className="flex-1 space-y-2">
                            <input 
                                type="text"
                                value={phase.title}
                                onChange={e => {
                                    const newPhases = [...(plan.phases || [])];
                                    newPhases[idx].title = e.target.value;
                                    setPlan({...plan, phases: newPhases});
                                }}
                                className="w-full bg-transparent border-b border-gray-600 focus:border-[#818cf8] outline-none text-lg font-medium placeholder-gray-600"
                                placeholder="Phase Title"
                            />
                            <input 
                                type="text"
                                value={phase.description || ''}
                                onChange={e => {
                                    const newPhases = [...(plan.phases || [])];
                                    newPhases[idx].description = e.target.value;
                                    setPlan({...plan, phases: newPhases});
                                }}
                                className="w-full bg-transparent text-sm text-gray-400 focus:text-gray-200 outline-none placeholder-gray-600"
                                placeholder="Phase description..."
                            />
                        </div>
                        <button 
                            onClick={() => {
                                const newPhases = plan.phases?.filter(p => p.id !== phase.id);
                                setPlan({...plan, phases: newPhases});
                            }}
                            className="text-gray-500 hover:text-red-400 transition-colors"
                            title="Delete Phase"
                        >
                            <Trash2 size={18} />
                        </button>
                    </div>

                    {/* Tasks */}
                    <div className="pl-10 space-y-2">
                        {phase.tasks.map((task, tIdx) => (
                            <div key={task.id} className="flex gap-2 items-center group">
                                <div className="text-gray-600 cursor-grab"><GripVertical size={14} /></div>
                                <input 
                                    type="text"
                                    value={task.description}
                                    onChange={e => {
                                        const newPhases = [...(plan.phases || [])];
                                        newPhases[idx].tasks[tIdx].description = e.target.value;
                                        setPlan({...plan, phases: newPhases});
                                    }}
                                    className="flex-1 bg-black/20 rounded px-2 py-1 text-sm border border-transparent focus:border-[#818cf8] outline-none transition-all placeholder-gray-600"
                                    placeholder="Task description"
                                />
                                <button 
                                    onClick={() => {
                                        const newPhases = [...(plan.phases || [])];
                                        newPhases[idx].tasks = phase.tasks.filter(t => t.id !== task.id);
                                        setPlan({...plan, phases: newPhases});
                                    }}
                                    className="opacity-0 group-hover:opacity-100 text-gray-500 hover:text-red-400 transition-opacity"
                                    title="Delete Task"
                                >
                                    <Trash2 size={14} />
                                </button>
                            </div>
                        ))}
                        <button 
                            onClick={() => {
                                const newPhases = [...(plan.phases || [])];
                                newPhases[idx].tasks.push({
                                    id: crypto.randomUUID(),
                                    description: '',
                                    status: 'pending',
                                    order: phase.tasks.length
                                });
                                setPlan({...plan, phases: newPhases});
                            }}
                            className="text-xs text-[#818cf8] hover:underline flex items-center gap-1 mt-2"
                        >
                            <Plus size={12} /> Add Task
                        </button>
                    </div>
                </div>
            ))}
        </div>
    </div>
  );
};
