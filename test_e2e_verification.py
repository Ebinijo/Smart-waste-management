import os
import sys
import json
import pandas as pd
import numpy as np

print("=========================================================")
print("  END-TO-END VERIFICATION: WASTE COLLECTION SYSTEM  ")
print("=========================================================\n")

# 1. PATH SETUP
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(PROJECT_DIR, "backend")
sys.path.insert(0, BACKEND_DIR)

from fastapi.testclient import TestClient
from main import app, MODEL_PATH, FEATURES_PATH, LATEST_BINS_PATH, HISTORICAL_PATH, EVALUATION_PATH
from services.prediction import load_model_and_features, predict_next_fill
from services.scheduling import evaluate_intelligent_priority, evaluate_dispatch_decision, evaluate_overflow_risk
from services.routing import generate_dijkstra_route

client = TestClient(app)
test_results = []

def log_test(name, passed, detail=""):
    status = "PASS [✓]" if passed else "FAIL [X]"
    print(f"[{status}] {name}")
    if detail:
        print(f"       -> {detail}")
    test_results.append({"name": name, "passed": passed, "detail": detail})

# ---------------------------------------------------------
# TEST 1: Model & Feature Load (.pkl files)
# ---------------------------------------------------------
try:
    model, features = load_model_and_features()
    model_exists = os.path.exists(MODEL_PATH) and os.path.exists(FEATURES_PATH)
    log_test("RF Model .pkl & Feature List Loading", model_exists and model is not None, 
             f"Features count: {len(features) if features else 0}, Model class: {type(model).__name__ if model else 'None'}")
except Exception as e:
    log_test("RF Model .pkl & Feature List Loading", False, str(e))

# ---------------------------------------------------------
# TEST 2: Datasets Loading (CSVs)
# ---------------------------------------------------------
try:
    latest_df = pd.read_csv(LATEST_BINS_PATH)
    hist_df = pd.read_csv(HISTORICAL_PATH)
    eval_df = pd.read_csv(EVALUATION_PATH)
    
    csv_ok = len(latest_df) == 50 and len(hist_df) > 0 and len(eval_df) == 30
    log_test("CSV Datasets Loading", csv_ok, 
             f"latest_bin_data: {len(latest_df)} rows, waste_decision_data: {len(hist_df)} rows, 30_day_evaluation: {len(eval_df)} rows")
except Exception as e:
    log_test("CSV Datasets Loading", False, str(e))

# ---------------------------------------------------------
# TEST 3: REST API GET /api/health
# ---------------------------------------------------------
res = client.get("/api/health")
log_test("API Endpoint GET /api/health", res.status_code == 200, f"Status: {res.status_code}, Body: {res.json().get('status')}")

# ---------------------------------------------------------
# TEST 4: REST API GET /api/dashboard & Stats Matching CSV
# ---------------------------------------------------------
res = client.get("/api/dashboard")
if res.status_code == 200:
    d = res.json()
    total_bins = d.get("total_bins")
    dist = d.get("total_route_distance_km")
    log_test("API Endpoint GET /api/dashboard", total_bins == 50 and dist >= 0, 
             f"Total Bins: {total_bins}, High Priority: {d.get('high_priority')}, Route Dist: {dist} km")
else:
    log_test("API Endpoint GET /api/dashboard", False, f"Status Code: {res.status_code}")

# ---------------------------------------------------------
# TEST 5: REST API GET /api/bins (with Priority & Decision Filters)
# ---------------------------------------------------------
res_all = client.get("/api/bins")
res_high = client.get("/api/bins?priority=HIGH")
res_search = client.get("/api/bins?search=BIN-005")

bins_ok = res_all.status_code == 200 and res_high.status_code == 200 and res_search.status_code == 200
log_test("API Endpoint GET /api/bins & Filtering", bins_ok, 
         f"Total returned: {len(res_all.json().get('bins', []))}, HIGH priority filtered: {len(res_high.json().get('bins', []))}, Search match: {len(res_search.json().get('bins', []))}")

