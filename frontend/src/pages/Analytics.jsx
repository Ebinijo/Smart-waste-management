import React, { useEffect, useState } from 'react';
import { Fuel, MapPin, StopCircle, AlertTriangle, ShieldAlert, CheckCircle2, TrendingDown, ArrowRight } from 'lucide-react';
import { fetchAnalytics } from '../services/api';

const PIE_COLORS = ['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6'];

export function Analytics({ dataMode = 'synthetic' }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    fetchAnalytics(dataMode)
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [dataMode]);


  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center space-y-3">
          <div className="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-sm text-slate-400 font-medium">Aggregating 30-Day Evaluation Metrics...</span>
        </div>
      </div>
    );
  }

  if (error || !data || data.status === 'warning') {
    return (
      <div className="p-8 bg-slate-900 border border-slate-800 rounded-xl text-center space-y-3">
        <AlertTriangle className="w-10 h-10 text-amber-400 mx-auto" />
        <h3 className="text-lg font-bold text-slate-200">Evaluation Data Not Loaded</h3>
        <p className="text-xs text-slate-400 max-w-md mx-auto">
          The 30-day evaluation simulation file (30_day_evaluation_results.csv) is currently unavailable or uninitialized.
        </p>
      </div>
    );
  }

  const { distance_reduction_percent, fuel_reduction_percent, stop_reduction_percent, summary, daily_evaluation, distributions } = data;

  // Calculate unnecessary visits reduction from actual data
  const tradStopsAvg = summary.avg_traditional_stops;
  const intelStopsAvg = summary.avg_intelligent_stops;
  const unnecessaryVisitsSaved = Math.round(tradStopsAvg - intelStopsAvg);

  return (
    <div className="space-y-6">
      {/* Title & Badges */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
            30-Day Simulation Analytics & Evaluation
            <span className="text-xs px-2.5 py-0.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-md font-mono font-semibold">
              30-Day Simulation
            </span>
          </h2>
          <p className="text-xs text-slate-400">
            Empirical evaluation results comparing traditional fixed schedule vs ML-driven Dijkstra optimization
          </p>
        </div>

        <div className="flex items-center space-x-2 px-3 py-1.5 bg-amber-500/10 border border-amber-500/30 rounded-lg text-xs text-amber-300 font-medium shrink-0">
          <ShieldAlert className="w-4 h-4 text-amber-400" />
          <span>Synthetic / Simulated Dataset</span>
        </div>
      </div>

      {/* 5. TRADITIONAL VS INTELLIGENT COMPARISON SECTION */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-5">
        <h3 className="text-base font-bold text-slate-100 flex items-center gap-2 border-b border-slate-800 pb-3">
          <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          Traditional Fixed Schedule vs Intelligent Scheduling
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Total Distance Card */}
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
            <div className="text-xs text-slate-400 font-semibold uppercase">Total Distance (Avg/Day)</div>
            <div className="flex items-baseline justify-between pt-1">
              <span className="text-xs text-rose-400 line-through">{summary.avg_traditional_distance_km} km</span>
              <span className="text-xl font-extrabold text-emerald-400">{summary.avg_intelligent_distance_km} km</span>
            </div>
            <div className="text-[11px] text-emerald-400 font-semibold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 text-center">
              -{distance_reduction_percent}% Distance Reduction
            </div>
          </div>

          {/* Estimated Fuel Card */}
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
            <div className="text-xs text-slate-400 font-semibold uppercase">Estimated Fuel (Avg/Day)</div>
            <div className="flex items-baseline justify-between pt-1">
              <span className="text-xs text-rose-400 line-through">{summary.avg_traditional_fuel_L} L</span>
              <span className="text-xl font-extrabold text-sky-400">{summary.avg_intelligent_fuel_L} L</span>
            </div>
            <div className="text-[11px] text-sky-400 font-semibold bg-sky-500/10 px-2 py-0.5 rounded border border-sky-500/20 text-center">
              -{fuel_reduction_percent}% Fuel Saved
            </div>
          </div>

          {/* Collection Stops Card */}
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
            <div className="text-xs text-slate-400 font-semibold uppercase">Collection Stops</div>
            <div className="flex items-baseline justify-between pt-1">
              <span className="text-xs text-rose-400 line-through">{summary.avg_traditional_stops} Stops</span>
              <span className="text-xl font-extrabold text-purple-400">{summary.avg_intelligent_stops} Stops</span>
            </div>
            <div className="text-[11px] text-purple-400 font-semibold bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20 text-center">
              -{stop_reduction_percent}% Stop Efficiency
            </div>
          </div>

          {/* Unnecessary Visits Saved Card */}
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
            <div className="text-xs text-slate-400 font-semibold uppercase">Unnecessary Visits Saved</div>
            <div className="flex items-baseline justify-between pt-1">
              <span className="text-xs text-slate-500">Fixed: 50 visits</span>
              <span className="text-xl font-extrabold text-amber-400">-{unnecessaryVisitsSaved} Bins</span>
            </div>
            <div className="text-[11px] text-amber-400 font-semibold bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20 text-center">
              Eliminated Empty Bin Visits
            </div>
          </div>
        </div>
      </div>

      {/* 6. 30-DAY ANALYTICS CHARTS */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily Distance Comparison Chart */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
              Daily Distance Comparison (km)
            </h3>
            <span className="text-[11px] text-slate-400 font-mono">30-Day Simulation</span>
          </div>
          <SVGLineChart
            data={daily_evaluation}
            key1="Traditional_Distance_km"
            key2="Intelligent_Distance_km"
            color1="#ef4444"
            color2="#10b981"
            label1="Traditional"
            label2="Intelligent ML"
          />
        </div>

        {/* Daily Fuel Comparison Chart */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
              Daily Fuel Consumption Comparison (L)
            </h3>
            <span className="text-[11px] text-slate-400 font-mono">30-Day Simulation</span>
          </div>
          <SVGLineChart
            data={daily_evaluation}
            key1="Traditional_Fuel_L"
            key2="Intelligent_Fuel_L"
            color1="#ef4444"
            color2="#3b82f6"
            label1="Traditional"
            label2="Intelligent ML"
          />
        </div>
      </div>

      {/* 3 Distributions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Priority Distribution */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl">
          <h3 className="text-xs font-bold text-slate-200 mb-3 uppercase tracking-wider">
            Priority Level Distribution
          </h3>
          <DonutChart dictData={distributions.priority || {}} />
        </div>

        {/* Fill Level Distribution */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl">
          <h3 className="text-xs font-bold text-slate-200 mb-3 uppercase tracking-wider">
            Fill-Level Brackets Distribution
          </h3>
          <HorizontalBarChart dictData={distributions.fill_level || {}} color="bg-sky-500" />
        </div>

        {/* Dispatch Requirement Distribution */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl">
          <h3 className="text-xs font-bold text-slate-200 mb-3 uppercase tracking-wider">
            Dispatch Requirement Distribution
          </h3>
          <DonutChart dictData={distributions.dispatch_decision || {}} />
        </div>
      </div>
    </div>
  );
}

// Custom SVG Chart components

function SVGLineChart({ data, key1, key2, color1, color2, label1, label2 }) {
  if (!data || data.length === 0) return null;

  const height = 180;
  const width = 600;

  const allVals = data.flatMap((d) => [d[key1] || 0, d[key2] || 0]);
  const minVal = Math.min(...allVals, 0);
  const maxVal = Math.max(...allVals, 100);

  const getY = (val) => height - ((val - minVal) / (maxVal - minVal || 1)) * (height - 30) - 15;

  const points1 = data.map((d, i) => {
    const x = (i / (data.length - 1)) * (width - 30) + 15;
    return `${x},${getY(d[key1])}`;
  }).join(' ');

  const points2 = data.map((d, i) => {
    const x = (i / (data.length - 1)) * (width - 30) + 15;
    return `${x},${getY(d[key2])}`;
  }).join(' ');

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-end space-x-4 text-[11px]">
        <span className="flex items-center gap-1.5"><span className="w-3 h-0.5" style={{ backgroundColor: color1 }}></span> {label1}</span>
        <span className="flex items-center gap-1.5"><span className="w-3 h-0.5" style={{ backgroundColor: color2 }}></span> {label2}</span>
      </div>

      <div className="w-full overflow-x-auto">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-44 overflow-visible">
          {[30, 70, 110, 150].map((yVal) => (
            <line key={yVal} x1="0" y1={yVal} x2={width} y2={yVal} stroke="#1e293b" strokeDasharray="3 3" />
          ))}

          <polyline fill="none" stroke={color1} strokeWidth="2" points={points1} />
          <polyline fill="none" stroke={color2} strokeWidth="2.5" points={points2} />

          {data.map((d, i) => {
            const x = (i / (data.length - 1)) * (width - 30) + 15;
            const y = getY(d[key2]);
            return (
              <circle key={i} cx={x} cy={y} r="2.5" fill={color2}>
                <title>Day {d.Day}: {d[key2]}</title>
              </circle>
            );
          })}
        </svg>
        <div className="flex justify-between text-[10px] text-slate-500 pt-1 border-t border-slate-800">
          <span>Day 1</span>
          <span>Day 15</span>
          <span>Day 30</span>
        </div>
      </div>
    </div>
  );
}

function DonutChart({ dictData }) {
  const entries = Object.entries(dictData);
  const total = entries.reduce((acc, [_, v]) => acc + Number(v), 0) || 1;

  return (
    <div className="space-y-3 py-1">
      {entries.map(([key, value], idx) => {
        const pct = Math.round((Number(value) / total) * 100);
        const color = PIE_COLORS[idx % PIE_COLORS.length];
        return (
          <div key={key} className="space-y-1">
            <div className="flex justify-between text-xs">
              <span className="text-slate-300 font-medium flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }}></span>
                {key}
              </span>
              <span className="font-bold text-slate-200">{value} ({pct}%)</span>
            </div>
            <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-800">
              <div className="h-full rounded-full transition-all duration-500" style={{ width: `${pct}%`, backgroundColor: color }}></div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function HorizontalBarChart({ dictData, color }) {
  const entries = Object.entries(dictData);
  const maxVal = Math.max(...entries.map(([_, v]) => Number(v)), 1);

  return (
    <div className="space-y-2.5 py-1">
      {entries.map(([key, value]) => {
        const pct = Math.round((Number(value) / maxVal) * 100);
        return (
          <div key={key} className="space-y-1">
            <div className="flex justify-between text-xs">
              <span className="text-slate-400 font-mono">{key}</span>
              <span className="font-bold text-slate-200">{value} Bins</span>
            </div>
            <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-800">
              <div className={`${color} h-full rounded-full transition-all duration-500`} style={{ width: `${pct}%` }}></div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
