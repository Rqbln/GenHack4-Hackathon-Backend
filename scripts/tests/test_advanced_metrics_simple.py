#!/usr/bin/env python3
"""
Simplified test for Day 10: Advanced Metrics
Tests the structure without requiring all dependencies
"""

import sys
from pathlib import Path

def test_advanced_metrics_structure():
    """Test advanced metrics structure"""
    print("=" * 60)
    print("Testing Advanced Metrics Structure (Day 10)")
    print("=" * 60)
    
    try:
        # Test that we can parse the file
        metrics_file = Path(__file__).parent.parent.parent / "src" / "advanced_metrics.py"
        with open(metrics_file, 'r') as f:
            code = f.read()
        
        # Check for key components
        checks = {
            "AdvancedMetrics class": "class AdvancedMetrics" in code,
            "perkins_skill_score method": "def perkins_skill_score" in code,
            "spectral_analysis method": "def spectral_analysis" in code,
            "compare_with_baseline method": "def compare_with_baseline" in code,
            "calculate_all_metrics method": "def calculate_all_metrics" in code,
            "Perkins Score formula": "min(Z_pred" in code or "minimum" in code,
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
            print("✅ Advanced metrics structure tests passed!")
            print("⚠️  Note: Full test requires scipy")
        else:
            print("❌ Some structure tests failed!")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_advanced_metrics_structure()
    sys.exit(0 if success else 1)

