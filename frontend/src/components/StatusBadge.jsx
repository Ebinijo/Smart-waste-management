import React from 'react';

export function PriorityBadge({ priority }) {
  const p = priority ? priority.toUpperCase() : 'LOW';
  if (p === 'HIGH') {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-500/20 text-rose-400 border border-rose-500/30">
        <span className="w-1.5 h-1.5 rounded-full bg-rose-500 mr-1.5 animate-pulse"></span>
        HIGH PRIORITY
      </span>
    );
  }
  if (p === 'MEDIUM') {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/20 text-amber-400 border border-amber-500/30">
        <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mr-1.5"></span>
        MEDIUM
      </span>
    );
  }
  return (
    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5"></span>
      LOW
    </span>
  );
}

export function DecisionBadge({ decision }) {
  if (decision === 'Dispatch Immediately') {
    return (
      <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-bold bg-red-600/30 text-red-300 border border-red-500/40">
        ⚡ Dispatch Immediately
      </span>
    );
  }
  if (decision === 'Schedule Collection') {
    return (
      <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-amber-500/20 text-amber-300 border border-amber-500/30">
        📅 Schedule Collection
      </span>
    );
  }
  return (
    <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-slate-800 text-slate-400 border border-slate-700">
      ✓ No Dispatch
    </span>
  );
}

export function OverflowBadge({ risk }) {
  if (risk) {
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-red-950 text-red-400 border border-red-800/60">
        ⚠️ Risk
      </span>
    );
  }
  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-800/80 text-slate-400">
      Safe
    </span>
  );
}
