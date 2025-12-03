# 📋 État des Lieux et Tâches Restantes - GenHack 2025

**Date** : 18 Décembre 2025  
**Statut** : Code structurellement complet, mais données réelles et entraînement non effectués

---

## ✅ Ce qui a été fait

### Backend
- ✅ Structure complète du code (ETL, gap_filling, baseline, finetuning, etc.)
- ✅ API simple fonctionnelle en local (`api_simple.py`)
- ✅ Tests de structure (13/13 modules)
- ✅ Documentation technique
- ✅ Métriques mockées (`results/all_metrics.json`)

### Frontend
- ✅ Application React 19 + Vite + Tailwind
- ✅ Composants Deck.gl (MapView, StationLayer, HeatmapLayer, etc.)
- ✅ Scrollytelling intégré
- ✅ Design system complet
- ✅ Build fonctionnel

### Infrastructure
- ✅ Configuration Vercel prête
- ✅ Scripts de test et d'intégration
- ✅ Documentation déploiement

---

## ❌ Ce qui n'a PAS été fait

### 1. 🔴 CRITIQUE : Utilisation des Vraies Données

**Problème** : Le code utilise des données mock, pas les vraies données dans `/datasets/`

**Données disponibles** :
```
/datasets/
├── main/
│   ├── derived-era5-land-daily-statistics/  # ERA5 NetCDF (2020-2025)
│   ├── sentinel2_ndvi/                      # Sentinel-2 NDVI GeoTIFF
│   └── gadm_410_europe.gpkg                 # GADM boundaries
├── ECA_blend_tx/                            # ECA&D stations (8572 fichiers)
└── ECA_blend_tx.zip                         # Archive ECA&D
```

**Tâches à faire** :
- [ ] **Modifier `src/etl.py`** pour charger les vraies données au lieu de générer des mocks
  - [ ] Charger ERA5 depuis `datasets/main/derived-era5-land-daily-statistics/`
  - [ ] Charger Sentinel-2 depuis `datasets/main/sentinel2_ndvi/`
  - [ ] Charger ECA&D depuis `datasets/ECA_blend_tx/` ou `ECA_blend_tx.zip`
  - [ ] Charger GADM depuis `datasets/main/gadm_410_europe.gpkg`
- [ ] **Tester l'ETL** avec les vraies données
- [ ] **Valider** que les données sont correctement alignées temporellement
- [ ] **Générer** les fichiers Zarr/NetCDF pour le training

**Fichiers à modifier** :
- `GenHack4-Hackathon-Vertex/src/etl.py` (actuellement utilise des chemins hardcodés)
- `GenHack4-Hackathon-Vertex/src/ingest.py` (actuellement génère des mocks)

---

### 2. 🔴 CRITIQUE : Entraînement du Modèle Prithvi WxC

**Problème** : Le modèle n'a jamais été entraîné. Le code existe mais n'a pas été exécuté.

**Tâches à faire** :
- [ ] **Télécharger Prithvi WxC** depuis Hugging Face
  ```bash
  # Le modèle fait ~9GB, nécessite GPU
  python3 src/prithvi_setup.py
  ```
- [ ] **Préparer le dataset** pour le fine-tuning
  ```bash
  python3 src/dataset_preparation.py
  ```
  - Créer les paires (LowRes ERA5, HighRes Sentinel-2, Target ECA&D)
  - Split train/validation
- [ ] **Lancer le fine-tuning** avec QLoRA
  ```bash
  python3 src/finetuning.py
  ```
  - Nécessite GPU (CUDA)
  - Peut prendre plusieurs heures
- [ ] **Sauvegarder le modèle** fine-tuné
- [ ] **Générer les prédictions** sur la période de test

**Fichiers à exécuter** :
- `GenHack4-Hackathon-Vertex/src/prithvi_setup.py`
- `GenHack4-Hackathon-Vertex/src/dataset_preparation.py`
- `GenHack4-Hackathon-Vertex/src/finetuning.py`

**Ressources nécessaires** :
- GPU avec CUDA (minimum 16GB VRAM recommandé)
- ~50GB d'espace disque pour le modèle et les données

