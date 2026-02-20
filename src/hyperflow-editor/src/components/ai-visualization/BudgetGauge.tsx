import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { useAIStore } from '../../stores/aiStore';
import { DollarSign } from 'lucide-react';

export default function BudgetGauge() {
  const { totalBudget, spentBudget } = useAIStore();
  
  const percentage = Math.min((spentBudget / totalBudget) * 100, 100);
  const remaining = Math.max(totalBudget - spentBudget, 0);
  
  const data = [
    { name: 'Spent', value: spentBudget },
    { name: 'Remaining', value: remaining }
  ];

  let color = '#10b981'; // Green
  if (percentage > 70) color = '#eab308'; // Yellow
  if (percentage > 90) color = '#ef4444'; // Red

  const COLORS = [color, '#1a1a2e'];

  return (
    <div className="bg-[var(--color-panel)] border border-[var(--color-primary)] rounded-xl p-4 h-full flex flex-col shadow-[0_0_20px_rgba(6,182,212,0.1)]">
      <div className="flex justify-between items-center mb-2">
        <h3 className="font-mono text-sm font-bold text-[var(--color-secondary)]">/ BUDGET ALLOCATION</h3>
        <DollarSign size={16} className="text-[var(--color-text)]" />
      </div>

      <div className="flex-1 relative min-h-[150px] w-full h-full">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="70%"
              startAngle={180}
              endAngle={0}
              innerRadius={60}
              outerRadius={80}
              paddingAngle={5}
              dataKey="value"
              stroke="none"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip 
              contentStyle={{ backgroundColor: '#0f0f1e', borderColor: '#7c3aed', color: '#fff' }}
              itemStyle={{ color: '#00ff88' }}
              formatter={(value: number | undefined) => [`$${(value ?? 0).toFixed(4)}`, 'Amount']}
            />
          </PieChart>
        </ResponsiveContainer>
        
        <div className="absolute top-[60%] left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center">
          <div className="text-3xl font-bold text-white transition-colors duration-500" style={{ color }}>
            {percentage.toFixed(1)}%
          </div>
          <div className="text-xs text-gray-400">USED</div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mt-2 border-t border-[rgba(255,255,255,0.1)] pt-3">
        <div>
          <div className="text-xs text-gray-500">TOTAL</div>
          <div className="text-lg font-mono text-[var(--color-text)]">${totalBudget.toFixed(2)}</div>
        </div>
        <div className="text-right">
          <div className="text-xs text-gray-500">REMAINING</div>
          <div className="text-lg font-mono text-white">${remaining.toFixed(4)}</div>
        </div>
      </div>
    </div>
  );
}
