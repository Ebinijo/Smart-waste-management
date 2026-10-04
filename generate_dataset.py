"""
Dataset Generator Script for Smart Waste Management Project.
Generates:
1. data/raw/Smart_Bin.csv: Benchmark dataset (~4,638 records, 10 features) matching Kaggle Smart Bin dataset schema.
2. data/simulated/simulated_city_bins.csv: 50 Municipal City Bins with simulated GPS coordinates for dynamic GIS route visualization.
"""

import os
import numpy as np
import pandas as pd

def generate_smart_bin_dataset(num_samples=4638, random_state=42):
    np.random.seed(random_state)
    
    # Target Class generation based on realistic fill level physics
    # Class = 1 if bin requires emptying, 0 if safe
    
    # Sensor A current fill level (0 - 100%)
    fl_a = np.random.beta(a=2, b=1.5, size=num_samples) * 100
    
    # Sensor B current fill level (correlated with A with slight variance)
    noise_b = np.random.normal(0, 5, size=num_samples)
    fl_b = np.clip(fl_a + noise_b, 0, 100)
    
    # Fill levels 3 hours ago (must be <= current fill level, accounting for accumulation)
    diff_a_3 = np.random.exponential(scale=6, size=num_samples)
    fl_a_3 = np.clip(fl_a - diff_a_3, 0, 100)
    
    diff_b_3 = np.random.exponential(scale=6, size=num_samples)
    fl_b_3 = np.clip(fl_b - diff_b_3, 0, 100)
    
    # Fill levels 12 hours ago
    diff_a_12 = diff_a_3 + np.random.exponential(scale=15, size=num_samples)
    fl_a_12 = np.clip(fl_a - diff_a_12, 0, 100)
    
    diff_b_12 = diff_b_3 + np.random.exponential(scale=15, size=num_samples)
    fl_b_12 = np.clip(fl_b - diff_b_12, 0, 100)
    
    # Volume/Vibration Sensor (VS) metric (0 - 100)
    vs = np.clip(0.6 * fl_a + 0.4 * fl_b + np.random.normal(0, 8, size=num_samples), 0, 100)
    
    # Container Type
    container_types = np.random.choice(['Small', 'Medium', 'Large', 'Industrial'], size=num_samples, p=[0.25, 0.40, 0.25, 0.10])
    
    # Recyclable Fraction (0.0 - 1.0)
    recyclable_fraction = np.round(np.random.uniform(0.10, 0.90, size=num_samples), 2)
    
    # Class logic: Emptying required if max sensor fill >= 75% OR (fill >= 60% AND rapid accumulation > 15% in 3h)
    max_fill = np.maximum(fl_a, fl_b)
    acc_rate = np.maximum(fl_a - fl_a_3, fl_b - fl_b_3)
    
    # Probabilistic logistic classification bound to create realistic noise & non-linear decision boundary
    logit = 0.12 * max_fill + 0.08 * acc_rate + 0.03 * vs - 9.5
    prob = 1.0 / (1.0 + np.exp(-logit))
    
    target_class = (prob >= 0.50).astype(int)
    
    df = pd.DataFrame({
        'FL_A': np.round(fl_a, 2),
        'FL_B': np.round(fl_b, 2),
        'FL_A_3': np.round(fl_a_3, 2),
        'FL_B_3': np.round(fl_b_3, 2),
        'FL_A_12': np.round(fl_a_12, 2),
        'FL_B_12': np.round(fl_b_12, 2),
        'VS': np.round(vs, 2),
        'Container Type': container_types,
        'Recyclable Fraction': recyclable_fraction,
        'Class': target_class
    })
    
    return df


def generate_simulated_city_bins(num_bins=50, base_lat=40.7128, base_lon=-74.0060, random_state=42):
    np.random.seed(random_state)
    
    bin_ids = [f"BIN-{100 + i}" for i in range(1, num_bins + 1)]
    
    # Municipal Zones
    zones = np.random.choice(['Downtown Commercial', 'Residential North', 'Industrial Park', 'Suburban East', 'University Campus'], size=num_bins)
    
    # Geofenced coordinates around municipal base
    lats = base_lat + np.random.uniform(-0.04, 0.04, size=num_bins)
    lons = base_lon + np.random.uniform(-0.04, 0.04, size=num_bins)
    
    fl_a = np.round(np.random.beta(a=2, b=1.5, size=num_bins) * 100, 2)
    fl_b = np.round(np.clip(fl_a + np.random.normal(0, 4, size=num_bins), 0, 100), 2)
    
    fl_a_3 = np.round(np.clip(fl_a - np.random.exponential(scale=7, size=num_bins), 0, 100), 2)
    fl_b_3 = np.round(np.clip(fl_b - np.random.exponential(scale=7, size=num_bins), 0, 100), 2)
    
    fl_a_12 = np.round(np.clip(fl_a_3 - np.random.exponential(scale=12, size=num_bins), 0, 100), 2)
    fl_b_12 = np.round(np.clip(fl_b_3 - np.random.exponential(scale=12, size=num_bins), 0, 100), 2)
    
    vs = np.round(np.clip(0.6 * fl_a + 0.4 * fl_b + np.random.normal(0, 5, size=num_bins), 0, 100), 2)
    container_type = np.random.choice(['Small', 'Medium', 'Large', 'Industrial'], size=num_bins, p=[0.25, 0.40, 0.25, 0.10])
    recyclable_fraction = np.round(np.random.uniform(0.15, 0.85, size=num_bins), 2)
    
    # Estimated waste weight in kg based on container type and fill level
    capacity_map = {'Small': 50, 'Medium': 100, 'Large': 200, 'Industrial': 500}
    max_cap = np.array([capacity_map[ct] for ct in container_type])
    estimated_weight_kg = np.round(max_cap * (np.maximum(fl_a, fl_b) / 100.0), 1)
    
    df_city = pd.DataFrame({
        'Bin_ID': bin_ids,
        'Zone': zones,
        'Latitude': np.round(lats, 6),
        'Longitude': np.round(lons, 6),
        'FL_A': fl_a,
        'FL_B': fl_b,
        'FL_A_3': fl_a_3,
        'FL_B_3': fl_b_3,
        'FL_A_12': fl_a_12,
        'FL_B_12': fl_b_12,
        'VS': vs,
        'Container Type': container_type,
        'Recyclable Fraction': recyclable_fraction,
        'Estimated_Weight_kg': estimated_weight_kg,
        'Last_Collected_Hours_Ago': np.random.randint(4, 72, size=num_bins)
    })
    
    return df_city


if __name__ == '__main__':
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/simulated', exist_ok=True)
    
    df_smart = generate_smart_bin_dataset(4638)
    df_smart.to_csv('data/raw/Smart_Bin.csv', index=False)
    print(f"Generated data/raw/Smart_Bin.csv with {len(df_smart)} records.")
    
    df_city = generate_simulated_city_bins(50)
    df_city.to_csv('data/simulated/simulated_city_bins.csv', index=False)
    print(f"Generated data/simulated/simulated_city_bins.csv with {len(df_city)} records.")
