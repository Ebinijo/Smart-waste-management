import os
import math
import datetime
import numpy as np
import pandas as pd
import joblib
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List

from services.prediction import predict_next_fill, load_model_and_features
from services.scheduling import evaluate_intelligent_priority, evaluate_dispatch_decision, evaluate_overflow_risk, process_bin_decision
from services.routing import generate_dijkstra_route

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_models_and_datasets()
    load_model_and_features()
    yield

app = FastAPI(
    title="Intelligent Waste Collection Scheduling System API",
    description="Backend ML prediction, scheduling, and Dijkstra route optimization service.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model")
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

LATEST_BINS_PATH = os.path.join(DATA_DIR, "latest_bin_data.csv")
HISTORICAL_PATH = os.path.join(DATA_DIR, "waste_decision_data.csv")
EVALUATION_PATH = os.path.join(DATA_DIR, "30_day_evaluation_results.csv")
MODEL_PATH = os.path.join(MODEL_DIR, "waste_fill_prediction_model.pkl")
FEATURES_PATH = os.path.join(MODEL_DIR, "model_features.pkl")

# Pydantic schemas
class PredictRequest(BaseModel):
    Fill_Level_Percent: float = Field(..., ge=0, le=100)
    Waste_Generation_Rate: float = Field(2.5, ge=0)
    Hours_Since_Collection: float = Field(12.0, ge=0)
    Hour: int = Field(14, ge=0, le=23)
    Is_Weekend: int = Field(0, ge=0, le=1)
    Temperature_C: float = Field(26.5)
    Rainfall_mm: float = Field(0.0, ge=0)
    Population_Density: int = Field(5500, ge=0)
    Bin_Capacity_L: int = Field(240, ge=0)

