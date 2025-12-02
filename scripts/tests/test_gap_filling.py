#!/usr/bin/env python3
"""
Test script for Gap Filling Algorithm (Day 2)
Tests Random Forest gap filling on NDVI data
"""

import sys
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import logging
from src.gap_filling import NDVIGapFiller

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_gap_filling():
    """Test gap filling algorithm with synthetic data"""
    print("=" * 60)
    print("Testing Gap Filling Algorithm (Day 2)")
    print("=" * 60)
    
    try:
        # Test 1: Initialize gap filler
        print("\n[Test 1] Initializing gap filler...")
        gap_filler = NDVIGapFiller(
            n_estimators=10,  # Reduced for faster testing
            max_depth=10,
            random_state=42
        )
        assert gap_filler is not None, "Failed to initialize gap filler"
        assert not gap_filler.is_fitted, "Gap filler should not be fitted initially"
        print("✅ Gap filler initialized")
        
        # Test 2: Create synthetic NDVI data with gaps
        print("\n[Test 2] Creating synthetic NDVI data with gaps...")
        np.random.seed(42)
        ndvi_array = np.random.rand(50, 50) * 2 - 1  # Values between -1 and 1
        
        # Create gaps (random NaN values)
        gap_mask = np.random.rand(50, 50) < 0.2  # 20% gaps
        ndvi_with_gaps = ndvi_array.copy()
        ndvi_with_gaps[gap_mask] = np.nan
        
        n_gaps = np.sum(np.isnan(ndvi_with_gaps))
        print(f"✅ Created synthetic data with {n_gaps} gaps ({n_gaps/(50*50)*100:.1f}%)")
        
        # Test 3: Extract features
        print("\n[Test 3] Extracting features...")
        features, missing_mask = gap_filler.extract_features(ndvi_with_gaps, window_size=5)
        assert features is not None, "Failed to extract features"
        assert len(features) > 0, "No features extracted"
        assert features.shape[1] == 16, f"Expected 16 features, got {features.shape[1]}"
        print(f"✅ Extracted {len(features)} feature vectors with {features.shape[1]} features each")
        
        # Test 4: Extract training data
        print("\n[Test 4] Extracting training data...")
        ndvi_arrays = [ndvi_array]  # Use complete array for training
        X_train, y_train = gap_filler.extract_training_data(ndvi_arrays, window_size=5)
        assert X_train is not None, "Failed to extract training data"
        assert len(X_train) > 0, "No training data extracted"
        assert len(X_train) == len(y_train), "X and y should have same length"
        print(f"✅ Extracted {len(X_train)} training samples")
        
        # Test 5: Train model
        print("\n[Test 5] Training Random Forest model...")
        metrics = gap_filler.train(ndvi_arrays, test_size=0.2, window_size=5)
        assert gap_filler.is_fitted, "Model should be fitted after training"
        assert metrics is not None, "Training should return metrics"
        assert 'test_r2' in metrics, "Metrics should include test_r2"
        print(f"✅ Model trained - Test R²: {metrics['test_r2']:.4f}, RMSE: {metrics['test_rmse']:.4f}")
        
        # Test 6: Fill gaps
        print("\n[Test 6] Filling gaps...")
        filled_array = gap_filler.fill_gaps(ndvi_with_gaps, window_size=5)
        assert filled_array is not None, "Failed to fill gaps"
        assert filled_array.shape == ndvi_with_gaps.shape, "Shape should be preserved"
        n_remaining_gaps = np.sum(np.isnan(filled_array))
        assert n_remaining_gaps == 0, f"Should have no remaining gaps, but found {n_remaining_gaps}"
        print(f"✅ Gaps filled - {n_gaps} pixels reconstructed")
        
        # Test 7: Check reconstruction quality
        print("\n[Test 7] Checking reconstruction quality...")
        original_values = ndvi_array[gap_mask]
        filled_values = filled_array[gap_mask]
        rmse = np.sqrt(np.mean((original_values - filled_values) ** 2))
        print(f"✅ Reconstruction RMSE: {rmse:.4f}")
        
        print("\n" + "=" * 60)
        print("✅ All gap filling tests passed!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Gap filling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gap_filling()
    sys.exit(0 if success else 1)

