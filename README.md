# GenHack4 - Climate Heat Downscaling Pipeline# 🌡️ GenHack Climate Heat Downscaling



[![Cloud Run](https://img.shields.io/badge/Cloud%20Run-Deployed-blue)](https://console.cloud.google.com/run/jobs?project=genhack-heat-dev)**Phase 1**: Mock data pipeline with complete infrastructure and contracts.  

[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://console.cloud.google.com/artifacts/docker/genhack-heat-dev/europe/heat)**Phase 2+**: Real ERA5/Sentinel-2 data + U-Net/SRGAN models.

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)

---

> Pipeline de downscaling climatique pour la détection et l'analyse des îlots de chaleur urbains avec données mock (Phase 1).

## 🎯 Quick Start (< 2 minutes)

## 🎯 Objectif

```bash

Système de traitement géospatial automatisé pour :# 1. Initialize infrastructure (check Phase 0 setup)

- Ingérer des données climatiques (température, humidité, vent)make init

- Calculer des indices spectraux (NDVI, NDBI)

- Générer des indicateurs de chaleur (intensité, durée, étendue, UHI)# 2. Build Docker image

- Produire des rapports HTML/PDF avec cartes et statistiquesmake build

- Exporter des GeoTIFF Cloud Optimized

# 3. Deploy to Cloud Run

## 🚀 Quick Startmake deploy



### Exécuter la pipeline sur Cloud Run# 4. Execute pipeline

make run

```bash

# Déployer le job# 5. View outputs

make deploygsutil ls gs://gh-exports-genhack-heat-dev/paris/2022/

```

# Exécuter la pipeline

make run**Output**: GeoTIFF temperature maps + NDVI/NDBI indices + HTML/PDF report



# Voir les logs---

make logs

```## 📋 Project Structure



### Développement local```

genhack-heat/

```bash├── src/               # Pipeline modules

# Installation│   ├── models.py      # Pydantic data models

make init│   ├── ingest.py      # Data ingestion (Phase 1: mock)

│   ├── preprocess.py  # Reprojection & resampling

# Build de l'image Docker│   ├── features.py    # Spectral indices (NDVI, NDBI)

make build│   ├── train.py       # Model training (Phase 2+)

│   ├── evaluate.py    # Metrics computation

# Test en local (dry-run)│   ├── indicators.py  # Heat indicators

make dryrun│   ├── publish.py     # GeoTIFF export

```│   └── report.py      # HTML/PDF generation

├── pipeline/

## 📋 Prérequis│   ├── job_main.py    # Orchestrator

│   ├── Dockerfile.geo # GDAL + geospatial stack

- **GCP Project**: `genhack-heat-dev`│   └── requirements.txt

- **Docker**: Pour le build local├── configs/

- **gcloud CLI**: Configuré avec les bonnes permissions│   └── paris_2022_mock.yml  # Pipeline configuration

- **Python 3.11+**: Pour le développement local├── schemas/           # JSON schemas for contracts

├── templates/         # Jinja2 report templates

## 🏗️ Architecture├── tests/             # Contract validation tests

├── infra/             # Deployment scripts

```│   ├── init-genhack.sh

┌─────────────────┐│   └── deploy_job.sh

│  Cloud Run Job  │├── .github/workflows/ # CI/CD

│  (genhack-heat) ││   └── build_deploy.yml

└────────┬────────┘└── Makefile           # Development commands

         │```

    ┌────▼────┐

    │ Docker  │---

    │ Image   │

    └────┬────┘## 🔧 Requirements

         │

    ┌────▼────────────────────────────────┐- **GCP Project**: `genhack-heat-dev` (Phase 0 setup complete)

    │  Pipeline (8 stages)                │- **Docker**: For local builds

    ├─────────────────────────────────────┤- **gcloud CLI**: For deployment

    │  1. Ingest    → Mock data           │- **Python 3.11+**: For local testing

    │  2. Preprocess → Reprojection       │

    │  3. Features  → NDVI/NDBI           │---

    │  4. Train     → (Phase 2)           │

    │  5. Evaluate  → Metrics             │## 🚀 Deployment

    │  6. Indicators → Heat stats         │

    │  7. Publish   → GeoTIFF/PNG         │### Local Testing (Dry-run)

    │  8. Report    → HTML/PDF            │

    └─────────────────────────────────────┘```bash

```# Run pipeline locally with mock data

make dryrun

## 📦 Structure du Projet

# Check outputs

```ls /tmp/genhack/exports/paris/

.```

├── src/                    # Modules Python de la pipeline

│   ├── models.py          # Modèles Pydantic### Cloud Run Job

│   ├── ingest.py          # Génération données mock

│   ├── preprocess.py      # Reprojection rasters```bash

│   ├── features.py        # Indices spectraux# Full deployment

│   ├── indicators.py      # Statistiques chaleurmake deploy

│   ├── publish.py         # Export GeoTIFF/PNG

│   └── report.py          # Génération rapports# Execute job

├── pipeline/make run

│   ├── job_main.py        # Orchestrateur

│   ├── Dockerfile.geo     # Image avec stack géospatial# View logs

│   └── requirements.txt   # Dépendances Pythonmake logs

├── configs/

│   └── paris_2022_mock.yml # Configuration pipeline# Check status

├── schemas/               # Contrats JSON Schemamake status

├── templates/             # Templates Jinja2```

├── infra/                 # Scripts déploiement

├── tests/                 # Tests unitaires---

└── docs/                  # Documentation

```## 📊 Pipeline Stages



## 🛠️ Technologies1. **Ingest** → Generate/download climate data

2. **Preprocess** → Reproject to target CRS

### Stack Géospatial3. **Features** → Compute NDVI, NDBI indices

- **GDAL 3.x** - Manipulation rasters4. **Train** → Model training (Phase 2+)

- **PROJ 9.x** - Transformations coordonnées5. **Evaluate** → Compute metrics

- **rasterio** - I/O rasters Python6. **Indicators** → Heat intensity, UHI, extent

- **xarray** - Arrays multidimensionnels7. **Publish** → Export GeoTIFF + PNG previews

- **geopandas** - Données vectorielles8. **Report** → Generate HTML/PDF



### Reporting---

- **Jinja2** - Templates HTML

- **Weasyprint** - Génération PDF## 📐 Data Contracts

- **matplotlib** - Visualisations

All stages communicate via validated JSON schemas:

### Infrastructure

- **Cloud Run Jobs** - Exécution serverless- **Manifest**: City, period, grid, variables

- **Artifact Registry** - Stockage images Docker- **RasterMetadata**: CRS, transform, bounds, dtype

- **Cloud KMS** - Chiffrement données- **Metrics**: RMSE, MAE, R², baseline comparison

- **Indicators**: Heat intensity, duration, extent, UHI

## 📊 Outputs

Run tests: `make test` or `pytest tests/test_contracts.py -v`

La pipeline génère :

---

- **GeoTIFF** : Rasters temperature, NDVI, NDBI (Cloud Optimized)

- **PNG** : Prévisualisations avec cartes de chaleur## 🔒 Security & Isolation

- **JSON** : Indicateurs, métriques, métadonnées

- **HTML/PDF** : Rapports complets avec visualisations✅ **Clean-room duplication** from Kura project  

✅ **Separate GCP project** (genhack-heat-dev)  

## 🔧 Configuration✅ **No shared resources** (buckets, SAs, KMS)  

✅ **CI/CD checks** block any Kura references  

Voir `configs/paris_2022_mock.yml` pour la configuration de la pipeline.

Verify: `make verify`

## 📖 Documentation

---

- **[Architecture](docs/ARCHITECTURE_CLIMATE.md)** - Design système détaillé

- **[Schemas](docs/SCHEMAS.md)** - Contrats de données## 📈 Phase 1 Status

- **[Reproduction](docs/REPRODUCE.md)** - Guide pas-à-pas

- **[Setup](docs/setup/PHASE0_COMPLETE.md)** - Infrastructure GCP- ✅ Infrastructure deployed (Phase 0)

- ✅ Docker image with GDAL/rasterio/xarray

## 🧪 Tests- ✅ Mock data pipeline (ingest → report)

- ✅ JSON schemas + Pydantic models

```bash- ✅ Cloud Run Job deployment

# Tests de validation des schemas- ✅ CI/CD with security checks

make test- ✅ HTML/PDF report generation



# Vérification de l'infrastructure**Phase 1 Complete** → Ready for Phase 2 (real data ingestion)

bash infra/init-genhack.sh

```---



## 📈 Métriques Pipeline## 🌍 Configuration



- ⏱️ **Temps d'exécution** : 2.4s (Phase 1 mock)Edit `configs/paris_2022_mock.yml`:

- 💾 **Taille image** : ~2.0 GB

- 🔄 **Build time** : ~2 min (première fois), ~5s (cache)```yaml

city: "paris"

## 🚦 Statutperiod:

  start: "2022-07-15"

| Composant | Statut |   end: "2022-07-17"

|-----------|--------|grid:

| Infrastructure (Phase 0) | ✅ Complet |  crs: "EPSG:3857"

| Pipeline Mock (Phase 1) | ✅ Déployé |  resolution_m: 200

| Cloud Run Job | ✅ Actif |variables: ["t2m", "tx", "tn", "rh"]

| Docker Image | ✅ Publié |mode:

| CI/CD | ✅ Configuré |  dry_run: true  # Phase 1: mock data

| Phase 2 (données réelles) | 🔜 À venir |```



## 🎯 Roadmap Phase 2---



- [ ] Ingestion ERA5 (Copernicus CDS API)## 📚 Documentation

- [ ] Intégration Sentinel-2 (Google Earth Engine)

- [ ] Extraction features OSM- [ARCHITECTURE.md](docs/ARCHITECTURE_CLIMATE.md) - System design

- [ ] Modèle U-Net pour downscaling- [SCHEMAS.md](docs/SCHEMAS.md) - Data contracts

- [ ] Upload outputs vers GCS- [REPRODUCE.md](docs/REPRODUCE.md) - Step-by-step reproduction

- [ ] API REST

---

## 🔐 Sécurité

## 🤝 Contributing

- ✅ **Isolation complète** : Projet GCP dédié (`genhack-heat-dev`)

- ✅ **CMEK** : Chiffrement avec Cloud KMSThis is a hackathon project for **GenHack 2025** (climate track).  

- ✅ **Service Account** : Permissions minimalesClean-room duplication from Kura mental health project.

- ✅ **CI/CD** : Vérification sécurité automatique

**License**: Apache 2.0  

## 📝 License**Author**: Robin Queriaux  

**Contact**: queriauxrobin@gmail.com

MIT License

---

---

## 🎯 Next Steps (Phase 2)

**Dernière mise à jour** : 8 novembre 2025  

**Version Pipeline** : 1.0.0 (Phase 1 - Mock Data)1. Real ERA5 data ingestion via Copernicus API

2. Sentinel-2 imagery download from Google Earth Engine
3. U-Net model training for downscaling
4. Multi-city heat analysis
5. Population exposure estimates

**See**: `GENHACK_CLEAN_ROOM_DUPLICATION.md` for full roadmap
