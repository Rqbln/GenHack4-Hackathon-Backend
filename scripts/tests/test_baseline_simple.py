#!/usr/bin/env python3
"""
Simplified baseline test that doesn't require all dependencies
Tests the logic with minimal imports
"""

import sys
from pathlib import Path

def test_baseline_structure():
    """Test baseline class structure without running full tests"""
    print("=" * 60)
    print("Testing Baseline Model Structure (Day 3)")
    print("=" * 60)
    
    try:
        # Test that we can parse the file
        baseline_file = Path(__file__).parent.parent.parent / "src" / "baseline.py"
        with open(baseline_file, 'r') as f:
            code = f.read()
        
        # Check for key components
        checks = {
            "BaselineDownscaler class": "class BaselineDownscaler" in code,
            "bicubic_interpolation method": "def bicubic_interpolation" in code,
            "altitude_correction method": "def altitude_correction" in code,
            "calculate_rmse method": "def calculate_rmse" in code,
            "calculate_mae method": "def calculate_mae" in code,
            "calculate_r2 method": "def calculate_r2" in code,
            "evaluate_baseline method": "def evaluate_baseline" in code,
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
            print("✅ Baseline structure tests passed!")
        else:
            print("❌ Some structure tests failed!")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_baseline_structure()
    sys.exit(0 if success else 1)

