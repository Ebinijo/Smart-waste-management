# Intelligent Waste Collection Scheduling System

An end-to-end full-stack machine learning web application for intelligent municipal waste bin prediction, dispatch scheduling, and graph-based Dijkstra route optimization.

> **Project Disclaimer**: This application operates on a synthetic/simulated municipal waste bin dataset for research and academic demonstration purposes. It does NOT process live physical IoT hardware sensors. The road network graph is synthesized from bin geographic coordinates.

---

## 1. Project Overview

Municipal waste collection using traditional fixed schedules leads to inefficient fuel consumption, premature bin visits, and unaddressed bin overflows. The **Intelligent Waste Collection Scheduling System** replaces rigid collection routes with a machine-learning dynamic dispatch pipeline:

1. Predicts bin fill levels using a Random Forest Regressor (`Next_Fill_Level_Percent`).
2. Classifies bin priority (`HIGH`, `MEDIUM`, `LOW`).
3. Evaluates rule-based dispatch decisions (`Dispatch Immediately`, `Schedule Collection`, `No Dispatch`).
4. Generates an optimized shortest-path truck route using Dijkstra's algorithm over NetworkX graphs.
5. Displays comparative analytics comparing traditional fixed collection vs intelligent ML routing over a 30-day simulation.

---

## 2. Architecture

```
smart-waste-management/
├── backend/
│   ├── main.py                  # FastAPI REST API endpoints & CORS middleware
│   ├── model/
│   │   ├── waste_fill_prediction_model.pkl # Trained Random Forest model (joblib)
│   │   └── model_features.pkl   # List of 9 model input feature names
│   ├── data/
│   │   ├── latest_bin_data.csv  # 50 municipal city bins current snapshot
│   │   ├── waste_decision_data.csv # Historical simulated time-series logs
│   │   └── 30_day_evaluation_results.csv # Daily evaluation comparison data
│   └── services/
│       ├── __init__.py
│       ├── prediction.py        # ML inference engine (clips predictions 0-100)
│       ├── scheduling.py        # Intelligent priority & dispatch decision rules
│       └── routing.py           # NetworkX graph construction & Dijkstra algorithm
└── frontend/
    ├── index.html               # Entry HTML with Leaflet & font dependencies
    ├── package.json             # React, Vite, Leaflet, Recharts, Tailwind
    ├── vite.config.js           # Vite dev server proxy to FastAPI (port 8000)
    ├── tailwind.config.js       # Custom Tailwind CSS styling
    └── src/
        ├── App.jsx              # Main app layout and page router
        ├── main.jsx             # React DOM entry
        ├── index.css            # Global CSS & Leaflet theme
        ├── services/api.js      # REST API client
        ├── components/
        │   ├── Navbar.jsx       # System header & synthetic data notice
        │   ├── Sidebar.jsx      # Navigation sidebar
        │   ├── MetricCard.jsx   # KPI metric stat cards
        │   ├── StatusBadge.jsx  # Color-coded priority & decision badges
        │   └── BinDetailModal.jsx # Detailed bin inspection modal
        └── pages/
            ├── Dashboard.jsx    # KPI cards & system workflow
            ├── BinMonitoring.jsx # Searchable & filterable bin table
            ├── CollectionSchedule.jsx # Recommended daily collection plan
            ├── RouteOptimization.jsx # Interactive Leaflet map & Dijkstra route
            ├── Analytics.jsx    # 7 interactive charts & evaluation metrics
            └── SystemInfo.jsx   # Methodology documentation & disclaimers
```

---

## 3. Technologies Used

- **Backend**: Python 3.14, FastAPI, Pandas, NumPy, scikit-learn, joblib, NetworkX, Uvicorn
- **Frontend**: React 18, Vite, Tailwind CSS, Lucide Icons, Leaflet / React-Leaflet, Recharts
- **ML & Graph Algorithms**: Random Forest Regressor, Dijkstra Shortest Path Algorithm, Haversine Distance Formula

---

## 4. Dataset Specification