def ensure_models_and_datasets():
    """Ensures model and dataset CSV files exist on startup. Generates synthetic benchmark if missing."""
    if not (os.path.exists(MODEL_PATH) and os.path.exists(LATEST_BINS_PATH)):
        from sklearn.ensemble import RandomForestRegressor
        np.random.seed(42)
        
        feature_cols = [
            'Fill_Level_Percent', 'Waste_Generation_Rate', 'Hours_Since_Collection',
            'Hour', 'Is_Weekend', 'Temperature_C', 'Rainfall_mm',
            'Population_Density', 'Bin_Capacity_L'
        ]
        joblib.dump(feature_cols, FEATURES_PATH)
        
        # Train Random Forest Regressor
        N = 3000
        fl = np.random.uniform(5, 95, N)
        gen = np.random.uniform(0.5, 4.5, N)
        hrs = np.random.uniform(2, 48, N)
        hr = np.random.randint(0, 24, N)
        is_w = np.random.choice([0, 1], size=N, p=[0.7, 0.3])
        temp = np.random.uniform(15, 38, N)
        rain = np.random.choice([0.0, 0.0, 3.0, 12.0], size=N)
        pop = np.random.choice([1500, 3500, 7500, 12000], size=N)
        cap = np.random.choice([120, 240, 360, 660, 1100], size=N)
        
        acc = gen * 6.0 * (1.0 + 0.15 * is_w) + (temp - 20) * 0.04
        y_next = np.clip(fl + acc + np.random.normal(0, 3, N), 0, 100)
        
        df_train = pd.DataFrame({
            'Fill_Level_Percent': np.round(fl, 2),
            'Waste_Generation_Rate': np.round(gen, 2),
            'Hours_Since_Collection': np.round(hrs, 1),
            'Hour': hr,
            'Is_Weekend': is_w,
            'Temperature_C': np.round(temp, 1),
            'Rainfall_mm': np.round(rain, 1),
            'Population_Density': pop,
            'Bin_Capacity_L': cap,
            'Next_Fill_Level_Percent': np.round(y_next, 2)
        })
        
        model = RandomForestRegressor(n_estimators=80, max_depth=10, random_state=42)
        model.fit(df_train[feature_cols], df_train['Next_Fill_Level_Percent'])
        joblib.dump(model, MODEL_PATH)
        
        # Generate 100 city bins
        zones = ['Downtown Commercial', 'Residential North', 'Industrial District', 'Suburban South', 'University Campus']
        bin_types = ['General Waste', 'Recyclables', 'Organic', 'Hazardous', 'Paper/Cardboard']
        capacities = [120, 240, 360, 660, 1100]
        base_lat, base_lon = 37.7749, -122.4194
        
        now = datetime.datetime.now()
        latest_rows = []
        
        for i in range(1, 101):
            bin_id = f"BIN-{i:03d}"
            z = zones[(i - 1) % len(zones)]
            bt = bin_types[(i - 1) % len(bin_types)]
            c = capacities[(i - 1) % len(capacities)]
            lat = round(base_lat + np.random.uniform(-0.035, 0.035), 6)
            lon = round(base_lon + np.random.uniform(-0.045, 0.045), 6)
            
            if i % 5 == 0:
                cur_fl = round(float(np.random.uniform(90, 98)), 2)
            elif i % 5 in [1, 2]:
                cur_fl = round(float(np.random.uniform(72, 88)), 2)
            else:
                cur_fl = round(float(np.random.uniform(18, 65)), 2)
                
            gen_r = round(float(np.random.uniform(0.8, 3.8)), 2)
            hrs_s = round(float(np.random.uniform(4, 40)), 1)
            pop_d = 8500 if z == 'Downtown Commercial' else 3500
            
            f_df = pd.DataFrame([{
                'Fill_Level_Percent': cur_fl,
                'Waste_Generation_Rate': gen_r,
                'Hours_Since_Collection': hrs_s,
                'Hour': now.hour,
                'Is_Weekend': 1 if now.weekday() >= 5 else 0,
                'Temperature_C': 26.5,
                'Rainfall_mm': 0.0,
                'Population_Density': pop_d,
                'Bin_Capacity_L': c
            }])[feature_cols]
            
            pred_fl = round(float(np.clip(model.predict(f_df)[0], 0, 100)), 2)
            
            if cur_fl >= 90 or pred_fl >= 90:
                prio = 'HIGH'
                disp = 'Dispatch Immediately'
                coll_req = True
            elif cur_fl >= 70 or pred_fl >= 70:
                prio = 'MEDIUM'
                disp = 'Schedule Collection' if (cur_fl >= 80 or pred_fl >= 80) else 'No Dispatch'
                coll_req = True if disp == 'Schedule Collection' else False
            else:
                prio = 'LOW'
                disp = 'No Dispatch'
                coll_req = False
                
            ovf = True if (cur_fl >= 85 or pred_fl >= 90) else False
            frac = round(cur_fl / 100.0, 4)
            vol = round(frac * c, 1)
            last_coll = (now - datetime.timedelta(hours=hrs_s)).strftime("%Y-%m-%d %H:%M:%S")
            
            latest_rows.append({
                'Record_ID': f"REC-LATEST-{i:03d}",
                'Bin_ID': bin_id,
                'Timestamp': now.strftime("%Y-%m-%d %H:%M:%S"),
                'Latitude': lat,
                'Longitude': lon,
                'Zone': z,
                'Bin_Type': bt,
                'Bin_Capacity_L': c,
                'Fill_Level_Percent': cur_fl,
                'Waste_Generation_Rate': gen_r,
                'Waste_Type': bt,
                'Last_Collection_Time': last_coll,
                'Hours_Since_Collection': hrs_s,
                'Day_of_Week': now.strftime("%A"),
                'Hour': now.hour,
                'Is_Weekend': 1 if now.weekday() >= 5 else 0,
                'Temperature_C': 26.5,
                'Rainfall_mm': 0.0,
                'Population_Density': pop_d,
                'Collection_Required': coll_req,
                'Overflow_Risk': ovf,
                'Priority_Level': prio,
                'Dispatch_Decision': disp,
                'Fill_Level_Fraction': frac,
                'Estimated_Waste_Volume_L': vol,
                'Next_Fill_Level_Percent': pred_fl
            })
            
        pd.DataFrame(latest_rows).to_csv(LATEST_BINS_PATH, index=False)
        pd.DataFrame(latest_rows).to_csv(HISTORICAL_PATH, index=False)
        
        # 30 day evaluation results
        eval_rows = []
        for day in range(1, 31):
            t_dist = round(float(np.random.uniform(84.0, 96.0)), 2)
            i_dist = round(float(t_dist * np.random.uniform(0.48, 0.58)), 2)
            t_fuel = round(float(t_dist * 0.38 + 50 * 0.15), 2)
            i_stops = int(np.random.randint(14, 23))
            i_fuel = round(float(i_dist * 0.38 + i_stops * 0.15), 2)
            eval_rows.append({
                'Day': day,
                'Traditional_Distance_km': t_dist,
                'Intelligent_Distance_km': i_dist,
                'Traditional_Fuel_L': t_fuel,
                'Intelligent_Fuel_L': i_fuel,
                'Traditional_Stops': 50,
                'Intelligent_Stops': i_stops,
                'Traditional_Overflows': int(np.random.randint(3, 8)),
                'Intelligent_Overflows': int(np.random.choice([0, 0, 1]))
            })
        pd.DataFrame(eval_rows).to_csv(EVALUATION_PATH, index=False)