---

### 3. 🟡 IMPORTANT : Génération des Vraies Métriques

**Problème** : Les métriques actuelles sont mockées dans `results/all_metrics.json`

**Tâches à faire** :
- [ ] **Exécuter le baseline model** sur les vraies données
  ```bash
  python3 src/baseline.py
  ```
- [ ] **Exécuter les métriques avancées** (Perkins Score, analyse spectrale)
  ```bash
  python3 src/advanced_metrics.py
  ```
- [ ] **Comparer** baseline vs Prithvi fine-tuné
- [ ] **Valider physiquement** les résultats (PINN)
  ```bash
  python3 src/physics_validation.py
  ```
- [ ] **Générer** le fichier `results/all_metrics.json` avec les vraies valeurs
- [ ] **Exporter** les graphiques et figures pour le rapport

**Fichiers à exécuter** :
- `GenHack4-Hackathon-Vertex/src/baseline.py`
- `GenHack4-Hackathon-Vertex/src/advanced_metrics.py`
- `GenHack4-Hackathon-Vertex/src/physics_validation.py`
- `GenHack4-Hackathon-Vertex/src/export_results.py`

---

### 4. 🟡 IMPORTANT : Déploiement Backend

**Problème** : L'API tourne uniquement en local

**Options de déploiement** :

#### Option A : Cloud Run (GCP) - Recommandé
- [ ] **Créer** un Dockerfile pour l'API
- [ ] **Configurer** Cloud Run
- [ ] **Déployer** l'API
- [ ] **Tester** les endpoints en production
- [ ] **Mettre à jour** l'URL dans le frontend

#### Option B : Vercel Serverless Functions
- [ ] **Créer** des fonctions serverless pour l'API
- [ ] **Adapter** le code pour Vercel
- [ ] **Déployer** sur Vercel
- [ ] **Tester** les endpoints

#### Option C : Railway / Render
- [ ] **Créer** un compte
- [ ] **Déployer** l'API
- [ ] **Configurer** les variables d'environnement

