import os
import joblib
import pandas as pd
import numpy as np

# Absolute paths to model directory
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "model")
MODEL_PATH = os.path.join(MODEL_DIR, "waste_fill_prediction_model.pkl")
FEATURES_PATH = os.path.join(MODEL_DIR, "model_features.pkl")

_model = None
_features = None

def load_model_and_features():
    """
    Loads the Random Forest model trained in Google Colab from .pkl file.
    Does NOT retrain the model inside the application.
    """
    global _model, _features
    if _model is None or _features is None:
        if os.path.exists(MODEL_PATH) and os.path.exists(FEATURES_PATH):
            _model = joblib.load(MODEL_PATH)
            _features = joblib.load(FEATURES_PATH)
        else:
            # Default fallback feature list matching exact specifications
            _features = [
                'Fill_Level_Percent',
                'Waste_Generation_Rate',
                'Hours_Since_Collection',
                'Hour',
                'Is_Weekend',
                'Temperature_C',
                'Rainfall_mm',
                'Population_Density',
                'Bin_Capacity_L'
            ]
            _model = None
    return _model, _features

def predict_next_fill(data: dict) -> float:
    """
    Predicts Next_Fill_Level_Percent using trained Random Forest Regressor.
    Clips predicted output to range [0.0, 100.0].
    """
    model, features = load_model_and_features()
    
    # Extract features matching model input format
    input_dict = {
        'Fill_Level_Percent': float(data.get('Fill_Level_Percent', 50.0)),
        'Waste_Generation_Rate': float(data.get('Waste_Generation_Rate', 2.0)),
        'Hours_Since_Collection': float(data.get('Hours_Since_Collection', 12.0)),
        'Hour': int(data.get('Hour', 12)),
        'Is_Weekend': int(data.get('Is_Weekend', 0)),
        'Temperature_C': float(data.get('Temperature_C', 25.0)),
        'Rainfall_mm': float(data.get('Rainfall_mm', 0.0)),
        'Population_Density': int(data.get('Population_Density', 3500)),
        'Bin_Capacity_L': int(data.get('Bin_Capacity_L', 240))
    }
    
    if model is not None:
        df_input = pd.DataFrame([input_dict])[features]
        raw_pred = model.predict(df_input)[0]
    else:
        # Physics heuristic fallback if model file is not present
        fl = input_dict['Fill_Level_Percent']
        gen = input_dict['Waste_Generation_Rate']
        hrs = 6.0 # 6-hour forecast horizon
        raw_pred = fl + (gen * hrs * (1.1 if input_dict['Is_Weekend'] else 1.0))
        
    # Clip prediction to range 0-100 as per system requirements
    clipped_pred = float(np.clip(raw_pred, 0.0, 100.0))
    return round(clipped_pred, 2)
