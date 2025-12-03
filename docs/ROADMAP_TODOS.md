# 🗺️ Roadmap GenHack 2025 - Liste de Todos Détaillée

> **Basé sur** : `GenHack2025_Report.md` - Section 5  
> **Période** : 01 Décembre - 20 Décembre 2025  
> **Objectif** : Exécution millimétrée de la stratégie Chronos-WxC

---

## 📊 Vue d'ensemble

- **Phase 1** : Consolidation des Données et Baseline (01-07 Déc) - **7 jours**
- **Phase 2** : Innovation et "Heavy Lifting" (08-14 Déc) - **7 jours**
- **Phase 3** : Finalisation et Rendu Final (15-20 Déc) - **6 jours**

**Total** : 20 jours de développement intensif

---

## 🚀 Phase 1 : Consolidation des Données et Baseline

**Objectif** : Sécuriser les flux de données et avoir une première version fonctionnelle (MVP).

### 📅 Jour 1 - 01 Décembre

#### Backend / Data Science
- [ ] **Script ETL robuste**
  - [ ] Téléchargement et alignement temporel ERA5/Sentinel-2/ECA&D
  - [ ] Stockage structuré (NetCDF/Zarr)
  - [ ] Validation de l'intégrité des données

#### Frontend / Visualisation
- [ ] **Init React 19 + Vite + Tailwind**
  - [ ] Setup projet avec Vite
  - [ ] Configuration Tailwind CSS
  - [ ] Structure de base des composants
- [ ] **Setup MapLibre + Deck.gl**
  - [ ] Installation des dépendances
  - [ ] Configuration de la base map
  - [ ] Test d'affichage basique
- [ ] **Affichage fond de carte custom (Dark Mode)**
  - [ ] Style personnalisé
  - [ ] Thème sombre

**Livrable** : Pipeline Data v1. Carte Hello World.

---

### 📅 Jour 2 - 02 Décembre

#### Backend / Data Science
- [ ] **Algorithme Gap-Filling (Random Forest)**
  - [ ] Entraînement sur Sentinel-2 pour combler les nuages
  - [ ] Production des cartes NDVI complètes
  - [ ] Validation de la qualité du gap-filling

#### Frontend / Visualisation
- [ ] **Composant StationLayer (Scatterplot)**
  - [ ] Visualisation des stations ECA&D
  - [ ] Tooltips interactifs avec informations détaillées
  - [ ] Intégration avec la carte Deck.gl

**Livrable** : Rasters NDVI propres. Viz Stations.

---

### 📅 Jour 3 - 03 Décembre

#### Backend / Data Science
- [ ] **Baseline Model**
  - [ ] Implémentation interpolation bicubique
  - [ ] Correction altitudinale
  - [ ] Calcul RMSE baseline (Benchmark Pentagen)
  - [ ] Documentation des métriques

#### Frontend / Visualisation
- [ ] **Graphiques temporels (Recharts/Nivo)**
  - [ ] Intégration bibliothèque de graphiques
  - [ ] Connexion aux stations sélectionnées sur la carte
  - [ ] Affichage des séries temporelles

**Livrable** : Baseline chiffrée. Dashboard Interactif v0.1.

---

### 📅 Jour 4 - 04 Décembre

#### Backend / Data Science
- [ ] **Extraction des mailles GADM**
  - [ ] Calcul des indicateurs par zone (moyennes spatiales)
  - [ ] Optimisation vecteurs (GeoArrow)
  - [ ] Préparation pour l'agrégation

#### Frontend / Visualisation
- [ ] **Sélecteur de dates (Timeline Slider)**
  - [ ] Composant slider temporel
  - [ ] Synchronisation avec les couches Deck.gl
  - [ ] Animation lors du changement de date

**Livrable** : Agrégats spatiaux. Contrôles temporels.

---

### 📅 Jour 5 - 05 Décembre

