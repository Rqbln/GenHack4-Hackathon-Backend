# 🚀 Quick Start - Utilisation des Datasets

## 📥 Téléchargement

Les datasets sont disponibles sur Google Drive : https://drive.google.com/drive/folders/1_uMrrq63e0iYCFj8A6ehN58641sJZ2x1

**Tous les fichiers téléchargés** ✅ :
- ✅ ERA5 Land Daily Statistics (24 fichiers NetCDF, ~2.4 GB)
- ✅ Sentinel-2 NDVI (8 fichiers GeoTIFF, ~8.3 GB)
- ✅ `ECA_blend_tx.zip` (736 MB) - Stations météo (8,568 stations)
- ✅ `gadm_410_europe.gpkg` (719 MB) - Limites administratives (106,252 entités)
- ✅ `read-era5-netcdf_v2.ipynb` (1.0 MB) - Notebook d'exemple
- ✅ `GenHack - Kayrros data User Guide.docx` (370 KB) - Guide officiel

## 📊 Structure des données

```
datasets/main/
├── derived-era5-land-daily-statistics/  (24 fichiers .nc)
│   ├── 2020_2m_temperature_daily_maximum.nc
│   ├── 2020_total_precipitation_daily_mean.nc
│   ├── 2020_10m_u_component_of_wind_daily_mean.nc
│   ├── 2020_10m_v_component_of_wind_daily_mean.nc
│   └── ... (2021-2025)
│
└── sentinel2_ndvi/  (8 fichiers .tif)
    ├── ndvi_2019-12-01_2020-03-01.tif
    ├── ndvi_2020-03-01_2020-06-01.tif
    └── ... (trimestres 2020-2021)
```

## 🔧 Lecture des données

### ERA5 (NetCDF)

```python
import xarray as xr

# Charger un fichier
ds = xr.open_dataset('datasets/main/derived-era5-land-daily-statistics/2023_2m_temperature_daily_maximum.nc')

# Afficher la structure
print(ds)
# Dimensions: valid_time, latitude, longitude
# Variables: t2m (température en Kelvin)

# Extraire une zone (ex: Paris)
paris_bbox = (2.2, 48.8, 2.4, 49.0)  # lon_min, lat_min, lon_max, lat_max
ds_paris = ds.sel(
    longitude=slice(paris_bbox[0], paris_bbox[2]),
    latitude=slice(paris_bbox[3], paris_bbox[1])  # Inversé car latitude décroît
)

# Convertir Kelvin en Celsius
ds_paris_celsius = ds_paris['t2m'] - 273.15

# Extraire une date spécifique
from datetime import datetime
day = datetime(2023, 7, 15)
ds_day = ds.sel(valid_time=day)

# Convertir en DataFrame
df = ds_paris.to_dataframe()
```

### Sentinel-2 NDVI (GeoTIFF)

```python
import rasterio
from rasterio.plot import show

# Charger un fichier
with rasterio.open('datasets/main/sentinel2_ndvi/ndvi_2020-03-01_2020-06-01.tif') as src:
    # Informations
    print(f"CRS: {src.crs}")
    print(f"Shape: {src.shape}")
    print(f"Bounds: {src.bounds}")
    
    # Lire les données (int8, 0-254, nodata=255)
    data_int8 = src.read(1)
    
    # Convertir vers échelle réelle (-1 à 1)
    import numpy as np
    data_float = data_int8.astype(float)
    data_float[data_float == 255] = np.nan  # NoData
    data_float = data_float / 254 * 2 - 1  # Conversion 0-254 → -1 à 1
    
    # Visualiser
    from rasterio.plot import show
    show(src, cmap='Greens', vmin=-1, vmax=1)
```

### ECA&D Stations (ZIP)

```python
import zipfile
import pandas as pd
import geopandas as gpd
from io import StringIO

# Extraire et lire les stations
with zipfile.ZipFile('ECA_blend_tx.zip') as z:
    # Lire stations.txt
    stations_content = z.read('stations.txt').decode('utf-8')
    stations_df = pd.read_csv(
        StringIO(stations_content),
        skiprows=17,
        skipinitialspace=True
    )
    
    # Convertir DMS en décimal
    def dms_to_decimal(dms_str):
        sign = 1 if dms_str[0] == '+' else -1
        parts = dms_str[1:].split(':')
        return sign * (float(parts[0]) + float(parts[1])/60 + float(parts[2])/3600)
    
    stations_df['LAT_decimal'] = stations_df['LAT'].apply(dms_to_decimal)
    stations_df['LON_decimal'] = stations_df['LON'].apply(dms_to_decimal)
    
    # Créer GeoDataFrame
    stations_gdf = gpd.GeoDataFrame(
        stations_df,
        geometry=gpd.points_from_xy(
            stations_df['LON_decimal'], 
            stations_df['LAT_decimal']
        ),
        crs="EPSG:4326"
    )
    
    # Lire les données d'une station
    station_id = 1
    station_file = f"TX_STAID{station_id:06d}.txt"
    station_content = z.read(station_file).decode('utf-8')
    station_data = pd.read_csv(
        StringIO(station_content),
        skiprows=20,
        skipinitialspace=True
    )
    
    # Filtrer données valides (Q_TX == 0)
    valid_data = station_data[station_data['Q_TX'] == 0].copy()
    valid_data['DATE'] = pd.to_datetime(valid_data['DATE'], format='%Y%m%d')
    valid_data['TX_celsius'] = valid_data['TX'] / 10  # 0.1°C → °C
```

### GADM Europe (GeoPackage)

```python
import geopandas as gpd

# Charger GADM
gadm_gdf = gpd.read_file('gadm_410_europe.gpkg')
print(f"Total rows: {len(gadm_gdf)}")  # 106,252

# Filtrer par pays et ville
country_code = "FRA"  # France
cityname = "Paris"
filtered = gadm_gdf[
    (gadm_gdf.GID_0 == country_code) & 
    (gadm_gdf.NAME_2 == cityname)  # Niveau peut varier selon la ville
]

# Dissoudre pour frontière unifiée
city_boundary = filtered.dissolve()

# Utiliser pour clipper les données raster
from rasterio.mask import mask
with rasterio.open('ndvi_file.tif') as src:
    city_geometry = [city_boundary.to_crs(src.crs).geometry.iloc[0]]
    clipped_image, clipped_transform = mask(src, city_geometry, crop=True)
```

## 🎯 Prochaines étapes

1. **Intégrer dans la pipeline** : Modifier `src/ingest.py` pour lire ces fichiers
2. **Harmoniser** : Reprojection et agrégation temporelle
3. **Visualiser** : Créer le frontend React avec cartes interactives

Voir `DATASETS_ANALYSIS.md` pour plus de détails.

