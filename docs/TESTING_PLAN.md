# Plan de Test Complet - GenHack 2025

**Date** : 17 Décembre 2025  
**Équipe** : Chronos-WxC  
**Objectif** : Valider toutes les fonctionnalités avant soumission finale

---

## 📋 Table des Matières

1. [Tests Backend](#tests-backend)
2. [Tests Frontend](#tests-frontend)
3. [Tests API](#tests-api)
4. [Tests Intégration](#tests-intégration)
5. [Tests Visualisations](#tests-visualisations)
6. [Tests Métriques](#tests-métriques)
7. [Tests End-to-End](#tests-end-to-end)

---

## 🔧 Tests Backend

### 1.1 ETL Pipeline

**Fichier** : `GenHack4-Hackathon-Vertex/src/etl.py`

**Commandes de test** :
```bash
cd GenHack4-Hackathon-Vertex
python3 scripts/tests/test_etl_simple.py
```

**Fonctionnalités à tester** :
- [ ] Chargement des limites de ville (GADM)
- [ ] Chargement des données ERA5 (NetCDF)
- [ ] Chargement des données NDVI (GeoTIFF)
- [ ] Chargement des stations ECA&D
- [ ] Alignement temporel
- [ ] Alignement spatial
- [ ] Sauvegarde en Zarr/NetCDF

**Résultat attendu** : ✅ Structure validée, pas d'erreurs de syntaxe

---

### 1.2 Gap-Filling (Random Forest)

**Fichier** : `GenHack4-Hackathon-Vertex/src/gap_filling.py`

**Commandes de test** :
```bash
cd GenHack4-Hackathon-Vertex
python3 scripts/tests/test_gap_filling_simple.py
```

**Fonctionnalités à tester** :
- [ ] Extraction de features spatiales
- [ ] Entraînement du modèle Random Forest
- [ ] Prédiction des pixels manquants
- [ ] Validation de la qualité du gap-filling

**Résultat attendu** : ✅ Structure validée, modèle peut être entraîné

---

### 1.3 Baseline Model

**Fichier** : `GenHack4-Hackathon-Vertex/src/baseline.py`

**Commandes de test** :
```bash
cd GenHack4-Hackathon-Vertex
python3 scripts/tests/test_baseline_simple.py
```

**Fonctionnalités à tester** :
- [ ] Interpolation bicubique
- [ ] Correction altitudinale
- [ ] Calcul RMSE
- [ ] Calcul MAE
- [ ] Calcul R²

**Résultat attendu** : ✅ Métriques calculables, pas d'erreurs

---

### 1.4 GADM Indicators

**Fichier** : `GenHack4-Hackathon-Vertex/src/gadm_indicators.py`

**Commandes de test** :
```bash
cd GenHack4-Hackathon-Vertex
python3 scripts/tests/test_gadm_simple.py
```

**Fonctionnalités à tester** :
- [ ] Chargement des données GADM
- [ ] Extraction de zones spécifiques
- [ ] Calcul de statistiques zonales
- [ ] Indicateurs température
- [ ] Indicateurs NDVI

**Résultat attendu** : ✅ Calculs d'indicateurs fonctionnels

---

### 1.5 Prithvi WxC Setup

**Fichier** : `GenHack4-Hackathon-Vertex/src/prithvi_setup.py`

**Commandes de test** :
```bash
cd GenHack4-Hackathon-Vertex
python3 scripts/tests/test_prithvi_simple.py
```

**Fonctionnalités à tester** :
- [ ] Téléchargement du modèle (si dépendances installées)
- [ ] Chargement du modèle
- [ ] Inférence simple
- [ ] Gestion gracieuse des dépendances manquantes

**Résultat attendu** : ✅ Structure validée, gestion d'erreurs OK

---

### 1.6 Dataset Preparation

**Fichier** : `GenHack4-Hackathon-Vertex/src/dataset_preparation.py`

**Commandes de test** :
```bash
cd GenHack4-Hackathon-Vertex
python3 scripts/tests/test_dataset_prep_simple.py
```

**Fonctionnalités à tester** :
- [ ] Création de paires (LowRes, HighRes, Target)
- [ ] Alignement temporel et spatial
- [ ] Split train/val/test
- [ ] Sauvegarde/chargement dataset

**Résultat attendu** : ✅ Structure validée, dataset préparable

---

### 1.7 Fine-Tuning (QLoRA)

**Fichier** : `GenHack4-Hackathon-Vertex/src/finetuning.py`

**Commandes de test** :
```bash
cd GenHack4-Hackathon-Vertex
python3 scripts/tests/test_finetuning_simple.py
```

**Fonctionnalités à tester** :
- [ ] Configuration QLoRA
- [ ] Setup modèle avec quantization
- [ ] Fonction de perte composite
- [ ] Training loop

**Résultat attendu** : ✅ Structure validée, configuration QLoRA OK

---

### 1.8 Model Analysis

**Fichier** : `GenHack4-Hackathon-Vertex/src/model_analysis.py`

**Commandes de test** :
```bash
cd GenHack4-Hackathon-Vertex
python3 scripts/tests/test_model_analysis_simple.py
```

**Fonctionnalités à tester** :
- [ ] Analyse historique d'entraînement
- [ ] Détection de convergence
- [ ] Détection d'overfitting
- [ ] Validation croisée spatiale
- [ ] Analyse sensibilité hyperparamètres

**Résultat attendu** : ✅ Structure validée, analyses possibles

---

### 1.9 Advanced Metrics

**Fichier** : `GenHack4-Hackathon-Vertex/src/advanced_metrics.py`

**Commandes de test** :
```bash
cd GenHack4-Hackathon-Vertex
python3 scripts/tests/test_advanced_metrics_simple.py
```

**Fonctionnalités à tester** :
- [ ] Calcul Perkins Skill Score
- [ ] Analyse spectrale (PSD)
- [ ] Comparaison avec baseline
- [ ] Calcul de toutes les métriques

**Résultat attendu** : ✅ Structure validée, métriques calculables

---

### 1.10 Physics Validation

**Fichier** : `GenHack4-Hackathon-Vertex/src/physics_validation.py`

**Commandes de test** :
```bash
cd GenHack4-Hackathon-Vertex
python3 scripts/tests/test_physics_validation_simple.py
```

**Fonctionnalités à tester** :
- [ ] Calcul NDBI
- [ ] Validation corrélation UHI-NDVI
- [ ] Validation corrélation UHI-NDBI
- [ ] Validation bilan énergétique
- [ ] Validation cohérence spatiale

**Résultat attendu** : ✅ Structure validée, validations possibles

---

### 1.11 Product Generation

**Fichier** : `GenHack4-Hackathon-Vertex/src/product_generation.py`

**Commandes de test** :
```bash
cd GenHack4-Hackathon-Vertex
python3 scripts/tests/test_product_generation_simple.py
```

**Fonctionnalités à tester** :
- [ ] Génération time series NetCDF
- [ ] Calcul indicateurs UHI
- [ ] Export rapports JSON
- [ ] Génération de tous les produits

**Résultat attendu** : ✅ Structure validée, exports possibles

---

### 1.12 Export Results

**Fichier** : `GenHack4-Hackathon-Vertex/src/export_results.py`

**Commandes de test** :
```bash
cd GenHack4-Hackathon-Vertex
python3 scripts/tests/test_export_results_simple.py
```

**Fonctionnalités à tester** :
- [ ] Export table métriques
- [ ] Génération graphiques comparaison
- [ ] Plot historique d'entraînement
- [ ] Export rapport résumé

**Résultat attendu** : ✅ Structure validée, exports possibles

---

### 1.13 Tests Backend Complets

**Commande** :
```bash
cd GenHack4-Hackathon-Vertex
python3 scripts/tests/test_all_days_1_4.py
```

**Résultat attendu** : ✅ 13/13 tests de structure passent

---

## 🎨 Tests Frontend

### 2.1 Build et Compilation

**Commande** :
```bash
cd GenHack4-Hackathon-Frontend
npm run build
```

**Vérifications** :
- [ ] Build réussit sans erreurs
- [ ] Pas d'erreurs TypeScript
- [ ] Pas d'erreurs de linting critiques
- [ ] Bundle généré dans `dist/`

**Résultat attendu** : ✅ Build réussi, warnings acceptables

---

### 2.2 MapView Component

**Fichier** : `GenHack4-Hackathon-Frontend/src/components/MapView.tsx`

**Test manuel** :
1. Démarrer le serveur : `npm run dev`
2. Ouvrir `http://localhost:5173`
3. Vérifier :
   - [ ] Carte s'affiche correctement
   - [ ] Fond de carte sombre visible
   - [ ] Zoom/Pan fonctionne
   - [ ] Stations météo visibles (points rouges)
   - [ ] Tooltip au survol des stations
   - [ ] Sélection de station fonctionne

**Résultat attendu** : ✅ Carte interactive fonctionnelle

---

### 2.3 StationLayer

**Fichier** : `GenHack4-Hackathon-Frontend/src/components/StationLayer.tsx`

**Test manuel** :
- [ ] Stations affichées sur la carte
- [ ] Couleur change au survol
- [ ] Tooltip affiche informations station
- [ ] Clic sur station sélectionne et affiche graphique

**Résultat attendu** : ✅ Interactions stations fonctionnelles

---

### 2.4 TimeSeriesChart

**Fichier** : `GenHack4-Hackathon-Frontend/src/components/TimeSeriesChart.tsx`

**Test manuel** :
- [ ] Graphique s'affiche après sélection station
- [ ] Données temporelles visibles
- [ ] Tooltip sur les points du graphique
- [ ] Clic sur point met à jour la date
- [ ] Zoom/Pan dans le graphique fonctionne

**Résultat attendu** : ✅ Graphiques temporels interactifs

---

### 2.5 TimelineSlider

**Fichier** : `GenHack4-Hackathon-Frontend/src/components/TimelineSlider.tsx`

**Test manuel** :
- [ ] Slider visible en bas de l'écran
- [ ] Déplacement du slider change la date
- [ ] Boutons navigation (début, fin, précédent, suivant) fonctionnent
- [ ] Sélection du pas temporel (jour, semaine, mois) fonctionne
- [ ] Date affichée correctement

**Résultat attendu** : ✅ Navigation temporelle fonctionnelle

---

### 2.6 HeatmapLayer

**Fichier** : `GenHack4-Hackathon-Frontend/src/components/HeatmapLayer.tsx`

**Test manuel** :
- [ ] Heatmap s'affiche sur la carte
- [ ] Couleurs varient selon l'intensité (bleu → rouge)
- [ ] Heatmap se met à jour avec la date
- [ ] Performance acceptable (pas de lag)

**Résultat attendu** : ✅ Heatmap dynamique fonctionnelle

---

### 2.7 SwipeMap

**Fichier** : `GenHack4-Hackathon-Frontend/src/components/SwipeMap.tsx`

**Test manuel** :
- [ ] Deux cartes affichées côte-à-côte
- [ ] Divider visible et draggable
- [ ] Drag du divider révèle différentes visualisations
- [ ] Labels affichés (ERA5 vs Prithvi)
- [ ] Instructions visibles

**Résultat attendu** : ✅ Comparaison swipe fonctionnelle

---

### 2.8 Scrollytelling

**Fichier** : `GenHack4-Hackathon-Frontend/src/components/Scrollytelling.tsx`

**Test manuel** :
- [ ] Panel narratif fixe à gauche
- [ ] Contenu scrollable à droite
- [ ] Changement de step au scroll
- [ ] Transitions de carte synchronisées
- [ ] Progress bar fonctionne
- [ ] Tous les 6 steps accessibles

**Résultat attendu** : ✅ Scrollytelling narratif fonctionnel

---

### 2.9 MapViewWithTransitions

**Fichier** : `GenHack4-Hackathon-Frontend/src/components/MapViewWithTransitions.tsx`

**Test manuel** :
- [ ] Transitions de caméra fluides
- [ ] FlyToInterpolator fonctionne
- [ ] Easing smooth (ease-in-out)
- [ ] Synchronisation avec scrollytelling

**Résultat attendu** : ✅ Transitions animées fluides

---

### 2.10 BackendConnectionStatus

**Fichier** : `GenHack4-Hackathon-Frontend/src/components/BackendConnectionStatus.tsx`

**Test manuel** :
- [ ] Indicateur visible en haut à droite
- [ ] Statut "Checking..." au démarrage
- [ ] Statut "Connected" si API disponible
- [ ] Statut "Offline" si API indisponible
- [ ] Mise à jour automatique toutes les 30s

**Résultat attendu** : ✅ Monitoring connexion fonctionnel

---

### 2.11 DemoMode

**Fichier** : `GenHack4-Hackathon-Frontend/src/components/DemoMode.tsx`

**Test manuel** :
- [ ] Bouton "Demo Mode" visible
- [ ] Activation affiche le panel
- [ ] Liste des fonctionnalités affichée
- [ ] Désactivation fonctionne

**Résultat attendu** : ✅ Mode démo fonctionnel

---

### 2.12 Animations et UI

**Fichier** : `GenHack4-Hackathon-Frontend/src/styles/animations.css`

**Test visuel** :
- [ ] Effets glassmorphism visibles
- [ ] Animations fade-in au chargement
- [ ] Animations slide-in-bottom pour timeline
- [ ] Hover effects fonctionnent
- [ ] Transitions fluides partout

**Résultat attendu** : ✅ UI polie et moderne

---

### 2.13 Performance

**Commande** :
```bash
cd GenHack4-Hackathon-Frontend
bash scripts/test_performance.sh
```

**Vérifications** :
- [ ] Bundle size acceptable
- [ ] Pas d'erreurs TypeScript
- [ ] Build rapide (< 5s)

**Résultat attendu** : ✅ Performance acceptable

---

## 🌐 Tests API

### 3.1 Démarrage API

**Commande** :
```bash
cd GenHack4-Hackathon-Vertex
pip install -r requirements-api.txt
python3 src/api.py
```

**Vérifications** :
- [ ] API démarre sur `http://localhost:8000`
- [ ] Pas d'erreurs au démarrage
- [ ] Documentation disponible sur `/docs`

**Résultat attendu** : ✅ API démarrée

---

### 3.2 Endpoints API

**Tests avec curl ou navigateur** :

#### Health Check
```bash
curl http://localhost:8000/health
```
- [ ] Retourne `{"status": "healthy"}`

#### Stations
```bash
curl http://localhost:8000/api/stations
```
- [ ] Retourne liste de stations
- [ ] Format JSON valide

#### Métriques
```bash
curl http://localhost:8000/api/metrics
```
- [ ] Retourne métriques complètes
- [ ] Baseline et Prithvi inclus

#### Comparaison
```bash
curl http://localhost:8000/api/metrics/comparison
```
- [ ] Retourne comparaison baseline vs Prithvi
- [ ] Améliorations calculées

#### Métriques Avancées
```bash
curl http://localhost:8000/api/metrics/advanced
```
- [ ] Retourne Perkins Score
- [ ] Retourne analyse spectrale

#### Validation Physique
```bash
curl http://localhost:8000/api/validation/physics
```
- [ ] Retourne résultats validation
- [ ] 4 validations incluses

#### Temperature
```bash
curl "http://localhost:8000/api/temperature?lat=48.8566&lon=2.3522&date=2020-01-01"
```
- [ ] Retourne prédiction température
- [ ] Coordonnées et date correctes

**Résultat attendu** : ✅ Tous les endpoints fonctionnent

---

## 🔗 Tests Intégration

### 4.1 Connexion Frontend-Backend

**Test manuel** :
1. Démarrer API : `python3 src/api.py` (port 8000)
2. Démarrer Frontend : `npm run dev` (port 5173)
3. Vérifier :
   - [ ] Indicateur connexion passe au vert
   - [ ] Stations chargées depuis API
   - [ ] Métriques affichées depuis API
   - [ ] Pas d'erreurs CORS

**Résultat attendu** : ✅ Intégration fonctionnelle

---

### 4.2 Flux Complet

**Scénario de test** :
1. [ ] Charger le dashboard
2. [ ] Vérifier connexion backend
3. [ ] Sélectionner une station
4. [ ] Vérifier graphique temporel
5. [ ] Changer la date avec timeline
6. [ ] Vérifier mise à jour heatmap
7. [ ] Tester scrollytelling
8. [ ] Tester SwipeMap

**Résultat attendu** : ✅ Flux complet fonctionnel

---

## 📊 Tests Visualisations

### 5.1 Carte Interactive

**Test visuel** :
- [ ] Fond de carte sombre lisible
- [ ] Stations visibles et cliquables
- [ ] Heatmap colorée et lisible
- [ ] Zoom/Pan fluides
- [ ] Pas de lag

**Résultat attendu** : ✅ Visualisations performantes

---

### 5.2 Graphiques Temporels

**Test visuel** :
- [ ] Axes lisibles
- [ ] Courbes lisses
- [ ] Couleurs distinctes
- [ ] Tooltips informatifs
- [ ] Zoom/Pan fonctionnels

**Résultat attendu** : ✅ Graphiques clairs

---

### 5.3 Scrollytelling

**Test visuel** :
- [ ] Panel narratif lisible
- [ ] Transitions fluides
- [ ] Carte synchronisée
- [ ] Progress bar visible
- [ ] Tous les steps accessibles

**Résultat attendu** : ✅ Expérience narrative fluide

---

## 📈 Tests Métriques

### 6.1 Calcul Métriques

**Commande** :
```bash
cd GenHack4-Hackathon-Vertex
python3 scripts/run_all_metrics.py
```

**Vérifications** :
- [ ] Script s'exécute sans erreur
- [ ] Métriques calculées
- [ ] Fichier JSON généré dans `results/all_metrics.json`
- [ ] Baseline et Prithvi inclus
- [ ] Perkins Score calculé
- [ ] Validation physique incluse

**Résultat attendu** : ✅ Toutes les métriques calculées

---

### 6.2 Validation Métriques

**Vérifier dans `results/all_metrics.json`** :
- [ ] Baseline RMSE ≈ 2.45°C
- [ ] Prithvi RMSE ≈ 1.52°C
- [ ] Amélioration RMSE ≈ 38%
- [ ] Perkins Score ≈ 0.84
- [ ] Validation physique : 4/4 passées

**Résultat attendu** : ✅ Métriques cohérentes

---

## 🎯 Tests End-to-End

### 7.1 Scénario Complet

**Workflow** :
1. [ ] Démarrer backend API
2. [ ] Démarrer frontend
3. [ ] Charger dashboard
4. [ ] Naviguer dans scrollytelling
5. [ ] Sélectionner station
6. [ ] Explorer données temporelles
7. [ ] Comparer ERA5 vs Prithvi (SwipeMap)
8. [ ] Vérifier métriques affichées
9. [ ] Tester toutes les interactions

**Résultat attendu** : ✅ Expérience utilisateur complète

---

### 7.2 Tests Cross-Browser

**Navigateurs à tester** :
- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari (si Mac disponible)

**Vérifications** :
- [ ] Dashboard s'affiche correctement
- [ ] Interactions fonctionnent
- [ ] Performance acceptable
- [ ] Pas d'erreurs console

**Résultat attendu** : ✅ Compatible multi-navigateurs

---

### 7.3 Tests Responsive

**Résolutions à tester** :
- [ ] Desktop (1920x1080)
- [ ] Laptop (1366x768)
- [ ] Tablet (768x1024)
- [ ] Mobile (375x667)

**Vérifications** :
- [ ] Layout s'adapte
- [ ] Interactions tactiles fonctionnent
- [ ] Textes lisibles
- [ ] Pas de débordements

**Résultat attendu** : ✅ Responsive design fonctionnel

---

## ✅ Checklist Finale

### Avant Soumission
- [ ] Tous les tests backend passent (13/13)
- [ ] Build frontend réussi
- [ ] Tous les composants testés
- [ ] API fonctionnelle
- [ ] Intégration validée
- [ ] Métriques calculées
- [ ] Tests E2E passés
- [ ] Cross-browser testé
- [ ] Responsive validé

---

## 🚀 Commandes Rapides

### Tests Backend Complets
```bash
cd GenHack4-Hackathon-Vertex
python3 scripts/tests/test_all_days_1_4.py
```

### Tests Frontend
```bash
cd GenHack4-Hackathon-Frontend
npm run build
bash scripts/test_performance.sh
```

### Démarrage Complet
```bash
# Terminal 1 - Backend API
cd GenHack4-Hackathon-Vertex
python3 src/api.py

# Terminal 2 - Frontend
cd GenHack4-Hackathon-Frontend
npm run dev
```

### Calcul Métriques
```bash
cd GenHack4-Hackathon-Vertex
python3 scripts/run_all_metrics.py
```

---

*Plan de test créé le 17 Décembre 2025*

