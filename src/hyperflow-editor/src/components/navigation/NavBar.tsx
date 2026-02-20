import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { Terminal, Brain, Activity } from 'lucide-react';
import clsx from 'clsx';

export const NavBar: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'EDITOR', icon: <Terminal size={18} /> },
    { path: '/ai-dashboard', label: 'VISUAL CORTEX', icon: <Brain size={18} /> },
  ];

  return (
    <nav className="flex items-center gap-2 px-4 py-2 bg-[var(--color-panel)] border-b border-[var(--color-secondary)] backdrop-blur-md">
      <div className="flex items-center gap-2 mr-8">
        <Activity className="text-[var(--color-primary)] animate-pulse" size={20} />
        <span className="font-bold text-[var(--color-secondary)] tracking-widest text-sm">HYPERCODE</span>
      </div>

      <div className="flex items-center gap-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              clsx(
                "flex items-center gap-2 px-4 py-2 rounded-md transition-all duration-200 text-sm font-mono tracking-wide",
                isActive
                  ? "bg-[rgba(124,58,237,0.2)] text-[var(--color-text)] border border-[var(--color-primary)] shadow-[0_0_10px_rgba(124,58,237,0.3)]"
                  : "text-gray-400 hover:text-[var(--color-secondary)] hover:bg-[rgba(6,182,212,0.1)]"
              )
            }
          >
            {item.icon}
            <span>{item.label}</span>
          </NavLink>
        ))}
      </div>

      <div className="ml-auto flex items-center gap-4 text-xs font-mono text-gray-500">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_5px_#22c55e] animate-pulse"></div>
          <span>SYSTEM ONLINE</span>
        </div>
        <span>v2.0.0</span>
      </div>
    </nav>
  );
};
