import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import HyperLayout from './components/HyperLayout';
import { NavBar } from './components/navigation/NavBar';
import EditorPage from './pages/Editor';
import AIDashboard from './pages/AIDashboard';

export default function App() {
  return (
    <BrowserRouter>
      <HyperLayout showHeader={false}>
        <div className="flex flex-col h-full w-full">
          <NavBar />
          <div className="flex-1 overflow-hidden relative z-10">
            <Routes>
              <Route path="/" element={<EditorPage />} />
              <Route path="/ai-dashboard" element={<AIDashboard />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </div>
        </div>
      </HyperLayout>
    </BrowserRouter>
  );
}
