# 🚀 Branch `romain-mallet-dev` - Phase 2 Real Data

**Auteur** : Romain Mallet  
**Date** : 10 novembre 2025  
**Statut** : ✅ Prêt pour review & merge

---

## 📋 Résumé des changements

Cette branche implémente **Phase 2 : Ingestion de données réelles** pour remplacer les données mock par :
1. **ERA5** - Données climatiques haute qualité (Copernicus)
2. **Sentinel-2** - Images satellites multispectrales (Google Earth Engine)

### Commits principaux

| Commit | Description | Fichiers |
|--------|-------------|----------|
| `085c81e` | ERA5 client + real data ingestion | `src/era5_client.py`, `src/ingest.py`, configs, docs |
| `a961c68` | Sentinel-2 client + NDVI/NDBI | `src/sentinel2_client.py`, `src/ingest.py` |

---

## 🎯 Objectif

Permettre à la pipeline de :
- Télécharger des **vraies données climatiques** (température, humidité, etc.) depuis ERA5
- Télécharger des **images satellites** Sentinel-2 pour calculer NDVI (végétation) et NDBI (urbanisation)
- Utiliser ces données pour entraîner le modèle de downscaling

---

## 📦 Nouveaux fichiers

### Core
- `src/era5_client.py` - Client pour télécharger données ERA5
- `src/sentinel2_client.py` - Client pour télécharger images Sentinel-2
- `src/ingest.py` - Mise à jour pour supporter mock + real data

### Configuration
- `configs/paris_2022_real.yml` - Config pour données réelles (dry_run: false)
- `.env.example` - Template pour API key Copernicus

### Documentation
- `docs/ERA5_SETUP.md` - Guide configuration CDS API
- `docs/BRANCH_ROMAIN_DEV.md` - Ce fichier

### Infrastructure
- `.gitignore` - Ajout protection fichiers sensibles (.env, .cdsapirc, PDFs)
- `pipeline/requirements.txt` - Ajout cdsapi, earthengine-api

---

## 🧪 Comment tester

### Prérequis

1. **Copernicus CDS API** (pour ERA5)
   - Créer compte : https://cds.climate.copernicus.eu/
   - Récupérer API key
   - Créer `~/.cdsapirc` :
   ```
   url: https://cds.climate.copernicus.eu/api
   key: VOTRE_API_KEY
   ```
   - Accepter licence ERA5 : https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=download

2. **Google Earth Engine** (pour Sentinel-2)
   - Authentifier : `earthengine authenticate`
   - Enregistrer projet GCP pour Earth Engine
   - Voir détails : `docs/ERA5_SETUP.md`

### Test 1 : ERA5 Client ✅

```bash
# Activer venv
cd /root/GenHack4-Hackathon-Vertex
python3 -m venv venv
source venv/bin/activate

# Installer dépendances
pip install -r pipeline/requirements.txt
pip install cdsapi xarray rasterio netcdf4

# Tester ERA5
python src/era5_client.py
```

**Résultat attendu** :
```
📥 Downloading ERA5 data...
✅ Downloaded t2m (2022-07-15)
✅ Test complete: 1 files downloaded

Fichiers créés:
/tmp/era5_test/t2m_era5.nc  (NetCDF ~26 KB)
/tmp/era5_test/t2m.tif      (GeoTIFF ~2 KB)

Températures:
Min: 14.6°C
Max: 26.3°C (15 juillet - avant canicule)
```

**🔥 Bonus** : Tester canicule (18-19 juillet) :
```python
from pathlib import Path
from src.era5_client import ERA5Client

client = ERA5Client()
files = client.download_era5(
    variables=['t2m'],
    bbox=[2.2, 48.8, 2.5, 48.9],
    start_date='2022-07-18',
    end_date='2022-07-19',
    output_dir=Path('/tmp/era5_heatwave')
)
# Max attendu: 38.6°C 🔥
```

---

### Test 2 : Sentinel-2 Client ✅

```bash
# S'assurer d'être authentifié sur Earth Engine
earthengine authenticate

# Tester Sentinel-2
python src/sentinel2_client.py
```

