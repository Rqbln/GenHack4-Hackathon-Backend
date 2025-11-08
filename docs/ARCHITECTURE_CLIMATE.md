# 🏗️ Architecture - GenHack Climate Heat Downscaling

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     CLOUD RUN JOB ORCHESTRATOR                  │
│                      (pipeline/job_main.py)                     │
└────────────┬────────────────────────────────────┬───────────────┘
             │                                    │
             ▼                                    ▼
    ┌────────────────────┐              ┌────────────────────┐
    │   GCS BUCKETS      │              │  ARTIFACT REGISTRY │
    │  (CMEK encrypted)  │              │   (Docker images)  │
    │                    │              └────────────────────┘
    │ • gh-raw-*         │
    │ • gh-intermediate-*│
    │ • gh-models-*      │
    │ • gh-exports-*     │
    └────────────────────┘
```

---

## Pipeline Stages

### 1. **Ingest** (`src/ingest.py`)

**Purpose**: Acquire climate and satellite data

**Phase 1 (Mock)**:
- Generates synthetic rasters (128×128) with spatial patterns
- Temperature: urban heat island effect (warmer center)
- Variables: t2m, tx, tn, rh, u10, v10

**Phase 2+ (Real)**:
- ERA5: Download from Copernicus Climate Data Store
- Sentinel-2: Query Google Earth Engine API
- OSM: Extract features via Overpass API

**Output**: Raw GeoTIFF files + `manifest.json`

---

### 2. **Preprocess** (`src/preprocess.py`)

**Purpose**: Spatial harmonization

**Operations**:
- Reproject to target CRS (EPSG:3857 or EPSG:2154)
- Resample to common resolution (200m)
- Apply bilinear/bicubic interpolation

**Output**: Reprojected rasters + `raster_metadata.json`

---

### 3. **Features** (`src/features.py`)

**Purpose**: Compute spectral indices from satellite imagery

**Indices**:
- **NDVI**: `(NIR - Red) / (NIR + Red)` - vegetation
- **NDBI**: `(SWIR - NIR) / (SWIR + NIR)` - built-up areas

**Phase 1**: Mock indices with inverse temp relationship  
**Phase 2+**: Real S2 bands (B2, B3, B4, B8, B11, B12)

**Output**: Feature rasters + metadata

---

### 4. **Train** (`src/train.py`)

**Purpose**: Model training for downscaling

**Phase 1**: No-op (placeholder)

**Phase 2+**:
- U-Net architecture (encoder-decoder)
- Input: Low-res ERA5 (25km) + features (NDVI, NDBI, elevation)
- Output: High-res temperature (100-200m)
- Loss: MSE + perceptual loss
- Training: 80/20 train/val split

---

### 5. **Evaluate** (`src/evaluate.py`)

**Purpose**: Quantitative model assessment

**Metrics**:
- RMSE (Root Mean Square Error)
- MAE (Mean Absolute Error)
- R² (coefficient of determination)
- Bias (mean predicted - observed)

**Baseline**: Bicubic upsampling for comparison

**Phase 1**: Placeholder (nulls)  
**Phase 2+**: Real validation against ground truth

---

### 6. **Indicators** (`src/indicators.py`)

**Purpose**: Climate impact indicators

**Computed**:
- Heat intensity (°C above threshold)
- Duration (days above 30°C)
- Spatial extent (km²)
- Urban heat island intensity (urban - rural)
- Percentiles (95th, 99th)

**Use Case**: Urban planning, public health alerts

---

### 7. **Publish** (`src/publish.py`)

**Purpose**: Export final outputs

**Formats**:
- **GeoTIFF**: Cloud Optimized (COG) with LZW compression
- **PNG**: Preview images with colormaps
- **JSON**: Metadata for downstream tools

**Output Structure**:
```
gs://gh-exports-genhack-heat-dev/
└── paris/
    └── 2022/
        ├── paris_temperature.tif
        ├── paris_temperature.png
        ├── paris_ndvi.tif
        ├── paris_ndbi.tif
        └── export_metadata.json
