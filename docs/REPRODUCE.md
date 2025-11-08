# 🔄 Reproduction Guide - GenHack Climate

Step-by-step instructions to reproduce the Phase 1 pipeline from scratch.

---

## Prerequisites

✅ GCP account with billing enabled  
✅ Docker installed locally  
✅ `gcloud` CLI installed and authenticated  
✅ `make` utility (macOS/Linux)  
✅ Phase 0 infrastructure complete (see `../genhack-duplication/PHASE0_COMPLETE.md`)

**Estimated Time**: 15 minutes (first run), 5 minutes (subsequent runs)

---

## Step 1: Verify Phase 0 Infrastructure

```bash
# Switch to GenHack project
gcloud config set project genhack-heat-dev

# Verify buckets exist
gsutil ls -p genhack-heat-dev | grep "gh-"

# Verify service account
gcloud iam service-accounts list --filter="email:gh-pipeline-sa@*"

# Verify Artifact Registry
gcloud artifacts repositories list --location=europe
```

**Expected Output**: 11 buckets, 1 service account, 1 repository

---

## Step 2: Clone Repository

```bash
cd ~/Documents/GitHub/GCPU-hackathon/genhack-heat
```

**Repository Structure**:
```
genhack-heat/
├── src/          # Pipeline modules
├── pipeline/     # Orchestrator + Dockerfile
├── configs/      # YAML configurations
├── schemas/      # JSON schemas
├── templates/    # Jinja2 templates
├── tests/        # Contract tests
├── infra/        # Deployment scripts
└── Makefile      # Commands
```

---

## Step 3: Initialize Infrastructure

```bash
make init
```

**What This Does**:
- Verifies GCP project is `genhack-heat-dev`
- Checks Phase 0 resources (buckets, KMS, Artifact Registry, SA)
- Enables required APIs (if not already)

**Expected Output**:
```
✅ Project: genhack-heat-dev
✅ KMS keyring 'gh-ring' exists
✅ Artifact Registry 'heat' exists
✅ Service account: gh-pipeline-sa@genhack-heat-dev.iam.gserviceaccount.com
✅ Found 11 buckets with 'gh-' prefix
✅ Infrastructure Check Complete
```

---

## Step 4: Build Docker Image

```bash
make build
```

**What This Does**:
- Builds `pipeline/Dockerfile.geo` with GDAL + geospatial stack
- Tags with timestamp + `latest`
- Multi-stage build for optimized size

**Expected Duration**: 5-10 minutes (first build), 1-2 minutes (cached)

**Expected Output**:
```
🐳 Building Docker image...
✅ Built: europe-docker.pkg.dev/genhack-heat-dev/heat/gh-pipeline:20250108-143022
```

---

## Step 5: Test Locally (Dry-Run)

```bash
make dryrun
```

**What This Does**:
- Runs pipeline in Docker container locally
- Uses mock data (no GCP access needed)
- Outputs to `/tmp/genhack/exports/`

**Expected Duration**: 30-60 seconds

**Expected Output**:
```
GenHack Climate Heat Downscaling Pipeline
=========================================
City: paris
Period: 2022-07-15 to 2022-07-17
Resolution: 200m
Mode: DRY RUN (mock data)
---
✅ INGEST complete (2.3s)
✅ PREPROCESS complete (4.1s)
✅ FEATURES complete (3.8s)
✅ TRAIN complete (0.1s)
✅ EVALUATE complete (0.2s)
✅ INDICATORS complete (1.5s)
✅ PUBLISH complete (5.2s)
✅ REPORT complete (3.1s)
---
✅ PIPELINE COMPLETE
Total duration: 20.3s
```

**Verify Outputs**:
```bash
ls /tmp/genhack/exports/paris/

# Expected files:
# - paris_temperature.tif
# - paris_temperature.png
# - paris_ndvi.tif
# - paris_ndbi.tif
# - indicators.json
# - metrics.json
# - export_metadata.json
# - paris_report.html
# - paris_report.pdf
```

---

## Step 6: Deploy to Cloud Run

```bash
make deploy
```

**What This Does**:
1. Builds Docker image
2. Pushes to Artifact Registry (europe-docker.pkg.dev)
3. Creates/updates Cloud Run Job `heat-downscaling-pipeline`

**Expected Duration**: 5-8 minutes

