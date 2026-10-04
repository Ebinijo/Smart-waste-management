import os
import datetime
import joblib
import numpy as np
import pandas as pd

np.random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "backend", "data")
MODEL_DIR = os.path.join(BASE_DIR, "backend", "model")

MODEL_PATH = os.path.join(MODEL_DIR, "waste_fill_prediction_model.pkl")
FEATURES_PATH = os.path.join(MODEL_DIR, "model_features.pkl")
LATEST_PATH = os.path.join(DATA_DIR, "latest_bin_data.csv")
HIST_PATH = os.path.join(DATA_DIR, "waste_decision_data.csv")

if os.path.exists(MODEL_PATH) and os.path.exists(FEATURES_PATH):
    model = joblib.load(MODEL_PATH)
    feature_cols = joblib.load(FEATURES_PATH)
else:
    from sklearn.ensemble import RandomForestRegressor
    feature_cols = [
        'Fill_Level_Percent', 'Waste_Generation_Rate', 'Hours_Since_Collection',
        'Hour', 'Is_Weekend', 'Temperature_C', 'Rainfall_mm',
        'Population_Density', 'Bin_Capacity_L'
    ]
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
    joblib.dump(feature_cols, FEATURES_PATH)

# Generate 100 unique city bins
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
    lat = round(base_lat + np.random.uniform(-0.038, 0.038), 6)
    lon = round(base_lon + np.random.uniform(-0.048, 0.048), 6)
    
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

pd.DataFrame(latest_rows).to_csv(LATEST_PATH, index=False)
pd.DataFrame(latest_rows).to_csv(HIST_PATH, index=False)
print(f"Successfully generated {len(latest_rows)} unique city bins into {LATEST_PATH}")
