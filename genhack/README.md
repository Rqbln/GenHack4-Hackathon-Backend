# Climate Downscaling with Residual Learning 🌡️🛰️

**High-Resolution Temperature Mapping for Climate Hazard Assessment**

This project implements a machine learning approach to downscale coarse climate data (ERA5, ~9km) to high-resolution maps (~80m) by leveraging satellite imagery and residual learning.

## 🎯 Purpose

Climate teams need accurate, high-resolution temperature data to model hazards like heat waves and urban heat islands. Traditional climate models (9km resolution) miss critical local effects. This project uses **residual learning** to correct ERA5's predictions using satellite-derived features.

### Core Formula

```
HighRes Temperature = ERA5 (9km) + ML_Model(NDVI, Elevation, Coordinates)
```

**Why this works:** ERA5 is already ~95% accurate. We only need ML to fix the last 5% (urban heat island effects).

---

## 📊 Data Sources

The project integrates three datasets:

1. **ECA&D Station Data** - Ground truth temperature observations
   - Format: Text files with daily maximum temperature
   - Quality control flags included
   - Location: `datasets/main/ECA_blend_tx/`

2. **ERA5-Land** - Coarse resolution climate reanalysis (~9km)
   - Variables: 2m temperature, wind, precipitation
   - Format: NetCDF (`.nc`)
   - Location: `datasets/main/derived-era5-land-daily-statistics/`

3. **Sentinel-2 NDVI** - Vegetation index from satellite (~80m)
   - Indicates vegetation health (parks vs concrete)
   - Format: GeoTIFF (`.tif`)
   - Location: `datasets/main/sentinel2_ndvi/`

---

## 🚀 Quick Start

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Run full pipeline for Sweden (2020-2023)
cd src
python main.py --country SE --start 2020-01-01 --end 2023-12-31

# With high-resolution map generation
python main.py --country DE --start 2023-01-01 --end 2023-12-31 \
               --generate-maps \
               --inference-start 2023-07-15 \
               --inference-end 2023-07-20
```

---

## 📁 Project Structure

```
Genhack/
├── datasets/main/           # Data directory
│   ├── ECA_blend_tx/        # Station observations
│   ├── derived-era5-land-daily-statistics/  # ERA5 NetCDF
│   └── sentinel2_ndvi/      # Satellite NDVI
│
├── src/                     # Source code
│   ├── data_preparation.py  # Phase 1: ETL pipeline
│   ├── modeling.py          # Phase 2: ML training
│   ├── inference.py         # Phase 3: Map generation
│   ├── visualization.py     # Phase 4: Evaluation
│   └── main.py              # Master pipeline
│
├── outputs/                 # Generated outputs
│   ├── training_data.csv    # Prepared training cube
│   ├── residual_model.pkl   # Trained model
│   ├── test_predictions.csv # Validation results
│   ├── evaluation/          # Performance plots
│   └── highres_maps/        # Generated temperature maps
│
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

---

## 🔬 Methodology

### Phase 1: Data Preparation

**Goal:** Merge three different data sources into a single training table.

**Steps:**
1. **Parse station metadata** - Convert DMS coordinates to decimal degrees
2. **Clean temperature data** - Filter quality flags, handle missing values, convert units
3. **Build training cube** - For each station observation:
   - Extract ERA5 value at that location/time
   - Extract NDVI from satellite at that location
   - Calculate residual: `Station_Temp - ERA5_Temp`

**Output:** Training DataFrame with columns:
```
[DATE, LAT, LON, ELEVATION, NDVI, ERA5_Temp, Station_Temp, Residual]
```

### Phase 2: Model Training

**Goal:** Train model to predict temperature residuals (corrections to ERA5).

**Key Decisions:**
- **Spatial Cross-Validation** - Split by station location (not time) to test generalization to unseen areas
- **Features:** `[ERA5_Temp, NDVI, Elevation, Lat, Lon, DayOfYear]`
- **Target:** `Residual = Station_Temp - ERA5_Temp`
- **Models:** Random Forest (default) or XGBoost

**Evaluation:**
- Compare `Model RMSE` vs `Baseline (ERA5 only) RMSE`
- Goal: Reduce temperature error by capturing urban heat island effects

### Phase 3: Inference

**Goal:** Generate high-resolution temperature maps for any date.

**Process:**
1. Load high-res NDVI (defines output grid at 80m)
2. Load coarse ERA5 temperature (~9km)
3. Upsample ERA5 to 80m using bicubic interpolation
4. Create feature grid for every pixel
5. Predict residual for each pixel using trained model
6. Combine: `HighRes = Upsampled_ERA5 + Predicted_Residual`

**Output:** GeoTIFF files with 80m resolution temperature maps

### Phase 4: Evaluation

**Visualizations:**
- Residual distributions (actual vs predicted)
- Scatter plots (predicted vs actual)
- Error analysis by feature (NDVI, elevation, etc.)
- Baseline comparison (ERA5 vs our model)
- Map comparisons (ERA5 → Residual → High-Res)

---

## 📈 Expected Results

### Success Criteria

