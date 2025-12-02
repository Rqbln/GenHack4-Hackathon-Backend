#!/usr/bin/env python3
"""
Simplified test for Day 5: Prithvi WxC Setup
Tests the structure without requiring model download
"""

import sys
from pathlib import Path

def test_prithvi_structure():
    """Test Prithvi WxC setup structure"""
    print("=" * 60)
    print("Testing Prithvi WxC Setup Structure (Day 5)")
    print("=" * 60)
    
    try:
        # Test that we can parse the file
        prithvi_file = Path(__file__).parent.parent.parent / "src" / "prithvi_setup.py"
        with open(prithvi_file, 'r') as f:
            code = f.read()
        
        # Check for key components
        checks = {
            "PrithviWxCSetup class": "class PrithviWxCSetup" in code,
            "download_model method": "def download_model" in code,
            "load_model method": "def load_model" in code,
            "simple_inference method": "def simple_inference" in code,
            "get_model_info method": "def get_model_info" in code,
            "MODEL_NAME constant": "MODEL_NAME" in code,
            "Hugging Face model": "ibm-granite" in code or "granite-geospatial" in code,
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
        
        # Check for transformers import handling
        if "TRANSFORMERS_AVAILABLE" in code:
            print("✅ Graceful handling of missing dependencies")
        
        print("=" * 60)
        if all_passed:
            print("✅ Prithvi WxC setup structure tests passed!")
            print("⚠️  Note: Full test requires transformers and torch")
        else:
            print("❌ Some structure tests failed!")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_prithvi_structure()
    sys.exit(0 if success else 1)

