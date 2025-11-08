# 🌡️ GenHack4 – Climate Heat Downscaling Pipeline

[![Cloud Run](https://img.shields.io/badge/Cloud%20Run-Deployed-blue)](https://console.cloud.google.com/run/jobs?project=genhack-heat-dev)  
**Phase 1**: Mock data pipeline with complete infrastructure and contracts.  

[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://console.cloud.google.com/artifacts/docker/genhack-heat-dev/europe/heat)  
**Phase 2+**: Real ERA5/Sentinel-2 data + U-Net/SRGAN models.

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)

---

> Pipeline de downscaling climatique pour la détection et l’analyse des îlots de chaleur urbains avec données mock (Phase 1).

---

## 🎯 Objectif

Système de traitement géospatial automatisé pour :

- Ingérer des données climatiques (température, humidité, vent)
- Calculer des indices spectraux (NDVI, NDBI)
- Générer des indicateurs de chaleur (intensité, durée, étendue, UHI)
- Produire des rapports HTML/PDF avec cartes et statistiques
- Exporter des GeoTIFF Cloud Optimized

---

## 🚀 Quick Start (< 2 minutes)

```bash
# 1. Initialize infrastructure (check Phase 0 setup)
make init

# 2. Build Docker image
make build

# 3. Deploy to Cloud Run
make deploy

# 4. Execute pipeline
make run

# 5. View outputs
gsutil ls gs://gh-exports-genhack-heat-dev/paris/2022/
```

Output: GeoTIFF temperature maps + NDVI/NDBI indices + HTML/PDF report

⸻

📋 Project Structure
```
genhack-heat/
├── src/                 # Pipeline modules
│   ├── models.py        # Pydantic data models
│   ├── ingest.py        # Data ingestion (Phase 1: mock)
│   ├── preprocess.py    # Reprojection & resampling
│   ├── features.py      # Spectral indices (NDVI, NDBI)
│   ├── train.py         # Model training (Phase 2+)
│   ├── evaluate.py      # Metrics computation
│   ├── indicators.py    # Heat indicators
│   ├── publish.py       # GeoTIFF export
│   └── report.py        # HTML/PDF generation
│
├── pipeline/
│   ├── job_main.py      # Orchestrator
│   ├── Dockerfile.geo   # GDAL + geospatial stack
│   └── requirements.txt
│
├── configs/
│   └── paris_2022_mock.yml  # Pipeline configuration
│
├── schemas/             # JSON schemas for contracts
├── templates/           # Jinja2 report templates
├── tests/               # Contract validation tests
├── infra/               # Deployment scripts
│   ├── init-genhack.sh
│   └── deploy_job.sh
├── .github/workflows/   # CI/CD
│   └── build_deploy.yml
└── Makefile             # Development commands
```

⸻

🔧 Requirements
	•	GCP Project: genhack-heat-dev (Phase 0 setup complete)
	•	Docker: For local builds
	•	gcloud CLI: For deployment
	•	Python 3.11+: For local testing

⸻

🏗️ Architecture
```
┌─────────────────┐
│  Cloud Run Job  │
│  (genhack-heat) │
└────────┬────────┘
         │
    ┌────▼────┐
    │ Docker  │
    │ Image   │
    └────┬────┘
         │
    ┌────▼────────────────────────────────┐
    │  Pipeline (8 stages)                │
    ├─────────────────────────────────────┤
    │  1. Ingest    → Mock data           │
    │  2. Preprocess → Reprojection       │
    │  3. Features  → NDVI/NDBI           │
    │  4. Train     → (Phase 2)           │
    │  5. Evaluate  → Metrics             │
    │  6. Indicators → Heat stats         │
    │  7. Publish   → GeoTIFF/PNG         │
    │  8. Report    → HTML/PDF            │
    └─────────────────────────────────────┘
```

⸻

📊 Pipeline Stages
	1.	Ingest → Generate/download climate data
	2.	Preprocess → Reproject to target CRS
	3.	Features → Compute NDVI, NDBI indices
	4.	Train → Model training (Phase 2+)
	5.	Evaluate → Compute metrics
	6.	Indicators → Heat intensity, UHI, extent
	7.	Publish → Export GeoTIFF + PNG previews
	8.	Report → Generate HTML/PDF

⸻

🛠️ Technologies

Stack Géospatial
	•	GDAL 3.x – Manipulation rasters
	•	PROJ 9.x – Transformations coordonnées
	•	rasterio – I/O rasters Python
	•	xarray – Arrays multidimensionnels
	•	geopandas – Données vectorielles

Reporting
	•	Jinja2 – Templates HTML
	•	Weasyprint – Génération PDF
	•	matplotlib – Visualisations

⸻

📐 Data Contracts

All stages communicate via validated JSON schemas:
	•	Manifest: City, period, grid, variables
	•	RasterMetadata: CRS, transform, bounds, dtype
	•	Metrics: RMSE, MAE, R², baseline comparison
	•	Indicators: Heat intensity, duration, extent, UHI

Run tests:
```bash
make test
pytest tests/test_contracts.py -v
```

⸻

📊 Outputs

La pipeline génère :
	•	GeoTIFF : Rasters temperature, NDVI, NDBI (Cloud Optimized)
	•	PNG : Prévisualisations avec cartes de chaleur
	•	JSON : Indicateurs, métriques, métadonnées
	•	HTML/PDF : Rapports complets avec visualisations

⸻

🔒 Security & Isolation

✅ Clean-room duplication from Kura project
✅ Separate GCP project (genhack-heat-dev)
✅ No shared resources (buckets, SAs, KMS)
✅ CI/CD checks block any Kura references

⸻

🧪 Tests

# Tests de validation des schemas
make test

# Vérification de l'infrastructure
bash infra/init-genhack.sh

Phase 1 Complete → Ready for Phase 2 (real data ingestion)

⸻

📈 Métriques Pipeline
	•	⏱️ Temps d’exécution : 2.4s (Phase 1 mock)
	•	💾 Taille image : ~2.0 GB
	•	🔄 Build time : ~2 min (première fois), ~5s (cache)

⸻

🌍 Configuration
```
city: "paris"
period:
  start: "2022-07-15"
  end: "2022-07-17"
grid:
  crs: "EPSG:3857"
  resolution_m: 200
variables: ["t2m", "tx", "tn", "rh"]
mode:
  dry_run: true  # Phase 1: mock data
```

⸻

🚦 Statut

Composant	Statut
Infrastructure (Phase 0)	✅ Complet
Pipeline Mock (Phase 1)	✅ Déployé
Cloud Run Job	✅ Actif
Docker Image	✅ Publié
CI/CD	✅ Configuré
Phase 2 (données réelles)	🔜 À venir


⸻

🎯 Roadmap Phase 2
	•	Ingestion ERA5 (Copernicus CDS API)
	•	Intégration Sentinel-2 (Google Earth Engine)
	•	Extraction features OSM
	•	Modèle U-Net pour downscaling
	•	Upload outputs vers GCS
	•	API REST

⸻

📚 Documentation
	•	ARCHITECTURE.md￼ – System design
	•	SCHEMAS.md￼ – Data contracts
	•	REPRODUCE.md￼ – Step-by-step reproduction

⸻

🔐 Sécurité
	•	✅ Isolation complète : Projet GCP dédié (genhack-heat-dev)
	•	✅ CMEK : Chiffrement avec Cloud KMS
	•	✅ Service Account : Permissions minimales
	•	✅ CI/CD : Vérification sécurité automatique

⸻

🤝 Contributing

This is a hackathon project for GenHack 2025 (climate track).
Clean-room duplication from Kura mental health project.

License: Apache 2.0
Author: Robin Quériaux
Contact: queriauxrobin@gmail.com

Dernière mise à jour : 8 novembre 2025
Version Pipeline : 1.0.0 (Phase 1 - Mock Data)

⸻

🎯 Next Steps (Phase 2)
	1.	Real ERA5 data ingestion via Copernicus API
	2.	Sentinel-2 imagery download from Google Earth Engine
	3.	U-Net model training for downscaling
	4.	Multi-city heat analysis
	5.	Population exposure estimates

See: GENHACK_CLEAN_ROOM_DUPLICATION.md for full roadmap