**Fichiers à créer/modifier** :
- `GenHack4-Hackathon-Vertex/Dockerfile` (si Cloud Run)
- `GenHack4-Hackathon-Vertex/vercel.json` (si Vercel)
- `GenHack4-Hackathon-Frontend/src/services/api.ts` (mettre à jour l'URL)

---

### 5. 🟢 MOYEN : Connexion Frontend aux Vraies Données

**Problème** : Le frontend utilise des données mockées

**Tâches à faire** :
- [ ] **Modifier** `src/services/api.ts` pour pointer vers l'API déployée
- [ ] **Tester** que les stations ECA&D s'affichent correctement
- [ ] **Tester** que les heatmaps utilisent les vraies données de température
- [ ] **Tester** que les graphiques temporels affichent les vraies séries
- [ ] **Valider** que le scrollytelling fonctionne avec les vraies données

**Fichiers à modifier** :
- `GenHack4-Hackathon-Frontend/src/services/api.ts`
- `GenHack4-Hackathon-Frontend/src/hooks/useHeatmapData.ts`
- `GenHack4-Hackathon-Frontend/src/components/MapView.tsx`

---

### 6. 🟢 MOYEN : Gap-Filling Sentinel-2

**Problème** : L'algorithme de gap-filling existe mais n'a pas été exécuté

**Tâches à faire** :
- [ ] **Exécuter** le gap-filling sur les vraies données Sentinel-2
  ```bash
  python3 src/gap_filling.py
  ```
- [ ] **Valider** la qualité du gap-filling
- [ ] **Sauvegarder** les rasters NDVI complétés

**Fichiers à exécuter** :
- `GenHack4-Hackathon-Vertex/src/gap_filling.py`

---

### 7. 🟢 MOYEN : Génération des Produits Finaux

**Tâches à faire** :
- [ ] **Générer** les time series complètes (NetCDF)
  ```bash
  python3 src/product_generation.py
  ```
- [ ] **Calculer** les indicateurs UHI par zone GADM
  ```bash
  python3 src/gadm_indicators.py
  ```
- [ ] **Exporter** tous les résultats pour le rapport

**Fichiers à exécuter** :
- `GenHack4-Hackathon-Vertex/src/product_generation.py`
- `GenHack4-Hackathon-Vertex/src/gadm_indicators.py`

---

## 🎯 Plan d'Action Prioritaire

### Phase 1 : Données Réelles (URGENT - 2-3h)
1. Modifier `src/etl.py` pour charger les vraies données
2. Tester l'ETL avec les données réelles
3. Valider l'alignement temporel

### Phase 2 : Baseline et Métriques (URGENT - 1-2h)
1. Exécuter le baseline model
2. Calculer les métriques baseline
3. Générer `results/all_metrics.json` avec vraies valeurs baseline

### Phase 3 : Entraînement Modèle (CRITIQUE - 4-8h si GPU disponible)
1. Télécharger Prithvi WxC
2. Préparer le dataset
3. Lancer le fine-tuning (nécessite GPU)
4. Générer les prédictions

**⚠️ Si pas de GPU disponible** :
- Utiliser Google Colab Pro ou Kaggle
- Ou utiliser un modèle pré-entraîné plus petit
- Ou se concentrer sur le baseline uniquement

### Phase 4 : Déploiement (IMPORTANT - 1-2h)
1. Déployer l'API (Cloud Run ou Vercel)
2. Mettre à jour le frontend
3. Tester l'intégration complète

### Phase 5 : Finalisation (1h)
1. Générer les produits finaux
2. Exporter les graphiques
3. Finaliser le rapport

---

## ⚠️ Contraintes et Limitations

### Ressources Nécessaires
- **GPU** : Nécessaire pour l'entraînement Prithvi (16GB+ VRAM recommandé)
- **Espace disque** : ~50GB pour le modèle et les données
- **Temps** : 8-12h pour l'entraînement complet

### Alternatives si Pas de GPU
1. **Utiliser Google Colab Pro** (GPU gratuit limité)
2. **Utiliser Kaggle** (GPU gratuit 30h/semaine)
3. **Se concentrer sur le baseline** uniquement
4. **Utiliser un modèle plus petit** (Prithvi-100M au lieu de 2.3B)

### Stratégie de Fallback
Si l'entraînement n'est pas possible :
- ✅ Présenter le baseline model (déjà implémenté)
- ✅ Expliquer l'architecture Prithvi (code prêt)
- ✅ Utiliser des prédictions mockées mais réalistes
- ✅ Mettre l'accent sur la méthodologie et l'innovation

---

## 📝 Checklist Finale

### Avant Soumission
- [ ] Vraies données chargées et validées
- [ ] Baseline model exécuté avec vraies métriques
- [ ] Modèle Prithvi entraîné (ou explication si impossible)
- [ ] API déployée et fonctionnelle
- [ ] Frontend connecté aux vraies données
- [ ] Métriques réelles dans `results/all_metrics.json`
- [ ] Rapport final avec vraies valeurs
- [ ] Vidéo démo avec vraies données
- [ ] Slides finalisées

---

## 🚀 Commandes Rapides

### Tester l'ETL avec vraies données
```bash
cd GenHack4-Hackathon-Vertex
python3 -c "
from src.etl import ETLPipeline
from pathlib import Path

etl = ETLPipeline(
    era5_dir=Path('../datasets/main/derived-era5-land-daily-statistics'),
    sentinel2_dir=Path('../datasets/main/sentinel2_ndvi'),
    ecad_zip=Path('../datasets/ECA_blend_tx.zip'),
    gadm_gpkg=Path('../datasets/main/gadm_410_europe.gpkg'),
    output_dir=Path('./data/processed'),
    city_name='Paris',
    country_code='FRA'
)
etl.run_etl()
"
```

### Lancer le baseline
```bash
cd GenHack4-Hackathon-Vertex
python3 scripts/generate_baseline_metrics.py
```

### Tester l'API localement
```bash
cd GenHack4-Hackathon-Vertex
python3 src/api_simple.py
# Dans un autre terminal
curl http://localhost:8000/health
```

---

**Dernière mise à jour** : 18 Décembre 2025

