# GenHack 2025 – Chronos-WxC Backend API

Backend serverless pour la production et la diffusion d’indicateurs climatiques downscalés (stations, séries temporelles, heatmaps) consommés par le dashboard React.

---

## 🚀 Quick Start

### 1. Installation

```bash
# Cloner le repo
git clone https://github.com/Rqbln/GenHack4-Hackathon-Vertex.git
cd GenHack4-Hackathon-Vertex

# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements-api.txt
```

### 2. Télécharger les datasets

```bash
# Installer gdown pour télécharger depuis Google Drive
pip install gdown

# Télécharger tous les datasets (~12 GB)
python3 scripts/download_datasets.py

# Ou vérifier seulement ce qui existe
python3 scripts/download_datasets.py --check-only
```

**Note** : Les datasets sont également disponibles manuellement sur [Google Drive](https://drive.google.com/drive/folders/1_uMrrq63e0iYCFj8A6ehN58641sJZ2x1)

### 3. Exécuter l'ETL (optionnel pour dev local)

```bash
# Exécuter le pipeline ETL avec les vraies données
python3 scripts/run_etl_simple.py
```

### 4. Lancer l'API (dev)

```bash
# Lancer l'API simple (port 8000)
python3 src/api_simple.py
```

---

## 📁 Structure du projet

```
GenHack4-Hackathon-Vertex/
├── api/                  # Fonctions serverless Vercel (handler Python)
├── src/                  # ETL, baseline, fine-tuning
├── scripts/              # Utilitaires (download, ETL, métriques)
├── genhack/              # Méthode complète de downscaling (code + docs)
├── docs/                 # Documentation (méthodo, déploiement, tests)
├── results/              # Métriques et sorties modèle
└── datasets/             # Jeux de données bruts (ignorés)
```

---

## 📊 Datasets
- **ERA5-Land** (NetCDF, 2020-2025)  
- **Sentinel-2 NDVI** (GeoTIFF, 2019-2023)  
- **ECA&D** (stations, TX max quotidiennes)  
- **GADM** (limites administratives)  
→ voir `docs/DATASETS_ANALYSIS.md` et `docs/QUICK_START.md`.

---

## 🔧 API (serverless)
- `GET /health` — Health check  
- `GET /api/stations` — Stations météo (GeoJSON simplifié)  
- `GET /api/temperature?station_id=&start_date=&end_date=` — Série temporelle réaliste (génération ou données)  
- `GET /api/heatmap?date=&bbox=` — Heatmap synthétique réaliste (effet UHI, saisonnalité)  
- `GET /api/metrics` — Métriques (baseline vs modèle)  

---

## 📚 Documentation
- Méthode downscaling (résumé): `docs/GENHACK_METHOD.md`
- Détails complets: dossier `genhack/` (`TECHNICAL_METHODOLOGY`, `RESULTS_SUMMARY`, `ARCHITECTURE`)
- Rapport stratégique: `docs/GenHack2025_Report.md`
- Guide déploiement: `docs/DEPLOYMENT_GUIDE.md`
- Plan de test: `docs/TESTING_PLAN.md`

---

## 🧪 Tests

```bash
# Tests complets
bash scripts/tests/run_all_tests.sh

# Test API
bash scripts/test_api_complete.sh
```

---

## 🚀 Déploiement

Voir `docs/DEPLOYMENT_GUIDE.md` pour les instructions de déploiement (Docker, Cloud Run, Vercel).

---

## 📝 License

Voir `LICENSE` pour plus d'informations.
