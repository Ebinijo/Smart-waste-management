import React, { useEffect, useRef, useState } from 'react';
import { RefreshCw, Layers, ShieldAlert, ArrowRight, MapPin } from 'lucide-react';
import { fetchOptimizedRoute } from '../services/api';
import { PriorityBadge } from '../components/StatusBadge';

export function RouteOptimization({ dataMode = 'synthetic' }) {
  const [maxStops, setMaxStops] = useState(30);
  const [routeData, setRouteData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);

  const loadRoute = () => {
    setLoading(true);
    fetchOptimizedRoute(dataMode, maxStops)
      .then((res) => {
        setRouteData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    loadRoute();
  }, [dataMode, maxStops]);

  // Initialize and update Leaflet Map
  useEffect(() => {
    if (!routeData || !mapRef.current) return;

    const L = window.L;
    if (!L) return;

    const { depot, stops, route_path } = routeData;
    const isChennai = dataMode === 'chennai';
    const centerLat = depot ? depot.latitude : (isChennai ? 13.0827 : 37.7749);
    const centerLon = depot ? depot.longitude : (isChennai ? 80.2707 : -122.4194);

    if (mapInstanceRef.current) {
      mapInstanceRef.current.remove();
      mapInstanceRef.current = null;
    }

    const map = L.map(mapRef.current).setView([centerLat, centerLon], isChennai ? 11 : 12);
    mapInstanceRef.current = map;

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; OpenStreetMap &copy; CARTO',
      maxZoom: 19
    }).addTo(map);

    const createCustomIcon = (color, label) => {
      const svg = `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 36" width="28" height="42">
          <path d="M12 0C5.37 0 0 5.37 0 12c0 9 12 24 12 24s12-15 12-24c0-6.63-5.37-12-12-12z" fill="${color}" stroke="#0f172a" stroke-width="1.5"/>
          <circle cx="12" cy="12" r="5" fill="#ffffff"/>
          <text x="12" y="15" font-size="8" font-weight="bold" text-anchor="middle" fill="#0f172a">${label || ''}</text>
        </svg>
      `;
      return L.divIcon({
        className: 'custom-leaflet-marker',
        html: svg,
        iconSize: [28, 42],
        iconAnchor: [14, 42],
        popupAnchor: [0, -38]
      });
    };

    const depotIcon = createCustomIcon('#8b5cf6', 'D');
    const highIcon = createCustomIcon('#ef4444', 'H');
    const medIcon = createCustomIcon('#f59e0b', 'M');
    const lowIcon = createCustomIcon('#10b981', 'L');

    if (depot) {
      L.marker([depot.latitude, depot.longitude], { icon: depotIcon })
        .addTo(map)
        .bindPopup(`
          <div style="font-family: Inter, sans-serif; font-size: 12px; color: #f8fafc;">
            <strong style="color: #a78bfa;">🏢 ${depot.name}</strong><br/>
            <span>Central Reference Depot Point</span>
          </div>
        `);
    }

    if (stops) {
      stops.forEach((stop) => {
        const icon = stop.priority === 'HIGH' ? highIcon : (stop.priority === 'MEDIUM' ? medIcon : lowIcon);
        const labelStr = stop.real_bin_id || stop.bin_id;
        const locStr = stop.location !== 'N/A' ? stop.location : stop.zone;
        L.marker([stop.latitude, stop.longitude], { icon })
          .addTo(map)
          .bindPopup(`
            <div style="font-family: Inter, sans-serif; font-size: 12px; color: #f8fafc; line-height: 1.5;">
              <strong style="color: #f1f5f9;">Stop #${stop.step}: ${labelStr}</strong><br/>
              <span>Location: ${locStr}</span><br/>
              <span>Current Fill: <strong>${stop.current_fill}%</strong></span><br/>
              <span style="color: #38bdf8;">Predicted Next Fill: <strong>${stop.predicted_fill}%</strong></span><br/>
              <span style="color: #34d399;">Leg Distance: +${stop.distance_from_prev_km} km</span>
            </div>
          `);
      });
    }

    if (route_path && route_path.length > 1) {
      const polyline = L.polyline(route_path, {
        color: '#10b981',
        weight: 4,
        opacity: 0.85,
        dashArray: '6, 8'
      }).addTo(map);

      map.fitBounds(polyline.getBounds(), { padding: [30, 30] });
    }
  }, [routeData]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center space-y-3">
          <div className="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-sm text-slate-400 font-medium">Computing Dijkstra Shortest Path Route...</span>
        </div>
      </div>
    );
  }

  if (error || !routeData) {
    return (
      <div className="p-6 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300">
        <h3 className="text-lg font-bold">Route Optimization Error</h3>
        <p className="text-sm mt-1 text-rose-200">{error || 'Failed to load route data'}</p>
      </div>
    );
  }

  const { depot, stops, total_distance_km, total_stops, high_priority_stops, medium_priority_stops, estimated_fuel_L } = routeData;
  const isChennai = dataMode === 'chennai';
  const fuelEst = estimated_fuel_L || (total_distance_km * 0.30 + total_stops * 0.05).toFixed(2);

  return (
    <div className="space-y-6">
      {/* Title & Reload Controls */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
            Dijkstra Shortest-Path Route Optimization
            <span className={`text-xs px-2.5 py-0.5 rounded-md font-mono font-semibold border ${
              isChennai ? 'bg-teal-500/10 text-teal-300 border-teal-500/30' : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
            }`}>
              {isChennai ? '📍 Chennai Dijkstra Route' : 'Dijkstra Demo Route'}
            </span>
          </h2>
          <p className="text-xs text-slate-400">
            Interactive collection route using Dijkstra's shortest-path algorithm over {isChennai ? 'real Chennai bin coordinates' : 'simulated bin coordinates'}
          </p>
        </div>

        <div className="flex items-center space-x-3 shrink-0">
          <div className="flex items-center space-x-2 bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800 text-xs">
            <span className="text-slate-400 font-medium">Route Limit:</span>
            <select
              value={maxStops}
              onChange={(e) => setMaxStops(Number(e.target.value))}
              className="bg-slate-950 text-slate-200 font-bold px-2 py-1 rounded border border-slate-800 focus:outline-none focus:border-emerald-500"
            >
              <option value={20}>20 Stops</option>
              <option value={30}>30 Stops (Default)</option>
              <option value={50}>50 Stops</option>
              <option value={100}>100 Stops</option>
            </select>
          </div>

          <button
            onClick={loadRoute}
            className="flex items-center space-x-2 px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700 transition"
          >
            <RefreshCw className="w-3.5 h-3.5 text-emerald-400" />
            <span>Recalculate Route</span>
          </button>
        </div>
      </div>

      {/* Simulated Route Notice */}
      <div className="p-3.5 bg-amber-500/10 border border-amber-500/30 rounded-xl flex items-center justify-between text-xs text-amber-200">
        <div className="flex items-center space-x-2">
          <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0" />
          <span>
            <strong>Dijkstra-based shortest-path route:</strong> Graph network is constructed via Haversine geographic distances between bin coordinates. Origin point is a central <em>Simulation Depot</em>.
          </span>
        </div>
        <span className="text-[11px] font-mono text-amber-300 hidden sm:inline">NetworkX Graph Engine</span>
      </div>

      {/* Metrics Summary Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
          <div className="text-xs text-slate-400 uppercase font-semibold">Total Distance</div>
          <div className="text-2xl font-extrabold text-emerald-400 mt-1">{total_distance_km} km</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
          <div className="text-xs text-slate-400 uppercase font-semibold">Collection Stops</div>
          <div className="text-2xl font-extrabold text-slate-100 mt-1">{total_stops} Bins</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
          <div className="text-xs text-slate-400 uppercase font-semibold">High Priority</div>
          <div className="text-2xl font-extrabold text-rose-400 mt-1">{high_priority_stops} Bins</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
          <div className="text-xs text-slate-400 uppercase font-semibold">Medium Priority</div>
          <div className="text-2xl font-extrabold text-amber-400 mt-1">{medium_priority_stops} Bins</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg col-span-2 sm:col-span-1">
          <div className="text-xs text-slate-400 uppercase font-semibold">Est. Fuel</div>
          <div className="text-2xl font-extrabold text-sky-400 mt-1">{fuelEst} L</div>
          <div className="text-[10px] text-slate-500 tracking-tight mt-0.5">Estimated Fuel — Simulation Assumption</div>
        </div>
      </div>

      {/* Map & Step Sequence Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Leaflet Map DOM Container */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-3 shadow-xl flex flex-col h-[530px]">
          <div className="flex items-center justify-between px-2 pb-2 text-xs">
            <span className="font-semibold text-slate-300 flex items-center gap-1.5">
              <Layers className="w-4 h-4 text-emerald-400" /> Interactive Route Map
            </span>
            <div className="flex items-center space-x-3 text-[11px]">
              <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-purple-500"></span> Simulation Depot</span>
              <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span> High Priority</span>
              <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span> Medium</span>
            </div>
          </div>

          <div ref={mapRef} className="flex-1 w-full rounded-lg overflow-hidden relative z-10 min-h-[440px]"></div>
        </div>

        {/* Route Sequence Panel */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl flex flex-col h-[530px]">
          <h3 className="text-sm font-bold text-slate-100 mb-3 flex items-center justify-between">
            <span>Dijkstra Route Sequence</span>
            <span className="text-xs text-slate-400">{stops.length} Stops Loop</span>
          </h3>

          <div className="flex-1 overflow-y-auto space-y-2.5 pr-1">
            {/* Start Depot */}
            <div className="p-3 bg-slate-950 rounded-lg border border-purple-500/40 flex items-center space-x-3">
              <div className="w-6 h-6 rounded-full bg-purple-500/20 text-purple-400 font-bold flex items-center justify-center text-xs shrink-0">
                DEPOT
              </div>
              <div>
                <div className="text-xs font-bold text-purple-300">Simulation Depot (Start)</div>
                <div className="text-[11px] text-slate-400">{depot?.name || 'Central Reference Hub'}</div>
              </div>
            </div>

            {/* Sequence stops */}
            {stops.map((stop) => (
              <div
                key={stop.bin_id}
                className="p-3 bg-slate-950 rounded-lg border border-slate-800 hover:border-slate-700 transition space-y-1.5"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="w-5 h-5 rounded-full bg-slate-800 text-slate-300 font-bold flex items-center justify-center text-[11px]">
                      {stop.step}
                    </span>
                    <span className="font-bold text-slate-100 text-xs font-mono">
                      {stop.real_bin_id || stop.bin_id}
                    </span>
                  </div>
                  <PriorityBadge priority={stop.priority} />
                </div>

                <div className="flex items-center justify-between text-[11px] text-slate-400">
                  <span className="truncate max-w-[140px]">{stop.street && stop.street !== 'N/A' ? stop.street : stop.zone}</span>
                  <span className="text-slate-300">Fill: {stop.current_fill}% (Pred: {stop.predicted_fill}%)</span>
                </div>

                <div className="text-[11px] text-emerald-400 font-medium pt-0.5 flex items-center justify-between border-t border-slate-900">
                  <span>Leg distance: +{stop.distance_from_prev_km} km</span>
                  <span className="text-slate-500 text-[10px]">Via Dijkstra</span>
                </div>
              </div>
            ))}

            {/* End Depot */}
            <div className="p-3 bg-slate-950 rounded-lg border border-purple-500/40 flex items-center space-x-3">
              <div className="w-6 h-6 rounded-full bg-purple-500/20 text-purple-400 font-bold flex items-center justify-center text-xs shrink-0">
                DEPOT
              </div>
              <div>
                <div className="text-xs font-bold text-purple-300">Simulation Depot (Return)</div>
                <div className="text-[11px] text-slate-400">Complete route loop</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

