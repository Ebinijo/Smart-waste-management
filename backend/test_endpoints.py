import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

print("--- Testing API Endpoints ---")

# 1. Health Check
res_health = client.get("/api/health")
print(f"GET /api/health Status: {res_health.status_code}")
assert res_health.status_code == 200

# 2. GET /api/dashboard?mode=synthetic
res_dash = client.get("/api/dashboard?mode=synthetic")
print(f"GET /api/dashboard?mode=synthetic Status: {res_dash.status_code}")
assert res_dash.status_code == 200
dash_json = res_dash.json()
print(f"Dashboard total_bins: {dash_json.get('total_bins')}, total_route_distance_km: {dash_json.get('total_route_distance_km')}")

# 3. GET /api/bins?mode=synthetic&page=1&limit=100
res_bins = client.get("/api/bins?mode=synthetic&page=1&limit=100")
print(f"GET /api/bins?mode=synthetic&page=1&limit=100 Status: {res_bins.status_code}")
assert res_bins.status_code == 200
bins_json = res_bins.json()
print(f"Bins total_count: {bins_json.get('total_count')}, total_pages: {bins_json.get('total_pages')}, page_bins: {len(bins_json.get('bins', []))}")

# 4. GET /api/bins?mode=chennai&page=1&limit=50
res_chennai_bins = client.get("/api/bins?mode=chennai&page=1&limit=50")
print(f"GET /api/bins?mode=chennai&page=1&limit=50 Status: {res_chennai_bins.status_code}")
assert res_chennai_bins.status_code == 200
chennai_json = res_chennai_bins.json()
print(f"Chennai Bins total_count: {chennai_json.get('total_count')}, total_pages: {chennai_json.get('total_pages')}, page_bins: {len(chennai_json.get('bins', []))}")

print("\n=== ALL VERIFICATION TESTS PASSED SUCCESSFULLY! ===")
