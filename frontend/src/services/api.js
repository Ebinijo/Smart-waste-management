const ENV_API_URL = import.meta.env.VITE_API_URL;
const BASE_API_PATH = ENV_API_URL 
  ? (ENV_API_URL.endsWith('/api') ? ENV_API_URL : `${ENV_API_URL.replace(/\/$/, '')}/api`)
  : '/api';

const FALLBACK_BASE_URL = ENV_API_URL ? BASE_API_PATH : 'http://127.0.0.1:8000/api';

async function smartFetch(endpoint, options = {}) {
  try {
    const targetUrl = endpoint.startsWith('http') ? endpoint : `${BASE_API_PATH}${endpoint}`;
    const res = await fetch(targetUrl, options);
    if (res.ok) return await res.json();
  } catch (err) {
    // Relative or primary fetch failed, try direct fallback URL if specified
  }

  try {
    const fallbackUrl = endpoint.startsWith('http') ? endpoint : `${FALLBACK_BASE_URL}${endpoint}`;
    const res = await fetch(fallbackUrl, options);
    if (res.ok) return await res.json();
    const errText = await res.text();
    throw new Error(`API Error (${res.status}): ${errText}`);
  } catch (err) {
    throw new Error(`Cannot connect to FastAPI backend at ${BASE_API_PATH}. Please start backend: python backend/main.py`);
  }
}


export async function fetchDashboard(mode = 'synthetic') {
  return await smartFetch(`/dashboard?mode=${encodeURIComponent(mode)}`);
}

export async function fetchBins(filters = {}, mode = 'synthetic', page = 1, limit = 50) {
  const params = new URLSearchParams();
  params.append('mode', mode);
  params.append('page', page);
  params.append('limit', limit);
  if (filters.priority) params.append('priority', filters.priority);
  if (filters.decision) params.append('decision', filters.decision);
  if (filters.overflow !== undefined && filters.overflow !== null && filters.overflow !== '') params.append('overflow', filters.overflow);
  if (filters.search) params.append('search', filters.search);
  if (filters.zone) params.append('zone', filters.zone);
  if (filters.division) params.append('division', filters.division);

  return await smartFetch(`/bins?${params.toString()}`);
}

export async function fetchFilters(mode = 'synthetic') {
  return await smartFetch(`/filters?mode=${encodeURIComponent(mode)}`);
}

export async function fetchBinDetail(binId, mode = 'synthetic') {
  return await smartFetch(`/bins/${encodeURIComponent(binId)}?mode=${encodeURIComponent(mode)}`);
}

export async function predictBinFill(inputData) {
  return await smartFetch('/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(inputData),
  });
}

export async function fetchCollectionPlan(mode = 'synthetic', limit = 100) {
  return await smartFetch(`/collection-plan?mode=${encodeURIComponent(mode)}&limit=${limit}`);
}

export async function fetchOptimizedRoute(mode = 'synthetic', maxStops = 30) {
  return await smartFetch(`/route?mode=${encodeURIComponent(mode)}&max_stops=${maxStops}`);
}

export async function fetchAnalytics(mode = 'synthetic') {
  return await smartFetch(`/analytics?mode=${encodeURIComponent(mode)}`);
}

