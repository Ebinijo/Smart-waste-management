"""
Master Pipeline Script for Smart Waste Management.
Executes dataset generation, data preprocessing, cross-validation, model training, tuning, and artifact serialization.
"""

import os
import sys

# Ensure local package import
sys.path.insert(0, os.path.abspath('.'))

from generate_dataset import generate_smart_bin_dataset, generate_simulated_city_bins
from src.train_model import train_and_compare_models

def main():
    print("===============================================================")
    print(" INTELLIGENT WASTE COLLECTION SCHEDULING - MASTER ML PIPELINE ")
    print("===============================================================\n")
    
    # 1. Create directories
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/simulated', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    # 2. Generate Benchmark Dataset
    print("[1/3] Generating Benchmark Dataset (data/raw/Smart_Bin.csv)...")
    df_smart = generate_smart_bin_dataset(num_samples=4638, random_state=42)
    df_smart.to_csv('data/raw/Smart_Bin.csv', index=False)
    print(f"      Successfully saved {len(df_smart)} rows to data/raw/Smart_Bin.csv")
    
    # 3. Generate Simulated Municipal City Bins
    print("\n[2/3] Generating Simulated City Bins (data/simulated/simulated_city_bins.csv)...")
    df_city = generate_simulated_city_bins(num_bins=50, random_state=42)
    df_city.to_csv('data/simulated/simulated_city_bins.csv', index=False)
    print(f"      Successfully saved {len(df_city)} city bin records to data/simulated/simulated_city_bins.csv")
    
    # 4. Run ML Model Training & Cross-Validation Pipeline
    print("\n[3/3] Training and Tuning ML Models...")
    model, metadata, cv_df = train_and_compare_models('data/raw/Smart_Bin.csv', 'models')
    
    print("\n===============================================================")
    print("                     PIPELINE COMPLETE                         ")
    print("===============================================================")
    print(f" Best Model:     {metadata['model_name']}")
    print(f" Test Accuracy:  {metadata['metrics']['test_accuracy']*100:.2f}%")
    print(f" Test F1-Score:  {metadata['metrics']['test_f1']*100:.2f}%")
    print(f" Artifacts:      Saved in 'models/' directory.")
    print("===============================================================\n")
    print("To launch the Streamlit dashboard, run:")
    print("  streamlit run app/app.py\n")

if __name__ == '__main__':
    main()