Synthesized dataset containing 25 schema fields per record:

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `Record_ID` | String | Unique record key (`REC-001`) |
| `Bin_ID` | String | Bin identifier (`BIN-001` to `BIN-050`) |
| `Timestamp` | Datetime | Measurement timestamp |
| `Latitude` | Float | Geographic latitude coordinate |
| `Longitude` | Float | Geographic longitude coordinate |
| `Zone` | String | Municipal zone (e.g. Downtown Commercial, Residential North) |
| `Bin_Type` | String | Container category (General Waste, Recyclables, Organic, etc.) |
| `Bin_Capacity_L` | Integer | Bin volume in Liters (120, 240, 360, 660, 1100) |
| `Fill_Level_Percent` | Float | Current fill level (0% - 100%) |
| `Waste_Generation_Rate` | Float | Fill accumulation rate (% per hour) |
| `Hours_Since_Collection`| Float | Time elapsed since last emptying |
| `Hour` | Integer | Hour of day (0–23) |
| `Is_Weekend` | Integer | Weekend binary flag (0 or 1) |
| `Temperature_C` | Float | Ambient temperature (°C) |
| `Rainfall_mm` | Float | Precipitation level (mm) |
| `Population_Density` | Integer | Surrounding population density per km² |
| `Next_Fill_Level_Percent`| Float | Target/Predicted fill level (% clipped to 0–100) |
| `Priority_Level` | String | Priority classification (`HIGH`, `MEDIUM`, `LOW`) |
| `Dispatch_Decision` | String | Action recommendation (`Dispatch Immediately`, `Schedule Collection`, `No Dispatch`) |

---

## 5. Machine Learning Model

The system utilizes a **Random Forest Regressor** loaded from `waste_fill_prediction_model.pkl` via `joblib`.

### Feature Vector (9 Input Features)
1. `Fill_Level_Percent`
2. `Waste_Generation_Rate`
3. `Hours_Since_Collection`
4. `Hour`
5. `Is_Weekend`
6. `Temperature_C`
7. `Rainfall_mm`
8. `Population_Density`
9. `Bin_Capacity_L`

Predictions are automatically clipped to the range `[0.0, 100.0]`.

---

## 6. Intelligent Priority & Dispatch Logic

### Priority Assignment
- **HIGH** (Priority Score = 3): Current Fill ≥ 90% **OR** Predicted Fill ≥ 90%
- **MEDIUM** (Priority Score = 2): Current Fill ≥ 70% **OR** Predicted Fill ≥ 70%
- **LOW** (Priority Score = 1): Otherwise

### Dispatch Decision Rules
- **Dispatch Immediately**: Current Fill ≥ 90% **OR** Predicted Fill ≥ 90%
- **Schedule Collection**: Current Fill ≥ 80% **OR** Predicted Fill ≥ 80%
- **No Dispatch**: Otherwise

---

## 7. Dijkstra Route Optimization

The backend builds a connected NetworkX graph `G(V, E)` where:
- Nodes $V$: Central Municipal Depot + Bins requiring collection (`Dispatch Immediately` or `Schedule Collection`).
- Edge weights $E$: Haversine geographic distances in kilometers computed from node latitude/longitude pairs.

### Routing Execution Procedure:
1. Filter bins requiring collection.
2. Group bins by priority tier (`HIGH` priority visited first, followed by `MEDIUM` priority).
3. Start route traversal at `DEPOT`.
4. Apply Dijkstra shortest-path search (`nx.dijkstra_path`) iteratively to select the next nearest unvisited collection bin in the priority queue.
5. Traverse back to `DEPOT` to complete the closed collection loop.
6. Render polylines and color-coded markers on the interactive Leaflet map.

---

## 8. How to Install & Run

### Prerequisites
- Python 3.9+ installed
- Node.js 18+ and npm installed

### Step 1: Install Backend Dependencies
```bash
cd smart-waste-management
pip install fastapi uvicorn pandas numpy scikit-learn joblib networkx
```

### Step 2: Start FastAPI Backend Server
```bash
python backend/main.py
```
*The backend server will run on `http://127.0.0.1:8000`. On first launch, it automatically initializes all synthetic datasets and model files if missing.*

### Step 3: Install Frontend Dependencies & Start Vite Server
Open a new terminal window:
```bash
cd smart-waste-management/frontend
npm install
npm run dev
```
*The frontend dashboard will open on `http://localhost:3000`.*

---

## 9. System Limitations

- **Simulated Data**: Telemetry metrics are synthetic benchmarks. The system does not interface with physical hardware sensors.
- **Geographic Graph**: Edge weights reflect Haversine distance lines rather than live turn-by-turn road navigation APIs (e.g. OpenStreetMap OSRM).
- **Static Fleet**: Assumes a single primary collection truck per route loop.

---

## 10. Future Enhancements

- Integration of live OpenStreetMap OSRM routing for actual road network turns and traffic congestion indexing.
- Multi-truck Vehicle Routing Problem (VRP) solving with capacity constraints (Capacitated VRP).
- Real-time IoT MQTT sensor telemetry ingestion pipeline.