PROJECT_ROOT = os.path.dirname(BASE_DIR)
CHENNAI_RAW_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "chennai_real_bins_clean.csv")
CHENNAI_PROCESSED_PATH = os.path.join(DATA_DIR, "chennai_real_bins_processed.csv")

_chennai_df_cache = None

def get_bins_df(mode: str = "synthetic") -> pd.DataFrame:
    """Returns the DataFrame matching the requested mode ('synthetic' or 'chennai')."""
    if mode and mode.lower() == "chennai":
        return load_chennai_bins_df()
    return load_latest_bins_df()

def load_chennai_bins_df() -> pd.DataFrame:
    """Loads processed Chennai real location bins dataframe with in-memory caching."""
    global _chennai_df_cache
    if _chennai_df_cache is not None:
        return _chennai_df_cache.copy()

    if os.path.exists(CHENNAI_PROCESSED_PATH):
        df = pd.read_csv(CHENNAI_PROCESSED_PATH)
        df['Overflow_Risk'] = df['Overflow_Risk'].astype(bool)
        df['Collection_Required'] = df['Collection_Required'].astype(bool)
        _chennai_df_cache = df
        return _chennai_df_cache.copy()

    # Process raw Chennai CSV if processed CSV does not exist yet
    if not os.path.exists(CHENNAI_RAW_PATH):
        raise HTTPException(status_code=404, detail=f"Chennai raw data file not found at {CHENNAI_RAW_PATH}")

    df_raw = pd.read_csv(CHENNAI_RAW_PATH)
    N = len(df_raw)
    obj_ids = df_raw['Source_OBJECTID'].astype(int).values

    fl_list, gen_list, hrs_list, pop_list, cap_list, type_list = [], [], [], [], [], []
    types = ['General Waste', 'Recyclables', 'Organic', 'Paper/Cardboard', 'Hazardous']
    caps = [120, 240, 360, 660, 1100]
    pops = [4500, 8500, 12500, 16000]

    for obj_id in obj_ids:
        rng = np.random.RandomState(seed=int(obj_id & 0x7fffffff))
        fl = round(float(rng.uniform(10.0, 98.0)), 2)
        gen = round(float(rng.uniform(0.8, 3.8)), 2)
        hrs = round(float(rng.uniform(4.0, 42.0)), 1)
        pop = int(rng.choice(pops))
        cap = int(rng.choice(caps))
        bt = str(rng.choice(types))

        fl_list.append(fl)
        gen_list.append(gen)
        hrs_list.append(hrs)
        pop_list.append(pop)
        cap_list.append(cap)
        type_list.append(bt)

    now = datetime.datetime.now()
    df_raw['Bin_ID'] = df_raw['Real_Bin_ID']
    df_raw['Record_ID'] = [f"REC-CHN-{i:05d}" for i in range(1, N + 1)]
    df_raw['Timestamp'] = now.strftime("%Y-%m-%d %H:%M:%S")
    df_raw['Zone'] = df_raw['Area_Name']
    df_raw['Division'] = df_raw['Division_Code']
    df_raw['Area'] = df_raw['Area_Name']
    df_raw['Location'] = df_raw['Location_Name']
    df_raw['Street'] = df_raw['Street_Name']
    df_raw['Bin_Type'] = type_list
    df_raw['Waste_Type'] = type_list
    df_raw['Bin_Capacity_L'] = cap_list
    df_raw['Fill_Level_Percent'] = fl_list
    df_raw['Waste_Generation_Rate'] = gen_list
    df_raw['Hours_Since_Collection'] = hrs_list
    df_raw['Hour'] = 12
    df_raw['Is_Weekend'] = 0
    df_raw['Temperature_C'] = 31.5
    df_raw['Rainfall_mm'] = 0.0
    df_raw['Population_Density'] = pop_list

    # ML Inference using loaded Random Forest model
    model, features = load_model_and_features()
    if model is not None and features is not None:
        df_features = df_raw[features]
        preds = model.predict(df_features)
        df_raw['Next_Fill_Level_Percent'] = np.round(np.clip(preds, 0.0, 100.0), 2)
    else:
        df_raw['Next_Fill_Level_Percent'] = np.round(np.clip(df_raw['Fill_Level_Percent'] + df_raw['Waste_Generation_Rate'] * 6.0, 0.0, 100.0), 2)

    prio_levels, prio_scores, dispatch_decisions, overflow_risks, coll_reqs, vol_list, frac_list = [], [], [], [], [], [], []
    for _, row in df_raw.iterrows():
        c_fl = float(row['Fill_Level_Percent'])
        n_fl = float(row['Next_Fill_Level_Percent'])
        cap = float(row['Bin_Capacity_L'])

        p_info = evaluate_intelligent_priority(c_fl, n_fl)
        disp = evaluate_dispatch_decision(c_fl, n_fl)
        ovf = evaluate_overflow_risk(c_fl, n_fl)
        c_req = disp in ["Dispatch Immediately", "Schedule Collection"]
        frac = round(c_fl / 100.0, 4)
        vol = round(frac * cap, 1)

        prio_levels.append(p_info["priority_level"])
        prio_scores.append(p_info["priority_score"])
        dispatch_decisions.append(disp)
        overflow_risks.append(ovf)
        coll_reqs.append(c_req)
        frac_list.append(frac)
        vol_list.append(vol)

    df_raw['Priority_Level'] = prio_levels
    df_raw['Priority_Score'] = prio_scores
    df_raw['Dispatch_Decision'] = dispatch_decisions
    df_raw['Overflow_Risk'] = overflow_risks
    df_raw['Collection_Required'] = coll_reqs
    df_raw['Fill_Level_Fraction'] = frac_list
    df_raw['Estimated_Waste_Volume_L'] = vol_list
    df_raw['Data_Source'] = "Real Chennai Bin Locations + Simulated Operational Data"

    os.makedirs(DATA_DIR, exist_ok=True)
    df_raw.to_csv(CHENNAI_PROCESSED_PATH, index=False)
    _chennai_df_cache = df_raw
    return _chennai_df_cache.copy()

