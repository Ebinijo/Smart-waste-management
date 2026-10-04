import React, { useEffect, useState } from 'react';
import { Search, RefreshCw, Eye, ArrowUpDown, Filter, ChevronLeft, ChevronRight, MapPin } from 'lucide-react';
import { fetchBins, fetchFilters } from '../services/api';
import { PriorityBadge, DecisionBadge, OverflowBadge } from '../components/StatusBadge';
import { BinDetailModal } from '../components/BinDetailModal';

export function BinMonitoring({ dataMode = 'synthetic' }) {
  const [bins, setBins] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedBin, setSelectedBin] = useState(null);

  // Pagination & Filter states
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(50);
  const [search, setSearch] = useState('');
  const [zoneFilter, setZoneFilter] = useState('');
  const [divisionFilter, setDivisionFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [decisionFilter, setDecisionFilter] = useState('');
  const [overflowFilter, setOverflowFilter] = useState('');
  const [sortOrder, setSortOrder] = useState('desc');

  // Metadata dropdowns
  const [availableZones, setAvailableZones] = useState([]);
  const [availableDivisions, setAvailableDivisions] = useState([]);

  useEffect(() => {
    fetchFilters(dataMode)
      .then((res) => {
        setAvailableZones(res.zones || []);
        setAvailableDivisions(res.divisions || []);
      })
      .catch(() => {});
  }, [dataMode]);

  const loadData = () => {
    setLoading(true);
    const filters = {
      search,
      zone: zoneFilter,
      division: divisionFilter,
      priority: priorityFilter,
      decision: decisionFilter,
      overflow: overflowFilter
    };
    fetchBins(filters, dataMode, page, limit)
      .then((res) => {
        setBins(res.bins || []);
        setTotalCount(res.total_count || res.count || 0);
        setTotalPages(res.total_pages || 1);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    loadData();
  }, [dataMode, page, limit, priorityFilter, decisionFilter, overflowFilter, zoneFilter, divisionFilter]);

  // Debounced search trigger or search submit
  const handleSearchChange = (e) => {
    setSearch(e.target.value);
    setPage(1);
  };

  const handleSearchKeyDown = (e) => {
    if (e.key === 'Enter') {
      loadData();
    }
  };

  // Sort by predicted fill % locally on active page
  const sortedBins = [...bins].sort((a, b) => {
    const valA = Number(a.Next_Fill_Level_Percent || 0);
    const valB = Number(b.Next_Fill_Level_Percent || 0);
    return sortOrder === 'desc' ? valB - valA : valA - valB;
  });

  const resetFilters = () => {
    setSearch('');
    setZoneFilter('');
    setDivisionFilter('');
    setPriorityFilter('');
    setDecisionFilter('');
    setOverflowFilter('');
    setSortOrder('desc');
    setPage(1);
  };

  const isChennai = dataMode === 'chennai';

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
            Municipal Bin Matrix & Monitoring
            <span className={`text-xs px-2.5 py-0.5 rounded-full font-medium border ${
              isChennai ? 'bg-teal-500/10 text-teal-300 border-teal-500/30' : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
            }`}>
              {isChennai ? '📍 Real Chennai Locations' : '🧪 Synthetic Demo'}
            </span>
          </h2>
          <p className="text-xs text-slate-400">
            {isChennai 
              ? `Real Chennai Corporation Bin Locations + Simulated Operational Data (${totalCount} Total Records)`
              : `Searchable matrix of ${totalCount} city bins with ML fill forecasts`}
          </p>
        </div>
        <button
          onClick={loadData}
          className="flex items-center space-x-2 px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700 transition shrink-0"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Matrix</span>
        </button>
      </div>

      {/* Filter & Search Toolbar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-3 shadow-xl">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3">
          {/* Search Box */}
          <div className="relative sm:col-span-2 lg:col-span-2">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
            <input
              type="text"
              placeholder={isChennai ? "Search Bin ID, Street, Area..." : "Search Bin ID, Zone..."}
              value={search}
              onChange={handleSearchChange}
              onKeyDown={handleSearchKeyDown}
              className="w-full pl-9 pr-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
            />
          </div>

          {/* Zone Filter */}
          <select
            value={zoneFilter}
            onChange={(e) => { setZoneFilter(e.target.value); setPage(1); }}
            className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
          >
            <option value="">All Zones / Areas</option>
            {availableZones.map((z) => (
              <option key={z} value={z}>{z}</option>
            ))}
          </select>

          {/* Division Filter */}
          {isChennai && (
            <select
              value={divisionFilter}
              onChange={(e) => { setDivisionFilter(e.target.value); setPage(1); }}
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
            >
              <option value="">All Divisions</option>
              {availableDivisions.map((d) => (
                <option key={d} value={d}>Div {d}</option>
              ))}
            </select>
          )}

          {/* Priority Filter */}
          <select
            value={priorityFilter}
            onChange={(e) => { setPriorityFilter(e.target.value); setPage(1); }}
            className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
          >
            <option value="">All Priority Levels</option>
            <option value="HIGH">High Priority</option>
            <option value="MEDIUM">Medium Priority</option>
            <option value="LOW">Low Priority</option>
          </select>

          {/* Decision Filter */}
          <select
            value={decisionFilter}
            onChange={(e) => { setDecisionFilter(e.target.value); setPage(1); }}
            className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
          >
            <option value="">All Dispatch Decisions</option>
            <option value="Dispatch Immediately">Dispatch Immediately</option>
            <option value="Schedule Collection">Schedule Collection</option>
            <option value="No Dispatch">No Dispatch</option>
          </select>
        </div>

        {/* Sorting & Filter Reset Bar */}
        <div className="flex flex-wrap items-center justify-between pt-2 border-t border-slate-800/80 text-xs gap-2">
          <div className="flex items-center space-x-2 text-slate-400">
            <Filter className="w-3.5 h-3.5 text-slate-500" />
            <span>Showing {sortedBins.length} on page {page} of {totalPages} ({totalCount} matching bins)</span>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={() => setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc')}
              className="flex items-center space-x-1.5 px-3 py-1 bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 rounded-md transition"
            >
              <ArrowUpDown className="w-3.5 h-3.5 text-emerald-400" />
              <span>Predicted Fill: {sortOrder === 'desc' ? 'Highest First ↓' : 'Lowest First ↑'}</span>
            </button>

            {(search || zoneFilter || divisionFilter || priorityFilter || decisionFilter || overflowFilter) && (
              <button
                onClick={resetFilters}
                className="text-xs text-emerald-400 hover:underline font-medium"
              >
                Reset Filters
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Bin Data Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950 text-slate-400 uppercase font-semibold border-b border-slate-800">
              <tr>
                <th className="px-4 py-3">Real Bin ID</th>
                <th className="px-4 py-3">{isChennai ? 'Area / Zone' : 'Zone'}</th>
                {isChennai && <th className="px-4 py-3">Division</th>}
                <th className="px-4 py-3">{isChennai ? 'Location / Street' : 'Waste Type'}</th>
                <th className="px-4 py-3">Current Fill % (Simulated)</th>
                <th 
                  className="px-4 py-3 cursor-pointer hover:text-slate-100 transition"
                  onClick={() => setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc')}
                >
                  Predicted Next Fill % {sortOrder === 'desc' ? '↓' : '↑'}
                </th>
                <th className="px-4 py-3">Priority</th>
                <th className="px-4 py-3">Dispatch Decision</th>
                <th className="px-4 py-3">Lat / Lon</th>
                <th className="px-4 py-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {loading ? (
                <tr>
                  <td colSpan="10" className="px-4 py-8 text-center text-slate-400">
                    Loading bin telemetry matrix...
                  </td>
                </tr>
              ) : sortedBins.length === 0 ? (
                <tr>
                  <td colSpan="10" className="px-4 py-8 text-center text-slate-400">
                    No bins match the selected search or filter criteria.
                  </td>
                </tr>
              ) : (
                sortedBins.map((bin) => (
                  <tr
                    key={bin.Bin_ID || bin.Real_Bin_ID}
                    onClick={() => setSelectedBin(bin)}
                    className="hover:bg-slate-800/60 cursor-pointer transition"
                  >
                    <td className="px-4 py-3 font-bold text-slate-100 font-mono">
                      {bin.Real_Bin_ID || bin.Bin_ID}
                    </td>
                    <td className="px-4 py-3 text-slate-300">
                      {bin.Area_Name || bin.Zone}
                    </td>
                    {isChennai && (
                      <td className="px-4 py-3 text-slate-400 font-mono">
                        {bin.Division_Code || bin.Division || 'N/A'}
                      </td>
                    )}
                    <td className="px-4 py-3 text-slate-400 max-w-[200px] truncate" title={bin.Street_Name || bin.Location_Name || bin.Bin_Type}>
                      {bin.Street_Name || bin.Location_Name || bin.Bin_Type}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center space-x-2">
                        <span className="font-semibold text-slate-200">{bin.Fill_Level_Percent}%</span>
                        <div className="w-14 bg-slate-800 h-1.5 rounded-full overflow-hidden hidden sm:block">
                          <div
                            className={`h-full ${
                              bin.Fill_Level_Percent >= 90
                                ? 'bg-rose-500'
                                : bin.Fill_Level_Percent >= 70
                                ? 'bg-amber-500'
                                : 'bg-emerald-500'
                            }`}
                            style={{ width: `${bin.Fill_Level_Percent}%` }}
                          ></div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 font-bold text-sky-400">
                      {bin.Next_Fill_Level_Percent}%
                    </td>
                    <td className="px-4 py-3">
                      <PriorityBadge priority={bin.Priority_Level} />
                    </td>
                    <td className="px-4 py-3">
                      <DecisionBadge decision={bin.Dispatch_Decision} />
                    </td>
                    <td className="px-4 py-3 font-mono text-[11px] text-slate-400">
                      {Number(bin.Latitude).toFixed(4)}, {Number(bin.Longitude).toFixed(4)}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedBin(bin);
                        }}
                        className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 transition"
                        title="View Details"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="p-4 bg-slate-950 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
          <div className="flex items-center space-x-3 text-slate-400">
            <span>Per page:</span>
            <select
              value={limit}
              onChange={(e) => { setLimit(Number(e.target.value)); setPage(1); }}
              className="px-2 py-1 bg-slate-900 border border-slate-800 rounded text-slate-200 focus:outline-none"
            >
              <option value={20}>20</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
            <span>Showing page {page} of {totalPages} ({totalCount} total bins)</span>
          </div>

          <div className="flex items-center space-x-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              className="flex items-center space-x-1 px-3 py-1.5 bg-slate-900 border border-slate-800 hover:bg-slate-800 disabled:opacity-40 disabled:hover:bg-slate-900 rounded-lg text-slate-300 font-medium transition"
            >
              <ChevronLeft className="w-4 h-4" />
              <span>Previous</span>
            </button>
            <span className="px-3 py-1 bg-slate-900 border border-slate-800 rounded text-emerald-400 font-mono font-bold">
              {page}
            </span>
            <button
              disabled={page >= totalPages}
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              className="flex items-center space-x-1 px-3 py-1.5 bg-slate-900 border border-slate-800 hover:bg-slate-800 disabled:opacity-40 disabled:hover:bg-slate-900 rounded-lg text-slate-300 font-medium transition"
            >
              <span>Next</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Bin Details Modal */}
      {selectedBin && (
        <BinDetailModal bin={selectedBin} onClose={() => setSelectedBin(null)} />
      )}
    </div>
  );
}

