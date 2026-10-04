import React, { useEffect, useState } from 'react';
import { 
  Trash2, 
  AlertTriangle, 
  AlertCircle, 
  CheckCircle2, 
  Truck, 
  Flame, 
  TrendingUp, 
  Navigation,
  ArrowRight,
  Info
} from 'lucide-react';
import { fetchDashboard, fetchBins } from '../services/api';
import { MetricCard } from '../components/MetricCard';
import { DecisionPipelineCard } from '../components/DecisionPipelineCard';

export function Dashboard({ setActiveTab, dataMode = 'synthetic' }) {
  const [data, setData] = useState(null);
  const [binsList, setBinsList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    Promise.all([fetchDashboard(dataMode), fetchBins({}, dataMode, 1, 100)])
      .then(([dashRes, binsRes]) => {
        setData(dashRes);
        setBinsList(binsRes.bins || []);
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
          <span className="text-sm text-slate-400 font-medium">
            Loading System Metrics ({dataMode === 'chennai' ? 'Chennai Real Locations' : 'Synthetic Demo'})...
          </span>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300">
        <h3 className="text-lg font-bold flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-rose-400" />
          Backend Service Connection Error
        </h3>
        <p className="text-sm mt-1 text-rose-200">{error}</p>
        <p className="text-xs text-slate-400 mt-2">Ensure FastAPI backend is running on http://127.0.0.1:8000</p>
      </div>
    );
  }

  const isChennai = dataMode === 'chennai';

  return (
    <div className="space-y-6">
      {/* Active Data Mode Banner */}
      <div className={`p-4 rounded-xl flex items-start space-x-3 border ${
        isChennai 
          ? 'bg-teal-500/10 border-teal-500/30 text-teal-200' 
          : 'bg-amber-500/10 border-amber-500/30 text-amber-200'
      }`}>
        <AlertTriangle className={`w-5 h-5 shrink-0 mt-0.5 ${isChennai ? 'text-teal-400' : 'text-amber-400'}`} />
        <div className="text-xs">
          <span className="font-bold text-sm block mb-0.5">
            {isChennai ? '📍 Real Chennai Bin Locations + Simulated Operational Data' : '🧪 Synthetic Demo Mode'}
          </span>
          {isChennai
            ? `Monitored coordinates are extracted from official Greater Chennai Corporation bin locations (${data.total_bins} bins). Operational parameters (fill level, generation rate) are simulated for research demonstration.`
            : 'Synthetic benchmark dataset featuring 100 municipal bins and simulated Dijkstra network graph routing.'}
        </div>
      </div>

      {/* 1. Main KPI Grid - 8 Dynamic Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Bins"
          value={data.total_bins}
          subtitle={isChennai ? "Chennai Municipal Bins" : "Monitored Municipal Bins"}
          icon={Trash2}
          color="emerald"
        />
        <MetricCard
          title="High Priority"
          value={data.high_priority}
          subtitle="Current/Predicted ≥ 90%"
          icon={AlertCircle}
          color="rose"
        />
        <MetricCard
          title="Medium Priority"
          value={data.medium_priority}
          subtitle="Current/Predicted ≥ 70%"
          icon={Flame}
          color="amber"
        />
        <MetricCard
          title="Low Priority"
          value={data.low_priority}
          subtitle="Normal Capacity Range"
          icon={CheckCircle2}
          color="sky"
        />

        <MetricCard
          title="Collection Required"
          value={data.collection_required}
          subtitle="Dispatch / Schedule Action"
          icon={Truck}
          color="purple"
        />
        <MetricCard
          title="Overflow Risk"
          value={data.overflow_risk}
          subtitle="Imminent Overflow Bins"
          icon={AlertTriangle}
          color="rose"
        />
        <MetricCard
          title="Predicted Collections"
          value={data.predicted_collections}
          subtitle="ML Forecasted Threshold"
          icon={TrendingUp}
          color="indigo"
        />
        <MetricCard
          title="Sample Route Distance"
          value={`${data.total_route_distance_km} km`}
          subtitle="Dijkstra Shortest Path"
          icon={Navigation}
          color="emerald"
        />
      </div>

      {/* 2. Collection Decision Pipeline */}
      <DecisionPipelineCard bins={binsList} />

      {/* 3. Quick Action Navigation & Controls */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-100 mb-2">Bin Matrix & Monitoring</h3>
            <p className="text-xs text-slate-400 mb-4 leading-relaxed">
              Inspect all {data.total_bins} {isChennai ? 'Chennai' : 'city'} bins, filter by zone, division, priority, or dispatch decision, and view individual bin fill progress.
            </p>
          </div>
          <button
            onClick={() => setActiveTab('monitoring')}
            className="w-full flex items-center justify-between px-4 py-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg font-medium text-xs transition border border-slate-700"
          >
            <span>Open Bin Monitoring Matrix ({data.total_bins} Bins)</span>
            <ArrowRight className="w-4 h-4 text-emerald-400" />
          </button>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-100 mb-2">Dijkstra Shortest-Path Route Map</h3>
            <p className="text-xs text-slate-400 mb-4 leading-relaxed">
              View the interactive Leaflet map displaying the optimal Dijkstra route path across high/medium priority collection stops starting from the {isChennai ? 'Simulation Depot in Chennai' : 'Central Depot'}.
            </p>
          </div>
          <button
            onClick={() => setActiveTab('route')}
            className="w-full flex items-center justify-between px-4 py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-medium text-xs transition shadow-lg shadow-emerald-950/40"
          >
            <span>View Interactive Dijkstra Route ({data.total_route_distance_km} km)</span>
            <ArrowRight className="w-4 h-4 text-white" />
          </button>
        </div>
      </div>
    </div>
  );
}