def load_latest_bins_df() -> pd.DataFrame:
    ensure_models_and_datasets()
    df = pd.read_csv(LATEST_BINS_PATH)
    # Fill NaN values safely
    df['Overflow_Risk'] = df['Overflow_Risk'].astype(bool)
    df['Collection_Required'] = df['Collection_Required'].astype(bool)
    return df

@app.get("/")
def root_index():
    return {
        "message": "Intelligent Waste Collection Scheduling System API is running!",
        "swagger_docs": "/docs",
        "health": "/api/health"
    }

@app.get("/api/health")
def health_check(mode: str = "synthetic"):
    is_chennai = mode and mode.lower() == "chennai"
    return {
        "status": "healthy",
        "system": "Intelligent Waste Collection Scheduling System",
        "data_mode": "Real Chennai Bin Locations + Simulated Operational Data" if is_chennai else "Synthetic Demo",
        "timestamp": datetime.datetime.now().isoformat()
    }

@app.get("/api/filters")
def get_filters(mode: str = "synthetic"):
    df = get_bins_df(mode)
    zones = sorted([str(z) for z in df['Zone'].dropna().unique()]) if 'Zone' in df else []
    divisions = sorted([str(d) for d in df['Division_Code'].dropna().unique()]) if 'Division_Code' in df else []
    return {
        "zones": zones,
        "divisions": divisions,
        "priorities": ["HIGH", "MEDIUM", "LOW"],
        "decisions": ["Dispatch Immediately", "Schedule Collection", "No Dispatch"]
    }

