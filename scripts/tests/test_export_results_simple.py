#!/usr/bin/env python3
"""
Simplified test for Day 13: Export Results
Tests the structure without requiring all dependencies
"""

import sys
from pathlib import Path

def test_export_results_structure():
    """Test export results structure"""
    print("=" * 60)
    print("Testing Export Results Structure (Day 13)")
    print("=" * 60)
    
    try:
        # Test that we can parse the file
        export_file = Path(__file__).parent.parent.parent / "src" / "export_results.py"
        with open(export_file, 'r') as f:
            code = f.read()
        
        # Check for key components
        checks = {
            "ResultsExporter class": "class ResultsExporter" in code,
            "export_metrics_table method": "def export_metrics_table" in code,
            "plot_metrics_comparison method": "def plot_metrics_comparison" in code,
            "plot_training_history method": "def plot_training_history" in code,
            "export_summary_report method": "def export_summary_report" in code,
            "export_all method": "def export_all" in code,
            "JSON export": "json.dump" in code,
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
            print("✅ Export results structure tests passed!")
            print("⚠️  Note: Full test requires matplotlib")
        else:
            print("❌ Some structure tests failed!")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_export_results_structure()
    sys.exit(0 if success else 1)

