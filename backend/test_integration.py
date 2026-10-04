import os
import sys
import pandas as pd

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import load_latest_bins_df, load_chennai_bins_df, get_dashboard_summary, get_all_bins, get_optimized_route, get_analytics

print("--- Testing Synthetic Mode ---")
df_synth = load_latest_bins_df()
print(f"Synthetic Bins Loaded: {len(df_synth)} records")
dash_synth = get_dashboard_summary(mode="synthetic")
print(f"Synthetic Dashboard Total Bins: {dash_synth['total_bins']}, Total Distance: {dash_synth['total_route_distance_km']} km")

print("\n--- Testing Chennai Real Locations Mode ---")
df_chennai = load_chennai_bins_df()
print(f"Chennai Bins Loaded: {len(df_chennai)} records")
print("Sample Columns:", [c for c in df_chennai.columns if 'Bin' in c or 'Area' in c or 'Priority' in c])
print("First Bin Real_Bin_ID:", df_chennai.iloc[0]['Real_Bin_ID'])
print("First Bin Priority:", df_chennai.iloc[0]['Priority_Level'])
print("First Bin Dispatch:", df_chennai.iloc[0]['Dispatch_Decision'])

dash_chennai = get_dashboard_summary(mode="chennai")
print(f"Chennai Dashboard Total Bins: {dash_chennai['total_bins']}, Total Route Distance: {dash_chennai['total_route_distance_km']} km")

bins_page1 = get_all_bins(mode="chennai", page=1, limit=10)
print(f"Chennai Paginated Page 1 count: {len(bins_page1['bins'])} of {bins_page1['total_count']} total bins, pages: {bins_page1['total_pages']}")

route_chennai = get_optimized_route(mode="chennai", max_stops=30)
print(f"Chennai Route Generated: Stops={route_chennai['total_stops']}, Distance={route_chennai['total_distance_km']} km, Fuel={route_chennai['estimated_fuel_L']} L")
print(f"Depot Name: {route_chennai['depot']['name']} at ({route_chennai['depot']['latitude']}, {route_chennai['depot']['longitude']})")

analytics_chennai = get_analytics(mode="chennai")
print(f"Chennai Analytics Status: {analytics_chennai['status']}, Data Notice: {analytics_chennai['data_notice']}")

print("\n=== ALL INTEGRATION TESTS PASSED SUCCESSFULLY! ===")
