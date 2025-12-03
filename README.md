# GenHack 2025 - Chronos-WxC Backend

**Modèles de Fondation Climatiques pour le Downscaling Urbain**

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

### 2. Télécharger les Datasets

```bash
# Installer gdown pour télécharger depuis Google Drive
pip install gdown

# Télécharger tous les datasets (~12 GB)
python3 scripts/download_datasets.py

# Ou vérifier seulement ce qui existe
python3 scripts/download_datasets.py --check-only
```

**Note** : Les datasets sont également disponibles manuellement sur [Google Drive](https://drive.google.com/drive/folders/1_uMrrq63e0iYCFj8A6ehN58641sJZ2x1)

### 3. Exécuter l'ETL

```bash
# Exécuter le pipeline ETL avec les vraies données
python3 scripts/run_etl_simple.py
```

### 4. Lancer l'API

```bash
# Lancer l'API simple (port 8000)
python3 src/api_simple.py
```

---

## 📁 Structure du Projet

```
GenHack4-Hackathon-Vertex/
├── src/                    # Code source principal
│   ├── etl.py             # Pipeline ETL complet
│   ├── etl_simple.py      # Pipeline ETL simplifié
│   ├── api_simple.py      # API HTTP simple
│   ├── baseline.py        # Modèle baseline
│   ├── finetuning.py      # Fine-tuning Prithvi WxC
│   └── ...
├── scripts/                # Scripts utilitaires
│   ├── download_datasets.py    # Téléchargement datasets
│   ├── run_etl_simple.py       # Exécution ETL
│   ├── calculate_real_baseline_metrics.py
│   └── ...
├── data/                   # Données
│   └── processed/         # Données traitées par l'ETL
├── results/               # Résultats et métriques
├── docs/                  # Documentation
│   ├── GenHack2025_Report.md
│   ├── REMAINING_TASKS.md
│   ├── ROADMAP_TODOS.md
│   ├── TESTING_PLAN.md
│   └── ...
└── datasets/              # Datasets bruts (à télécharger)
```

---

## 📊 Datasets

Les datasets sont téléchargés dans `datasets/` :

- **ERA5 Land Daily Statistics** : Données climatiques (2020-2025)
- **Sentinel-2 NDVI** : Indices de végétation (2019-2021)
- **ECA&D Stations** : Observations météo au sol
- **GADM Europe** : Limites administratives

Voir `docs/DATASETS_ANALYSIS.md` et `docs/QUICK_START.md` pour plus de détails.

---

## 🔧 API Endpoints

L'API simple expose les endpoints suivants :

- `GET /health` - Health check
- `GET /api/metrics` - Métriques baseline et Prithvi
- `GET /api/stations` - Stations météo
- `GET /api/metrics/comparison` - Comparaison baseline vs Prithvi
- `GET /api/metrics/advanced` - Métriques avancées
- `GET /api/validation/physics` - Validation physique

---

## 📚 Documentation

- **Rapport Principal** : `docs/GenHack2025_Report.md`
- **Roadmap** : `docs/ROADMAP_TODOS.md`
- **Tâches Restantes** : `docs/REMAINING_TASKS.md`
- **Plan de Test** : `docs/TESTING_PLAN.md`
- **Guide Déploiement** : `docs/DEPLOYMENT_GUIDE.md`
- **Statut Données Réelles** : `docs/STATUS_REAL_DATA.md`

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
