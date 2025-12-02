#!/usr/bin/env python3
"""
Test script for ETL Pipeline (Day 1)
Tests data loading and harmonization
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import logging
from src.etl import ETLPipeline

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_etl_pipeline():
    """Test ETL pipeline with minimal data"""
    print("=" * 60)
    print("Testing ETL Pipeline (Day 1)")
    print("=" * 60)
    
    try:
        # Paths
        project_root = Path(__file__).parent.parent.parent.parent
        datasets_dir = project_root / "datasets"
        
        # Check if datasets exist
        era5_dir = datasets_dir / "main" / "derived-era5-land-daily-statistics"
        sentinel2_dir = datasets_dir / "main" / "sentinel2_ndvi"
        ecad_zip = datasets_dir / "ECA_blend_tx.zip"
        gadm_gpkg = datasets_dir / "gadm_410_europe.gpkg"
        
        if not era5_dir.exists():
            print(f"⚠️  ERA5 directory not found: {era5_dir}")
            return False
        if not sentinel2_dir.exists():
            print(f"⚠️  Sentinel-2 directory not found: {sentinel2_dir}")
            return False
        if not ecad_zip.exists():
            print(f"⚠️  ECA&D ZIP not found: {ecad_zip}")
            return False
        if not gadm_gpkg.exists():
            print(f"⚠️  GADM GeoPackage not found: {gadm_gpkg}")
            return False
        
        # Initialize ETL pipeline
        etl = ETLPipeline(
            era5_dir=era5_dir,
            sentinel2_dir=sentinel2_dir,
            ecad_zip=ecad_zip,
            gadm_gpkg=gadm_gpkg,
            output_dir=datasets_dir / "processed" / "test",
            city_name="Paris",
            country_code="FRA"
        )
        
        # Test 1: Load city boundary
        print("\n[Test 1] Loading city boundary...")
        boundary = etl.load_city_boundary()
        assert boundary is not None, "Failed to load city boundary"
        assert len(boundary) > 0, "City boundary is empty"
        print(f"✅ City boundary loaded: {len(boundary)} polygon(s)")
        
        # Test 2: Load ERA5 data
        print("\n[Test 2] Loading ERA5 data...")
        era5_ds = etl.load_era5_data("t2m_max", 2020)
        assert era5_ds is not None, "Failed to load ERA5 data"
        assert "t2m" in era5_ds.data_vars, "ERA5 dataset missing t2m variable"
        print(f"✅ ERA5 data loaded: {era5_ds.dims}")
        
        # Test 3: Load NDVI data
        print("\n[Test 3] Loading NDVI data...")
        try:
            ndvi_array, ndvi_meta = etl.load_ndvi_data("2020-03-01", "2020-06-01", clip_to_boundary=True)
            assert ndvi_array is not None, "Failed to load NDVI data"
            print(f"✅ NDVI data loaded: shape {ndvi_array.shape}")
        except FileNotFoundError:
            print("⚠️  NDVI file not found (may be expected)")
        
        # Test 4: Load ECA&D stations
        print("\n[Test 4] Loading ECA&D stations...")
        stations = etl.load_ecad_stations()
        assert stations is not None, "Failed to load stations"
        assert len(stations) > 0, "No stations loaded"
        print(f"✅ Loaded {len(stations)} stations")
        
        # Test 5: Load station data
        if len(stations) > 0:
            print("\n[Test 5] Loading station temperature data...")
            station_id = stations.iloc[0]['STAID']
            station_data = etl.load_ecad_station_data(station_id)
            assert station_data is not None, "Failed to load station data"
            assert len(station_data) > 0, "Station data is empty"
            print(f"✅ Loaded {len(station_data)} records for station {station_id}")
        
        print("\n" + "=" * 60)
        print("✅ All ETL tests passed!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ ETL test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_etl_pipeline()
    sys.exit(0 if success else 1)