#### Backend / Data Science
- [ ] **Setup Prithvi WxC**
  - [ ] Téléchargement poids Hugging Face (granite-geospatial-wxc)
  - [ ] Test inférence simple
  - [ ] Vérification de l'environnement GPU/CPU

#### Frontend / Visualisation
- [ ] **Design System**
  - [ ] Finalisation palette couleurs (Viridis/Magma pour chaleur)
  - [ ] Typographie cohérente
  - [ ] Composants UI réutilisables

**Livrable** : Env. IA prêt. UI cohérente.

---

### 📅 Jour 6 - 06 Décembre

#### Backend / Data Science
- [ ] **Préparation dataset Fine-Tuning**
  - [ ] Création des paires (LowRes, HighRes, Target)
  - [ ] Split train/validation
  - [ ] Vérification de la qualité des données

#### Frontend / Visualisation
- [ ] **Optimisation perfs**
  - [ ] Chargement asynchrone des layers
  - [ ] Lazy loading des composants
  - [ ] Optimisation du rendu

**Livrable** : Dataset Train/Val prêt.

---

### 📅 Jour 7 - 07 Décembre ⚠️ LIVRABLE SEMAINE 3

#### Backend / Data Science
- [ ] **Rendu Hebdomadaire Semaine 3**
  - [ ] Rapport d'avancement
  - [ ] Baseline Metrics documentées
  - [ ] Démo MVP Dashboard

#### Frontend / Visualisation
- [ ] **Rendu Hebdomadaire Semaine 3**
  - [ ] Capture vidéo des fonctionnalités de base
  - [ ] Documentation des features implémentées

**Livrable** : **LIVRABLE SEMAINE 3**

---

## 🎯 Phase 2 : Innovation et "Heavy Lifting"

**Objectif** : Déployer l'IA avancée et le Scrollytelling.

### 📅 Jour 8 - 08 Décembre

#### Backend / Data Science
- [ ] **Lancement Fine-Tuning Prithvi (QLoRA)**
  - [ ] Configuration QLoRA (rank=8)
  - [ ] Setup de la boucle d'entraînement
  - [ ] Focus sur la convergence de la Loss (Pixel + Perceptual)
  - [ ] Monitoring des logs d'entraînement

#### Frontend / Visualisation
- [ ] **Intégration react-scrollama**
  - [ ] Installation et configuration
  - [ ] Structure de base du scrollytelling
- [ ] **Rédaction du script narratif (Storyboarding)**
  - [ ] Scénario de narration
  - [ ] Points d'intérêt à mettre en avant

**Livrable** : Logs entraînement. Draft Scrollytelling.

---

### 📅 Jour 9 - 09 Décembre

#### Backend / Data Science
- [ ] **Analyse 1ers résultats IA**
  - [ ] Évaluation des prédictions
  - [ ] Ajustement hyperparamètres
  - [ ] Validation croisée spatiale

#### Frontend / Visualisation
- [ ] **Transitions FlyToInterpolator**
  - [ ] Codage des transitions liées au scroll
  - [ ] Tests d'animations caméra
  - [ ] Fluidité des mouvements

**Livrable** : Modèle Alpha. Transitions fluides.

---

### 📅 Jour 10 - 10 Décembre

#### Backend / Data Science
- [ ] **Calculs métriques avancées**
  - [ ] **Perkins Score** (S-score)
  - [ ] Analyse Spectrale (PSD)
  - [ ] Comparaison vs Baseline
  - [ ] Documentation des résultats

#### Frontend / Visualisation
- [ ] **HeatmapLayer dynamique**
  - [ ] Intégration avec les nouvelles données IA
  - [ ] Configuration de l'agrégation GPU
  - [ ] Ajustement des paramètres de visualisation

**Livrable** : Preuves de supériorité. Viz Heatmap.

---

### 📅 Jour 11 - 11 Décembre