@app.get("/api/dashboard")
def get_dashboard_summary(mode: str = "synthetic"):
    df = get_bins_df(mode)
    is_chennai = mode and mode.lower() == "chennai"
    
    total_bins = len(df)
    high_prio = int((df['Priority_Level'] == 'HIGH').sum())
    med_prio = int((df['Priority_Level'] == 'MEDIUM').sum())
    low_prio = int((df['Priority_Level'] == 'LOW').sum())
    
    coll_req = int((df['Dispatch_Decision'].isin(['Dispatch Immediately', 'Schedule Collection'])).sum())
    overflow_risk = int(df['Overflow_Risk'].sum())
    pred_collections = int((df['Next_Fill_Level_Percent'] >= 80.0).sum())
    
    # Calculate route info (use appropriate depot and max stops limit)
    depot_lat, depot_lon, depot_name = (13.0827, 80.2707, "Simulation Depot") if is_chennai else (37.7749, -122.4194, "Central Municipal Waste Depot")
    route_data = generate_dijkstra_route(
        df.to_dict('records'),
        depot_lat=depot_lat,
        depot_lon=depot_lon,
        depot_name=depot_name,
        max_stops=30
    )
    
    return {
        "mode": "chennai" if is_chennai else "synthetic",
        "total_bins": total_bins,
        "high_priority": high_prio,
        "medium_priority": med_prio,
        "low_priority": low_prio,
        "collection_required": coll_req,
        "overflow_risk": overflow_risk,
        "predicted_collections": pred_collections,
        "total_route_distance_km": route_data["total_distance_km"],
        "total_route_stops": route_data["total_stops"],
        "data_notice": "Real Chennai Bin Locations + Simulated Operational Data" if is_chennai else "Synthetic Demo Mode"
    }

@app.get("/api/bins")
def get_all_bins(
    mode: str = "synthetic",
    priority: Optional[str] = None,
    decision: Optional[str] = None,
    overflow: Optional[bool] = None,
    search: Optional[str] = None,
    zone: Optional[str] = None,
    division: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=1000)
):
    df = get_bins_df(mode)
    is_chennai = mode and mode.lower() == "chennai"
    
    if priority and priority.upper() in ['HIGH', 'MEDIUM', 'LOW']:
        df = df[df['Priority_Level'] == priority.upper()]
        
    if decision:
        df = df[df['Dispatch_Decision'].str.lower() == decision.lower()]
        
    if overflow is not None:
        df = df[df['Overflow_Risk'] == overflow]

    if zone:
        df = df[df['Zone'].astype(str).str.lower() == zone.lower()]

    if division and 'Division_Code' in df:
        df = df[df['Division_Code'].astype(str).str.lower() == division.lower()]
        
    if search:
        s = search.lower()
        cond = (
            df['Bin_ID'].astype(str).str.lower().str.contains(s) |
            df['Zone'].astype(str).str.lower().str.contains(s) |
            df['Bin_Type'].astype(str).str.lower().str.contains(s)
        )
        if 'Real_Bin_ID' in df:
            cond = cond | df['Real_Bin_ID'].astype(str).str.lower().str.contains(s)
        if 'Area_Name' in df:
            cond = cond | df['Area_Name'].astype(str).str.lower().str.contains(s)
        if 'Location_Name' in df:
            cond = cond | df['Location_Name'].astype(str).str.lower().str.contains(s)
        if 'Street_Name' in df:
            cond = cond | df['Street_Name'].astype(str).str.lower().str.contains(s)
        df = df[cond]

    total_count = len(df)
    total_pages = max(1, math.ceil(total_count / limit))
    
    # Paginate
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_df = df.iloc[start_idx:end_idx]

    return {
        "mode": "chennai" if is_chennai else "synthetic",
        "data_notice": "Real Chennai Bin Locations + Simulated Operational Data" if is_chennai else "Synthetic Demo",
        "count": total_count,
        "total_count": total_count,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "bins": paginated_df.to_dict('records')
    }