**Résultat attendu** :
```
✅ Earth Engine initialized
📥 Downloading Sentinel-2 data...
  Found 5 images with <20.0% cloud cover
  Downloading B4 (red)...
    ✅ Saved to /tmp/sentinel2_test/red_s2.tif
  Downloading B8 (nir)...
    ✅ Saved to /tmp/sentinel2_test/nir_s2.tif
  Downloading B11 (swir1)...
    ✅ Saved to /tmp/sentinel2_test/swir1_s2.tif

✅ Test complete: 3 bands downloaded
🌿 Computing NDVI...
🏙️ Computing NDBI...

Fichiers créés:
/tmp/sentinel2_test/red_s2.tif   (~5.5 MB)
/tmp/sentinel2_test/nir_s2.tif   (~5.9 MB)
/tmp/sentinel2_test/swir1_s2.tif (~1.8 MB)
/tmp/sentinel2_test/ndvi.tif     (~15 MB)
/tmp/sentinel2_test/ndbi.tif     (~16 MB)

Dimensions: 3340x1115 pixels
Résolution: ~7-10m

NDVI (végétation):
  Min: -0.57 (eau/bâtiments)
  Max: 0.92 (végétation dense)
  Mean: 0.33 (mix urbain Paris)

NDBI (zones bâties):
  Min: -0.69 (végétation)
  Max: 0.78 (zones très urbanisées)
  Mean: -0.02 (Paris = ville avec parcs)
```

---

### Test 3 : Pipeline complète (optionnel)

```bash
# Construire image Docker
make build

# Test avec données mock (baseline)
make dryrun

# Test avec données réelles
docker run --rm \
  -v $(PWD)/configs:/app/configs \
  -v ~/.cdsapirc:/root/.cdsapirc \
  -v /tmp/genhack:/tmp/genhack \
  europe-docker.pkg.dev/genhack-heat-dev/heat/gh-pipeline:latest \
  --config configs/paris_2022_real.yml
```

**Note** : Pour que Earth Engine fonctionne dans Docker, il faut monter les credentials.

---

## ✅ Critères de validation

### Test ERA5 réussi si :
- [x] Téléchargement NetCDF sans erreur
- [x] Conversion GeoTIFF réussie
- [x] Températures cohérentes (14-27°C pour juillet Paris)
- [x] Fichiers créés dans `/tmp/era5_test/`

### Test Sentinel-2 réussi si :
- [x] Authentication Earth Engine OK
- [x] 3-5 images trouvées (juillet 2022, Paris)
- [x] 3 bandes téléchargées (B4, B8, B11)
- [x] NDVI calculé : -1 < valeurs < 1
- [x] NDBI calculé : -1 < valeurs < 1
- [x] Taille fichiers cohérente (MB, pas KB)

### Tests unitaires :
```bash
# Vérifier que les contrats sont toujours valides
pytest tests/test_contracts.py -v
# Attendu: 6/6 tests passed
```

---

## 🐛 Problèmes connus & solutions

### ERA5 : `403 Forbidden - required licences not accepted`
**Solution** : Accepter la licence du dataset ERA5 sur le site CDS  
→ https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=download

### Earth Engine : `Project not registered`
**Solution** : Enregistrer le projet pour usage non-commercial  
→ https://console.cloud.google.com/earth-engine/configuration?project=genhack-heat-dev

### `ModuleNotFoundError: No module named 'xarray'`
**Solution** : `pip install xarray netcdf4 rasterio`

---

## 🔀 Merge sur main ?

**Checklist avant merge** :

- [ ] Les 2 clients fonctionnent sur ma machine (ERA5 + S2)
- [ ] Les tests unitaires passent (`pytest`)
- [ ] Le Dockerfile build sans erreur (`make build`)
- [ ] La doc est claire et complète
- [ ] Pas de clés API hardcodées (vérifier `.gitignore`)
- [ ] Branch à jour avec `main` (`git merge main`)

**Si tous les tests passent → ✅ Prêt à merge !**

---

## 📚 Documentation détaillée

- **Setup ERA5** : `docs/ERA5_SETUP.md`
- **Architecture** : `docs/ARCHITECTURE_CLIMATE.md`
- **Schemas** : `docs/SCHEMAS.md`

---

## 🚀 Prochaines étapes (après merge)

1. **Phase 2.3** : OSM features (bâtiments, routes, végétation)
2. **Phase 3** : U-Net downscaling model (PyTorch)
3. **Phase 4** : Multi-city analysis
4. **Phase 5** : Indicateurs avancés + API REST

---

## 📞 Contact

**Questions / bugs ?** → Romain Mallet  
**Branch** : `romain-mallet-dev`  
**Base** : `main` (clean-room duplication)

---

**Merci de tester ! 🙏**
