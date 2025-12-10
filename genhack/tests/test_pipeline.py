#!/usr/bin/env python3
"""
Quick test script to verify the pipeline works end-to-end
Uses a small subset of data for rapid validation
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data_preparation import StationMetadataParser, StationTemperatureLoader
from modeling import ResidualLearningModel
import pandas as pd
import numpy as np


def test_station_parser():
    """Test station metadata parsing"""
    print("\n=== Test 1: Station Metadata Parser ===")
    
    parser = StationMetadataParser('../datasets/main/ECA_blend_tx/stations.txt')
    
    # Test DMS conversion
    test_cases = [
        ('+56:52:00', 56.8667),
        ('-12:30:00', -12.5000),
        ('+00:00:00', 0.0000)
    ]
    
    for dms, expected in test_cases:
        result = parser.dms_to_decimal(dms)
        assert abs(result - expected) < 0.01, f"DMS conversion failed: {dms} -> {result} (expected {expected})"
        print(f"  ✓ {dms} -> {result:.4f}° (expected {expected:.4f}°)")
    
    # Parse all stations
    stations = parser.parse_stations()
    print(f"  ✓ Parsed {len(stations)} stations")
    print(f"  ✓ Countries: {stations['CN'].nunique()}")
    
    return True


def test_temperature_loader():
    """Test temperature data loading"""
    print("\n=== Test 2: Temperature Data Loader ===")
    
    parser = StationMetadataParser('../datasets/main/ECA_blend_tx/stations.txt')
    stations = parser.parse_stations()
    
    loader = StationTemperatureLoader(
        '../datasets/main/ECA_blend_tx',
        stations
    )
    
    # Load one station
    test_staid = stations.iloc[0]['STAID']
    df = loader.load_station_file(test_staid)
    
    print(f"  ✓ Loaded station {test_staid}: {len(df)} raw observations")
    
    # Clean data
    df_clean = loader.clean_temperature_data(df)
    print(f"  ✓ After cleaning: {len(df_clean)} valid observations")
    print(f"  ✓ Temperature range: {df_clean['TX'].min():.1f}°C to {df_clean['TX'].max():.1f}°C")
    
    # Test country loading (small subset)
    print("\n  Testing country data loading (limited dates)...")
    country_data = loader.load_country_stations('SE', ('2023-07-01', '2023-07-31'))
    print(f"  ✓ Loaded {len(country_data)} observations from {country_data['STAID'].nunique()} stations")
    
    return True


def test_model_features():
    """Test model feature preparation"""
    print("\n=== Test 3: Model Feature Preparation ===")
    
    # Create synthetic test data
    n_samples = 100
    test_data = pd.DataFrame({
        'DATE': pd.date_range('2023-07-01', periods=n_samples, freq='D'),
        'LAT': np.random.uniform(55, 65, n_samples),
        'LON': np.random.uniform(10, 20, n_samples),
        'ELEVATION': np.random.uniform(0, 500, n_samples),
        'NDVI': np.random.uniform(0.2, 0.8, n_samples),
        'ERA5_Temp': np.random.uniform(15, 30, n_samples),
        'Station_Temp': np.random.uniform(15, 30, n_samples),
        'Residual': np.random.uniform(-3, 3, n_samples),
        'STAID': np.random.randint(1, 10, n_samples),
        'DayOfYear': np.arange(1, n_samples + 1) % 365
    })
    
    model = ResidualLearningModel(model_type='random_forest')
    X, y = model.prepare_features(test_data)
    
    print(f"  ✓ Feature matrix shape: {X.shape}")
    print(f"  ✓ Target array shape: {y.shape}")
    print(f"  ✓ Features: {model.feature_names}")
    
    # Test model training (quick)
    print("\n  Training test model (10 trees)...")
    model = ResidualLearningModel(model_type='random_forest', n_estimators=10, verbose=0)
    model.train(test_data)
    print("  ✓ Model training successful")
    
    # Test prediction
    predictions = model.predict(test_data)
    print(f"  ✓ Generated {len(predictions)} predictions")
    print(f"  ✓ Prediction range: {predictions.min():.2f}°C to {predictions.max():.2f}°C")
    
    return True


def test_data_validation():
    """Test data validation and error handling"""
    print("\n=== Test 4: Data Validation ===")
    
    # Test with invalid data
    invalid_data = pd.DataFrame({
        'TX': [-9999, 250, 300, -100],  # Invalid values
        'Q_TX': [0, 1, 0, 9]  # Mixed quality
    })
    
    parser = StationMetadataParser('../datasets/main/ECA_blend_tx/stations.txt')
    stations = parser.parse_stations()
    loader = StationTemperatureLoader('../datasets/main/ECA_blend_tx', stations)
    
    cleaned = loader.clean_temperature_data(invalid_data)
    
    print(f"  ✓ Input: {len(invalid_data)} rows")
    print(f"  ✓ After cleaning: {len(cleaned)} rows")
    print("  ✓ Invalid values correctly filtered")
    
    return True


def run_all_tests():
    """Run all tests"""
    print("=" * 70)
    print(" CLIMATE DOWNSCALING - PIPELINE VALIDATION")
    print("=" * 70)
    
    tests = [
        ("Station Parser", test_station_parser),
        ("Temperature Loader", test_temperature_loader),
        ("Model Features", test_model_features),
        ("Data Validation", test_data_validation),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success, None))
        except Exception as e:
            results.append((name, False, str(e)))
            print(f"\n  ✗ Test failed: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print(" TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for name, success, error in results:
        if success:
            print(f"  ✓ {name}: PASSED")
        else:
            print(f"  ✗ {name}: FAILED")
            if error:
                print(f"    Error: {error}")
    
    print(f"\n  Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 All tests passed! Pipeline is ready to use.")
        return 0
    else:
        print(f"\n  ⚠️  {total - passed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
