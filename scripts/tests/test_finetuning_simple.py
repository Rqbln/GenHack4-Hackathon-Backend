#!/usr/bin/env python3
"""
Simplified test for Day 8: Fine-Tuning Prithvi WxC
Tests the structure without requiring model download
"""

import sys
from pathlib import Path

def test_finetuning_structure():
    """Test fine-tuning structure"""
    print("=" * 60)
    print("Testing Fine-Tuning Structure (Day 8)")
    print("=" * 60)
    
    try:
        # Test that we can parse the file
        finetuning_file = Path(__file__).parent.parent.parent / "src" / "finetuning.py"
        with open(finetuning_file, 'r') as f:
            code = f.read()
        
        # Check for key components
        checks = {
            "PrithviFineTuner class": "class PrithviFineTuner" in code,
            "setup_model method": "def setup_model" in code,
            "create_composite_loss method": "def create_composite_loss" in code,
            "train method": "def train" in code,
            "QLoRA": "LoraConfig" in code or "LoRA" in code,
            "composite loss": "composite_loss" in code or "pixel_weight" in code,
            "PINN loss": "pinn" in code.lower() or "physics" in code.lower(),
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
            print("✅ Fine-tuning structure tests passed!")
            print("⚠️  Note: Full test requires transformers, peft, and torch")
        else:
            print("❌ Some structure tests failed!")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_finetuning_structure()
    sys.exit(0 if success else 1)

