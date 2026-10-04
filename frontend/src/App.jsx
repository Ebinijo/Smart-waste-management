import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { BinMonitoring } from './pages/BinMonitoring';
import { CollectionSchedule } from './pages/CollectionSchedule';
import { RouteOptimization } from './pages/RouteOptimization';
import { Analytics } from './pages/Analytics';
import { SystemInfo } from './pages/SystemInfo';
import { LayoutDashboard, Trash2, CalendarCheck, MapPin, BarChart3, Info } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [dataMode, setDataMode] = useState('synthetic');

  const mobileNavItems = [
    { id: 'dashboard', label: 'Dash', icon: LayoutDashboard },
    { id: 'monitoring', label: 'Bins', icon: Trash2 },
    { id: 'schedule', label: 'Schedule', icon: CalendarCheck },
    { id: 'route', label: 'Route', icon: MapPin },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'system-info', label: 'Info', icon: Info },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-[#090d16] text-slate-100">
      <Navbar dataMode={dataMode} setDataMode={setDataMode} />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} dataMode={dataMode} />

        <main className="flex-1 p-4 md:p-6 overflow-y-auto pb-24 md:pb-6">
          {activeTab === 'dashboard' && <Dashboard setActiveTab={setActiveTab} dataMode={dataMode} />}
          {activeTab === 'monitoring' && <BinMonitoring dataMode={dataMode} />}
          {activeTab === 'schedule' && <CollectionSchedule dataMode={dataMode} />}
          {activeTab === 'route' && <RouteOptimization dataMode={dataMode} />}
          {activeTab === 'analytics' && <Analytics dataMode={dataMode} />}
          {activeTab === 'system-info' && <SystemInfo dataMode={dataMode} />}
        </main>
      </div>

      {/* Mobile Bottom Navigation Bar */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-slate-900 border-t border-slate-800 z-40 flex justify-around p-2">
        {mobileNavItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`flex flex-col items-center p-1.5 rounded-lg text-[10px] font-medium transition ${
                isActive ? 'text-emerald-400 bg-emerald-500/10' : 'text-slate-400'
              }`}
            >
              <Icon className="w-5 h-5 mb-0.5" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>
    </div>
  );
}