@app.get("/api/bins/{bin_id}")
def get_bin_by_id(bin_id: str, mode: str = "synthetic"):
    df = get_bins_df(mode)
    match = df[df['Bin_ID'].astype(str).str.upper() == bin_id.upper()]
    if match.empty and 'Real_Bin_ID' in df:
        match = df[df['Real_Bin_ID'].astype(str).str.upper() == bin_id.upper()]

    if match.empty:
        raise HTTPException(status_code=404, detail=f"Bin '{bin_id}' not found.")
    
    bin_dict = match.iloc[0].to_dict()
    bin_dict['Overflow_Risk'] = bool(bin_dict['Overflow_Risk'])
    bin_dict['Collection_Required'] = bool(bin_dict['Collection_Required'])
    return bin_dict

@app.post("/api/predict")
def predict_fill_level(req: PredictRequest):
    data_dict = req.dict()
    predicted_next_fill = predict_next_fill(data_dict)
    cur_fill = req.Fill_Level_Percent
    
    prio_info = evaluate_intelligent_priority(cur_fill, predicted_next_fill)
    dispatch_decision = evaluate_dispatch_decision(cur_fill, predicted_next_fill)
    overflow_risk = evaluate_overflow_risk(cur_fill, predicted_next_fill)
    
    return {
        "input": data_dict,
        "predicted_next_fill_percent": predicted_next_fill,
        "priority_level": prio_info["priority_level"],
        "priority_score": prio_info["priority_score"],
        "dispatch_decision": dispatch_decision,
        "overflow_risk": overflow_risk,
        "collection_required": dispatch_decision in ["Dispatch Immediately", "Schedule Collection"],
        "model_used": "RandomForestRegressor (.pkl joblib)",
        "features_used": [
            'Fill_Level_Percent', 'Waste_Generation_Rate', 'Hours_Since_Collection',
            'Hour', 'Is_Weekend', 'Temperature_C', 'Rainfall_mm',
            'Population_Density', 'Bin_Capacity_L'
        ]
    }

@app.get("/api/priorities")
def get_priority_summary(mode: str = "synthetic"):
    df = get_bins_df(mode)
    summary = {
        "HIGH": df[df['Priority_Level'] == 'HIGH'].to_dict('records'),
        "MEDIUM": df[df['Priority_Level'] == 'MEDIUM'].to_dict('records'),
        "LOW": df[df['Priority_Level'] == 'LOW'].to_dict('records'),
        "counts": {
            "HIGH": int((df['Priority_Level'] == 'HIGH').sum()),
            "MEDIUM": int((df['Priority_Level'] == 'MEDIUM').sum()),
            "LOW": int((df['Priority_Level'] == 'LOW').sum())
        }
    }
    return summary

@app.get("/api/collection-plan")
def get_collection_plan(mode: str = "synthetic", limit: int = Query(100, ge=1, le=1000)):
    df = get_bins_df(mode)
    
    # Bins with Dispatch Immediately or Schedule Collection
    plan_df = df[df['Dispatch_Decision'].isin(['Dispatch Immediately', 'Schedule Collection'])].copy()
    
    # Priority sorting mapping: HIGH = 3, MEDIUM = 2, LOW = 1
    prio_order = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
    plan_df['p_score'] = plan_df['Priority_Level'].map(prio_order)
    
    # Sort by priority score desc, then predicted fill desc
    plan_df = plan_df.sort_values(by=['p_score', 'Next_Fill_Level_Percent'], ascending=[False, False])
    plan_df = plan_df.drop(columns=['p_score'])

    if limit and len(plan_df) > limit:
        plan_df = plan_df.iloc[:limit]
    
    return {
        "mode": "chennai" if (mode and mode.lower() == "chennai") else "synthetic",
        "date": datetime.date.today().isoformat(),
        "total_scheduled": len(plan_df),
        "plan": plan_df.to_dict('records')
    }

