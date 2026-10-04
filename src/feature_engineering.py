"""
Feature Engineering Module for Smart Waste Management.
Computes domain-specific fill rates, accumulation velocities, sensor delta checks, and volumetric weights.
"""

import numpy as np
import pandas as pd

def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes domain-specific engineered features from raw sensor data.
    Preserves all original columns and appends engineered features.
    """
    df = df.copy()
    
    # 1. Fill level differences (Rate of accumulation)
    df['fill_diff_A_3'] = df['FL_A'] - df['FL_A_3']
    df['fill_diff_B_3'] = df['FL_B'] - df['FL_B_3']
    df['fill_diff_A_12'] = df['FL_A'] - df['FL_A_12']
    df['fill_diff_B_12'] = df['FL_B'] - df['FL_B_12']
    
    # 2. Combined Sensor Statistics
    df['max_fill'] = np.maximum(df['FL_A'], df['FL_B'])
    df['min_fill'] = np.minimum(df['FL_A'], df['FL_B'])
    df['avg_fill'] = (df['FL_A'] + df['FL_B']) / 2.0
    
    # 3. Sensor discrepancy (detect sensor fault or obstruction)
    df['sensor_delta'] = np.abs(df['FL_A'] - df['FL_B'])
    
    # 4. Hourly accumulation velocity (% per hour over 3-hour window)
    df['acc_rate_3h'] = np.maximum(0, df['fill_diff_A_3']) / 3.0
    
    # 5. Volumetric Weight factor based on Container Type
    vol_map = {'Small': 0.6, 'Medium': 0.8, 'Large': 1.0, 'Industrial': 1.2}
    df['container_vol_weight'] = df['Container Type'].map(vol_map).fillna(1.0)
    
    return df


def get_feature_names():
    """
    Returns list of feature column names used for model training.
    """
    return [
        'FL_A', 'FL_B', 'FL_A_3', 'FL_B_3', 'FL_A_12', 'FL_B_12', 'VS',
        'Recyclable Fraction', 'fill_diff_A_3', 'fill_diff_B_3',
        'fill_diff_A_12', 'fill_diff_B_12', 'max_fill', 'min_fill',
        'avg_fill', 'sensor_delta', 'acc_rate_3h', 'container_vol_weight',
        'Container Type_Medium', 'Container Type_Large', 'Container Type_Industrial'
    ]