#### Backend / Data Science
- [ ] **Génération des produits finaux**
  - [ ] Time Series complètes sur la période Hackathon
  - [ ] Export des résultats en formats standards
  - [ ] Validation de la cohérence temporelle

#### Frontend / Visualisation
- [ ] **Composant "Swipe Map"**
  - [ ] Comparaison Avant/Après
  - [ ] Comparaison ERA5/Prithvi
  - [ ] Interface intuitive

**Livrable** : Données Finales. Feature Swipe.

---

### 📅 Jour 12 - 12 Décembre

#### Backend / Data Science
- [ ] **Analyse Physique (PINN validation)**
  - [ ] Vérification cohérence UHI vs NDBI/NDVI
  - [ ] Validation des lois physiques
  - [ ] Documentation des contraintes physiques

#### Frontend / Visualisation
- [ ] **Polissage UI**
  - [ ] Animations CSS
  - [ ] Glassmorphism sur les panneaux de contrôle
  - [ ] Refinement visuel général

**Livrable** : Validation Physique. UI Premium.

---

### 📅 Jour 13 - 13 Décembre

#### Backend / Data Science
- [ ] **Export des résultats et figures**
  - [ ] Préparation pour le rapport final
  - [ ] Génération des visualisations scientifiques
  - [ ] Organisation des assets

#### Frontend / Visualisation
- [ ] **Tests cross-browser et performance**
  - [ ] Tests sur différents navigateurs
  - [ ] Audit Lighthouse
  - [ ] Optimisations finales

**Livrable** : Assets Rapport. App Robuste.

---

### 📅 Jour 14 - 14 Décembre ⚠️ LIVRABLE SEMAINE 4

#### Backend / Data Science
- [ ] **Rendu Hebdomadaire Semaine 4**
  - [ ] Résultats préliminaires IA
  - [ ] Démo Scrollytelling

#### Frontend / Visualisation
- [ ] **Rendu Hebdomadaire Semaine 4**
  - [ ] Vidéo démo avancée
  - [ ] Documentation complète

**Livrable** : **LIVRABLE SEMAINE 4**

---

## 🏁 Phase 3 : Finalisation et Rendu Final

**Objectif** : Perfectionnement et Communication.

### 📅 Jour 15 - 15 Décembre

#### Backend / Data Science
- [ ] **Rédaction technique détaillée**
  - [ ] Justification ViT vs CNN
  - [ ] Analyse Perkins
  - [ ] Documentation scientifique complète

#### Frontend / Visualisation
- [ ] **Finalisation textes Scrollytelling**
  - [ ] Vérification des liens
  - [ ] Vérification des sources
  - [ ] Relecture finale

**Livrable** : Textes finaux.

---

### 📅 Jour 16 - 16 Décembre

#### Backend / Data Science
- [ ] **Création Vidéo Démo "Marketing"**
  - [ ] Capture 4K du dashboard
  - [ ] Montage et post-production
  - [ ] Narration et sous-titres

#### Frontend / Visualisation
- [ ] **Mise en production**
  - [ ] Déploiement Vercel/Netlify
  - [ ] Backend API léger (FastAPI)
  - [ ] Configuration des environnements

**Livrable** : URL Prod. Vidéo.

---

### 📅 Jour 17 - 17 Décembre

#### Backend / Data Science
- [ ] **Relecture finale**
  - [ ] Vérification conformité critères Hackathon
  - [ ] Checklist complète
  - [ ] Dernières corrections

#### Frontend / Visualisation
- [ ] **Derniers fixes bugs mineurs**
  - [ ] Glitches visuels
  - [ ] Problèmes de performance
  - [ ] Tests finaux

**Livrable** : Projet "Gold".

---

### 📅 Jour 18 - 18 Décembre ⚠️ SOUMISSION FINALE

#### Backend / Data Science
- [ ] **SOUMISSION FINALE GENHACK 2025**
  - [ ] Upload du code
  - [ ] Upload du rapport
  - [ ] Upload de la vidéo
  - [ ] Vérification de tous les fichiers

