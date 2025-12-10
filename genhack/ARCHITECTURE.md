# Climate Downscaling - Technical Architecture

## Project Overview

**Objective:** Generate high-resolution (~80m) temperature maps from coarse climate model output (ERA5, ~9km) using machine learning and satellite imagery.

**Approach:** Residual learning - train ML models to predict corrections (residuals) to ERA5 rather than absolute temperatures.

**Formula:** `HighRes_Temp = ERA5_Temp + ML_Residual(NDVI, Elevation, Coordinates)`

---

## System Architecture

### Data Flow Diagram

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Station Data   │     │   ERA5 NetCDF    │     │  Sentinel NDVI  │
│  (Point obs)    │     │   (~9km grid)    │     │  (~80m grid)    │
└────────┬────────┘     └────────┬─────────┘     └────────┬────────┘
         │                       │                         │
         │                       │                         │
         └───────────────────────┴─────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   DATA PREPARATION      │
                    │  (Merge & Align)        │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    TRAINING CUBE        │
                    │ [Lat, Lon, Features,    │
                    │  Temp, Residual]        │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┴──────────────────┐
              │                                     │
    ┌─────────▼─────────┐             ┌───────────▼──────────┐
    │  TRAINING SET     │             │    TEST SET          │
    │  (80% stations)   │             │   (20% stations)     │
    └─────────┬─────────┘             └───────────┬──────────┘
              │                                     │
    ┌─────────▼──────────┐                        │
    │  MODEL TRAINING    │                        │
    │  (Random Forest    │                        │
    │   or XGBoost)      │                        │
    └─────────┬──────────┘                        │
              │                                     │
    ┌─────────▼──────────┐                        │
    │  TRAINED MODEL     │────────────────────────┤
    │  residual_model.pkl│                        │
    └─────────┬──────────┘                        │
              │                            ┌───────▼────────┐
              │                            │  EVALUATION    │
              │                            │  & METRICS     │
              │                            └────────────────┘
              │
    ┌─────────▼──────────┐
    │   INFERENCE        │
    │  (Map Generation)  │
    └─────────┬──────────┘
              │
    ┌─────────▼──────────┐
    │  HIGH-RES MAPS     │
    │  (GeoTIFF, 80m)    │
    └────────────────────┘
