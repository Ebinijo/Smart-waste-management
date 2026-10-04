import React, { useState } from 'react';
import { Cpu, ArrowRight, Sparkles, AlertTriangle, ShieldCheck, Clock } from 'lucide-react';
import { PriorityBadge, DecisionBadge } from './StatusBadge';

export function DecisionPipelineCard({ bins = [] }) {
  const [selectedBinId, setSelectedBinId] = useState(bins.length > 0 ? bins[0].Bin_ID : '');

  const selectedBin = bins.find((b) => b.Bin_ID === selectedBinId) || (bins.length > 0 ? bins[0] : null);

  if (!selectedBin) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 text-slate-400 text-xs">
        No bin data available for AI Decision Pipeline visualization.
      </div>
    );
  }

  const curFill = Number(selectedBin.Fill_Level_Percent || 0);
  const predFill = Number(selectedBin.Next_Fill_Level_Percent || curFill);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <Cpu className="w-5 h-5 text-emerald-400" />
            AI-Based Collection Decision Pipeline
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Interactive demonstration of ML prediction, priority calculation, and dispatch rules
          </p>
        </div>

        {/* Bin Selector Dropdown */}
        <div className="flex items-center space-x-2">
          <label className="text-xs text-slate-400 font-medium">Select Bin:</label>
          <select
            value={selectedBinId}
            onChange={(e) => setSelectedBinId(e.target.value)}
            className="px-3 py-1.5 bg-slate-950 border border-slate-700 rounded-lg text-xs text-slate-200 font-mono font-bold focus:outline-none focus:border-emerald-500"
          >
            {bins.map((b) => (
              <option key={b.Bin_ID} value={b.Bin_ID}>
                {b.Bin_ID} ({b.Zone} - {b.Fill_Level_Percent}%)
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Visual Pipeline Steps Flow (Current Fill -> ML Predicted Fill -> Priority -> Dispatch Decision) */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 relative">
        {/* Step 1: Current Fill */}
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex flex-col justify-between space-y-3 relative">
          <div className="flex items-center justify-between">
            <span className="text-[11px] uppercase font-bold text-slate-400">Step 1: Current Bin Data</span>
            <span className="text-xs text-slate-500">Current</span>
          </div>
          <div>
            <div className="text-2xl font-extrabold text-slate-100">{curFill}%</div>
            <div className="text-[11px] text-slate-400 mt-1">Current Fill Level</div>
          </div>
          <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
            <div
              className={`h-full ${curFill >= 90 ? 'bg-rose-500' : curFill >= 70 ? 'bg-amber-500' : 'bg-emerald-500'}`}
              style={{ width: `${curFill}%` }}
            ></div>
          </div>
        </div>

        {/* Step 2: ML Predicted Fill */}
        <div className="bg-slate-950 p-4 rounded-xl border border-sky-500/30 flex flex-col justify-between space-y-3 relative">
          <div className="flex items-center justify-between">
            <span className="text-[11px] uppercase font-bold text-sky-400 flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5 text-sky-400" /> Step 2: Random Forest Regression
            </span>
            <span className="text-xs text-sky-400/80 font-mono">RF Regressor</span>
          </div>
          <div>
            <div className="text-2xl font-extrabold text-sky-300">{predFill}%</div>
            <div className="text-[11px] text-slate-400 mt-1">Predicted Next Fill</div>
          </div>
          <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
            <div
              className={`h-full ${predFill >= 90 ? 'bg-rose-500' : predFill >= 70 ? 'bg-amber-500' : 'bg-sky-400'}`}
              style={{ width: `${predFill}%` }}
            ></div>
          </div>
        </div>

        {/* Step 3: Priority */}
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex flex-col justify-between space-y-3 relative">
          <div className="flex items-center justify-between">
            <span className="text-[11px] uppercase font-bold text-slate-400">Step 3: Priority Engine</span>
            <span className="text-xs text-slate-500">Threshold Rules</span>
          </div>
          <div>
            <div className="mt-1">
              <PriorityBadge priority={selectedBin.Priority_Level} />
            </div>
            <div className="text-[11px] text-slate-400 mt-2">
              Score: {selectedBin.Priority_Level === 'HIGH' ? 3 : selectedBin.Priority_Level === 'MEDIUM' ? 2 : 1} / 3
            </div>
          </div>
          <div className="text-[10px] text-slate-500">
            {curFill >= 90 || predFill >= 90 ? 'Max Fill ≥ 90%' : (curFill >= 70 || predFill >= 70 ? 'Max Fill ≥ 70%' : 'Safe Fill')}
          </div>
        </div>

        {/* Step 4: Dispatch Decision */}
        <div className="bg-slate-950 p-4 rounded-xl border border-purple-500/30 flex flex-col justify-between space-y-3 relative">
          <div className="flex items-center justify-between">
            <span className="text-[11px] uppercase font-bold text-purple-400">Step 4: Dispatch Decision</span>
            <span className="text-xs text-purple-400/80 font-mono">Action</span>
          </div>
          <div>
            <div className="mt-1">
              <DecisionBadge decision={selectedBin.Dispatch_Decision} />
            </div>
            <div className="text-[11px] text-slate-400 mt-2">
              {selectedBin.Dispatch_Decision === 'Dispatch Immediately'
                ? 'Immediate Truck Allocation'
                : selectedBin.Dispatch_Decision === 'Schedule Collection'
                ? 'Added to Today\'s Route'
                : 'No Collection Required'}
            </div>
          </div>
          <div className="text-[10px] text-slate-500">
            Overflow Risk: <span className={selectedBin.Overflow_Risk ? 'text-rose-400 font-bold' : 'text-slate-400'}>{selectedBin.Overflow_Risk ? 'YES' : 'NO'}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
