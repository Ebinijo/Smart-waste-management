import React from 'react';
import { Trash2, Cpu, MapPin, Database } from 'lucide-react';

export function Navbar({ dataMode, setDataMode }) {
  return (
    <header className="bg-slate-900/90 backdrop-blur border-b border-slate-800 sticky top-0 z-30 px-4 md:px-6 py-3 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
      <div className="flex items-center space-x-3">
        <div className="p-2 bg-gradient-to-tr from-emerald-600 to-teal-500 rounded-xl shadow-lg shadow-emerald-950/50 shrink-0">
          <Trash2 className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-base md:text-lg font-bold text-slate-100 tracking-tight flex items-center gap-2">
            Intelligent Waste Collection Scheduling System
            <span className="text-[10px] md:text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
              ML v1.0
            </span>
          </h1>
          <p className="text-xs text-slate-400">Random Forest Regressor & Dijkstra Route Optimization Engine</p>
        </div>
      </div>

      <div className="flex items-center space-x-3 text-xs">
        {/* Data Mode Selector */}
        <div className="flex items-center space-x-2 bg-slate-950 border border-slate-700 rounded-lg p-1">
          <button
            onClick={() => setDataMode('synthetic')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md font-medium transition ${
              dataMode === 'synthetic'
                ? 'bg-emerald-600 text-white shadow'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Database className="w-3.5 h-3.5" />
            <span>Synthetic Demo</span>
          </button>
          <button
            onClick={() => setDataMode('chennai')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md font-medium transition ${
              dataMode === 'chennai'
                ? 'bg-teal-600 text-white shadow'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <MapPin className="w-3.5 h-3.5 text-amber-300" />
            <span>Chennai Real Locations</span>
          </button>
        </div>

        <div className="hidden lg:flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 border border-slate-700">
          <Cpu className="w-4 h-4 text-sky-400" />
          <span>RF ML Active</span>
        </div>
      </div>
    </header>
  );
}

