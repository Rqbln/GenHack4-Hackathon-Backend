#!/usr/bin/env python3
"""
Simplified test for Day 9: Model Analysis
Tests the structure without requiring all dependencies
"""

import sys
from pathlib import Path

def test_model_analysis_structure():
    """Test model analysis structure"""
    print("=" * 60)
    print("Testing Model Analysis Structure (Day 9)")
    print("=" * 60)
    
    try:
        # Test that we can parse the file
        analysis_file = Path(__file__).parent.parent.parent / "src" / "model_analysis.py"
        with open(analysis_file, 'r') as f:
            code = f.read()
        
        # Check for key components
        checks = {
            "ModelAnalyzer class": "class ModelAnalyzer" in code,
            "analyze_training_history method": "def analyze_training_history" in code,
            "spatial_cross_validation method": "def spatial_cross_validation" in code,
            "hyperparameter_sensitivity method": "def hyperparameter_sensitivity" in code,
            "convergence detection": "_detect_convergence" in code,
            "overfitting detection": "_detect_overfitting" in code,
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
            print("✅ Model analysis structure tests passed!")
        else:
            print("❌ Some structure tests failed!")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_model_analysis_structure()
    sys.exit(0 if success else 1)