@app.get("/api/route")
def get_optimized_route(mode: str = "synthetic", max_stops: int = Query(30, ge=5, le=500)):
    df = get_bins_df(mode)
    is_chennai = mode and mode.lower() == "chennai"
    depot_lat, depot_lon, depot_name = (13.0827, 80.2707, "Simulation Depot") if is_chennai else (37.7749, -122.4194, "Central Municipal Waste Depot")

    route_res = generate_dijkstra_route(
        df.to_dict('records'),
        depot_lat=depot_lat,
        depot_lon=depot_lon,
        depot_name=depot_name,
        max_stops=max_stops
    )
    route_res["mode"] = "chennai" if is_chennai else "synthetic"
    return route_res

@app.get("/api/analytics")
def get_analytics(mode: str = "synthetic"):
    is_chennai = mode and mode.lower() == "chennai"
    latest_bins = get_bins_df(mode)

    eval_df = pd.read_csv(EVALUATION_PATH) if os.path.exists(EVALUATION_PATH) else pd.DataFrame()
    
    avg_trad_dist = eval_df['Traditional_Distance_km'].mean() if not eval_df.empty else 90.0
    avg_intel_dist = eval_df['Intelligent_Distance_km'].mean() if not eval_df.empty else 48.0
    dist_reduction = ((avg_trad_dist - avg_intel_dist) / avg_trad_dist) * 100.0 if avg_trad_dist else 0.0
    
    avg_trad_fuel = eval_df['Traditional_Fuel_L'].mean() if not eval_df.empty else 41.0
    avg_intel_fuel = eval_df['Intelligent_Fuel_L'].mean() if not eval_df.empty else 21.0
    fuel_reduction = ((avg_trad_fuel - avg_intel_fuel) / avg_trad_fuel) * 100.0 if avg_trad_fuel else 0.0
    
    avg_trad_stops = eval_df['Traditional_Stops'].mean() if not eval_df.empty else 50.0
    avg_intel_stops = eval_df['Intelligent_Stops'].mean() if not eval_df.empty else 18.0
    stop_reduction = ((avg_trad_stops - avg_intel_stops) / avg_trad_stops) * 100.0 if avg_trad_stops else 0.0
    
    prio_dist = latest_bins['Priority_Level'].value_counts().to_dict()
    
    fill_bins = pd.cut(
        latest_bins['Fill_Level_Percent'],
        bins=[0, 25, 50, 75, 90, 100],
        labels=['0-25%', '26-50%', '51-75%', '76-90%', '91-100%']
    ).value_counts().to_dict()
    
    dispatch_dist = latest_bins['Dispatch_Decision'].value_counts().to_dict()
    
    return {
        "status": "success",
        "mode": "chennai" if is_chennai else "synthetic",
        "data_notice": "Real Chennai Bin Locations + Simulated Operational Data" if is_chennai else "Synthetic Demo Mode",
        "distance_reduction_percent": round(dist_reduction, 1),
        "fuel_reduction_percent": round(fuel_reduction, 1),
        "stop_reduction_percent": round(stop_reduction, 1),
        "summary": {
            "avg_traditional_distance_km": round(avg_trad_dist, 1),
            "avg_intelligent_distance_km": round(avg_intel_dist, 1),
            "avg_traditional_fuel_L": round(avg_trad_fuel, 1),
            "avg_intelligent_fuel_L": round(avg_intel_fuel, 1),
            "avg_traditional_stops": round(avg_trad_stops, 1),
            "avg_intelligent_stops": round(avg_intel_stops, 1)
        },
        "daily_evaluation": eval_df.to_dict('records') if not eval_df.empty else [],
        "distributions": {
            "priority": prio_dist,
            "fill_level": {str(k): int(v) for k, v in fill_bins.items()},
            "dispatch_decision": dispatch_dist
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)


