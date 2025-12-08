# 📊 Données Traitées - ETL Pipeline

Ce répertoire contient les résultats de l'ETL pipeline exécuté avec les **vraies données** du hackathon.

## 📁 Fichiers Générés

### `era5_aligned.nc`
Données ERA5 alignées et traitées :
- **Variables** : t2m (température), tp (précipitations), u10, v10 (vent)
- **Période** : 2020-2021 (731 jours)
- **Résolution spatiale** : Extraite pour la région de Paris
- **Format** : NetCDF

### `city_boundary.geojson`
Limites administratives de Paris extraites de GADM.

### `stations.geojson`
Stations météo ECA&D filtrées pour Paris (actuellement 0 stations - à investiguer).

### `etl_summary.json`
Résumé de l'exécution de l'ETL avec métadonnées.

## 🚀 Utilisation

### Charger les données ERA5

```python
import xarray as xr

# Charger les données
era5 = xr.open_dataset('data/processed/era5_aligned.nc')

# Accéder aux variables
temperature = era5['t2m']  # Température en °C
precipitation = era5['tp']  # Précipitations en m
```

### Charger les limites de la ville

```python
import geopandas as gpd

boundary = gpd.read_file('data/processed/city_boundary.geojson')
```

## 📝 Notes

- Les données ERA5 ont été converties de Kelvin à Celsius pour la température
- Les données sont filtrées spatialement pour la région de Paris
- Les données sont alignées temporellement (2020-2021)

## 🔄 Régénérer les Données

Pour régénérer ces fichiers :

```bash
cd GenHack4-Hackathon-Vertex
source venv/bin/activate
python3 scripts/run_etl_simple.py
```

---

**Date de génération** : 18 Décembre 2025  
**Script utilisé** : `scripts/run_etl_simple.py`