# ---------------------------------------------------------
# TEST 6: REST API GET /api/bins/{bin_id}
# ---------------------------------------------------------
res_single = client.get("/api/bins/BIN-001")
single_ok = res_single.status_code == 200 and res_single.json().get("Bin_ID") == "BIN-001"
log_test("API Endpoint GET /api/bins/{bin_id}", single_ok, 
         f"Bin_ID: {res_single.json().get('Bin_ID')}, Zone: {res_single.json().get('Zone')}, Fill %: {res_single.json().get('Fill_Level_Percent')}%")

# ---------------------------------------------------------
# TEST 7: REST API POST /api/predict (Random Forest Inference)
# ---------------------------------------------------------
payload = {
    "Fill_Level_Percent": 88.5,
    "Waste_Generation_Rate": 3.2,
    "Hours_Since_Collection": 24.0,
    "Hour": 14,
    "Is_Weekend": 0,
    "Temperature_C": 28.5,
    "Rainfall_mm": 0.0,
    "Population_Density": 8500,
    "Bin_Capacity_L": 360
}
res_pred = client.post("/api/predict", json=payload)
if res_pred.status_code == 200:
    pred_data = res_pred.json()
    pred_val = pred_data.get("predicted_next_fill_percent")
    prio = pred_data.get("priority_level")
    disp = pred_data.get("dispatch_decision")
    log_test("API Endpoint POST /api/predict (RF Model Inference)", 0.0 <= pred_val <= 100.0, 
             f"Input Fill: 88.5% -> Predicted Next Fill: {pred_val}%, Priority: {prio}, Decision: {disp}")
else:
    log_test("API Endpoint POST /api/predict", False, f"Status Code: {res_pred.status_code}")

# ---------------------------------------------------------
# TEST 8: REST API GET /api/priorities & GET /api/collection-plan
# ---------------------------------------------------------
res_prio = client.get("/api/priorities")
res_plan = client.get("/api/collection-plan")
plan_ok = res_prio.status_code == 200 and res_plan.status_code == 200
log_test("API Endpoints GET /api/priorities & /api/collection-plan", plan_ok, 
         f"Scheduled Bins for Collection: {res_plan.json().get('total_scheduled') if plan_ok else 0}")

# ---------------------------------------------------------
# TEST 9: REST API GET /api/route (NetworkX + Dijkstra Algorithm)
# ---------------------------------------------------------
res_route = client.get("/api/route")
if res_route.status_code == 200:
    r = res_route.json()
    stops = r.get("stops", [])
    dist = r.get("total_distance_km", 0)
    route_path = r.get("route_path", [])
    route_ok = len(stops) > 0 and dist > 0 and len(route_path) > len(stops)
    log_test("API Endpoint GET /api/route (Dijkstra Algorithm)", route_ok, 
             f"Total Distance: {dist} km, Collection Stops: {len(stops)}, Coordinate Path Nodes: {len(route_path)}")
else:
    log_test("API Endpoint GET /api/route", False, f"Status Code: {res_route.status_code}")

# ---------------------------------------------------------
# TEST 10: REST API GET /api/analytics (30-day evaluation)
# ---------------------------------------------------------
res_analytics = client.get("/api/analytics")
if res_analytics.status_code == 200:
    a = res_analytics.json()
    dist_red = a.get("distance_reduction_percent", 0)
    fuel_red = a.get("fuel_reduction_percent", 0)
    stop_red = a.get("stop_reduction_percent", 0)
    log_test("API Endpoint GET /api/analytics (Evaluation Metrics)", dist_red > 0 and fuel_red > 0, 
             f"Distance Reduction: -{dist_red}%, Fuel Reduction: -{fuel_red}%, Stop Reduction: -{stop_red}%")
else:
    log_test("API Endpoint GET /api/analytics", False, f"Status Code: {res_analytics.status_code}")

# ---------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------
passed_count = sum(1 for t in test_results if t["passed"])
total_count = len(test_results)

print("\n=========================================================")
print(f"  VERIFICATION RESULTS: {passed_count}/{total_count} PASSED  ")
print("=========================================================\n")
