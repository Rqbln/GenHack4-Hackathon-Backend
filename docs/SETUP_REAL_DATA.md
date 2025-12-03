# 📊 Guide : Utilisation des Vraies Données

Ce guide explique comment utiliser les vraies données du hackathon au lieu des données mockées.

---

## ✅ Étape 1 : Vérifier les Données

Avant de commencer, vérifiez que tous les fichiers sont présents :

```bash
cd GenHack4-Hackathon-Vertex
python3 scripts/check_real_data.py
```

Ce script vérifie la présence de :
- ✅ ERA5 NetCDF files (2020-2025)
- ✅ Sentinel-2 NDVI GeoTIFF files
- ✅ ECA&D stations ZIP
- ✅ GADM boundaries GeoPackage

---

## 📦 Étape 2 : Installer les Dépendances

### Option A : Installation Globale (si vous avez les permissions)

```bash
pip install xarray geopandas rasterio zarr netcdf4 fsspec
```

### Option B : Environnement Virtuel (Recommandé)

```bash
# Créer un environnement virtuel
python3 -m venv venv

# Activer l'environnement
source venv/bin/activate  # Sur macOS/Linux
# ou
venv\Scripts\activate  # Sur Windows

# Installer les dépendances
pip install xarray geopandas rasterio zarr netcdf4 fsspec
```

### Option C : Utiliser les Requirements Existants

```bash
cd GenHack4-Hackathon-Vertex
pip install -r requirements.txt
```

---

## 🚀 Étape 3 : Exécuter l'ETL

Une fois les dépendances installées, exécutez l'ETL :

```bash
cd GenHack4-Hackathon-Vertex
python3 scripts/run_etl_real_data.py
```

### Ce que fait le script :

1. **Charge les limites de la ville** depuis GADM (Paris par défaut)
2. **Charge les données ERA5** pour 2020-2021 (température, précipitations, vent)
3. **Charge les données Sentinel-2 NDVI** (8 périodes trimestrielles)
4. **Charge les stations ECA&D** et filtre celles dans Paris
5. **Aligne temporellement** toutes les données
6. **Sauvegarde** les résultats dans `data/processed/` :
   - `era5_aligned.zarr` : Données ERA5 alignées
   - `stations.geojson` : Stations météo
   - `city_boundary.geojson` : Limites de Paris
   - `ndvi_metadata.json` : Métadonnées NDVI

---

## 📁 Structure des Données

### Données d'Entrée

```
datasets/
├── main/
│   ├── derived-era5-land-daily-statistics/  # ERA5 NetCDF
│   │   ├── 2020_2m_temperature_daily_maximum.nc
│   │   ├── 2020_total_precipitation_daily_mean.nc
│   │   ├── 2020_10m_u_component_of_wind_daily_mean.nc
│   │   ├── 2020_10m_v_component_of_wind_daily_mean.nc
│   │   └── ... (pour 2021, 2022, etc.)
│   │
│   ├── sentinel2_ndvi/                      # Sentinel-2 NDVI
│   │   ├── ndvi_2019-12-01_2020-03-01.tif
│   │   ├── ndvi_2020-03-01_2020-06-01.tif
│   │   └── ... (8 fichiers trimestriels)
│   │
│   └── gadm_410_europe.gpkg                 # GADM boundaries
│
└── ECA_blend_tx.zip                         # ECA&D stations
```

### Données de Sortie

```
GenHack4-Hackathon-Vertex/
└── data/
    └── processed/
        ├── era5_aligned.zarr/               # Données ERA5 alignées (Zarr)
        ├── stations.geojson                 # Stations ECA&D filtrées
        ├── city_boundary.geojson            # Limites de Paris
        └── ndvi_metadata.json               # Métadonnées NDVI
```

---

## 🔧 Personnalisation

### Changer la Ville

Modifiez les paramètres dans `scripts/run_etl_real_data.py` :

```python
etl = ETLPipeline(
    ...
    city_name="Lille",  # Au lieu de "Paris"
    country_code="FRA"
)
```

### Changer les Années

```python
results = etl.run_etl(
    years=[2020, 2021, 2022, 2023],  # Ajouter plus d'années
    variables=["t2m_max", "precipitation", "u10", "v10"],
    output_format="zarr"
)
```

### Changer le Format de Sortie

```python
results = etl.run_etl(
    ...
    output_format="netcdf"  # Au lieu de "zarr"
)
```

---

## 🐛 Dépannage

### Erreur : "ModuleNotFoundError: No module named 'xarray'"

**Solution** : Installez les dépendances (voir Étape 2)

### Erreur : "FileNotFoundError: ERA5 file not found"

**Solution** : Vérifiez que les fichiers NetCDF sont dans le bon répertoire :
```bash
ls datasets/main/derived-era5-land-daily-statistics/*.nc
```

### Erreur : "City Paris not found in GADM"

**Solution** : Vérifiez le nom de la ville dans GADM. Pour Paris, essayez :
- `NAME_2 == "Paris"` (par défaut)
- `NAME_5 == "Paris"` (si Paris est au niveau 5)

### Erreur : "Memory Error"

**Solution** : Réduisez le nombre d'années ou de variables :
```python
results = etl.run_etl(
    years=[2020],  # Une seule année
    variables=["t2m_max"],  # Une seule variable
    output_format="zarr"
)
```

---

## 📊 Utilisation des Données Traitées

Une fois l'ETL terminé, vous pouvez utiliser les données dans vos scripts :

```python
import xarray as xr
import geopandas as gpd

# Charger ERA5
era5 = xr.open_zarr("data/processed/era5_aligned.zarr")

# Charger stations
stations = gpd.read_file("data/processed/stations.geojson")

# Charger boundary
boundary = gpd.read_file("data/processed/city_boundary.geojson")
```

---

## ✅ Checklist

- [ ] Vérifier que tous les fichiers sont présents (`check_real_data.py`)
- [ ] Installer les dépendances Python
- [ ] Exécuter l'ETL (`run_etl_real_data.py`)
- [ ] Vérifier les fichiers de sortie dans `data/processed/`
- [ ] Tester le chargement des données traitées

---

**Dernière mise à jour** : 18 Décembre 2025