**Expected Output**:
```
📤 Pushing to Artifact Registry...
✅ Pushed: europe-docker.pkg.dev/genhack-heat-dev/heat/gh-pipeline:20250108-143022

🚀 Deploying Cloud Run Job...
✅ Job created: heat-downscaling-pipeline
```

---

## Step 7: Execute Pipeline in Cloud

```bash
make run
```

**What This Does**:
- Executes Cloud Run Job with mock data
- Uploads outputs to `gs://gh-exports-genhack-heat-dev/`
- Waits for completion

**Expected Duration**: 60-90 seconds

**Expected Output**:
```
▶️  Executing Cloud Run Job...
✅ Execution complete!

View outputs:
  gsutil ls gs://gh-exports-genhack-heat-dev/paris/2022/
```

---

## Step 8: Verify Outputs

```bash
# List outputs in GCS
gsutil ls gs://gh-exports-genhack-heat-dev/paris/2022/

# Download report
gsutil cp gs://gh-exports-genhack-heat-dev/paris/2022/paris_report.html .
open paris_report.html

# Download GeoTIFF
gsutil cp gs://gh-exports-genhack-heat-dev/paris/2022/paris_temperature.tif .

# View in QGIS or similar
```

---

## Step 9: Run Contract Tests

```bash
# Install test dependencies locally
pip install pytest jsonschema pydantic pyyaml

# Run tests
make test
```

**Expected Output**:
```
🧪 Running tests...
tests/test_contracts.py::test_manifest_schema PASSED
tests/test_contracts.py::test_raster_metadata_schema PASSED
tests/test_contracts.py::test_metrics_schema PASSED
tests/test_contracts.py::test_indicators_schema PASSED
tests/test_contracts.py::test_all_schemas_exist PASSED
tests/test_contracts.py::test_pydantic_models_match_schemas PASSED
✅ Tests passed!
```

---

## Troubleshooting

### Build Fails with GDAL Errors

**Solution**: Clear Docker build cache
```bash
docker system prune -a
make build
```

### Permission Denied on GCS

**Solution**: Verify service account permissions
```bash
gcloud projects get-iam-policy genhack-heat-dev \
  --flatten="bindings[].members" \
  --filter="bindings.members:gh-pipeline-sa@*"
```

### Job Execution Timeout

**Solution**: Increase timeout in `infra/deploy_job.sh`
```bash
--task-timeout=3600  # Change to 7200 (2 hours)
```

### Weasyprint PDF Generation Fails

**Solution**: Check Dockerfile.geo has all dependencies
```dockerfile
libpango-1.0-0 \
libpangocairo-1.0-0 \
libgdk-pixbuf2.0-0 \
shared-mime-info
```

---

## Advanced Usage

### Custom Configuration

```bash
# Edit config
vim configs/paris_2022_mock.yml

# Deploy with custom config
gcloud run jobs execute heat-downscaling-pipeline \
  --region=europe-west1 \
  --args="--config,configs/paris_2022_mock.yml"
```

### View Logs

```bash
make logs

# Or directly
gcloud logging read \
  "resource.type=cloud_run_job AND resource.labels.job_name=heat-downscaling-pipeline" \
  --limit=100 \
  --format=json
```

### Check Deployment Status

```bash
make status
```

---

## Cleanup

```bash
# Delete Cloud Run Job
gcloud run jobs delete heat-downscaling-pipeline --region=europe-west1

# Delete outputs
gsutil -m rm -r gs://gh-exports-genhack-heat-dev/paris/

# Clean local artifacts
make clean
```

**Note**: Does NOT delete Phase 0 infrastructure (buckets, SA, KMS)

---

## Next Steps: Phase 2

Once Phase 1 is working:

1. **Real ERA5 data**: Implement Copernicus CDS API client
2. **Sentinel-2 imagery**: Integrate Google Earth Engine
3. **U-Net model**: Train downscaling model
4. **Multi-city**: Process Lyon, Marseille, Toulouse, Bordeaux
5. **Evaluation**: Compare with ground truth weather stations

**See**: `GENHACK_CLEAN_ROOM_DUPLICATION.md` Phase 2-4 roadmap

---

## Support

**Issues**: Check `docs/ARCHITECTURE_CLIMATE.md` for design details  
**Schemas**: See `docs/SCHEMAS.md` for data contracts  
**Contact**: queriauxrobin@gmail.com