```

---

## Module Breakdown

### 1. `data_preparation.py`

**Purpose:** Parse and merge heterogeneous data sources into unified training data.

**Classes:**

#### `StationMetadataParser`
- Parses ECA&D `stations.txt` file
- Converts DMS coordinates to decimal degrees
- Output: DataFrame with station locations and metadata

**Key Method:** `dms_to_decimal(dms_string) -> float`

```python
# Example: '+56:52:00' -> 56.8667
decimal = sign * (degrees + minutes/60 + seconds/3600)
```

#### `StationTemperatureLoader`
- Loads individual station temperature files
- Applies quality control filters
- Converts units (0.1°C → °C)
- Aggregates data by country

**Cleaning Rules:**
1. Keep only `Q_TX == 0` (valid quality)
2. Drop `TX == -9999` (missing)
3. Convert: `TX_celsius = TX / 10.0`
4. Parse date: `YYYYMMDD -> datetime`

#### `TrainingCubeBuilder`
- Extracts ERA5 values at station locations
- Extracts NDVI values at station locations
- Computes residuals: `Station_Temp - ERA5_Temp`
- Handles temporal alignment and spatial interpolation

**Critical Methods:**
- `get_era5_value(date, lat, lon)` - Nearest neighbor extraction from NetCDF
- `get_ndvi_value(date, lat, lon)` - Pixel value from GeoTIFF
- `build_training_cube()` - Main orchestration

**Output Schema:**
```
DATE         | datetime  | Observation date
LAT          | float     | Decimal degrees
LON          | float     | Decimal degrees
ELEVATION    | int       | Meters above sea level
NDVI         | float     | Normalized Difference Vegetation Index [-1, 1]
ERA5_Temp    | float     | ERA5 temperature (°C)
Station_Temp | float     | Ground truth temperature (°C)
Residual     | float     | Station_Temp - ERA5_Temp (°C)
STAID        | int       | Station identifier
DayOfYear    | int       | 1-365/366
```

---

### 2. `modeling.py`

**Purpose:** Train and evaluate residual learning models with spatial cross-validation.

**Classes:**

#### `SpatialCrossValidator`
- Implements spatial train/test split
- **Critical:** Splits by station, not by time
- Prevents spatial autocorrelation leakage

**Methods:**
- `spatial_split()` - Random split of stations (default 80/20)
- `geographic_split()` - Split by latitude or longitude (North/South or East/West)

**Why Spatial CV?**
Standard random split would put observations from the same station in both train and test, allowing the model to "cheat" by memorizing nearby locations. Spatial CV tests true generalization to unseen areas.

#### `ResidualLearningModel`
- Wrapper for scikit-learn/XGBoost models
- Handles feature engineering
- Provides evaluation metrics
- Saves/loads trained models

**Features Used:**
```python
features = [
    'ERA5_Temp',    # Baseline temperature
    'NDVI',         # Vegetation proxy
    'ELEVATION',    # Altitude effect
    'LAT',          # Latitude (climate zone)
    'LON',          # Longitude
    'DayOfYear'     # Seasonal cycle
]
```

**Target:** `Residual` (°C)

**Model Hyperparameters (Random Forest):**
```python
{
    'n_estimators': 200,      # Number of trees
    'max_depth': 15,          # Tree depth
    'min_samples_split': 10,  # Min samples to split node
    'min_samples_leaf': 5,    # Min samples in leaf
    'n_jobs': -1,             # Use all CPU cores
    'random_state': 42        # Reproducibility
}
```

**Evaluation Metrics:**
- **Residual RMSE** - How well we predict corrections
- **Residual MAE** - Mean absolute error of corrections
- **Residual R²** - Explained variance
- **Temperature RMSE** - Final temperature prediction error
- **Baseline RMSE** - ERA5 alone (for comparison)
- **Improvement** - Baseline RMSE - Model RMSE

---

### 3. `inference.py`

**Purpose:** Generate high-resolution temperature maps using trained models.

**Classes:**

#### `HighResMapGenerator`
- Orchestrates map generation pipeline
- Manages data loading and caching
- Performs spatial upsampling
- Generates GeoTIFF outputs

**Key Process:**

**Step 1:** Load High-Res NDVI
- Defines output grid (e.g., 80m resolution)
- Provides spatial reference

**Step 2:** Load Coarse ERA5
- Temperature for target date
- Original resolution: ~9km

**Step 3:** Upsample ERA5
- Resize to match NDVI grid using bicubic interpolation
- Now have "blurry" 80m temperature

**Step 4:** Create Feature Grid
- Flatten 2D grids into table (millions of rows)
- Each row = one pixel with all features

**Step 5:** Predict Residuals
- Feed feature table through trained model
- Get residual for each pixel

**Step 6:** Combine
```python
HighRes_Map = Upsampled_ERA5 + Predicted_Residuals
```

**Output:** Two GeoTIFF files:
1. `highres_temp_YYYYMMDD.tif` - Final temperature map
2. `residual_YYYYMMDD.tif` - Residual map (for verification)

---

### 4. `visualization.py`

**Purpose:** Evaluation and result visualization.

**Classes:**

#### `ModelEvaluator`
Comprehensive performance analysis:
- Residual distributions (actual vs predicted)
- Scatter plots (prediction vs truth)
- Error analysis by feature
- Baseline comparison (ERA5 vs our model)

**Key Plots:**

**1. Residual Distribution**
- Shows if model captures the full range of corrections
- Should match actual residual distribution

**2. Scatter Prediction**
- Points on diagonal = perfect predictions
- Spread indicates error magnitude

**3. Error by Feature**
- Identifies systematic biases
- E.g., "Does model fail at high elevations?"

**4. Baseline Comparison**
- Histogram of improvements
- Percentage of samples improved

#### `MapVisualizer`
Spatial visualization tools:
- Single map plotting with colorbars
- Side-by-side comparisons (ERA5 | Residual | High-Res)
- Animated GIF generation for time series

**Color Schemes:**
- Temperature: Red-Yellow-Blue (hot to cold)
- Residual: Red-White-Blue (positive/negative corrections)

---

## File Formats

### Input Formats

**1. Station Temperature (`.txt`)**
```
STAID, SOUID,    DATE,   TX, Q_TX
    1, 35382,20230715,  289,    0
```
- Fixed-width or comma-separated
- TX in 0.1°C units
- Q_TX quality flag

**2. ERA5 NetCDF (`.nc`)**
```python
<xarray.Dataset>
Dimensions:  (time: 365, latitude: 200, longitude: 300)
Coordinates:
    time       datetime64[ns] ...
    latitude   float32 ...
    longitude  float32 ...
Data variables:
    2m_temperature  float32 (time, latitude, longitude)
