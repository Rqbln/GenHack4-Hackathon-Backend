#!/usr/bin/env python3
"""
Script pour charger plus de stations ECA&D autour de Paris
Élargit la zone de recherche pour trouver plus de stations
"""

import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

import geopandas as gpd
import pandas as pd
import numpy as np
from io import StringIO
import zipfile
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_all_ecad_stations(ecad_zip_path: Path) -> gpd.GeoDataFrame:
    """Load all ECA&D stations"""
    logger.info("Loading all ECA&D stations...")
    
    def dms_to_decimal(dms_str):
        if pd.isna(dms_str) or dms_str == '':
            return np.nan
        dms_str = str(dms_str).strip()
        if dms_str[0] in ['+', '-']:
            sign = 1 if dms_str[0] == '+' else -1
            parts = dms_str[1:].split(':')
        else:
            sign = 1
            parts = dms_str.split(':')
        
        if len(parts) != 3:
            return np.nan
        
        try:
            return sign * (float(parts[0]) + float(parts[1])/60 + float(parts[2])/3600)
        except:
            return np.nan
    
    with zipfile.ZipFile(ecad_zip_path) as z:
        stations_content = z.read('stations.txt').decode('utf-8', errors='ignore')
        stations_df = pd.read_csv(
            StringIO(stations_content),
            skiprows=17,
            skipinitialspace=True
        )
        
        stations_df['LAT_decimal'] = stations_df['LAT'].apply(dms_to_decimal)
        stations_df['LON_decimal'] = stations_df['LON'].apply(dms_to_decimal)
        stations_df = stations_df.dropna(subset=['LAT_decimal', 'LON_decimal'])
        
        stations_gdf = gpd.GeoDataFrame(
            stations_df,
            geometry=gpd.points_from_xy(
                stations_df['LON_decimal'],
                stations_df['LAT_decimal']
            ),
            crs="EPSG:4326"
        )
    
    logger.info(f"Loaded {len(stations_gdf)} total stations")
    return stations_gdf


def filter_stations_near_paris(stations_gdf: gpd.GeoDataFrame, radius_km: float = 50) -> gpd.GeoDataFrame:
    """Filter stations within radius_km of Paris center"""
    paris_center = (2.3522, 48.8566)  # Longitude, Latitude
    
    # Convert radius from km to degrees (approximate)
    # 1 degree latitude ≈ 111 km, longitude varies by latitude
    radius_deg_lat = radius_km / 111.0
    radius_deg_lon = radius_km / (111.0 * np.cos(np.radians(paris_center[1])))
    
    # Simple bounding box filter first (faster)
    lon_min = paris_center[0] - radius_deg_lon
    lon_max = paris_center[0] + radius_deg_lon
    lat_min = paris_center[1] - radius_deg_lat
    lat_max = paris_center[1] + radius_deg_lat
    
    filtered = stations_gdf[
        (stations_gdf['LON_decimal'] >= lon_min) &
        (stations_gdf['LON_decimal'] <= lon_max) &
        (stations_gdf['LAT_decimal'] >= lat_min) &
        (stations_gdf['LAT_decimal'] <= lat_max)
    ]
    
    # Also filter by country code (France)
    filtered = filtered[filtered['CN'].str.strip() == 'FR']
    
    logger.info(f"Found {len(filtered)} stations within {radius_km}km of Paris (France only)")
    return filtered


def main():
    project_root = Path(__file__).parent.parent
    base_dir = project_root.parent / "datasets"
    output_dir = project_root / "data" / "processed"
    
    ecad_zip = base_dir / "ECA_blend_tx.zip"
    if not ecad_zip.exists():
        logger.error(f"ECA&D ZIP not found: {ecad_zip}")
        return 1
    
    # Load all stations
    all_stations = load_all_ecad_stations(ecad_zip)
    
    # Filter stations near Paris (try different radii)
    paris_stations = filter_stations_near_paris(all_stations, radius_km=100)
    
    if len(paris_stations) < 5:
        logger.warning(f"Only {len(paris_stations)} stations found. Trying larger radius...")
        paris_stations = filter_stations_near_paris(all_stations, radius_km=200)
    
    # If still not enough, add some known Paris stations manually
    if len(paris_stations) < 3:
        logger.info("Adding known Paris stations manually...")
        known_stations = [
            {"STAID": 1, "STANAME": "Paris Montsouris", "CN": "FR", "LAT_decimal": 48.8222, "LON_decimal": 2.3364, "HGHT": 75},
            {"STAID": 2, "STANAME": "Paris Orly", "CN": "FR", "LAT_decimal": 48.7233, "LON_decimal": 2.3794, "HGHT": 89},
            {"STAID": 3, "STANAME": "Paris Le Bourget", "CN": "FR", "LAT_decimal": 48.9694, "LON_decimal": 2.4414, "HGHT": 66},
        ]
        
        known_gdf = gpd.GeoDataFrame(
            known_stations,
            geometry=gpd.points_from_xy(
                [s["LON_decimal"] for s in known_stations],
                [s["LAT_decimal"] for s in known_stations]
            ),
            crs="EPSG:4326"
        )
        
        # Add columns to match existing structure
        for col in ['STAID', 'STANAME', 'CN', 'LAT_decimal', 'LON_decimal', 'HGHT']:
            if col not in known_gdf.columns:
                known_gdf[col] = [s.get(col, 0) for s in known_stations]
        
        paris_stations = pd.concat([paris_stations, known_gdf], ignore_index=True)
        logger.info(f"Added {len(known_stations)} known stations. Total: {len(paris_stations)}")
    
    # Save to GeoJSON
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "stations.geojson"
    
    # Convert to format expected by API
    features = []
    for idx, row in paris_stations.iterrows():
        features.append({
            "type": "Feature",
            "properties": {
                "STAID": int(row.get('STAID', idx)),
                "STANAME": str(row.get('STANAME', f"Station {idx}")),
                "CN": str(row.get('CN', 'FRA')),
                "HGHT": float(row.get('HGHT', 0)) if pd.notna(row.get('HGHT')) else 0
            },
            "geometry": {
                "type": "Point",
                "coordinates": [float(row['LON_decimal']), float(row['LAT_decimal'])]
            }
        })
    
    geojson = {
        "type": "FeatureCollection",
        "name": "stations",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "features": features
    }
    
    with open(output_path, 'w') as f:
        json.dump(geojson, f, indent=2)
    
    logger.info(f"✅ Saved {len(paris_stations)} stations to {output_path}")
    
    # Print sample
    logger.info("\n📊 Sample stations:")
    for i, row in paris_stations.head(5).iterrows():
        logger.info(f"  - {row.get('STANAME', 'Unknown')}: ({row['LAT_decimal']:.4f}, {row['LON_decimal']:.4f})")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

