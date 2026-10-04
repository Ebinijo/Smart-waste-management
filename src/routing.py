"""
Route Optimization Engine for Smart Waste Management.
Calculates Haversine distance matrices and solves TSP/VRP using Nearest-Neighbor + 2-Opt local search refinement.
Compares unoptimized vs optimized travel distance, fuel consumption, and carbon emissions.
"""

import numpy as np
import pandas as pd

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes Great-Circle (Haversine) distance between two lat/lon pairs in kilometers.
    """
    R = 6371.0 # Earth radius in kilometers
    
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)
    
    a = np.sin(delta_phi / 2.0)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0)**2
    c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
    
    return R * c


def compute_distance_matrix(coords: list) -> np.ndarray:
    """
    Computes N x N distance matrix for a list of (lat, lon) tuples.
    """
    n = len(coords)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                dist_matrix[i, j] = haversine_distance(coords[i][0], coords[i][1], coords[j][0], coords[j][1])
    return dist_matrix


def route_length(route: list, dist_matrix: np.ndarray) -> float:
    """
    Calculates total round-trip distance for a sequence of node indices.
    """
    total_dist = 0.0
    for i in range(len(route) - 1):
        total_dist += dist_matrix[route[i], route[i+1]]
    total_dist += dist_matrix[route[-1], route[0]] # Return to depot
    return total_dist


def solve_nearest_neighbor(dist_matrix: np.ndarray, start_node: int = 0) -> list:
    """
    Nearest Neighbor TSP heuristic starting from depot (node 0).
    """
    n = len(dist_matrix)
    unvisited = set(range(n))
    unvisited.remove(start_node)
    
    route = [start_node]
    current = start_node
    
    while unvisited:
        next_node = min(unvisited, key=lambda node: dist_matrix[current, node])
        unvisited.remove(next_node)
        route.append(next_node)
        current = next_node
        
    return route


def solve_2opt(route: list, dist_matrix: np.ndarray, max_iterations: int = 100) -> list:
    """
    2-Opt local search improvement for TSP route.
    """
    best_route = list(route)
    best_distance = route_length(best_route, dist_matrix)
    n = len(best_route)
    
    improved = True
    iteration = 0
    
    while improved and iteration < max_iterations:
        improved = False
        iteration += 1
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                if j - i == 1:
                    continue
                # Swap sub-route between i and j
                new_route = best_route[:i] + best_route[i:j][::-1] + best_route[j:]
                new_distance = route_length(new_route, dist_matrix)
                if new_distance < best_distance:
                    best_route = new_route
                    best_distance = new_distance
                    improved = True
                    break
            if improved:
                break
                
    return best_route


def optimize_collection_route(
    scheduled_df: pd.DataFrame,
    depot_lat: float = 40.7128,
    depot_lon: float = -74.0060,
    vehicle_filter: str = None
) -> dict:
    """
    Optimizes collection route for scheduled bins.
    
    Compares:
    1. Static Unoptimized Route (sequential allocation order)
    2. Optimized Route (Nearest Neighbor + 2-Opt refinement)
    
    Returns route dataframes, total distances, estimated fuel, and savings percentage.
    """
    df = scheduled_df.copy()
    
    if vehicle_filter:
        df = df[df['Vehicle_ID'] == vehicle_filter].reset_index(drop=True)
    else:
        df = df[df['Dispatch_Status'] == 'Scheduled Today'].reset_index(drop=True)
        
    if df.empty:
        return {
            'optimized_df': df,
            'depot_coords': (depot_lat, depot_lon),
            'unoptimized_route_indices': [],
            'optimized_route_indices': [],
            'unoptimized_distance_km': 0.0,
            'optimized_distance_km': 0.0,
            'distance_saved_km': 0.0,
            'distance_saved_pct': 0.0,
            'fuel_saved_liters': 0.0,
            'co2_saved_kg': 0.0,
            'total_bins_routed': 0
        }
        
    # Build coordinate array including Depot at index 0
    depot_node = {'Bin_ID': 'DEPOT', 'Zone': 'Municipal Central Hub', 'Latitude': depot_lat, 'Longitude': depot_lon}
    coords = [(depot_lat, depot_lon)] + list(zip(df['Latitude'], df['Longitude']))
    
    dist_matrix = compute_distance_matrix(coords)
    
    # 1. Unoptimized baseline route: Sequential node order (1, 2, ..., N, 0)
    unoptimized_route = list(range(len(coords)))
    unoptimized_dist = route_length(unoptimized_route, dist_matrix)
    
    # 2. Optimized route using NN + 2-Opt
    nn_route = solve_nearest_neighbor(dist_matrix, start_node=0)
    opt_route = solve_2opt(nn_route, dist_matrix)
    opt_dist = route_length(opt_route, dist_matrix)
    
    # Reorder DataFrame matching optimized route sequence (excluding depot at index 0)
    opt_bin_indices = [idx - 1 for idx in opt_route if idx != 0]
    optimized_df = df.iloc[opt_bin_indices].copy().reset_index(drop=True)
    optimized_df['Collection_Order'] = range(1, len(optimized_df) + 1)
    
    saved_km = max(0.0, unoptimized_dist - opt_dist)
    saved_pct = round((saved_km / unoptimized_dist) * 100.0, 1) if unoptimized_dist > 0 else 0.0
    
    # Fuel estimation: Average waste collection truck consumes ~0.35 L per km
    fuel_saved = round(saved_km * 0.35, 1)
    co2_saved_kg = round(saved_km * 0.35 * 2.68, 1) # ~2.68 kg CO2 per liter diesel
    
    return {
        'optimized_df': optimized_df,
        'depot_coords': (depot_lat, depot_lon),
        'unoptimized_route_indices': unoptimized_route,
        'optimized_route_indices': opt_route,
        'unoptimized_distance_km': round(unoptimized_dist, 2),
        'optimized_distance_km': round(opt_dist, 2),
        'distance_saved_km': round(saved_km, 2),
        'distance_saved_pct': saved_pct,
        'fuel_saved_liters': fuel_saved,
        'co2_saved_kg': co2_saved_kg,
        'total_bins_routed': len(df)
    }
