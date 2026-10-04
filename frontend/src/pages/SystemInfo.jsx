import React from 'react';
import { 
  Database, 
  Layers, 
  Cpu, 
  Sparkles, 
  CheckCircle, 
  GitBranch, 
  Network, 
  CalendarCheck, 
  BarChart3, 
  ShieldAlert, 
  ArrowRight,
  AlertCircle
} from 'lucide-react';

export function SystemInfo({ dataMode = 'synthetic' }) {
  const isChennai = dataMode === 'chennai';

  const steps = [
    { title: '1. Current Bin Data', desc: isChennai ? 'Real Greater Chennai Corporation bin locations from CSV' : 'Synthesized 100-bin municipal dataset', icon: Database, color: 'text-emerald-400 border-emerald-500/30' },
    { title: '2. Preprocessing & Encoding', desc: '9-feature vector extraction, temporal encoding, density scaling', icon: Layers, color: 'text-sky-400 border-sky-500/30' },
    { title: '3. Random Forest Regression', desc: 'RandomForestRegressor (.pkl joblib) loaded for fill level prediction', icon: Cpu, color: 'text-purple-400 border-purple-500/30' },
    { title: '4. Fill-Level Prediction', desc: 'Target Next_Fill_Level_Percent predicted and clipped [0, 100]', icon: Sparkles, color: 'text-indigo-400 border-indigo-500/30' },
    { title: '5. Priority Engine', desc: 'HIGH (≥90%), MEDIUM (≥70%), LOW (<70%) rule-based decision thresholds', icon: CheckCircle, color: 'text-amber-400 border-amber-500/30' },
    { title: '6. Dispatch Policy Logic', desc: 'Dispatch Immediately (≥90%), Schedule Collection (≥80%), No Dispatch (<80%)', icon: GitBranch, color: 'text-rose-400 border-rose-500/30' },
    { title: '7. Dijkstra Route Optimization', desc: 'NetworkX graph Dijkstra algorithm shortest-path calculation from Simulation Depot', icon: Network, color: 'text-emerald-400 border-emerald-500/30' },
    { title: '8. Collection Schedule', desc: 'Optimized manifest prioritized by high/medium bin urgency', icon: CalendarCheck, color: 'text-sky-400 border-sky-500/30' },
    { title: '9. 30-Day Evaluation', desc: '30-day simulation comparing traditional vs intelligent metrics', icon: BarChart3, color: 'text-purple-400 border-purple-500/30' },
  ];

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h2 className="text-xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
          Project Methodology & Technical Specifications
          <span className="text-xs px-2.5 py-0.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-md font-mono">
            Research Architecture
          </span>
        </h2>
        <p className="text-xs text-slate-400">
          Complete end-to-end architecture from data ingestion to ML inference and Dijkstra shortest-path routing
        </p>
      </div>

      {/* Mode Technical Summary Banner */}
      <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-2">
        <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
          <Database className="w-4 h-4 text-emerald-400" />
          Active Data Architecture Mode: <span className="text-emerald-400">{isChennai ? 'Real Chennai Locations + Simulated Operational Data' : 'Synthetic Demo Mode'}</span>
        </h3>
        <p className="text-xs text-slate-400 leading-relaxed">
          {isChennai
            ? 'Geographic lat/lon coordinates, Bin IDs, Area names, and Division codes are read directly from data/raw/chennai_real_bins_clean.csv (real municipal bin locations across 15 zones and 199 divisions). Operational parameters (current fill level, generation rate, hours since collection) are deterministically simulated for research evaluation.'
            : 'Synthetic benchmark dataset comprising 100 municipal bins with simulated fill telemetry and simulated road network graph coordinates.'}
        </p>
      </div>

      {/* Visual Pipeline Flow */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-5">
        <h3 className="text-base font-bold text-slate-100 flex items-center gap-2 border-b border-slate-800 pb-3">
          <Cpu className="w-5 h-5 text-emerald-400" />
          End-to-End System Pipeline Flow
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {steps.map((s, idx) => {
            const Icon = s.icon;
            return (
              <div key={idx} className={`bg-slate-950 p-4 rounded-xl border ${s.color} space-y-2 flex flex-col justify-between`}>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-200">{s.title}</span>
                  <div className="p-1.5 bg-slate-900 rounded-lg">
                    <Icon className="w-4 h-4" />
                  </div>
                </div>
                <p className="text-[11px] text-slate-400 leading-relaxed">{s.desc}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Project Scope & System Limitations */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-4">
        <div className="flex items-center space-x-2 text-amber-300 font-bold text-base border-b border-slate-800 pb-3">
          <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0" />
          <span>Project Scope & System Assumptions</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs text-slate-300">
          <div className="p-3.5 bg-slate-950 rounded-lg border border-slate-800 space-y-1">
            <div className="font-bold text-amber-400 flex items-center gap-1.5">
              <AlertCircle className="w-3.5 h-3.5" /> Source Data vs Operational Simulation
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Chennai geographic bin locations and municipal attributes are real source data. Operational bin parameters (fill levels, generation rates) are simulated using deterministic seeds. No physical sensors or live IoT hardware telemetry are used.
            </p>
          </div>

          <div className="p-3.5 bg-slate-950 rounded-lg border border-slate-800 space-y-1">
            <div className="font-bold text-amber-400 flex items-center gap-1.5">
              <AlertCircle className="w-3.5 h-3.5" /> Random Forest Regression Model
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              The model is a Random Forest Regressor trained on 9 environmental/operational features to predict continuous next fill level (0–100%). Priority levels and dispatch decisions are determined by the project's prototype rule-based priority engine.
            </p>
          </div>

          <div className="p-3.5 bg-slate-950 rounded-lg border border-slate-800 space-y-1">
            <div className="font-bold text-amber-400 flex items-center gap-1.5">
              <AlertCircle className="w-3.5 h-3.5" /> Dijkstra Network Graph Routing
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Haversine geographic distances between bin coordinates form a complete NetworkX graph. Shortest-path TSP routes originate from a central <em>Simulation Depot</em>.
            </p>
          </div>

          <div className="p-3.5 bg-slate-950 rounded-lg border border-slate-800 space-y-1">
            <div className="font-bold text-amber-400 flex items-center gap-1.5">
              <AlertCircle className="w-3.5 h-3.5" /> Fuel & Efficiency Assumptions
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Fuel consumption (L) is calculated using the baseline formula: <code>0.30 L/km + 0.05 L/stop</code> ("Estimated Fuel — Simulation Assumption").
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

