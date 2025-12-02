#!/usr/bin/env python3
"""
Simplified test for Day 11: Product Generation
Tests the structure without requiring all dependencies
"""

import sys
from pathlib import Path

def test_product_generation_structure():
    """Test product generation structure"""
    print("=" * 60)
    print("Testing Product Generation Structure (Day 11)")
    print("=" * 60)
    
    try:
        # Test that we can parse the file
        product_file = Path(__file__).parent.parent.parent / "src" / "product_generation.py"
        with open(product_file, 'r') as f:
            code = f.read()
        
        # Check for key components
        checks = {
            "ProductGenerator class": "class ProductGenerator" in code,
            "generate_time_series method": "def generate_time_series" in code,
            "generate_uhi_indicators method": "def generate_uhi_indicators" in code,
            "export_summary_report method": "def export_summary_report" in code,
            "generate_all_products method": "def generate_all_products" in code,
            "NetCDF export": "to_netcdf" in code or "NETCDF" in code,
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
            print("✅ Product generation structure tests passed!")
            print("⚠️  Note: Full test requires numpy and xarray")
        else:
            print("❌ Some structure tests failed!")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_product_generation_structure()
    sys.exit(0 if success else 1)

