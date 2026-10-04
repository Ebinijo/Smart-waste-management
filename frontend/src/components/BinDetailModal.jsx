import React from 'react';
import { X, MapPin, Gauge, Clock, Thermometer, CloudRain, Users, Trash2 } from 'lucide-react';
import { PriorityBadge, DecisionBadge, OverflowBadge } from './StatusBadge';

export function BinDetailModal({ bin, onClose }) {
  if (!bin) return null;

  const currentFill = Number(bin.Fill_Level_Percent || 0);
  const predictedFill = Number(bin.Next_Fill_Level_Percent || currentFill);
  const isChennai = Boolean(bin.Real_Bin_ID || bin.Street_Name || bin.Division_Code);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
      <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-2xl w-full p-6 shadow-2xl relative max-h-[90vh] overflow-y-auto">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-slate-400 hover:text-slate-100 bg-slate-800 rounded-lg border border-slate-700 hover:bg-slate-700 transition"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-3 bg-emerald-500/10 rounded-xl border border-emerald-500/20 text-emerald-400">
            <Trash2 className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-xl font-bold text-slate-100">{bin.Real_Bin_ID || bin.Bin_ID}</h2>
              <PriorityBadge priority={bin.Priority_Level} />
            </div>
            <p className="text-xs text-slate-400">
              {bin.Street_Name ? `${bin.Street_Name}, ${bin.Area_Name}` : `${bin.Zone}`} • {bin.Bin_Type || 'General Waste'} ({bin.Bin_Capacity_L} L)
            </p>
          </div>
        </div>

        {isChennai && (
          <div className="mb-4 p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs space-y-1 text-slate-300">
            <div className="font-bold text-teal-400">Real Chennai Source Location</div>
            <div>Area: <strong>{bin.Area_Name || bin.Zone}</strong> | Division: <strong>{bin.Division_Code || bin.Division || 'N/A'}</strong></div>
            <div>Location: <strong>{bin.Location_Name || 'N/A'}</strong></div>
            <div>Street: <strong>{bin.Street_Name || 'N/A'}</strong></div>
          </div>
        )}

        {/* Fill Level Gauges */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs font-semibold uppercase text-slate-400">Current Fill (Simulated)</span>
              <span className="text-lg font-bold text-slate-100">{currentFill}%</span>
            </div>
            <div className="w-full bg-slate-800 h-3 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-500 ${
                  currentFill >= 90 ? 'bg-rose-500' : currentFill >= 70 ? 'bg-amber-500' : 'bg-emerald-500'
                }`}
                style={{ width: `${currentFill}%` }}
              ></div>
            </div>
          </div>

          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs font-semibold uppercase text-sky-400">Predicted Next Fill (ML Regressor)</span>
              <span className="text-lg font-bold text-sky-300">{predictedFill}%</span>
            </div>
            <div className="w-full bg-slate-800 h-3 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-500 ${
                  predictedFill >= 90 ? 'bg-rose-500' : predictedFill >= 70 ? 'bg-amber-500' : 'bg-sky-400'
                }`}
                style={{ width: `${predictedFill}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Decision & Status summary */}
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 mb-6 flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="text-xs text-slate-400 mb-1">Dispatch Recommendation</div>
            <DecisionBadge decision={bin.Dispatch_Decision} />
          </div>
          <div>
            <div className="text-xs text-slate-400 mb-1">Overflow Risk</div>
            <OverflowBadge risk={bin.Overflow_Risk} />
          </div>
          <div>
            <div className="text-xs text-slate-400 mb-1">Estimated Waste Volume</div>
            <div className="text-sm font-semibold text-slate-200">{bin.Estimated_Waste_Volume_L || 0} Liters</div>
          </div>
        </div>

        {/* Grid of features */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-4">
          <div className="bg-slate-850 p-3 rounded-lg border border-slate-800">
            <div className="flex items-center space-x-1.5 text-xs text-slate-400 mb-1">
              <Gauge className="w-3.5 h-3.5 text-emerald-400" />
              <span>Generation Rate</span>
            </div>
            <div className="text-sm font-semibold text-slate-200">{bin.Waste_Generation_Rate} %/hr</div>
          </div>

          <div className="bg-slate-850 p-3 rounded-lg border border-slate-800">
            <div className="flex items-center space-x-1.5 text-xs text-slate-400 mb-1">
              <Clock className="w-3.5 h-3.5 text-sky-400" />
              <span>Hours Since Collection</span>
            </div>
            <div className="text-sm font-semibold text-slate-200">{bin.Hours_Since_Collection} hrs</div>
          </div>

          <div className="bg-slate-850 p-3 rounded-lg border border-slate-800">
            <div className="flex items-center space-x-1.5 text-xs text-slate-400 mb-1">
              <Thermometer className="w-3.5 h-3.5 text-amber-400" />
              <span>Temperature</span>
            </div>
            <div className="text-sm font-semibold text-slate-200">{bin.Temperature_C} °C</div>
          </div>

          <div className="bg-slate-850 p-3 rounded-lg border border-slate-800">
            <div className="flex items-center space-x-1.5 text-xs text-slate-400 mb-1">
              <CloudRain className="w-3.5 h-3.5 text-blue-400" />
              <span>Rainfall</span>
            </div>
            <div className="text-sm font-semibold text-slate-200">{bin.Rainfall_mm} mm</div>
          </div>

          <div className="bg-slate-850 p-3 rounded-lg border border-slate-800">
            <div className="flex items-center space-x-1.5 text-xs text-slate-400 mb-1">
              <Users className="w-3.5 h-3.5 text-purple-400" />
              <span>Pop. Density</span>
            </div>
            <div className="text-sm font-semibold text-slate-200">{bin.Population_Density} /km²</div>
          </div>

          <div className="bg-slate-850 p-3 rounded-lg border border-slate-800">
            <div className="flex items-center space-x-1.5 text-xs text-slate-400 mb-1">
              <MapPin className="w-3.5 h-3.5 text-rose-400" />
              <span>GPS Location</span>
            </div>
            <div className="text-xs font-mono font-medium text-slate-300">{Number(bin.Latitude).toFixed(5)}, {Number(bin.Longitude).toFixed(5)}</div>
          </div>
        </div>

        <div className="text-right pt-2 border-t border-slate-800">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold transition"
          >
            Close Details
          </button>
        </div>
      </div>
    </div>
  );
}

