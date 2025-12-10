# GenHack Climate Downscaling Method (Residual Learning)

## Vue d’ensemble
- **Objectif** : Affiner les températures ERA5 (9 km) en cartes haute résolution (~80 m) pour capturer les effets urbains (UHI).
- **Approche** : Apprentissage résiduel — le modèle prédit uniquement l’écart entre ERA5 et les observations stations, puis on corrige ERA5.
- **Statut** : ✅ Pipeline complet (données → entraînement → inférence → évaluation) opérationnel et documenté.

## Données utilisées
- **Stations ECA&D** (`datasets/main/ECA_blend_tx/`) : TX max quotidiennes + métadonnées stations.
- **ERA5-Land** (`datasets/main/derived-era5-land-daily-statistics/`) : t2m max quotidien (~9 km).
- **Sentinel-2 NDVI** (`datasets/main/sentinel2_ndvi/`) : NDVI 80 m, base des grilles haute résolution.

## Pipeline en 4 phases
1) **Préparation** (`src/data_preparation.py`)
   - Parse stations (DMS→decimal), QC sur TX, jointure ERA5 (interpolation), extraction NDVI/Elevation, calcul résidu `Station_Temp - ERA5_Temp`.
2) **Entraînement** (`src/modeling.py`)
   - Cross-validation spatiale (split par stations), modèles RF/XGBoost, features : ERA5_Temp, NDVI, Elevation, Lat, Lon, DayOfYear.
3) **Inférence** (`src/inference.py`)
   - Upsampling ERA5 (bicubique 9 km → 80 m), prédiction résidu pixel-wise (≈93 M pixels), sortie GeoTIFF haute résolution.
4) **Évaluation** (`src/visualization.py`)
   - RMSE/MAE/R², comparaisons baseline, distributions d’erreurs, importance des features, cartes résidu/haute résolution.

## Résultats clés (Suède, juin 2020)
- **Baseline ERA5** : RMSE 2.45 °C, MAE 1.85 °C.
- **Modèle résiduel (Random Forest 200 arbres)** : RMSE 1.24 °C, MAE 0.88 °C.
- **Gain** : −1.21 °C (−49.5 % RMSE) sur stations tenues à l’écart (split spatial).
- **Sorties générées** : GeoTIFF 80 m (3 cartes d’exemple), métriques complètes (`outputs/evaluation*`), modèle sérialisé (`outputs/residual_model.pkl`).

## Commandes essentielles
```bash
# Installation
python -m venv venv && source venv/bin/activate
pip install -r Genhack/requirements.txt  # dépendances méthode

# Pipeline complet (exemple Suède 2020-2023)
cd Genhack/src
python main.py --country SE --start 2020-01-01 --end 2023-12-31 --generate-maps \
  --inference-start 2023-07-15 --inference-end 2023-07-20

# Tests rapides
cd Genhack/tests && python test_pipeline.py
```

## Où trouver le détail
- **README (utilisation)** : `Genhack/README.md`
- **Méthodo détaillée** : `Genhack/TECHNICAL_METHODOLOGY.md`
- **Synthèse implementation** : `Genhack/SUMMARY.md`
- **Résultats & métriques** : `Genhack/RESULTS_SUMMARY.md`
- **Architecture** : `Genhack/ARCHITECTURE.md`

## Intégration avec l’API backend
- Les sorties haute résolution peuvent être servies via les endpoints API existants (voir `api/index.py`) en exposant les GeoTIFF/NetCDF produits par le pipeline.
- Les fonctions de génération peuvent être orchestrées depuis `scripts/run_etl_simple.py` ou un job dédié (CRON/Celery) pour régénérer les cartes.

## État final
- Code, données, entraînement, inférence, évaluation : **terminés**.
- Documentation consolidée dans `docs/` et dossier `Genhack/`.


