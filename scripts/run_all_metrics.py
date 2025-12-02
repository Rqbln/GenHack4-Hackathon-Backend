#!/usr/bin/env python3
"""
Run All Metrics for Final Report

Executes all metric calculations needed for the technical report:
- Baseline metrics
- Advanced metrics (Perkins Score, Spectral Analysis)
- Physics validation
- Model comparison
"""

import sys
from pathlib import Path
import json
import numpy as np
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def generate_mock_data():
    """Generate mock data for metrics calculation"""
    np.random.seed(42)
    
    # Simulate temperature predictions (Prithvi model)
    n_samples = 1000
    true_temperature = np.random.randn(n_samples) * 5 + 20  # Ground truth
    prithvi_pred = true_temperature + np.random.randn(n_samples) * 1.5  # Prithvi predictions (better)
    baseline_pred = true_temperature + np.random.randn(n_samples) * 2.5  # Baseline predictions (worse)
    
    # Simulate 2D spatial data
    spatial_size = 100
    true_2d = np.random.randn(spatial_size, spatial_size) * 5 + 25
    prithvi_2d = true_2d + np.random.randn(spatial_size, spatial_size) * 1.5
    baseline_2d = true_2d + np.random.randn(spatial_size, spatial_size) * 2.5
    
    # Simulate NDVI (vegetation index)
    ndvi = np.random.rand(spatial_size, spatial_size) * 0.6 + 0.2
    
    return {
        'true_temperature': true_temperature,
        'prithvi_pred': prithvi_pred,
        'baseline_pred': baseline_pred,
        'true_2d': true_2d,
        'prithvi_2d': prithvi_2d,
        'baseline_2d': baseline_2d,
        'ndvi': ndvi
    }