```

---

### 8. **Report** (`src/report.py`)

**Purpose**: Human-readable summaries

**Features**:
- Jinja2 templating (HTML)
- Weasyprint conversion (PDF)
- Embedded maps (PNG previews)
- Metrics tables
- Indicator visualizations

**Output**: `paris_report.html` + `paris_report.pdf`

---

## Data Flow

```
CONFIG (YAML)
     │
     ▼
 MANIFEST (init)
     │
     ├─→ INGEST ──────→ Raw GeoTIFFs ──────┐
     │                                       │
     ├─→ PREPROCESS ──→ Reprojected ────────┤
     │                                       │
     ├─→ FEATURES ────→ NDVI/NDBI ──────────┤
     │                                       │
     ├─→ TRAIN ───────→ Model weights ──────┤
     │                                       │
     ├─→ EVALUATE ────→ metrics.json ───────┤
     │                                       │
     ├─→ INDICATORS ──→ indicators.json ────┤
     │                                       │
     ├─→ PUBLISH ─────→ COG + PNG ──────────┤
     │                                       │
     └─→ REPORT ──────→ HTML/PDF ───────────┘
                            │
                            ▼
                     gs://gh-exports-*/
```

---

## Infrastructure Components

### GCP Resources

| Resource | Name | Purpose |
|----------|------|---------|
| Project | `genhack-heat-dev` | Isolated environment |
| Cloud Run Job | `heat-downscaling-pipeline` | Pipeline execution |
| Artifact Registry | `europe-docker.pkg.dev/.../heat` | Container images |
| GCS Buckets | `gh-raw-*`, `gh-intermediate-*`, etc. | Data storage |
| KMS | `gh-ring/gh-key` | CMEK encryption |
| Service Account | `gh-pipeline-sa@...` | Job identity |

### Docker Image Stack

```dockerfile
Base: python:3.11-slim
├── GDAL 3.x (geospatial I/O)
├── PROJ 9.x (coordinate transforms)
├── rasterio (Python GDAL bindings)
├── xarray (n-dimensional arrays)
├── rioxarray (raster extensions)
├── geopandas (vector data)
├── matplotlib (plotting)
└── weasyprint (PDF generation)
```

**Image Size**: ~2.0 GB (optimized multi-stage build)

---

## Security & Isolation

### Clean-Room Principles

✅ **Separate project** (genhack-heat-dev ≠ mental-journal-dev)  
✅ **No shared buckets** (gh- prefix vs mj- prefix)  
✅ **Separate KMS keys** (gh-ring vs mj-ring)  
✅ **Separate service accounts** (no cross-project IAM)  
✅ **CI/CD checks** (block Kura references)

### IAM Roles (gh-pipeline-sa)

- `roles/run.admin` - Manage Cloud Run resources
- `roles/run.invoker` - Execute jobs
- `roles/storage.admin` - Read/write GCS
- `roles/artifactregistry.reader` - Pull images
- `roles/logging.logWriter` - Write logs
- `roles/monitoring.metricWriter` - Write metrics
- `roles/cloudkms.cryptoKeyEncrypterDecrypter` - Use KMS key

---

## Scalability Considerations

### Phase 1 (Current)

- Single city (Paris)
- 3-day period
- 128×128 rasters
- Sequential execution
- ~60s total runtime

### Phase 2+ (Future)

- Multi-city processing (5-10 cities)
- Full summer season (June-August)
- High-resolution (1024×1024+)
- Parallel tile processing
- GPU-accelerated training
- Distributed training (Cloud TPU)

### Optimization Strategies

1. **Tiling**: Split large areas into manageable tiles
2. **Caching**: Store preprocessed data for reuse
3. **Lazy loading**: Use xarray Dask integration
4. **Parallelization**: Cloud Run Jobs with `--tasks` flag
5. **Cloud Storage**: Use Parallel Composite Uploads

---

## Monitoring & Observability

### Logs

```bash
# View job logs
gcloud logging read \
  "resource.type=cloud_run_job AND \
   resource.labels.job_name=heat-downscaling-pipeline" \
  --limit=50 \
  --format=json
```

### Metrics

- Execution duration
- Memory/CPU utilization
- GCS bandwidth usage
- Stage-specific timings

### Alerts (Future)

- Job failure notifications
- Cost threshold alerts
- Data quality checks

---

## Tech Stack Summary

| Layer | Technologies |
|-------|-------------|
| **Compute** | Cloud Run Jobs, Docker |
| **Storage** | Cloud Storage (CMEK), Artifact Registry |
| **Security** | KMS, IAM, Service Accounts |
| **Geospatial** | GDAL, PROJ, rasterio, xarray |
| **ML** | (Phase 2+) PyTorch, U-Net, SRGAN |
| **CI/CD** | GitHub Actions, Cloud Build |
| **Observability** | Cloud Logging, Cloud Monitoring |

---

## Evolution Path

```
Phase 0: Infrastructure ✅
    ↓
Phase 1: Mock pipeline ✅
    ↓
Phase 2: Real data ingestion
    ↓
Phase 3: ML model training
    ↓
Phase 4: Multi-city analysis
    ↓
Production: Operational system
```

**Current Status**: Phase 1 complete, ready for Phase 2
