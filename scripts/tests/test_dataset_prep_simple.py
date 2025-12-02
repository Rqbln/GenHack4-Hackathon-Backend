#!/usr/bin/env python3
"""
Simplified test for Day 6: Dataset Preparation
Tests the structure without requiring all dependencies
"""

import sys
from pathlib import Path

def test_dataset_prep_structure():
    """Test dataset preparation structure"""
    print("=" * 60)
    print("Testing Dataset Preparation Structure (Day 6)")
    print("=" * 60)
    
    try:
        # Test that we can parse the file
        dataset_file = Path(__file__).parent.parent.parent / "src" / "dataset_preparation.py"
        with open(dataset_file, 'r') as f:
            code = f.read()
        
        # Check for key components
        checks = {
            "FineTuningDataset class": "class FineTuningDataset" in code,
            "create_training_pairs method": "def create_training_pairs" in code,
            "save_dataset method": "def save_dataset" in code,
            "load_dataset method": "def load_dataset" in code,
            "split_dataset method": "_split_dataset" in code,
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
            print("✅ Dataset preparation structure tests passed!")
        else:
            print("❌ Some structure tests failed!")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_dataset_prep_structure()
    sys.exit(0 if success else 1)