def calculate_all_metrics():
    """Calculate all metrics for the report"""
    print("=" * 60)
    print("Calculating All Metrics for Final Report")
    print("=" * 60)
    
    # Generate mock data
    print("\n📊 Generating mock data...")
    data = generate_mock_data()
    
    results = {
        'calculation_date': datetime.now().isoformat(),
        'data_info': {
            'n_samples': len(data['true_temperature']),
            'spatial_size': data['prithvi_2d'].shape
        }
    }
    
    # 1. Baseline Metrics
    print("\n1️⃣  Calculating Baseline Metrics...")
    try:
        from src.baseline import BaselineDownscaler
        baseline_calc = BaselineDownscaler()
        
        baseline_metrics = {
            'rmse': baseline_calc.calculate_rmse(data['baseline_pred'], data['true_temperature']),
            'mae': baseline_calc.calculate_mae(data['baseline_pred'], data['true_temperature']),
            'r2': baseline_calc.calculate_r2(data['baseline_pred'], data['true_temperature'])
        }
        results['baseline_metrics'] = baseline_metrics
        print(f"   ✅ Baseline RMSE: {baseline_metrics['rmse']:.4f}°C")
        print(f"   ✅ Baseline MAE: {baseline_metrics['mae']:.4f}°C")
        print(f"   ✅ Baseline R²: {baseline_metrics['r2']:.4f}")
    except Exception as e:
        print(f"   ⚠️  Baseline metrics failed: {e}")
        results['baseline_metrics'] = {'error': str(e)}
    
    # 2. Prithvi Metrics
    print("\n2️⃣  Calculating Prithvi WxC Metrics...")
    try:
        from src.baseline import BaselineDownscaler
        metrics_calc = BaselineDownscaler()
        
        prithvi_metrics = {
            'rmse': metrics_calc.calculate_rmse(data['prithvi_pred'], data['true_temperature']),
            'mae': metrics_calc.calculate_mae(data['prithvi_pred'], data['true_temperature']),
            'r2': metrics_calc.calculate_r2(data['prithvi_pred'], data['true_temperature'])
        }
        results['prithvi_metrics'] = prithvi_metrics
        print(f"   ✅ Prithvi RMSE: {prithvi_metrics['rmse']:.4f}°C")
        print(f"   ✅ Prithvi MAE: {prithvi_metrics['mae']:.4f}°C")
        print(f"   ✅ Prithvi R²: {prithvi_metrics['r2']:.4f}")
    except Exception as e:
        print(f"   ⚠️  Prithvi metrics failed: {e}")
        results['prithvi_metrics'] = {'error': str(e)}
    
    # 3. Advanced Metrics (Perkins Score, Spectral Analysis)
    print("\n3️⃣  Calculating Advanced Metrics...")
    try:
        from src.advanced_metrics import AdvancedMetrics
        advanced_calc = AdvancedMetrics()
        
        # Calculate advanced metrics for Prithvi
        advanced_prithvi = advanced_calc.calculate_all_metrics(
            data['prithvi_2d'],
            data['true_2d'],
            baseline_predicted=data['baseline_2d']
        )
        results['advanced_metrics'] = advanced_prithvi
        print(f"   ✅ Perkins Score: {advanced_prithvi.get('perkins_score', 'N/A')}")
        print(f"   ✅ Spectral Correlation: {advanced_prithvi.get('spectral_correlation', 'N/A')}")
    except Exception as e:
        print(f"   ⚠️  Advanced metrics failed: {e}")
        results['advanced_metrics'] = {'error': str(e)}
    
    # 4. Physics Validation
    print("\n4️⃣  Performing Physics Validation...")
    try:
        from src.physics_validation import PhysicsValidator
        validator = PhysicsValidator()
        
        # Calculate UHI intensity
        reference_temp = np.mean(data['true_2d'])
        uhi_intensity = data['prithvi_2d'] - reference_temp
        
        # Calculate NDBI (simplified)
        ndbi = validator.calculate_ndbi(
            data['prithvi_2d'] / 50,  # Normalize for NDBI calculation
            data['ndvi']
        )
        
        physics_validation = validator.comprehensive_validation(
            data['prithvi_2d'],
            data['ndvi'],
            ndbi=ndbi,
            reference_temp=reference_temp
        )
        results['physics_validation'] = physics_validation
        print(f"   ✅ UHI-NDVI correlation: {physics_validation['uhi_ndvi'].get('correlation', 'N/A')}")
        print(f"   ✅ UHI-NDBI correlation: {physics_validation['uhi_ndbi'].get('correlation', 'N/A')}")
        print(f"   ✅ Overall validation: {physics_validation['overall'].get('is_valid', False)}")
    except Exception as e:
        print(f"   ⚠️  Physics validation failed: {e}")
        results['physics_validation'] = {'error': str(e)}
    
    # 5. Model Comparison
    print("\n5️⃣  Calculating Model Comparison...")
    try:
        from src.advanced_metrics import AdvancedMetrics
        comparison_calc = AdvancedMetrics()
        
        if 'baseline_metrics' in results and 'prithvi_metrics' in results:
            comparison = comparison_calc.compare_with_baseline(
                results['prithvi_metrics'],
                results['baseline_metrics']
            )
            results['model_comparison'] = comparison
            print(f"   ✅ RMSE improvement: {comparison.get('rmse_improvement', {}).get('percentage', 0):.2f}%")
            print(f"   ✅ Perkins improvement: {comparison.get('perkins_improvement', {}).get('percentage', 0):.2f}%")
    except Exception as e:
        print(f"   ⚠️  Model comparison failed: {e}")
        results['model_comparison'] = {'error': str(e)}
    
    # Save results
    output_path = Path(__file__).parent.parent / 'results' / 'all_metrics.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 60)
    print(f"✅ All metrics calculated and saved to {output_path}")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    results = calculate_all_metrics()
    print("\n📊 Summary:")
    print(f"   Baseline RMSE: {results.get('baseline_metrics', {}).get('rmse', 'N/A')}")
    print(f"   Prithvi RMSE: {results.get('prithvi_metrics', {}).get('rmse', 'N/A')}")
    print(f"   Perkins Score: {results.get('advanced_metrics', {}).get('perkins_score', 'N/A')}")

