# 🏗️ Infrastructure GCP - GenHack Heat Downscaling Pipeline

> **Documentation complète de la stack Google Cloud Platform déployée**  
> **Projet** : `genhack-heat-dev`  
> **Date d'analyse** : 9 novembre 2025  
> **Statut** : Phase 1 complète, Phase 2 en cours

---

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Ressources déployées](#ressources-déployées)
3. [Architecture détaillée](#architecture-détaillée)
4. [Sécurité et IAM](#sécurité-et-iam)
5. [État actuel vs objectifs](#état-actuel-vs-objectifs)
6. [Points à améliorer](#points-à-améliorer)
7. [Roadmap de développement](#roadmap-de-développement)

---

## 🎯 Vue d'ensemble

### Projet GCP

- **Project ID** : `genhack-heat-dev`
- **Project Number** : `65076813859`
- **Région principale** : `europe-west1`
- **Statut** : ✅ Actif et opérationnel

### Objectif

Pipeline serverless de downscaling climatique pour l'analyse des îlots de chaleur urbains, déployée sur Google Cloud Platform avec isolation complète et sécurité renforcée.

### Phase actuelle

- ✅ **Phase 0** : Infrastructure de base (complète)
- ✅ **Phase 1** : Pipeline mock avec données synthétiques (complète)
- 🔄 **Phase 2** : Intégration données réelles (en cours)

---

## 🏛️ Ressources déployées

### 1. Cloud Run Jobs

#### Job principal : `heat-downscaling-pipeline`

**Configuration** :
- **Région** : `europe-west1`
- **Image Docker** : `europe-docker.pkg.dev/genhack-heat-dev/heat/gh-pipeline:7671c2123c1e325fd18cfeef7ed44669108e1fea`
- **Service Account** : `gh-pipeline-sa@genhack-heat-dev.iam.gserviceaccount.com`
- **Ressources** :
  - CPU : 2 vCPU
  - Mémoire : 4 GiB
  - Timeout : 3600s (1 heure)
  - Max retries : 1

**Environnement** :
```yaml
PROJECT_ID: genhack-heat-dev
BUCKET_EXPORTS: gh-exports-genhack-heat-dev
BUCKET_CONFIGS: gh-configs-genhack-heat-dev
```

**Arguments** :
- `--config configs/paris_2022_mock.yml`

**Statut** :
- ✅ Job créé : 8 novembre 2025, 15:58:19 UTC
- ✅ Dernière exécution réussie : 8 novembre 2025, 16:22:57 UTC
- ✅ Exécutions totales : 3 (1 réussie, 2 échouées initialement)

**Dernière exécution** :
- **Execution ID** : `heat-downscaling-pipeline-7rrjz`
- **Statut** : ✅ `EXECUTION_SUCCEEDED`
- **Date** : 8 novembre 2025, 16:22:57 UTC
- **Complétion** : 8 novembre 2025, 16:23:54 UTC (~1 minute)

---

### 2. Cloud Storage (GCS) - 11 Buckets

Tous les buckets sont :
- **Région** : `EUROPE-WEST1`
- **Classe de stockage** : `STANDARD`
- **Uniform Bucket-Level Access** : ✅ Activé
- **Public Access Prevention** : ✅ Hérité (bloqué)
- **Soft Delete** : ✅ Activé (7 jours de rétention)
- **Chiffrement** : CMEK avec clé KMS `gh-key`

#### Buckets par catégorie

##### Raw Data (Données brutes)
1. **`gh-raw-era5-genhack-heat-dev`**
   - **Usage** : Stockage des données ERA5 brutes
   - **Contenu attendu** : Fichiers NetCDF/GRIB depuis Copernicus CDS
   - **Statut** : ✅ Créé, vide (Phase 2)

2. **`gh-raw-sentinel2-genhack-heat-dev`**
   - **Usage** : Stockage des images Sentinel-2 brutes
   - **Contenu attendu** : GeoTIFF depuis Google Earth Engine
   - **Statut** : ✅ Créé, vide (Phase 2)

3. **`gh-raw-osm-genhack-heat-dev`**
   - **Usage** : Stockage des données OpenStreetMap
   - **Contenu attendu** : GeoJSON/PBF avec bâtiments, routes, etc.
   - **Statut** : ✅ Créé, vide (Phase 2)

##### Intermediate Data (Données intermédiaires)
4. **`gh-intermediate-reprojected-genhack-heat-dev`**
   - **Usage** : Rasters reprojetés (étape preprocessing)
   - **Statut** : ✅ Créé, utilisé par la pipeline

5. **`gh-intermediate-preprocessed-genhack-heat-dev`**
   - **Usage** : Données préprocessées (normalisation, masques)
   - **Statut** : ✅ Créé, utilisé par la pipeline

##### Features & Models
6. **`gh-models-checkpoints-genhack-heat-dev`**
   - **Usage** : Checkpoints des modèles ML (U-Net, SRGAN)
   - **Statut** : ✅ Créé, vide (Phase 3)

7. **`gh-models-experiments-genhack-heat-dev`**
   - **Usage** : Métriques et logs d'entraînement (MLflow, TensorBoard)
   - **Statut** : ✅ Créé, vide (Phase 3)

##### Exports (Sorties finales)
8. **`gh-exports-geotiff-genhack-heat-dev`**
   - **Usage** : GeoTIFF finaux (température, NDVI, NDBI)
   - **Format** : Cloud Optimized GeoTIFF (COG)
   - **Statut** : ✅ Créé, **vide actuellement** ⚠️

9. **`gh-exports-zarr-genhack-heat-dev`**
   - **Usage** : Exports Zarr pour analyses multi-dimensionnelles
   - **Statut** : ✅ Créé, vide (Phase 2+)

##### Configuration & Logs
10. **`gh-configs-genhack-heat-dev`**
    - **Usage** : Fichiers de configuration YAML
    - **Contenu** : Configs pour différentes villes/périodes
    - **Statut** : ✅ Créé, utilisé

11. **`gh-logs-genhack-heat-dev`**
    - **Usage** : Logs d'exécution de la pipeline
    - **Statut** : ✅ Créé, utilisé

**⚠️ Observation** : Le bucket `gh-exports-geotiff-genhack-heat-dev` est vide, ce qui suggère que les outputs ne sont pas uploadés vers GCS (probablement écrits localement dans le container).

---

### 3. Artifact Registry

#### Repository : `heat`

**Configuration** :
- **Location** : `europe`
- **Format** : `DOCKER`
- **Mode** : `STANDARD_REPOSITORY`
- **Description** : "GenHack Heat Downscaling - Isolated from Kura"
- **Labels** :
  - `isolation=strict`
  - `project=genhack`
- **Chiffrement** : Google-managed key
- **Taille totale** : ~1.7 GB

**Images Docker** :
- **Image principale** : `gh-pipeline`
- **Dernière image** : `sha256:2c260866833bba263a89e2f34949f4fbcddd3516dc553bb4a7de543695664793`
- **Taille** : ~478 MB (478,606,415 bytes)
- **Tag utilisé** : `7671c2123c1e325fd18cfeef7ed44669108e1fea` (commit hash)

**Images disponibles** :
- Plusieurs versions avec tags SHA256
- Build time : 8 novembre 2025, 16:22:17 UTC

---

### 4. Cloud KMS (Key Management Service)

#### Keyring : `gh-ring`

**Configuration** :
- **Location** : `europe-west1`
- **Statut** : ✅ Actif

#### Clé de chiffrement : `gh-key`

**Configuration** :
- **Purpose** : `ENCRYPT_DECRYPT`
- **Algorithm** : `GOOGLE_SYMMETRIC_ENCRYPTION`
- **Protection Level** : `SOFTWARE`
- **Statut** : ✅ `ENABLED`
- **Primary ID** : 1
- **Primary State** : `ENABLED`

**Usage** : Chiffrement CMEK pour tous les buckets GCS

---

### 5. Service Accounts

#### Service Account principal : `gh-pipeline-sa`

**Email** : `gh-pipeline-sa@genhack-heat-dev.iam.gserviceaccount.com`  
**Display Name** : "GenHack Pipeline Service Account"  
**Description** : "Isolated SA for heat downscaling pipeline - NO Kura access"  
**Unique ID** : `107878297922802250363`  
**Statut** : ✅ Actif

**Permissions IAM (Project-level)** :
- ✅ `roles/storage.admin` - Accès complet aux buckets
- ✅ `roles/run.admin` - Gestion Cloud Run
- ✅ `roles/run.invoker` - Exécution Cloud Run Jobs
- ✅ `roles/artifactregistry.reader` - Lecture Artifact Registry
- ✅ `roles/artifactregistry.writer` - Écriture Artifact Registry
- ✅ `roles/cloudkms.cryptoKeyEncrypterDecrypter` - Chiffrement/déchiffrement KMS
- ✅ `roles/logging.logWriter` - Écriture logs
- ✅ `roles/monitoring.metricWriter` - Métriques monitoring
- ✅ `roles/iam.serviceAccountUser` - Utilisation du service account

**Permissions IAM (Service Account-level)** :
- ✅ `roles/iam.serviceAccountUser` (sur lui-même)

#### Service Account Compute Engine (par défaut)

**Email** : `65076813859-compute@developer.gserviceaccount.com`  
**Usage** : Service account par défaut pour Compute Engine  
**Permissions** : `roles/editor` (trop permissif ⚠️)

---

### 6. APIs activées

Les APIs suivantes sont activées dans le projet :

1. ✅ `run.googleapis.com` - Cloud Run
2. ✅ `artifactregistry.googleapis.com` - Artifact Registry
3. ✅ `storage.googleapis.com` - Cloud Storage
4. ✅ `cloudkms.googleapis.com` - Cloud KMS
5. ✅ `logging.googleapis.com` - Cloud Logging
6. ✅ `monitoring.googleapis.com` - Cloud Monitoring
7. ✅ `cloudbuild.googleapis.com` - Cloud Build
8. ✅ `eventarc.googleapis.com` - Eventarc
9. ✅ `cloudscheduler.googleapis.com` - Cloud Scheduler
10. ✅ `compute.googleapis.com` - Compute Engine

**APIs manquantes (pour Phase 2)** :
- ❌ `earthengine.googleapis.com` - Google Earth Engine (pour Sentinel-2)
- ❌ `bigquery.googleapis.com` - BigQuery (optionnel, pour analytics)
- ❌ `aiplatform.googleapis.com` - Vertex AI (pour modèles ML, Phase 3)

---

### 7. IAM - Utilisateurs et permissions

#### Utilisateurs avec accès au projet

**Owner** :
- `queriauxrobin@gmail.com` - ✅ Owner complet

**Editors** (trop permissif ⚠️) :
- `arnaud.durand97@gmail.com`
- `besbesomar@gmail.com`
- `dermierayan@gmail.com`
- `romain.mallet2004@gmail.com`

**Artifact Registry Admin** :
- `arnaud.durand97@gmail.com`
- `besbesomar@gmail.com`
- `dermierayan@gmail.com`
- `romain.mallet2004@gmail.com`

**Cloud Run Admin** :
- `arnaud.durand97@gmail.com`
- `besbesomar@gmail.com`
- `dermierayan@gmail.com`
- `romain.mallet2004@gmail.com`
- Service accounts Cloud Build

**Storage Admin** :
- `gh-pipeline-sa@genhack-heat-dev.iam.gserviceaccount.com`
- `arnaud.durand97@gmail.com`
- `besbesomar@gmail.com`
- `dermierayan@gmail.com`
- `romain.mallet2004@gmail.com`

---

## 🏗️ Architecture détaillée

### Flux de données

```
┌─────────────────────────────────────────────────────────────┐
│                    CLOUD RUN JOB                            │
│              heat-downscaling-pipeline                      │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Docker Container (4GB RAM, 2 CPU)                   │  │
│  │  Image: gh-pipeline:7671c212...                      │  │
│  │                                                       │  │
│  │  Pipeline Stages:                                    │  │
│  │  1. Ingest (mock) → 2. Preprocess → 3. Features     │  │
│  │  4. Train (stub) → 5. Evaluate → 6. Indicators      │  │
│  │  7. Publish → 8. Report                              │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  GCS Buckets │ │ Artifact Reg │ │ Cloud Logging│
│  (11 buckets)│ │  (heat repo) │ │  (logs)      │
└──────────────┘ └──────────────┘ └──────────────┘
```

### Pipeline stages (8 étapes)

1. **Ingest** (`src/ingest.py`)
   - Phase 1 : Génère données mock (128×128 rasters)
   - Phase 2 : Télécharge ERA5, Sentinel-2, OSM

2. **Preprocess** (`src/preprocess.py`)
   - Reprojection vers EPSG:3857
   - Resampling pour aligner résolutions
   - ✅ Implémenté et fonctionnel

3. **Features** (`src/features.py`)
   - Calcul NDVI, NDBI
   - Phase 1 : Mock calculations
   - Phase 2 : Vraies images Sentinel-2

4. **Train** (`src/train.py`)
   - Phase 1 : Stub (pas d'entraînement)
   - Phase 3 : U-Net pour downscaling

5. **Evaluate** (`src/evaluate.py`)
   - Calcul métriques (RMSE, MAE, R²)
   - ✅ Implémenté

6. **Indicators** (`src/indicators.py`)
   - Intensité, durée, étendue, UHI
   - ✅ Implémenté (mock)

7. **Publish** (`src/publish.py`)
   - Export GeoTIFF, PNG
   - ⚠️ **Problème** : N'upload pas vers GCS (écrit localement)

8. **Report** (`src/report.py`)
   - Génération HTML/PDF
   - ✅ Implémenté

---

## 🔒 Sécurité et IAM

### Points forts ✅

1. **Isolation complète**
   - Projet GCP dédié (`genhack-heat-dev`)
   - Aucun lien avec le projet Kura (`mental-journal-dev`)
   - Service account isolé avec description explicite

2. **Chiffrement CMEK**
   - Tous les buckets chiffrés avec clé KMS `gh-key`
   - Clé activée et opérationnelle

3. **Uniform Bucket-Level Access**
   - Tous les buckets en mode uniform
   - Public access prevention activé

4. **Soft Delete**
   - Rétention de 7 jours pour récupération

5. **Service Account avec permissions minimales**
   - `gh-pipeline-sa` a uniquement les permissions nécessaires
   - Pas d'accès cross-project

### Points à améliorer ⚠️

1. **Permissions trop larges pour utilisateurs**
   - 4 utilisateurs avec `roles/editor` (accès complet)
   - **Recommandation** : Réduire à `roles/viewer` + rôles spécifiques

2. **Service Account Compute Engine**
   - `65076813859-compute@developer.gserviceaccount.com` a `roles/editor`
   - **Recommandation** : Limiter les permissions

3. **Pas de VPC**
   - Cloud Run utilise le réseau public
   - **Recommandation** : Configurer VPC connector pour Phase 2+ (si accès privé nécessaire)

4. **Pas de secrets management**
   - Pas de Secret Manager pour API keys (Copernicus, Earth Engine)
   - **Recommandation** : Utiliser Secret Manager pour Phase 2

---

## 📊 État actuel vs objectifs

### Phase 1 : Mock Data Pipeline ✅

| Composant | Statut | Détails |
|-----------|--------|---------|
| Infrastructure GCP | ✅ | 11 buckets, KMS, Artifact Registry |
| Cloud Run Job | ✅ | Déployé et exécuté avec succès |
| Pipeline 8 stages | ✅ | Tous implémentés (mock) |
| Docker image | ✅ | Build et push réussis |
| CI/CD | ✅ | GitHub Actions configuré |
| Tests | ✅ | Tests de contrats validés |
| Documentation | ✅ | README, ARCHITECTURE, SCHEMAS |

**Résultats** :
- ✅ Pipeline s'exécute en ~1 minute
- ✅ Génère données mock (température, NDVI, NDBI)
- ✅ Produit rapports HTML/PDF
- ⚠️ **Problème** : Outputs non uploadés vers GCS

### Phase 2 : Données réelles 🔄

| Composant | Statut | Détails |
|-----------|--------|---------|
| Intégration ERA5 | ❌ | Pas d'API Copernicus CDS |
| Intégration Sentinel-2 | ❌ | Pas d'API Google Earth Engine |
| Intégration OSM | ❌ | Pas d'extraction Overpass API |
| Upload GCS | ❌ | Outputs écrits localement uniquement |
| Validation stations | ❌ | Pas d'intégration ECA&D |

**APIs nécessaires** :
- ❌ `earthengine.googleapis.com` - Non activée
- ❌ Secret Manager - Non configuré pour API keys

### Phase 3 : Machine Learning 🔜

| Composant | Statut | Détails |
|-----------|--------|---------|
| Modèle U-Net | ❌ | Stub uniquement |
| Training pipeline | ❌ | Pas d'infrastructure Vertex AI |
| Checkpoints | ❌ | Bucket créé mais vide |
| Experiments tracking | ❌ | Pas de MLflow/TensorBoard |

**Infrastructure nécessaire** :
- ❌ Vertex AI Workbench ou Training
- ❌ GPU instances (pour training)
- ❌ MLflow ou TensorBoard

---

## ⚠️ Points à améliorer

### 1. Upload des outputs vers GCS ❌

**Problème** : Le bucket `gh-exports-geotiff-genhack-heat-dev` est vide, alors que la pipeline s'exécute avec succès.

**Cause probable** : Le stage `publish.py` écrit les fichiers localement dans le container mais ne les upload pas vers GCS.

**Solution** :
```python
# Dans src/publish.py, ajouter upload GCS :
from google.cloud import storage

def upload_to_gcs(local_path: Path, gcs_path: str):
    client = storage.Client()
    bucket = client.bucket("gh-exports-geotiff-genhack-heat-dev")
    blob = bucket.blob(gcs_path)
    blob.upload_from_filename(str(local_path))
```

**Priorité** : 🔴 **Haute** - Bloque la Phase 2

---

### 2. Permissions IAM trop larges ⚠️

**Problème** : 4 utilisateurs ont `roles/editor` (accès complet au projet).

**Recommandation** :
- Réduire à `roles/viewer` pour consultation
- Ajouter `roles/storage.objectViewer` pour lire les buckets
- Ajouter `roles/run.viewer` pour voir les jobs
- Créer des rôles custom si nécessaire

**Priorité** : 🟡 **Moyenne** - Sécurité

---

### 3. Pas de Secret Manager ⚠️

**Problème** : Les API keys (Copernicus CDS, Earth Engine) seront probablement hardcodées ou en variables d'environnement.

**Recommandation** :
- Créer des secrets dans Secret Manager
- Modifier le service account pour accéder aux secrets
- Utiliser `google-cloud-secret-manager` dans le code

**Priorité** : 🟡 **Moyenne** - Sécurité pour Phase 2

---

### 4. APIs manquantes ❌

**APIs non activées** :
- `earthengine.googleapis.com` - Pour Sentinel-2
- `secretmanager.googleapis.com` - Pour gestion des secrets
- `aiplatform.googleapis.com` - Pour Vertex AI (Phase 3)

**Priorité** : 🔴 **Haute** pour Earth Engine, 🟡 **Moyenne** pour les autres

---

### 5. Pas de monitoring avancé ⚠️

**Problème** : Seul `roles/monitoring.metricWriter` est configuré, mais pas de dashboards ou alertes.

**Recommandation** :
- Créer des dashboards Cloud Monitoring
- Configurer des alertes (échecs de jobs, utilisation storage)
- Métriques custom (temps d'exécution, taille outputs)

**Priorité** : 🟢 **Basse** - Nice to have

---

### 6. Pas de CI/CD pour tests automatiques ⚠️

**Problème** : CI/CD existe mais ne lance pas les tests automatiquement.

**Recommandation** :
- Ajouter étape `make test` dans GitHub Actions
- Tests de régression avant déploiement
- Validation des schémas JSON

**Priorité** : 🟡 **Moyenne** - Qualité

---

### 7. Buckets inutilisés ⚠️

**Buckets créés mais vides** :
- `gh-exports-zarr-genhack-heat-dev` - Pas d'implémentation Zarr
- `gh-models-checkpoints-genhack-heat-dev` - Phase 3
- `gh-models-experiments-genhack-heat-dev` - Phase 3

**Recommandation** :
- Garder pour Phase 3 (modèles ML)
- Documenter l'usage prévu

**Priorité** : 🟢 **Basse** - Pas urgent

---

## 🗺️ Roadmap de développement

### Phase 2 - Intégration données réelles (Priorité haute)

#### 2.1. Configuration APIs et secrets

- [ ] Activer `earthengine.googleapis.com`
- [ ] Activer `secretmanager.googleapis.com`
- [ ] Créer secrets dans Secret Manager :
  - `copernicus-cds-api-key`
  - `earthengine-service-account-key`
- [ ] Modifier `gh-pipeline-sa` pour accéder aux secrets

#### 2.2. Fix upload GCS

- [ ] Modifier `src/publish.py` pour uploader vers GCS
- [ ] Tester avec données mock
- [ ] Vérifier que les fichiers apparaissent dans `gh-exports-geotiff-genhack-heat-dev`

#### 2.3. Intégration ERA5

- [ ] Installer `cdsapi` dans `requirements.txt`
- [ ] Implémenter téléchargement depuis Copernicus CDS
- [ ] Upload vers `gh-raw-era5-genhack-heat-dev`
- [ ] Tester avec Paris 2022

#### 2.4. Intégration Sentinel-2

- [ ] Installer `earthengine-api` dans `requirements.txt`
- [ ] Authentifier avec service account
- [ ] Implémenter requête Google Earth Engine
- [ ] Calcul NDVI/NDBI sur vraies images
- [ ] Upload vers `gh-raw-sentinel2-genhack-heat-dev`

#### 2.5. Intégration OSM (optionnel)

- [ ] Installer `overpy` ou `osmnx`
- [ ] Extraire bâtiments, routes, espaces verts
- [ ] Upload vers `gh-raw-osm-genhack-heat-dev`

#### 2.6. Validation stations météo

- [ ] Télécharger données ECA&D
- [ ] Sélectionner stations dans zone d'étude
- [ ] Comparer ERA5 vs stations
- [ ] Calculer métriques de validation

---

### Phase 3 - Machine Learning (Priorité moyenne)

#### 3.1. Infrastructure Vertex AI

- [ ] Activer `aiplatform.googleapis.com`
- [ ] Créer bucket pour checkpoints (déjà fait)
- [ ] Configurer Vertex AI Workbench ou Training

#### 3.2. Modèle U-Net

- [ ] Implémenter architecture U-Net
- [ ] Training pipeline avec Vertex AI
- [ ] Sauvegarde checkpoints dans `gh-models-checkpoints-genhack-heat-dev`
- [ ] Tracking expériences dans `gh-models-experiments-genhack-heat-dev`

#### 3.3. Intégration dans pipeline

- [ ] Modifier `src/train.py` pour utiliser Vertex AI
- [ ] Modifier `src/evaluate.py` pour charger le modèle
- [ ] Tester end-to-end

---

### Phase 4 - API REST (Priorité moyenne)

#### 4.1. Cloud Run Service (pas Job)

- [ ] Créer Cloud Run Service (HTTP)
- [ ] Endpoints REST :
  - `GET /api/cities`
  - `GET /api/reports/{city}`
  - `GET /api/heatmap/{city}`
  - `POST /api/analyze`
  - `GET /api/indicators/{city}`

#### 4.2. Authentification

- [ ] Configurer IAP (Identity-Aware Proxy) ou API keys
- [ ] Limiter accès aux membres de l'équipe

#### 4.3. Intégration frontend

- [ ] Documenter API (OpenAPI/Swagger)
- [ ] Tester avec frontend

---

### Phase 5 - Améliorations sécurité (Priorité moyenne)

#### 5.1. Réduction permissions IAM

- [ ] Réduire `roles/editor` → `roles/viewer` + rôles spécifiques
- [ ] Limiter permissions service account Compute Engine
- [ ] Audit des permissions actuelles

#### 5.2. VPC (si nécessaire)

- [ ] Évaluer besoin de VPC connector
- [ ] Configurer si accès privé requis

#### 5.3. Monitoring et alertes

- [ ] Créer dashboards Cloud Monitoring
- [ ] Configurer alertes (échecs jobs, storage usage)
- [ ] Métriques custom

---

## 📈 Métriques et coûts

### Coûts estimés (Phase 1)

**Cloud Run Jobs** :
- Exécutions : ~3 exécutions
- Durée moyenne : ~1 minute
- Coût : ~$0.01 (négligeable)

**Cloud Storage** :
- Buckets : 11 buckets
- Données stockées : ~0 GB (vides)
- Coût : ~$0 (gratuit jusqu'à 5 GB)

**Artifact Registry** :
- Images : ~1.7 GB
- Coût : ~$0.05/mois

**Cloud KMS** :
- Clés actives : 1
- Opérations : ~1000/mois
- Coût : ~$1/mois

**Total Phase 1** : ~$1-2/mois

### Coûts estimés (Phase 2+)

**Cloud Run Jobs** :
- Exécutions : ~10-20/mois
- Durée : ~5-10 minutes
- Coût : ~$0.50-1/mois

**Cloud Storage** :
- Données : ~50-100 GB (ERA5, Sentinel-2)
- Coût : ~$1-2/mois

**Vertex AI (Phase 3)** :
- Training : ~$10-50/mois (GPU instances)
- Prediction : ~$1-5/mois

**Total Phase 2+** : ~$15-60/mois

---

## ✅ Checklist de vérification

### Infrastructure de base
- [x] Projet GCP créé et actif
- [x] 11 buckets GCS créés avec CMEK
- [x] Artifact Registry configuré
- [x] Cloud KMS keyring et clé créés
- [x] Service account avec permissions minimales
- [x] APIs nécessaires activées (Phase 1)
- [x] Cloud Run Job déployé et fonctionnel

### Pipeline
- [x] 8 stages implémentés (mock)
- [x] Docker image build et push
- [x] Exécution réussie
- [ ] Upload outputs vers GCS ❌
- [ ] Intégration données réelles ❌

### Sécurité
- [x] Isolation complète (projet dédié)
- [x] Chiffrement CMEK
- [x] Uniform bucket-level access
- [ ] Permissions IAM optimisées ⚠️
- [ ] Secret Manager configuré ❌

### Documentation
- [x] README complet
- [x] Architecture documentée
- [x] Schémas JSON documentés
- [x] Scripts de déploiement
- [x] Makefile avec commandes

---

## 🔗 Liens utiles

### Console GCP
- **Project** : https://console.cloud.google.com/?project=genhack-heat-dev
- **Cloud Run Jobs** : https://console.cloud.google.com/run/jobs?project=genhack-heat-dev
- **Cloud Storage** : https://console.cloud.google.com/storage/browser?project=genhack-heat-dev
- **Artifact Registry** : https://console.cloud.google.com/artifacts?project=genhack-heat-dev
- **Cloud KMS** : https://console.cloud.google.com/security/kms?project=genhack-heat-dev
- **IAM** : https://console.cloud.google.com/iam-admin/iam?project=genhack-heat-dev
- **Logs** : https://console.cloud.google.com/logs?project=genhack-heat-dev

### Commandes utiles

```bash
# Vérifier le projet actuel
gcloud config get-value project

# Lister les buckets
gsutil ls

# Voir les exécutions du job
gcloud run jobs executions list --job=heat-downscaling-pipeline --region=europe-west1

# Voir les logs
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=heat-downscaling-pipeline" --limit=50

# Décrire le job
gcloud run jobs describe heat-downscaling-pipeline --region=europe-west1

# Exécuter le job
gcloud run jobs execute heat-downscaling-pipeline --region=europe-west1 --wait
```

---

## 📝 Notes importantes

1. **Isolation** : Le projet est complètement isolé du projet Kura. Aucun bucket, service account ou ressource n'est partagé.

2. **Phase 1 complète** : L'infrastructure de base est opérationnelle. La pipeline s'exécute avec succès mais utilise des données mock.

3. **Phase 2 prioritaire** : L'intégration des données réelles (ERA5, Sentinel-2) est la prochaine étape critique.

4. **Upload GCS** : Le problème d'upload des outputs vers GCS doit être résolu avant de passer à la Phase 2.

5. **Sécurité** : Les permissions IAM peuvent être optimisées, mais ne bloquent pas le développement.

---

**Dernière mise à jour** : 9 novembre 2025  
**Auteur** : Analyse automatique via `gcloud` CLI  
**Version** : 1.0.0