#### Frontend / Visualisation
- [ ] **SOUMISSION FINALE GENHACK 2025**
  - [ ] Vérification du déploiement
  - [ ] Tests finaux en production

**Livrable** : **PROJET SOUMIS.**

---

### 📅 Jours 19-20 - 19-20 Décembre

#### Préparation Pitch
- [ ] **Préparation du Pitch Oral**
  - [ ] Slides basés sur le Scrollytelling
  - [ ] Répétition de la présentation
  - [ ] Support visuel finalisé

**Livrable** : Support Présentation.

---

## 📋 Checklist Générale par Domaine

### 🔬 Backend / Data Science

#### Infrastructure
- [ ] Pipeline ETL robuste
- [ ] Stockage structuré (NetCDF/Zarr)
- [ ] Environnement Prithvi WxC configuré

#### Traitement des Données
- [ ] Gap-Filling Sentinel-2 (Random Forest)
- [ ] Harmonisation temporelle/spatiale
- [ ] Extraction GADM et agrégation

#### Modélisation
- [ ] Baseline Model (interpolation bicubique)
- [ ] Fine-Tuning Prithvi WxC (QLoRA)
- [ ] Validation PINN

#### Métriques
- [ ] RMSE Baseline
- [ ] Perkins Score
- [ ] Analyse Spectrale

#### Production
- [ ] Export des résultats finaux
- [ ] Génération des figures
- [ ] Documentation technique

---

### 🎨 Frontend / Visualisation

#### Infrastructure
- [ ] React 19 + Vite + Tailwind
- [ ] MapLibre + Deck.gl
- [ ] Design System complet

#### Composants Cartographiques
- [ ] StationLayer (Scatterplot)
- [ ] HeatmapLayer dynamique
- [ ] Timeline Slider
- [ ] Swipe Map

#### Visualisations
- [ ] Graphiques temporels (Recharts/Nivo)
- [ ] Scrollytelling interactif
- [ ] Animations caméra (FlyToInterpolator)

#### Optimisation
- [ ] Chargement asynchrone
- [ ] Performance (Lighthouse)
- [ ] Tests cross-browser

#### Production
- [ ] Déploiement (Vercel/Netlify)
- [ ] API Backend (FastAPI)
- [ ] Vidéo démo

---

## 🎯 Points Critiques à Surveiller

### ⚠️ Risques Techniques

1. **Prithvi WxC** : Modèle de 2.3B paramètres - nécessite GPU puissant
   - **Mitigation** : QLoRA pour réduire la mémoire
   - **Backup** : Baseline Model si échec

2. **Gap-Filling Sentinel-2** : Complexité algorithmique
   - **Mitigation** : Random Forest (compromis rapidité/robustesse)
   - **Backup** : Interpolation simple si temps manquant

3. **Performance Deck.gl** : Datasets massifs
   - **Mitigation** : Chargement asynchrone, tiling
   - **Backup** : Réduction de la résolution si nécessaire

### 📊 Métriques de Succès

- **Phase 1** : MVP fonctionnel avec baseline
- **Phase 2** : Modèle IA opérationnel avec Perkins Score > 0.7
- **Phase 3** : Dashboard en production, vidéo de qualité

---

## 📚 Ressources Clés

### Modèles et Bibliothèques
- **Prithvi WxC** : `ibm-granite/granite-geospatial-wxc-downscaling` (Hugging Face)
- **Deck.gl** : Documentation officielle
- **React 19** : Latest features

### Documentation
- `GenHack2025_Report.md` : Stratégie complète
- `DATASETS_ANALYSIS.md` : Structure des données
- `GCP_INFRASTRUCTURE.md` : Infrastructure backend

---

**Dernière mise à jour** : 9 novembre 2025  
**Statut** : Prêt pour l'implémentation

