#!/usr/bin/env python3
"""
Simplified ETL test that doesn't require all dependencies
Tests the structure and logic
"""

import sys
from pathlib import Path

def test_etl_structure():
    """Test ETL class structure without running full tests"""
    print("=" * 60)
    print("Testing ETL Pipeline Structure (Day 1)")
    print("=" * 60)
    
    try:
        # Test that we can parse the file
        etl_file = Path(__file__).parent.parent.parent / "src" / "etl.py"
        with open(etl_file, 'r') as f:
            code = f.read()
        
        # Check for key components
        checks = {
            "ETLPipeline class": "class ETLPipeline" in code,
            "load_city_boundary method": "def load_city_boundary" in code,
            "load_era5_data method": "def load_era5_data" in code,
            "load_ndvi_data method": "def load_ndvi_data" in code,
            "load_ecad_stations method": "def load_ecad_stations" in code,
            "load_ecad_station_data method": "def load_ecad_station_data" in code,
            "align_temporal method": "def align_temporal" in code,
            "save_to_zarr method": "def save_to_zarr" in code,
            "run_etl method": "def run_etl" in code,
        }
        
        all_passed = True
        for check_name, passed in checks.items():
            if passed:
                print(f"✅ {check_name} found")
            else:
                print(f"❌ {check_name} not found")
                all_passed = False
        
        # Test syntax
        import ast
        try:
            ast.parse(code)
            print("✅ Syntax is valid")
        except SyntaxError as e:
            print(f"❌ Syntax error: {e}")
            all_passed = False
        
        print("=" * 60)
        if all_passed:
            print("✅ ETL structure tests passed!")
        else:
            print("❌ Some structure tests failed!")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_etl_structure()
    sys.exit(0 if success else 1)

