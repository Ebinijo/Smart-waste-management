import React, { useEffect, useState } from 'react';
import { CalendarCheck, ArrowUpDown, Clock, CheckCircle2, ShieldAlert } from 'lucide-react';
import { fetchCollectionPlan } from '../services/api';
import { PriorityBadge, DecisionBadge } from '../components/StatusBadge';

export function CollectionSchedule({ dataMode = 'synthetic' }) {
  const [planData, setPlanData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortBy, setSortBy] = useState('priority');

  useEffect(() => {
    setLoading(true);
    fetchCollectionPlan(dataMode, 100)
      .then((res) => {
        setPlanData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [dataMode]);

  const getSortedPlan = () => {
    if (!planData || !planData.plan) return [];
    const list = [...planData.plan];
    if (sortBy === 'priority') {
      const prioScore = { HIGH: 3, MEDIUM: 2, LOW: 1 };
      list.sort((a, b) => {
        const diff = (prioScore[a.Priority_Level] || 0) - (prioScore[b.Priority_Level] || 0);
        if (diff !== 0) return b.p_score - a.p_score || (prioScore[b.Priority_Level] - prioScore[a.Priority_Level]);
        return b.Next_Fill_Level_Percent - a.Next_Fill_Level_Percent;
      });
    } else if (sortBy === 'predicted') {
      list.sort((a, b) => b.Next_Fill_Level_Percent - a.Next_Fill_Level_Percent);
    }
    return list;
  };

  const sortedList = getSortedPlan();
  const isChennai = dataMode === 'chennai';

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
            Recommended Collection Schedule
            <span className={`text-xs px-2.5 py-0.5 rounded-md font-mono border ${
              isChennai ? 'bg-teal-500/10 text-teal-300 border-teal-500/30' : 'bg-purple-500/10 text-purple-400 border-purple-500/20'
            }`}>
              {isChennai ? '📍 Chennai Schedule' : 'Intelligent Dispatch'}
            </span>
          </h2>
          <p className="text-xs text-slate-400">
            Filtered collection manifest based on prototype dispatch policy (Current/Predicted fill ≥ 80%)
          </p>
        </div>

        {/* Sort Controls */}
        <div className="flex items-center space-x-2 bg-slate-900 p-1.5 rounded-lg border border-slate-800 shrink-0">
          <span className="text-xs text-slate-400 px-2 font-medium flex items-center gap-1">
            <ArrowUpDown className="w-3.5 h-3.5 text-slate-500" /> Sort By:
          </span>
          <button
            onClick={() => setSortBy('priority')}
            className={`px-3 py-1 rounded text-xs font-semibold transition ${
              sortBy === 'priority'
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Priority Level
          </button>
          <button
            onClick={() => setSortBy('predicted')}
            className={`px-3 py-1 rounded text-xs font-semibold transition ${
              sortBy === 'predicted'
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Predicted Fill %
          </button>
        </div>
      </div>

      {/* Plan Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
          <div>
            <div className="text-xs text-slate-400 uppercase font-semibold">Total Scheduled Bins</div>
            <div className="text-2xl font-extrabold text-slate-100 mt-1">
              {loading ? '...' : planData?.total_scheduled || 0} Bins
            </div>
          </div>
          <div className="p-3 bg-purple-500/10 border border-purple-500/20 text-purple-400 rounded-lg">
            <CalendarCheck className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
          <div>
            <div className="text-xs text-slate-400 uppercase font-semibold">Immediate Dispatch (High)</div>
            <div className="text-2xl font-extrabold text-rose-400 mt-1">
              {loading ? '...' : sortedList.filter((b) => b.Priority_Level === 'HIGH').length} Bins
            </div>
          </div>
          <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-lg">
            <ShieldAlert className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
          <div>
            <div className="text-xs text-slate-400 uppercase font-semibold">Scheduled Collection (Medium)</div>
            <div className="text-2xl font-extrabold text-amber-400 mt-1">
              {loading ? '...' : sortedList.filter((b) => b.Priority_Level === 'MEDIUM').length} Bins
            </div>
          </div>
          <div className="p-3 bg-amber-500/10 border border-amber-500/20 text-amber-400 rounded-lg">
            <Clock className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Manifest Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950 text-slate-400 uppercase font-semibold border-b border-slate-800">
              <tr>
                <th className="px-4 py-3">Priority</th>
                <th className="px-4 py-3">Real Bin ID</th>
                <th className="px-4 py-3">{isChennai ? 'Area / Zone' : 'Zone'}</th>
                {isChennai && <th className="px-4 py-3">Location / Street</th>}
                <th className="px-4 py-3">Current Fill % (Simulated)</th>
                <th className="px-4 py-3">Predicted Next Fill %</th>
                <th className="px-4 py-3">Dispatch Decision</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {loading ? (
                <tr>
                  <td colSpan="7" className="px-4 py-8 text-center text-slate-400">
                    Calculating daily dispatch plan...
                  </td>
                </tr>
              ) : sortedList.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-4 py-8 text-center text-slate-400">
                    No bins currently meet the dispatch threshold (Fill ≥ 80%).
                  </td>
                </tr>
              ) : (
                sortedList.map((b) => (
                  <tr key={b.Bin_ID || b.Real_Bin_ID} className="hover:bg-slate-800/60 transition">
                    <td className="px-4 py-3">
                      <PriorityBadge priority={b.Priority_Level} />
                    </td>
                    <td className="px-4 py-3 font-bold text-slate-100 font-mono">{b.Real_Bin_ID || b.Bin_ID}</td>
                    <td className="px-4 py-3 text-slate-300">{b.Area_Name || b.Zone}</td>
                    {isChennai && (
                      <td className="px-4 py-3 text-slate-400 truncate max-w-[220px]">
                        {b.Street_Name || b.Location_Name || 'N/A'}
                      </td>
                    )}
                    <td className="px-4 py-3 font-semibold text-slate-200">{b.Fill_Level_Percent}%</td>
                    <td className="px-4 py-3 font-bold text-sky-400">{b.Next_Fill_Level_Percent}%</td>
                    <td className="px-4 py-3">
                      <DecisionBadge decision={b.Dispatch_Decision} />
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

