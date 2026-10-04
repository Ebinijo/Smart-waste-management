"""
Smart Collection Scheduler for Smart Waste Management.
Allocates prioritized bins to available vehicle fleet capacity and assigns shift schedules.
"""

import pandas as pd
import numpy as np

def generate_collection_schedule(
    bins_df: pd.DataFrame,
    num_vehicles: int = 3,
    max_bins_per_vehicle: int = 15,
    max_weight_per_vehicle_kg: float = 1200.0
) -> dict:
    """
    Allocates collection tasks to available vehicles based on priority score and truck payload capacities.
    
    Returns:
    - scheduled_df: DataFrame with assigned Vehicle_ID, Collection_Shift, and Sequence_Order.
    - summary: Key fleet utilization statistics.
    """
    df = bins_df.copy()
    
    if 'Priority_Score' not in df.columns:
        df['Priority_Score'] = 50.0
        df['Priority_Level'] = 'MEDIUM'
        
    # Sort bins strictly by Priority Score descending (highest urgency first)
    df = df.sort_values(by='Priority_Score', ascending=False).reset_index(drop=True)
    
    # Filter bins requiring collection (CRITICAL, HIGH, and top MEDIUM)
    bins_to_collect = df[df['Priority_Level'].isin(['CRITICAL', 'HIGH', 'MEDIUM'])].copy()
    deferred_bins = df[~df['Bin_ID'].isin(bins_to_collect['Bin_ID'])].copy()
    
    deferred_bins['Vehicle_ID'] = 'None (Deferred)'
    deferred_bins['Collection_Shift'] = 'Deferred to Tomorrow'
    deferred_bins['Dispatch_Status'] = 'Deferred'
    
    vehicle_assignments = []
    
    vehicle_ids = [f"Truck-{i+1}" for i in range(num_vehicles)]
    current_vehicle_idx = 0
    current_vehicle_bin_count = 0
    current_vehicle_weight = 0.0
    
    total_fleet_max_capacity = num_vehicles * max_bins_per_vehicle
    
    scheduled_rows = []
    
    for idx, row in bins_to_collect.iterrows():
        est_weight = row.get('Estimated_Weight_kg', 80.0)
        
        # Check if current vehicle exceeds capacity limits
        if (current_vehicle_bin_count >= max_bins_per_vehicle or 
            current_vehicle_weight + est_weight > max_weight_per_vehicle_kg):
            current_vehicle_idx += 1
            current_vehicle_bin_count = 0
            current_vehicle_weight = 0.0
            
        if current_vehicle_idx < num_vehicles:
            assigned_truck = vehicle_ids[current_vehicle_idx]
            shift = "Shift 1 (Morning)" if current_vehicle_idx < (num_vehicles // 2 + 1) else "Shift 2 (Afternoon)"
            status = "Scheduled Today"
            
            current_vehicle_bin_count += 1
            current_vehicle_weight += est_weight
        else:
            assigned_truck = 'None (Capacity Exceeded)'
            shift = 'Deferred (Fleet Full)'
            status = 'Overload Deferred'
            
        row_dict = row.to_dict()
        row_dict['Vehicle_ID'] = assigned_truck
        row_dict['Collection_Shift'] = shift
        row_dict['Dispatch_Status'] = status
        scheduled_rows.append(row_dict)
        
    scheduled_df = pd.DataFrame(scheduled_rows)
    if not deferred_bins.empty:
        scheduled_df = pd.concat([scheduled_df, deferred_bins], ignore_index=True)
        
    # Calculate fleet summary
    total_bins = len(df)
    collected_today = len(scheduled_df[scheduled_df['Dispatch_Status'] == 'Scheduled Today'])
    critical_count = len(df[df['Priority_Level'] == 'CRITICAL'])
    high_count = len(df[df['Priority_Level'] == 'HIGH'])
    
    summary = {
        'total_bins': total_bins,
        'critical_bins': critical_count,
        'high_priority_bins': high_count,
        'scheduled_today': collected_today,
        'deferred_bins': total_bins - collected_today,
        'num_vehicles': num_vehicles,
        'max_fleet_capacity_bins': total_fleet_max_capacity,
        'fleet_utilization_pct': round((collected_today / total_fleet_max_capacity) * 100.0, 1) if total_fleet_max_capacity > 0 else 0.0
    }
    
    return {
        'scheduled_df': scheduled_df,
        'summary': summary
    }
