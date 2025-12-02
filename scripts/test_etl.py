#!/usr/bin/env python3
"""
Test script for ETL Pipeline
Run this to verify the ETL pipeline works with the downloaded datasets
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.etl import ETLPipeline
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    # Paths relative to project root
    project_root = Path(__file__).parent.parent.parent
    datasets_dir = project_root / "datasets"
    
    print("=" * 60)
    print("ETL Pipeline Test")
    print("=" * 60)
    print(f"Project root: {project_root}")
    print(f"Datasets dir: {datasets_dir}")
    print()
    
    # Initialize ETL pipeline
    etl = ETLPipeline(
        era5_dir=datasets_dir / "main" / "derived-era5-land-daily-statistics",
        sentinel2_dir=datasets_dir / "main" / "sentinel2_ndvi",
        ecad_zip=datasets_dir / "ECA_blend_tx.zip",
        gadm_gpkg=datasets_dir / "gadm_410_europe.gpkg",
        output_dir=datasets_dir / "processed",
        city_name="Paris",
        country_code="FRA"
    )
    
    # Run ETL (test with 2020 only for speed)
    print("Running ETL pipeline...")
    try:
        results = etl.run_etl(
            years=[2020],  # Start with one year for testing
            variables=["t2m_max", "precipitation"],  # Test with 2 variables
            output_format="zarr"
        )
        
        print("\n" + "=" * 60)
        print("✅ ETL Pipeline completed successfully!")
        print("=" * 60)
        print(f"\nOutput directory: {etl.output_dir}")
        print(f"Files created:")
        for file in etl.output_dir.glob("*"):
            print(f"  - {file.name}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

