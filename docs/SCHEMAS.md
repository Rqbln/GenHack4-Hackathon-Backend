# 📐 Data Contracts - JSON Schemas

All pipeline stages communicate through validated JSON schemas. This ensures type safety and compatibility between stages.

---

## Manifest Schema

**Purpose**: Describes the data context passed between pipeline stages

**File**: `schemas/manifest.schema.json`

**Example**:
```json
{
  "city": "paris",
  "period": {
    "start": "2022-07-15",
    "end": "2022-07-17"
  },
  "grid": {
    "crs": "EPSG:3857",
    "resolution_m": 200
  },
  "tiles": [
    {
      "id": "tile_01",
      "bbox": [2.224, 48.815, 2.347, 48.859]
    }
  ],
  "variables": ["t2m", "tx", "tn", "rh", "u10", "v10"],
  "created_at": "2024-01-15T12:00:00Z",
  "stage": "preprocess",
  "mode": {
    "dry_run": true
  },
  "paths": {
    "raw": "gs://gh-raw-genhack-heat-dev/paris/2022/",
    "intermediate": "gs://gh-intermediate-genhack-heat-dev/paris/2022/",
    "features": "gs://gh-intermediate-genhack-heat-dev/paris/2022/features/",
    "exports": "gs://gh-exports-genhack-heat-dev/paris/2022/"
  }
}
```

**Pydantic Model**: `src/models.Manifest`

---

## Raster Metadata Schema

**Purpose**: Describes georeferenced raster files

**File**: `schemas/raster_metadata.schema.json`

**Example**:
```json
{
  "crs": "EPSG:3857",
  "transform": [200.0, 0.0, 259272.0, 0.0, -200.0, 6250464.0],
  "width": 128,
  "height": 128,
  "nodata": -9999.0,
  "dtype": "float32",
  "units": "celsius",
  "bounds": {
    "minx": 259272.0,
    "miny": 6224864.0,
    "maxx": 284872.0,
    "maxy": 6250464.0
  },
  "band_count": 1,
  "band_names": ["t2m"]
}
```

**Key Fields**:
- `transform`: Affine transform [a, b, c, d, e, f] (GDAL convention)
- `bounds`: Geographic extent in CRS units
- `dtype`: NumPy data type (float32, int16, etc.)

**Pydantic Model**: `src/models.RasterMetadata`

---

## Metrics Schema

**Purpose**: Model evaluation metrics for downscaling performance

**File**: `schemas/metrics.schema.json`

**Example** (Phase 1 - placeholders):
```json
{
  "rmse": null,
  "mae": null,
  "r2": null,
  "bias": null,
  "correlation": null,
  "baseline": "bicubic",
  "baseline_rmse": null,
  "improvement_percent": null,
  "spatial_resolution_m": 200,
  "sample_count": null,
  "evaluation_date": "2024-01-15T12:00:00Z"
}
```

**Example** (Phase 2+ - real values):
```json
{
  "rmse": 2.45,
  "mae": 1.82,
  "r2": 0.87,
  "bias": -0.15,
  "correlation": 0.93,
  "baseline": "bicubic",
  "baseline_rmse": 3.21,
  "improvement_percent": 23.7,
  "spatial_resolution_m": 100,
  "sample_count": 15000,
  "evaluation_date": "2024-01-15T12:00:00Z"
}
```

**Pydantic Model**: `src/models.Metrics`

---

## Indicators Schema

**Purpose**: Climate heat indicators for impact assessment

**File**: `schemas/indicators.schema.json`

**Example**:
```json
{
  "intensity": 5.2,
  "duration": 3,
  "extent_km2": 125.5,
  "max_temperature_c": 35.8,
  "mean_temperature_c": 32.1,
  "threshold_c": 30.0,
  "days_above_threshold": 3,
  "affected_population_estimate": 2500000,
  "urban_heat_island_intensity_c": 4.5,
  "percentile_95": 34.2,
  "percentile_99": 35.5,
  "computed_at": "2024-01-15T12:00:00Z"
}
```

**Indicator Definitions**:

- **intensity**: Temperature anomaly above threshold (°C)
- **duration**: Number of days in heat event
- **extent_km2**: Spatial area affected
- **urban_heat_island_intensity_c**: Urban-rural temperature difference
- **percentile_95/99**: Statistical extremes

**Pydantic Model**: `src/models.Indicators`

---

## Validation

### Automatic Validation

All Pydantic models automatically validate data:

```python
from src.models import Manifest, Period, Grid

# This will raise ValidationError if invalid
manifest = Manifest(
    city="paris",
    period=Period(start="2022-07-15", end="2022-07-17"),
    grid=Grid(crs="EPSG:3857", resolution_m=200),
    variables=["t2m"],
    stage="ingest",
    tiles=[]
)

# Export to JSON
manifest_json = manifest.to_json()
```

### Contract Tests

Run contract tests to verify schemas:

```bash
pytest tests/test_contracts.py -v
```

**Tests Include**:
- Schema file existence
- JSON Schema validity
- Pydantic model compatibility
- Valid/invalid data examples

---

## Stage I/O Contracts

### Ingest → Preprocess

**Input**: Configuration YAML  
**Output**: 
- Raw GeoTIFF files
- `manifest.json` with stage="ingest"

### Preprocess → Features

**Input**: `manifest.json` (stage="ingest")  
**Output**: 
- Reprojected GeoTIFFs
- `raster_metadata.json`
- Updated `manifest.json` (stage="preprocess")

### Features → Train

**Input**: `manifest.json` (stage="preprocess")  
**Output**: 
- Feature rasters (NDVI, NDBI)
- `features_metadata.json`
- Updated `manifest.json` (stage="features")

### Train → Evaluate

**Input**: `manifest.json` (stage="features")  
**Output**: 
- Model weights (Phase 2+)
- Updated `manifest.json` (stage="train")

### Evaluate → Indicators

**Input**: `manifest.json` (stage="train")  
**Output**: 
- `metrics.json`
- Updated `manifest.json` (stage="evaluate")

### Indicators → Publish

**Input**: `manifest.json` (stage="evaluate")  
**Output**: 
- `indicators.json`
- Updated `manifest.json` (stage="indicators")

### Publish → Report

**Input**: `manifest.json` (stage="indicators")  
**Output**: 
- Cloud Optimized GeoTIFFs
- PNG previews
- `export_metadata.json`
- Updated `manifest.json` (stage="publish")

### Report → End

**Input**: `manifest.json` (stage="publish")  
**Output**: 
- HTML report
- PDF report
- Final `manifest.json` (stage="report")

---

## Schema Evolution

When adding new fields in Phase 2+:

1. **Add field to JSON schema** with `required: false`
2. **Update Pydantic model** with `Optional[T] = None`
3. **Run contract tests** to verify backward compatibility
4. **Update documentation**

**Example**:
```python
# Phase 2: Add population data
class Indicators(BaseModel):
    # ... existing fields ...
    affected_population_estimate: Optional[int] = None  # New field
```

---

## Best Practices

✅ **Always validate** before stage transitions  
✅ **Use Pydantic models** for type safety  
✅ **Write tests** for new schemas  
✅ **Document fields** with descriptions  
✅ **Version schemas** with semver (`$id` in JSON)  
✅ **Keep schemas DRY** (reuse definitions)

---

## Schema Registry

Future enhancement: Store schemas in centralized registry (e.g., Confluent Schema Registry, Google Cloud Schema Registry) for versioning and governance.
