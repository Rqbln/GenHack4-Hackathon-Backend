#!/usr/bin/env python3
"""
Test script for Baseline Model (Day 3)
Tests bicubic interpolation and altitude correction
"""

import sys
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import logging
from src.baseline import BaselineDownscaler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_baseline():
    """Test baseline downscaling model"""
    print("=" * 60)
    print("Testing Baseline Model (Day 3)")
    print("=" * 60)
    
    try:
        # Test 1: Initialize downscaler
        print("\n[Test 1] Initializing baseline downscaler...")
        downscaler = BaselineDownscaler(
            target_resolution=100.0,
            lapse_rate=-0.0065,
            interpolation_method='cubic'
        )
        assert downscaler is not None, "Failed to initialize downscaler"
        print("✅ Baseline downscaler initialized")
        
        # Test 2: Bicubic interpolation
        print("\n[Test 2] Testing bicubic interpolation...")
        from rasterio.transform import from_bounds
        
        # Create low resolution data
        low_res = np.random.rand(10, 10) * 20 + 15  # 10x10 grid, 15-35°C
        low_res_transform = from_bounds(2.0, 48.5, 2.5, 49.0, 10, 10)
        target_shape = (50, 50)  # 5x upscaling
        target_transform = from_bounds(2.0, 48.5, 2.5, 49.0, 50, 50)
        
        high_res = downscaler.bicubic_interpolation(
            low_res,
            low_res_transform,
            target_shape,
            target_transform
        )
        
        assert high_res is not None, "Failed to interpolate"
        assert high_res.shape == target_shape, f"Shape mismatch: {high_res.shape} != {target_shape}"
        print(f"✅ Interpolated from {low_res.shape} to {high_res.shape}")
        
        # Test 3: Altitude correction
        print("\n[Test 3] Testing altitude correction...")
        temperature = np.ones((50, 50)) * 20.0  # 20°C everywhere
        elevation = np.random.rand(50, 50) * 500  # 0-500m elevation
        reference_elevation = 100.0
        
        corrected = downscaler.altitude_correction(
            temperature,
            elevation,
            reference_elevation
        )
        
        assert corrected is not None, "Failed to apply altitude correction"
        assert corrected.shape == temperature.shape, "Shape should be preserved"
        
        # Check that higher elevations are cooler
        high_elev_idx = elevation > reference_elevation
        low_elev_idx = elevation < reference_elevation
        assert np.mean(corrected[high_elev_idx]) < np.mean(corrected[low_elev_idx]), \
            "Higher elevations should be cooler"
        print(f"✅ Altitude correction applied - Mean temp: {np.mean(corrected):.2f}°C")
        
        # Test 4: RMSE calculation
        print("\n[Test 4] Testing RMSE calculation...")
        predicted = np.array([20.0, 25.0, 30.0, 35.0])
        observed = np.array([21.0, 24.0, 29.0, 36.0])
        
        rmse = downscaler.calculate_rmse(predicted, observed)
        expected_rmse = np.sqrt(np.mean((predicted - observed) ** 2))
        
        assert abs(rmse - expected_rmse) < 1e-6, f"RMSE mismatch: {rmse} != {expected_rmse}"
        print(f"✅ RMSE calculation correct: {rmse:.4f}")
        
        # Test 5: MAE calculation
        print("\n[Test 5] Testing MAE calculation...")
        mae = downscaler.calculate_mae(predicted, observed)
        expected_mae = np.mean(np.abs(predicted - observed))
        
        assert abs(mae - expected_mae) < 1e-6, f"MAE mismatch: {mae} != {expected_mae}"
        print(f"✅ MAE calculation correct: {mae:.4f}")
        
        # Test 6: R² calculation
        print("\n[Test 6] Testing R² calculation...")
        r2 = downscaler.calculate_r2(predicted, observed)
        assert r2 is not None, "R² should not be None"
        assert -np.inf < r2 <= 1.0, f"R² should be between -inf and 1, got {r2}"
        print(f"✅ R² calculation correct: {r2:.4f}")
        
        # Test 7: Evaluate baseline
        print("\n[Test 7] Testing evaluate_baseline...")
        metrics = downscaler.evaluate_baseline(predicted, observed)
        assert 'rmse' in metrics, "Metrics should include RMSE"
        assert 'mae' in metrics, "Metrics should include MAE"
        assert 'r2' in metrics, "Metrics should include R²"
        print(f"✅ Baseline evaluation: RMSE={metrics['rmse']:.4f}, MAE={metrics['mae']:.4f}, R²={metrics['r2']:.4f}")
        
        print("\n" + "=" * 60)
        print("✅ All baseline tests passed!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Baseline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_baseline()
    sys.exit(0 if success else 1)