✅ **Visual Check:** Residual map shows urban structure (hot roads, cool parks)  
✅ **Quantitative:** Model RMSE < Baseline RMSE  
✅ **Improvement:** Typical gain of 0.5-2°C error reduction

### Example Metrics

```
ERA5 Baseline RMSE: 2.1°C
Our Model RMSE:     1.4°C
Improvement:        0.7°C (33% reduction)
```

---

## 🛠️ Advanced Usage

### Custom Configuration

```python
from data_preparation import prepare_training_data
from modeling import train_and_evaluate_model
from inference import generate_maps_for_period

# Phase 1: Prepare data
training_data = prepare_training_data(
    data_dir='datasets/main',
    country_code='SE',
    date_range=('2020-01-01', '2023-12-31'),
    output_path='outputs/training_data.csv'
)

# Phase 2: Train model
model, metrics = train_and_evaluate_model(
    training_data=training_data,
    split_type='spatial',
    model_type='xgboost',
    output_dir='outputs'
)

# Phase 3: Generate maps
generate_maps_for_period(
    model_path='outputs/residual_model.pkl',
    era5_dir='datasets/main/derived-era5-land-daily-statistics',
    ndvi_dir='datasets/main/sentinel2_ndvi',
    start_date='2023-07-15',
    end_date='2023-07-20',
    output_dir='outputs/highres_maps'
)
```

### Country Codes

Common country codes (ISO 3166):
- `SE` - Sweden
- `DE` - Germany
- `FR` - France
- `GB` - United Kingdom
- `ES` - Spain
- `IT` - Italy
- `NL` - Netherlands
- `NO` - Norway

---

## 📊 Data Format Details

### Station Temperature Files

**Format:** `TX_STAID000001.txt`

```
STAID, SOUID,    DATE,   TX, Q_TX
    1, 35382,20230715,  289,    0
```

- `TX`: Temperature in 0.1°C (289 = 28.9°C)
- `Q_TX`: Quality flag (0 = valid, 1 = suspect, 9 = missing)

### ERA5 NetCDF

**Variables:**
- `2m_temperature_daily_maximum` (Kelvin)
- `10m_u_component_of_wind_daily_mean` (m/s)
- `10m_v_component_of_wind_daily_mean` (m/s)
- `total_precipitation_daily_mean` (m)

**Dimensions:** `[time, latitude, longitude]`

### NDVI GeoTIFF

**Range:** -1 (water) to +1 (dense vegetation)
**Typical values:**
- 0.6-0.9: Dense vegetation
- 0.2-0.4: Sparse vegetation
- < 0.1: Urban/bare soil

---

## 🐛 Troubleshooting

### Common Issues

**1. "No training data generated"**
- Check that station files exist for your country
- Verify date range overlaps with available ERA5 and NDVI data
- Some countries have limited station coverage

**2. "ERA5 file not found"**
- ERA5 files must match the year in training data
- File naming: `YYYY_2m_temperature_daily_maximum.nc`

**3. "NDVI file not found for date"**
- NDVI files cover 3-month periods
- Check that your date falls within available NDVI timeframes

**4. Low model performance**
- Increase training data (expand date range or add countries)
- Try XGBoost instead of Random Forest
- Check for data quality issues in stations

---

## 📚 References

### Scientific Background

1. **Urban Heat Island Effect**
   - Urban areas can be 3-5°C warmer than rural surroundings
   - Caused by heat-absorbing materials, reduced vegetation
   - Critical for heat hazard assessment

2. **Residual Learning**
   - Train model to predict errors, not absolute values
   - More efficient when baseline is already good
   - Used in computer vision (ResNet) and climate science

3. **Spatial Cross-Validation**
   - Essential for geospatial ML
   - Prevents data leakage from nearby locations
   - Tests true generalization capability

### Data Sources

- **ECA&D:** https://www.ecad.eu
- **ERA5-Land:** https://cds.climate.copernicus.eu
- **Sentinel-2:** https://scihub.copernicus.eu

---

## 🤝 Contributing

Improvements welcome! Key areas:
- Add more countries/regions
- Integrate additional satellite features (LST, albedo)
- Implement temporal modeling (LSTM for time series)
- Optimize for GPU acceleration
- Add uncertainty quantification

---

## 📄 License

This project is for research and educational purposes. Please cite data sources appropriately:

```
Klein Tank, A.M.G. and Coauthors, 2002. Daily dataset of 20th-century surface
air temperature and precipitation series for the European Climate Assessment.
Int. J. of Climatol., 22, 1441-1453.
```

---

## ✅ Checklist for Success

- [ ] Data files in correct locations (`datasets/main/`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Selected country has station data
- [ ] Date range has ERA5 and NDVI coverage
- [ ] Sufficient disk space for outputs (~1-5GB)
- [ ] Run pipeline with `python src/main.py`
- [ ] Check evaluation plots in `outputs/evaluation/`
- [ ] Verify residual map shows urban structure
- [ ] Model RMSE < Baseline RMSE ✓

---

**Happy Downscaling! 🌍📉**