```
- CF-compliant NetCDF4
- Temperature in Kelvin
- Regular lat/lon grid

**3. NDVI GeoTIFF (`.tif`)**
- Single band raster
- May have scale/offset metadata
- Typical range: -10000 to 10000 (scaled by 10000)
- After scaling: -1 to 1

### Output Formats

**1. Training Data (`.csv`)**
- Tabular format for easy inspection
- Can be loaded into pandas/Excel
- ~100MB for 100k samples

**2. Trained Model (`.pkl`)**
- Joblib-serialized Python object
- Contains model, feature names, metadata
- ~50-200MB depending on model size

**3. High-Res Maps (`.tif`)**
- Standard GeoTIFF (GDAL-compatible)
- Single-band float32
- LZW compression
- Typical size: 50-500MB per map

---

## Performance Considerations

### Memory Management

**Issue:** Loading large rasters can exceed RAM.

**Solutions:**
1. **Windowed reading** - Process tiles instead of full rasters
2. **Caching** - Keep recent files in memory
3. **Chunking** - Process feature grid in batches

### Computational Bottlenecks

**Phase 1 (Data Prep):** I/O bound
- Bottleneck: Reading thousands of text files
- Optimization: Parallel file reading, caching

**Phase 2 (Training):** CPU bound
- Bottleneck: Random Forest fitting
- Optimization: Use `n_jobs=-1`, consider XGBoost

**Phase 3 (Inference):** Memory + CPU bound
- Bottleneck: Feature grid construction
- Optimization: Process regions in tiles

### Scaling Estimates

**Training Data Size:**
- 1 station, 1 year: ~365 samples
- 50 stations, 3 years: ~55,000 samples
- Training time (RF): ~1-5 minutes

**Inference:**
- 1000×1000 km at 80m: ~150 million pixels
- Processing time: ~10-30 minutes per map
- Memory needed: ~8-16 GB

---

## Error Handling

### Common Errors and Solutions

**1. Missing Data**
```python
if np.isnan(era5_temp) or np.isnan(ndvi):
    continue  # Skip this sample
```

**2. Coordinate Mismatch**
```python
# Ensure all data use same CRS
point = ds.sel(latitude=lat, longitude=lon, method='nearest')
```

**3. Date Range Issues**
```python
# Find appropriate NDVI file
if start <= date < end:
    selected_file = f
```

---

## Testing Strategy

### Unit Tests (`tests/test_pipeline.py`)

**Test 1:** DMS coordinate conversion
**Test 2:** Temperature data cleaning
**Test 3:** Model feature preparation
**Test 4:** Data validation

### Integration Test
Run full pipeline on 1-month subset:
```bash
python src/main.py --country SE --start 2023-07-01 --end 2023-07-31
```

Expected runtime: ~10 minutes  
Expected output: ~1000 training samples, RMSE improvement ~0.5°C

---

## Extension Points

### Adding New Features

**1. Land Surface Temperature (LST)**
```python
# In TrainingCubeBuilder
lst = self.get_lst_value(date, lat, lon)
features.append(lst)
```

**2. Urban/Rural Classification**
```python
# Binary feature from land cover map
is_urban = self.classify_urban(lat, lon)
features.append(is_urban)
```

### Adding New Models

```python
# In modeling.py
elif self.model_type == 'lightgbm':
    import lightgbm as lgb
    self.model = lgb.LGBMRegressor(**params)
```

### Multi-Target Learning

Predict multiple variables simultaneously:
```python
# Predict both temperature and humidity
y_multi = df[['Temp_Residual', 'Humidity_Residual']].values
```

---

## Best Practices

### Data Preparation
1. Always validate date ranges overlap
2. Check coordinate reference systems match
3. Handle missing data explicitly
4. Save intermediate outputs for debugging

### Model Training
1. Use spatial cross-validation
2. Track feature importance
3. Save multiple model checkpoints
4. Monitor validation metrics during training

### Inference
1. Process maps in tiles for memory efficiency
2. Save both residuals and final maps
3. Include metadata in GeoTIFF tags
4. Validate output ranges (e.g., -50°C to +60°C)

### Evaluation
1. Always compare to baseline
2. Visualize residuals geographically
3. Check for systematic biases
4. Test on extreme events separately

---

## Troubleshooting Guide

**Symptom:** Model RMSE worse than baseline  
**Diagnosis:** Model is overfitting or features are uninformative  
**Solution:** Increase regularization, check data quality, add more training data

**Symptom:** Residual map shows random noise  
**Diagnosis:** Model hasn't learned spatial patterns  
**Solution:** Add spatial features, check NDVI quality, increase model complexity

**Symptom:** Urban heat islands not visible  
**Diagnosis:** NDVI resolution insufficient or model underfitting  
**Solution:** Verify NDVI resolution, check for cloud contamination, tune model

**Symptom:** High memory usage during inference  
**Diagnosis:** Feature grid too large  
**Solution:** Process in tiles, reduce ROI size, use data types efficiently

---

## References & Citations

**Data Sources:**
- Klein Tank et al. (2002) - ECA&D dataset
- Muñoz Sabater et al. (2021) - ERA5-Land
- ESA Copernicus - Sentinel-2

**Methods:**
- He et al. (2016) - Residual learning (ResNet)
- Roberts et al. (2017) - Spatial cross-validation for geospatial ML
- Oyler et al. (2016) - Statistical downscaling of temperature

---

**Document Version:** 1.0  
**Last Updated:** December 2025
