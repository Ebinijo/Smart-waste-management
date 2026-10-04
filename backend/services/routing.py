"""
Route Optimization Service using NetworkX and Dijkstra's Shortest Path Algorithm.
Generates connected graph from geographic coordinates and routes trucks efficiently across high/medium priority bins.
"""

import math
import networkx as nx

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates geographic distance in kilometers between two lat/lon pairs using Haversine formula.
    """
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def generate_dijkstra_route(
    bins_list: list, 
    depot_lat: float = 37.7749, 
    depot_lon: float = -122.4194,
    depot_name: str = "Simulation Depot",
    max_stops: int = 30
) -> dict:
    """
    Builds a connected NetworkX graph between collection bins and Depot, then uses Dijkstra's algorithm
    to sequence collection stops prioritizing High Priority bins followed by Medium Priority bins.
    Limits stops to max_stops for computational efficiency.
    """
    # Filter bins requiring collection
    collection_bins = [
        b for b in bins_list
        if b.get("Dispatch_Decision") in ["Dispatch Immediately", "Schedule Collection"] or b.get("Collection_Required") is True
    ]
    
    # Sort collection target bins by priority score desc, then predicted fill desc
    prio_score_map = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    collection_bins.sort(
        key=lambda x: (
            prio_score_map.get(str(x.get("Priority_Level", "MEDIUM")).upper(), 1),
            float(x.get("Next_Fill_Level_Percent", x.get("Fill_Level_Percent", 0)))
        ),
        reverse=True
    )
    
    # Cap to max_stops if specified
    if max_stops and max_stops > 0 and len(collection_bins) > max_stops:
        collection_bins = collection_bins[:max_stops]

    # If no bins require collection, return empty route from depot
    if not collection_bins:
        return {
            "depot": {
                "id": "DEPOT",
                "name": depot_name,
                "latitude": depot_lat,
                "longitude": depot_lon
            },
            "stops": [],
            "route_path": [[depot_lat, depot_lon]],
            "total_distance_km": 0.0,
            "total_stops": 0,
            "high_priority_stops": 0,
            "medium_priority_stops": 0,
            "estimated_fuel_L": 0.0,
            "fuel_label": "Estimated Fuel — Simulation Assumption"
        }

    # Construct Depot node and Bin nodes
    depot_node = {
        "id": "DEPOT",
        "name": depot_name,
        "latitude": depot_lat,
        "longitude": depot_lon,
        "Priority_Level": "DEPOT",
        "Dispatch_Decision": "DEPOT"
    }

    nodes = [depot_node] + collection_bins
    node_map = {}
    for n in nodes:
        nid = str(n.get("Bin_ID", n.get("id")))
        node_map[nid] = n

    # Build fully connected NetworkX graph where edges are Haversine distances
    G = nx.Graph()
    for n in nodes:
        nid = str(n.get("Bin_ID", n.get("id")))
        G.add_node(nid, lat=float(n.get("Latitude", depot_lat)), lon=float(n.get("Longitude", depot_lon)))

    node_ids = list(G.nodes)
    for i in range(len(node_ids)):
        for j in range(i + 1, len(node_ids)):
            u, v = node_ids[i], node_ids[j]
            lat1, lon1 = G.nodes[u]["lat"], G.nodes[u]["lon"]
            lat2, lon2 = G.nodes[v]["lat"], G.nodes[v]["lon"]
            dist = haversine_distance(lat1, lon1, lat2, lon2)
            G.add_edge(u, v, weight=dist)

    # Separate collection target bin IDs into priority tiers
    high_bins = [
        str(b["Bin_ID"]) for b in collection_bins
        if b.get("Priority_Level") == "HIGH" or b.get("Dispatch_Decision") == "Dispatch Immediately"
    ]
    med_bins = [
        str(b["Bin_ID"]) for b in collection_bins
        if str(b["Bin_ID"]) not in high_bins
    ]

    # Run Dijkstra TSP traversal: Depot -> High Priority bins -> Medium Priority bins -> Depot
    route_sequence = ["DEPOT"]
    current_loc = "DEPOT"
    unvisited_high = set(high_bins)
    unvisited_med = set(med_bins)
    total_dist = 0.0

    # 1. Visit High Priority Bins
    while unvisited_high:
        nearest_bin = None
        min_dist = float("inf")
        
        for target in unvisited_high:
            if not nx.has_path(G, current_loc, target):
                continue
            try:
                length = nx.dijkstra_path_length(G, current_loc, target, weight="weight")
                if length < min_dist:
                    min_dist = length
                    nearest_bin = target
            except nx.NetworkXNoPath:
                continue

        if nearest_bin is None:
            break

        total_dist += min_dist
        route_sequence.append(nearest_bin)
        unvisited_high.remove(nearest_bin)
        current_loc = nearest_bin

    # 2. Visit Medium Priority Bins
    while unvisited_med:
        nearest_bin = None
        min_dist = float("inf")
        
        for target in unvisited_med:
            if not nx.has_path(G, current_loc, target):
                continue
            try:
                length = nx.dijkstra_path_length(G, current_loc, target, weight="weight")
                if length < min_dist:
                    min_dist = length
                    nearest_bin = target
            except nx.NetworkXNoPath:
                continue

        if nearest_bin is None:
            break

        total_dist += min_dist
        route_sequence.append(nearest_bin)
        unvisited_med.remove(nearest_bin)
        current_loc = nearest_bin

    # 3. Return to Depot via Dijkstra
    if current_loc != "DEPOT":
        if nx.has_path(G, current_loc, "DEPOT"):
            return_dist = nx.dijkstra_path_length(G, current_loc, "DEPOT", weight="weight")
            total_dist += return_dist
            route_sequence.append("DEPOT")

    # Formulate output stops and coordinates path
    stops_output = []
    path_coords = []
    step_count = 1

    for step_idx, nid in enumerate(route_sequence):
        info = node_map.get(nid, {})
        lat = float(info.get("Latitude", depot_lat))
        lon = float(info.get("Longitude", depot_lon))
        path_coords.append([lat, lon])

        if nid != "DEPOT":
            prev_nid = route_sequence[step_idx - 1]
            prev_info = node_map.get(prev_nid, {})
            prev_lat = float(prev_info.get("Latitude", depot_lat))
            prev_lon = float(prev_info.get("Longitude", depot_lon))
            leg_dist = round(haversine_distance(prev_lat, prev_lon, lat, lon), 2)

            stops_output.append({
                "step": step_count,
                "bin_id": nid,
                "real_bin_id": info.get("Real_Bin_ID", nid),
                "zone": info.get("Zone", info.get("Area_Name", "N/A")),
                "division": info.get("Division_Code", "N/A"),
                "area": info.get("Area_Name", "N/A"),
                "location": info.get("Location_Name", "N/A"),
                "street": info.get("Street_Name", "N/A"),
                "waste_type": info.get("Waste_Type", info.get("Bin_Type", "General Waste")),
                "current_fill": info.get("Fill_Level_Percent", 0),
                "predicted_fill": info.get("Next_Fill_Level_Percent", 0),
                "priority": info.get("Priority_Level", "MEDIUM"),
                "dispatch_decision": info.get("Dispatch_Decision", "Schedule Collection"),
                "latitude": lat,
                "longitude": lon,
                "distance_from_prev_km": leg_dist
            })
            step_count += 1

    # Fuel formula: 0.30 L/km + 0.05 L/stop
    total_stops = len(stops_output)
    est_fuel = round(total_dist * 0.30 + total_stops * 0.05, 2)

    return {
        "depot": {
            "id": "DEPOT",
            "name": depot_name,
            "latitude": depot_lat,
            "longitude": depot_lon
        },
        "stops": stops_output,
        "route_path": path_coords,
        "total_distance_km": round(total_dist, 2),
        "total_stops": total_stops,
        "high_priority_stops": len([s for s in stops_output if s["priority"] == "HIGH"]),
        "medium_priority_stops": len([s for s in stops_output if s["priority"] == "MEDIUM"]),
        "estimated_fuel_L": est_fuel,
        "fuel_label": "Estimated Fuel — Simulation Assumption"
    }

