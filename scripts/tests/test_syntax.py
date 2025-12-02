#!/usr/bin/env python3
"""
Syntax and import validation tests
Tests that code compiles and basic structure is correct
"""

import sys
import ast
from pathlib import Path

def test_syntax(file_path):
    """Test that a Python file has valid syntax"""
    try:
        with open(file_path, 'r') as f:
            source = f.read()
        ast.parse(source)
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def test_imports():
    """Test that modules can be imported (may fail if deps missing, but syntax should be OK)"""
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    results = {}
    
    # Test ETL module
    try:
        # Just check syntax, don't actually import (deps may be missing)
        etl_file = project_root / "src" / "etl.py"
        success, error = test_syntax(etl_file)
        results["etl.py"] = (success, error)
    except Exception as e:
        results["etl.py"] = (False, str(e))
    
    # Test gap_filling module
    try:
        gap_file = project_root / "src" / "gap_filling.py"
        success, error = test_syntax(gap_file)
        results["gap_filling.py"] = (success, error)
    except Exception as e:
        results["gap_filling.py"] = (False, str(e))
    
    # Test baseline module
    try:
        baseline_file = project_root / "src" / "baseline.py"
        success, error = test_syntax(baseline_file)
        results["baseline.py"] = (success, error)
    except Exception as e:
        results["baseline.py"] = (False, str(e))
    
    # Test GADM indicators module
    try:
        gadm_file = project_root / "src" / "gadm_indicators.py"
        success, error = test_syntax(gadm_file)
        results["gadm_indicators.py"] = (success, error)
    except Exception as e:
        results["gadm_indicators.py"] = (False, str(e))
    
    # Test Prithvi setup module
    try:
        prithvi_file = project_root / "src" / "prithvi_setup.py"
        success, error = test_syntax(prithvi_file)
        results["prithvi_setup.py"] = (success, error)
    except Exception as e:
        results["prithvi_setup.py"] = (False, str(e))
    
    # Test dataset preparation module
    try:
        dataset_file = project_root / "src" / "dataset_preparation.py"
        success, error = test_syntax(dataset_file)
        results["dataset_preparation.py"] = (success, error)
    except Exception as e:
        results["dataset_preparation.py"] = (False, str(e))
    
    # Test fine-tuning module
    try:
        finetuning_file = project_root / "src" / "finetuning.py"
        success, error = test_syntax(finetuning_file)
        results["finetuning.py"] = (success, error)
    except Exception as e:
        results["finetuning.py"] = (False, str(e))
    
    # Test model analysis module
    try:
        analysis_file = project_root / "src" / "model_analysis.py"
        success, error = test_syntax(analysis_file)
        results["model_analysis.py"] = (success, error)
    except Exception as e:
        results["model_analysis.py"] = (False, str(e))
    
    # Test advanced metrics module
    try:
        metrics_file = project_root / "src" / "advanced_metrics.py"
        success, error = test_syntax(metrics_file)
        results["advanced_metrics.py"] = (success, error)
    except Exception as e:
        results["advanced_metrics.py"] = (False, str(e))
    
    # Test product generation module
    try:
        product_file = project_root / "src" / "product_generation.py"
        success, error = test_syntax(product_file)
        results["product_generation.py"] = (success, error)
    except Exception as e:
        results["product_generation.py"] = (False, str(e))
    
    # Test physics validation module
    try:
        physics_file = project_root / "src" / "physics_validation.py"
        success, error = test_syntax(physics_file)
        results["physics_validation.py"] = (success, error)
    except Exception as e:
        results["physics_validation.py"] = (False, str(e))
    
    return results

def main():
    print("=" * 60)
    print("Syntax and Structure Validation")
    print("=" * 60)
    
    results = test_imports()
    
    all_passed = True
    for module, (success, error) in results.items():
        if success:
            print(f"✅ {module} - Syntax OK")
        else:
            print(f"❌ {module} - Syntax Error: {error}")
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("✅ All syntax checks passed!")
        return 0
    else:
        print("❌ Some syntax checks failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())

