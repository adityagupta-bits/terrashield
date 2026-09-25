import React from 'react';
import { Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { Navbar } from './components/layout/Navbar';
import { Sidebar } from './components/layout/Sidebar';
import { EmergencyStrip } from './components/layout/EmergencyStrip';
import { NewsTicker } from './components/layout/NewsTicker';
import { useWebSocket } from './hooks/useWebSocket';

// Pages
import { Dashboard } from './pages/Dashboard';
import { Alerts } from './pages/Alerts';
import { Broadcast } from './pages/Broadcast';
import { Contacts } from './pages/Contacts';
import { Weather } from './pages/Weather';
import { News } from './pages/News';
import { MeshTopologyPage } from './pages/MeshTopologyPage';
import { WhatsAppPage } from './pages/WhatsAppPage';
import { CitizenPortal } from './pages/CitizenPortal';
import { Login } from './pages/Login';

// Authority Layout Wrapper
const AuthorityLayout: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans selection:bg-sky-500/20 selection:text-sky-900">
      <Navbar />
      <EmergencyStrip />
      
      <div className="flex-1 flex overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8 bg-slate-50">
          <Outlet />
        </main>
      </div>

      <NewsTicker />
    </div>
  );
};

export default function App() {
  // Global live WebSocket connection with exponential backoff & React Query invalidation
  useWebSocket();

  return (
    <Routes>
      {/* Standalone Citizen Portal (Mobile-first, Light Mode) */}
      <Route path="/citizen" element={<CitizenPortal />} />

      {/* Login Page */}
      <Route path="/login" element={<Login />} />

      {/* Authority Command Center Shell */}
      <Route element={<AuthorityLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/alerts" element={<Alerts />} />
        <Route path="/broadcast" element={<Broadcast />} />
        <Route path="/contacts" element={<Contacts />} />
        <Route path="/weather" element={<Weather />} />
        <Route path="/news" element={<News />} />
        <Route path="/mesh" element={<MeshTopologyPage />} />
        <Route path="/whatsapp" element={<WhatsAppPage />} />
      </Route>

      {/* Catch-all fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
