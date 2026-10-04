import React from 'react';
import { 
  LayoutDashboard, 
  Trash2, 
  CalendarCheck, 
  MapPin, 
  BarChart3, 
  Info 
} from 'lucide-react';

export function Sidebar({ activeTab, setActiveTab, dataMode }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'monitoring', label: 'Bin Monitoring', icon: Trash2 },
    { id: 'schedule', label: 'Collection Schedule', icon: CalendarCheck },
    { id: 'route', label: 'Route Optimization', icon: MapPin },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'system-info', label: 'System Information', icon: Info },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 shrink-0 p-4 flex flex-col justify-between hidden md:flex min-h-[calc(100vh-65px)]">
      <nav className="space-y-1">
        <div className="px-3 py-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
          System Menu
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg font-medium text-sm transition-all ${
                isActive
                  ? 'bg-emerald-600 text-white shadow-md shadow-emerald-950/40'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800 text-xs text-slate-400 space-y-1">
        <div className="font-semibold text-slate-300">Intelligent Waste System</div>
        <div>RF Regressor + Dijkstra</div>
        <div className="text-[11px] text-amber-400/90 pt-1 font-medium">
          {dataMode === 'chennai' ? '📍 Real Chennai + Simulated Ops' : '🧪 Synthetic Demo Mode'}
        </div>
      </div>
    </aside>
  );
}

