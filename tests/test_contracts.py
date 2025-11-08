"""
GenHack Climate - Contract Tests

Validates that pipeline stages produce data matching JSON schemas.
"""

import json
import pytest
from pathlib import Path
from jsonschema import validate, ValidationError

# Paths
SCHEMAS_DIR = Path(__file__).parent.parent / "schemas"


def load_schema(schema_name: str):
    """Load JSON schema"""
    schema_path = SCHEMAS_DIR / f"{schema_name}.schema.json"
    with open(schema_path) as f:
        return json.load(f)


def test_manifest_schema():
    """Test manifest schema validation"""
    schema = load_schema("manifest")
    
    # Valid manifest
    valid_manifest = {
        "city": "paris",
        "period": {
            "start": "2022-07-15",
            "end": "2022-07-17"
        },
        "grid": {
            "crs": "EPSG:3857",
            "resolution_m": 200
        },
        "tiles": [],
        "variables": ["t2m", "tx"],
        "created_at": "2024-01-01T12:00:00Z",
        "stage": "ingest"
    }
    
    # Should not raise
    validate(instance=valid_manifest, schema=schema)
    
    # Invalid manifest (missing required field)
    invalid_manifest = {
        "city": "paris",
        # Missing period
        "grid": {"crs": "EPSG:3857", "resolution_m": 200},
        "tiles": [],
        "variables": ["t2m"],
        "created_at": "2024-01-01T12:00:00Z",
        "stage": "ingest"
    }
    
    with pytest.raises(ValidationError):
        validate(instance=invalid_manifest, schema=schema)


def test_raster_metadata_schema():
    """Test raster metadata schema validation"""
    schema = load_schema("raster_metadata")
    
    # Valid metadata
    valid_metadata = {
        "crs": "EPSG:3857",
        "transform": [100.0, 0.0, 2.0e6, 0.0, -100.0, 6.0e6],
        "width": 128,
        "height": 128,
        "dtype": "float32",
        "nodata": -9999.0,
        "bounds": {
            "minx": 2.0e6,
            "miny": 5.9e6,
            "maxx": 2.1e6,
            "maxy": 6.0e6
        }
    }
    
    validate(instance=valid_metadata, schema=schema)
    
    # Invalid metadata (negative dimensions)
    invalid_metadata = {
        "crs": "EPSG:3857",
        "transform": [100.0, 0.0, 2.0e6, 0.0, -100.0, 6.0e6],
        "width": -128,  # Invalid
        "height": 128,
        "dtype": "float32"
    }
    
    with pytest.raises(ValidationError):
        validate(instance=invalid_metadata, schema=schema)


def test_metrics_schema():
    """Test metrics schema validation"""
    schema = load_schema("metrics")
    
    # Valid metrics (placeholders OK)
    valid_metrics = {
        "rmse": None,
        "mae": None,
        "r2": None,
        "baseline": "bicubic",
        "spatial_resolution_m": 200,
        "sample_count": None,
        "evaluation_date": "2024-01-01T12:00:00Z"
    }
    
    validate(instance=valid_metrics, schema=schema)
    
    # Valid metrics with values
    valid_metrics_with_values = {
        "rmse": 2.5,
        "mae": 1.8,
        "r2": 0.85,
        "baseline": "bilinear",
        "baseline_rmse": 3.2,
        "improvement_percent": 21.9,
        "spatial_resolution_m": 100,
        "sample_count": 5000,
        "evaluation_date": "2024-01-01T12:00:00Z"
    }
    
    validate(instance=valid_metrics_with_values, schema=schema)


def test_indicators_schema():
    """Test indicators schema validation"""
    schema = load_schema("indicators")
    
    # Valid indicators
    valid_indicators = {
        "intensity": 5.2,
        "duration": 3,
        "extent_km2": 125.5,
        "max_temperature_c": 35.8,
        "mean_temperature_c": 32.1,
        "threshold_c": 30.0,
        "days_above_threshold": 3,
        "urban_heat_island_intensity_c": 4.5,
        "percentile_95": 34.2,
        "percentile_99": 35.5,
        "computed_at": "2024-01-01T12:00:00Z"
    }
    
    validate(instance=valid_indicators, schema=schema)
    
    # Valid with nulls (Phase 1)
    valid_indicators_nulls = {
        "intensity": None,
        "duration": None,
        "extent_km2": None,
        "threshold_c": 30.0,
        "computed_at": "2024-01-01T12:00:00Z"
    }
    
    validate(instance=valid_indicators_nulls, schema=schema)


def test_all_schemas_exist():
    """Test that all expected schema files exist"""
    expected_schemas = [
        "manifest.schema.json",
        "raster_metadata.schema.json",
        "metrics.schema.json",
        "indicators.schema.json"
    ]
    
    for schema_file in expected_schemas:
        schema_path = SCHEMAS_DIR / schema_file
        assert schema_path.exists(), f"Schema file missing: {schema_file}"
        
        # Verify it's valid JSON
        with open(schema_path) as f:
            data = json.load(f)
            assert "$schema" in data, f"Schema {schema_file} missing $schema property"
            assert "type" in data, f"Schema {schema_file} missing type property"


def test_pydantic_models_match_schemas():
    """Test that Pydantic models can generate valid schema instances"""
    from src.models import Manifest, Period, Grid, RasterMetadata, Bounds, Metrics, Indicators
    
    # Test Manifest
    manifest = Manifest(
        city="paris",
        period=Period(start="2022-07-15", end="2022-07-17"),
        grid=Grid(crs="EPSG:3857", resolution_m=200),
        tiles=[],
        variables=["t2m"],
        stage="ingest"
    )
    manifest_schema = load_schema("manifest")
    validate(instance=manifest.to_json(), schema=manifest_schema)
    
    # Test RasterMetadata
    metadata = RasterMetadata(
        crs="EPSG:3857",
        transform=[100.0, 0.0, 2.0e6, 0.0, -100.0, 6.0e6],
        width=128,
        height=128,
        dtype="float32",
        bounds=Bounds(minx=2.0e6, miny=5.9e6, maxx=2.1e6, maxy=6.0e6)
    )
    metadata_schema = load_schema("raster_metadata")
    validate(instance=metadata.to_json(), schema=metadata_schema)
    
    # Test Metrics
    metrics = Metrics(baseline="bicubic", spatial_resolution_m=200)
    metrics_schema = load_schema("metrics")
    validate(instance=metrics.to_json(), schema=metrics_schema)
    
    # Test Indicators
    indicators = Indicators(threshold_c=30.0)
    indicators_schema = load_schema("indicators")
    validate(instance=indicators.to_json(), schema=indicators_schema)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
