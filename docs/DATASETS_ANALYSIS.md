# 📊 Analyse des Datasets GenHack 2025

> **Documentation complète des datasets fournis pour le hackathon**  
> **Source** : Google Drive GenHack 2025  
> **Date d'analyse** : 9 novembre 2025

---

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Datasets disponibles](#datasets-disponibles)
3. [Structure des données](#structure-des-données)
4. [Exploitation pour le hackathon](#exploitation-pour-le-hackathon)
5. [Intégration avec notre pipeline](#intégration-avec-notre-pipeline)
6. [Recommandations pour le frontend React](#recommandations-pour-le-frontend-react)

---

## 🎯 Vue d'ensemble

Les organisateurs ont fourni **3 types de datasets principaux** pour analyser les îlots de chaleur urbains :

1. **ERA5 Land Daily Statistics** - Données climatiques quotidiennes (2020-2025)
2. **Sentinel-2 NDVI** - Indices de végétation trimestriels (2019-2021)
3. **ECA&D Stations** - Observations météo des stations au sol (fichier ZIP)
4. **GADM Europe** - Limites administratives (fichier GeoPackage)

**Total téléchargé** : ~12.2 GB de données
- ERA5 : ~2.4 GB
- Sentinel-2 NDVI : ~8.3 GB
- ECA&D : 736 MB
- GADM : 719 MB
- Documentation : ~1.4 MB

---

## 📦 Datasets disponibles

### 1. ERA5 Land Daily Statistics

**Emplacement** : `datasets/main/derived-era5-land-daily-statistics/`  
**Taille totale** : ~2.4 GB  
**Format** : NetCDF (.nc)  
**Période** : 2020-2025 (6 années)

#### Fichiers disponibles (24 fichiers)

**Température maximale quotidienne (2m)** :
- `2020_2m_temperature_daily_maximum.nc`
- `2021_2m_temperature_daily_maximum.nc`
- `2022_2m_temperature_daily_maximum.nc`
- `2023_2m_temperature_daily_maximum.nc`
- `2024_2m_temperature_daily_maximum.nc`
- `2025_2m_temperature_daily_maximum.nc`

**Composante U du vent (10m)** :
- `2020_10m_u_component_of_wind_daily_mean.nc`
- `2021_10m_u_component_of_wind_daily_mean.nc`
- `2022_10m_u_component_of_wind_daily_mean.nc`
- `2023_10m_u_component_of_wind_daily_mean.nc`
- `2024_10m_u_component_of_wind_daily_mean.nc`
- `2025_10m_u_component_of_wind_daily_mean.nc`

**Composante V du vent (10m)** :
- `2020_10m_v_component_of_wind_daily_mean.nc`
- `2021_10m_v_component_of_wind_daily_mean.nc`
- `2022_10m_v_component_of_wind_daily_mean.nc`
- `2023_10m_v_component_of_wind_daily_mean.nc`
- `2024_10m_v_component_of_wind_daily_mean.nc`
- `2025_10m_v_component_of_wind_daily_mean.nc`

**Précipitations totales (moyenne quotidienne)** :
- `2020_total_precipitation_daily_mean.nc`
- `2021_total_precipitation_daily_mean.nc`
- `2022_total_precipitation_daily_mean.nc`
- `2023_total_precipitation_daily_mean.nc`
- `2024_total_precipitation_daily_mean.nc`
- `2025_total_precipitation_daily_mean.nc`

#### Structure (NetCDF)

D'après le notebook `read-era5-netcdf_v2.ipynb` et le User Guide :

**Dimensions** :
- `valid_time` : Jours (365 ou 366 selon l'année)
- `latitude` : Grille latitudinale
- `longitude` : Grille longitudinale

**Variables** (noms dans les fichiers NetCDF) :
- `t2m` : Température maximale quotidienne (2m) en **Kelvin** (convertir en °C : K - 273.15)
- `tp` : Précipitations totales (moyenne quotidienne) en **mètres**
- `u10` : Composante U du vent (10m, moyenne quotidienne) en **m/s**
- `v10` : Composante V du vent (10m, moyenne quotidienne) en **m/s**

**Coordonnées** :
- `valid_time` : Timestamps quotidiens (dimension temporelle)
- `latitude` : Latitudes (WGS84, EPSG:4326) - ordre décroissant (Nord → Sud)
- `longitude` : Longitudes (WGS84, EPSG:4326) - ordre croissant (Ouest → Est)

**⚠️ Important** : 
- La dimension temporelle s'appelle `valid_time` (pas `time`)
- Les latitudes sont en ordre décroissant (utiliser `slice(lat_max, lat_min)` pour sélectionner)

**Résolution spatiale** : ~9 km × 9 km (selon User Guide)  
**Période** : Janvier 2020 - Octobre 2025  
**Source** : ERA5-Land hourly data (agrégé en quotidien)

---

### 2. Sentinel-2 NDVI

**Emplacement** : `datasets/main/sentinel2_ndvi/`  
**Taille totale** : ~8.3 GB  
**Format** : GeoTIFF (.tif)  
**Période disponible** : Décembre 2019 - Décembre 2021 (8 trimestres)  
**Note** : Le User Guide mentionne 2020-2023, mais seuls 8 fichiers sont disponibles dans le Drive (2020-2021). Les données 2022-2023 peuvent être manquantes ou non fournies.

#### Fichiers disponibles (8 fichiers)

**Trimestres disponibles** :
- `ndvi_2019-12-01_2020-03-01.tif` (Hiver 2019-2020)
- `ndvi_2020-03-01_2020-06-01.tif` (Printemps 2020)
- `ndvi_2020-06-01_2020-09-01.tif` (Été 2020)
- `ndvi_2020-09-01_2020-12-01.tif` (Automne 2020)
- `ndvi_2020-12-01_2021-03-01.tif` (Hiver 2020-2021)
- `ndvi_2021-03-01_2021-06-01.tif` (Printemps 2021)
- `ndvi_2021-06-01_2021-09-01.tif` (Été 2021)
- `ndvi_2021-09-01_2021-12-01.tif` (Automne 2021)

**Taille moyenne** : ~1.1 GB par fichier  
**Stockage** : Format int8 compressé (nécessite conversion vers float -1 à 1)

#### Structure (GeoTIFF)

**Format** : GeoTIFF  
**Résolution spatiale** : **80 m × 80 m** (selon User Guide)  
**CRS** : Variable selon le fichier (à vérifier avec rasterio)  
**Stockage** : **int8** sur échelle 0-254 (nécessite conversion)
- **0-254** : Valeurs NDVI linéaires
- **255** : NoData (à remplacer par NaN)
- **Conversion** : `(value / 254) * 2 - 1` → échelle -1 à 1

**Valeurs NDVI après conversion** : -1 à 1 (float)
- **< 0** : Eau, nuages
- **0 - 0.2** : Sol nu, zones urbaines
- **0.2 - 0.5** : Végétation clairsemée
- **> 0.5** : Végétation dense

**Période** : 2020-2023 (selon User Guide, mais fichiers disponibles jusqu'à 2021)  
**Résolution temporelle** : Trimestrielle (4 fichiers/an)  
**Source** : Calculé depuis bandes B04 et B08 de Sentinel-2  
**Couverture** : Europe

---

### 3. ECA&D Stations ✅

**Fichier** : `ECA_blend_tx.zip`  
**Taille** : 736 MB  
**Format** : ZIP contenant des fichiers TXT  
**Source** : European Climate Assessment & Dataset (ECAD.eu)

#### Contenu

Le fichier ZIP contient **8,572 fichiers** :
- **`stations.txt`** : Métadonnées des stations (8,568 stations)
- **`sources.txt`** : Informations sur les sources de données
- **`elements.txt`** : Description des éléments météorologiques
- **`date_timestamp.txt`** : Informations temporelles
- **`TX_STAID{XXXXXX}.txt`** : Données de température maximale par station (8,568 fichiers)

#### Structure des fichiers

**`stations.txt`** :
- Format : CSV avec en-tête
- Colonnes :
  - `STAID` : Identifiant de station (1-8568)
  - `STANAME` : Nom de la station
  - `CN` : Code pays (ISO 3166)
  - `LAT` : Latitude en DMS (Degrees:Minutes:Seconds)
  - `LON` : Longitude en DMS
  - `HGHT` : Altitude en mètres
- **Total** : 8,568 stations en Europe

**`TX_STAID{XXXXXX}.txt`** (exemple : `TX_STAID000001.txt`) :
- Format : CSV avec en-tête (20 lignes de métadonnées)
- Colonnes :
  - `STAID` : Identifiant de station
  - `SOUID` : Identifiant de source
  - `DATE` : Date au format YYYYMMDD
  - `TX` : Température maximale en 0.1°C (diviser par 10 pour obtenir °C)
  - `Q_TX` : Code qualité (0='valid', 1='suspect', 9='missing')
- **Valeur manquante** : -9999
- **Période** : Données historiques depuis 1882 (selon le notebook, certaines stations ont >54,000 enregistrements)

#### Utilisation

- **Validation** : Comparer ERA5 avec observations réelles
- **Calibration** : Ajuster les modèles de downscaling
- **Analyse** : Identifier les biais systématiques dans ERA5

**Exemple d'utilisation** (d'après le notebook) :
```python
import pandas as pd
import geopandas as gpd

# Lire les stations
stations_df = pd.read_csv('stations.txt', skiprows=17)
# Convertir DMS en décimal
stations_df['LAT_decimal'] = stations_df['LAT'].apply(dms_to_decimal)
stations_df['LON_decimal'] = stations_df['LON'].apply(dms_to_decimal)

# Filtrer par zone d'intérêt
stations_gdf = gpd.GeoDataFrame(
    stations_df,
    geometry=gpd.points_from_xy(stations_df['LON_decimal'], stations_df['LAT_decimal']),
    crs="EPSG:4326"
)

# Lire les données d'une station
station_data = pd.read_csv('TX_STAID000001.txt', skiprows=20)
valid_data = station_data[station_data['Q_TX'] == 0]  # Qualité valide
valid_data['TX_celsius'] = valid_data['TX'] / 10  # Conversion 0.1°C → °C
```

---

### 4. GADM Europe ✅

**Fichier** : `gadm_410_europe.gpkg`  
**Taille** : 719 MB  
**Format** : GeoPackage (.gpkg)  
**Source** : Global Administrative Areas Database (GADM.org)  
**Version** : 4.1.0 (latest)

#### Contenu

**Limites administratives** pour l'Europe :
- **Table principale** : `gadm_410_europe_light`
- **Total de lignes** : 106,252 entités administratives
- **Format vectoriel** : Polygones (MULTIPOLYGON) avec attributs

#### Structure de la table

**Colonnes principales** :
- `fid` : Identifiant unique
- `geom` : Géométrie (MULTIPOLYGON)
- `UID` : Identifiant utilisateur
- `GID_0` : Identifiant niveau 0 (pays)
- `NAME_0` : Nom du pays
- `GID_1` : Identifiant niveau 1 (région/état)
- `NAME_1` : Nom de la région
- `ENGTYPE_1` : Type de région (ex: "State", "Province")
- `GID_2` : Identifiant niveau 2 (département/comté)
- `NAME_2` : Nom du département
- `ENGTYPE_2` : Type de département
- `GID_3`, `NAME_3`, `ENGTYPE_3` : Niveau 3 (sous-département)
- `GID_4`, `NAME_4`, `ENGTYPE_4` : Niveau 4 (commune/ville)
- ... (jusqu'à GID_5, NAME_5, ENGTYPE_5)

**⚠️ Important** : Le niveau administratif des villes varie selon les pays :
- **Berlin (Allemagne)** : `NAME_2` (niveau 2)
- **Paris (France)** : `NAME_2` (niveau 2, car divisé en arrondissements)
- **Lille (France)** : `NAME_5` (niveau 5)
- **Autres villes** : Peuvent être à différents niveaux

#### Utilisation

**Exemple d'utilisation** (d'après le notebook) :
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
    (gadm_gdf.NAME_2 == cityname)
]

# Dissoudre les polygones pour obtenir une frontière unifiée
city_boundary = filtered.dissolve()

# Utiliser pour clipper les données raster
from rasterio.mask import mask
with rasterio.open('ndvi_file.tif') as src:
    city_geometry = [city_boundary.geometry.iloc[0]]
    clipped_image, clipped_transform = mask(src, city_geometry, crop=True)
```

**Utilisations principales** :
- Définir les zones d'étude (villes, régions)
- Clipper les données raster par zone administrative
- Analyser les îlots de chaleur par zone urbaine
- Calculer des statistiques par zone administrative

---

### 5. Notebook d'exemple ✅

**Fichier** : `read-era5-netcdf_v2.ipynb`  
**Taille** : 1.0 MB  
**Format** : Jupyter Notebook

#### Contenu

Le notebook contient **65 cellules** avec des exemples complets :

**1. Import des bibliothèques** :
- `xarray` : Manipulation NetCDF
- `pandas` : Manipulation de données tabulaires
- `rasterio` : Lecture/écriture GeoTIFF
- `rioxarray` : Combinaison xarray + rasterio
- `geopandas` : Données vectorielles
- `matplotlib` : Visualisations

**2. GADM - Limites administratives** :
- Chargement du fichier GeoPackage
- Filtrage par pays et ville
- Dissolution des polygones pour frontière unifiée
- Visualisation des limites

**3. ERA5-Land - Données météorologiques** :
- Structure des fichiers NetCDF
- Variables disponibles et mapping
- Lecture d'un fichier unique
- Lecture de multiples fichiers (combinaison)
- Sélection spatiale (latitude/longitude)
- Sélection temporelle (date spécifique)
- Visualisations

**4. Sentinel-2 NDVI - Indices de végétation** :
- Fonction de conversion NDVI (int8 0-254 → float -1 à 1)
- Clipping par zone d'intérêt
- Visualisation des cartes NDVI
- Calcul de séries temporelles (moyenne NDVI par trimestre)
- Graphiques d'évolution temporelle

**5. Reprojection ERA5 sur grille NDVI** :
- Reprojection de données ERA5 (EPSG:4326) vers CRS NDVI
- Alignement spatial pour analyse combinée
- Visualisation des données reprojetées

**6. ECA&D - Stations météo** :
- Lecture du fichier `stations.txt`
- Conversion DMS → décimal
- Filtrage des stations par zone d'intérêt
- Lecture des données d'une station spécifique
- Visualisation des séries temporelles
- Validation avec code qualité

#### Points clés du notebook

**Mapping des variables ERA5** :
```python
variable2statistic = {
    "2m_temperature": "daily_maximum",
    "total_precipitation": "daily_mean",
    "10m_u_component_of_wind": "daily_mean",
    "10m_v_component_of_wind": "daily_mean",
}

variable2datavar = {
    "2m_temperature": "t2m",
    "total_precipitation": "tp",
    "10m_u_component_of_wind": "u10",
    "10m_v_component_of_wind": "v10",
}
```

**Conversion NDVI** :
```python
def convert_ndvi_to_real_scale(ndvi_img, out_meta):
    # NDVI stocké en int8 sur échelle 0/254, nodata = 255
    # Conversion vers float -1/1, nodata → np.nan
    ndvi_img = ndvi_img.astype(float)
    ndvi_img[ndvi_img == out_meta["nodata"]] = np.nan
    ndvi_img = ndvi_img / 254 * 2 - 1
    return ndvi_img
```

**Période NDVI** :
- Trimestres disponibles : 2020 Q1-Q4, 2021 Q1-Q4 (8 fichiers)
- Format de nommage : `ndvi_YYYY-MM-DD_YYYY-MM-DD.tif`
- Mapping trimestre → période :
  - Q1 : `{year-1}-12-01_{year}-03-01` (Hiver)
  - Q2 : `{year}-03-01_{year}-06-01` (Printemps)
  - Q3 : `{year}-06-01_{year}-09-01` (Été)
  - Q4 : `{year}-09-01_{year}-12-01` (Automne)

---

## 🔍 Structure des données

### Harmonisation temporelle

**Problème** : Les datasets ont des résolutions temporelles différentes :
- **ERA5** : Quotidien (365-366 jours/an, 2020-2025)
- **Sentinel-2 NDVI** : Trimestriel (4 fichiers/an, 2020-2021 seulement)
- **ECA&D** : Quotidien (données historiques depuis 1882)

**Solution** : Agrégation mensuelle (comme l'équipe Pentagen)
- **ERA5** : Moyenne mensuelle des valeurs quotidiennes
- **Sentinel-2 NDVI** : Utiliser la valeur trimestrielle pour les 3 mois correspondants
  - Q1 (Hiver) : Déc-Mar → appliquer à Jan, Fév, Mar
  - Q2 (Printemps) : Mar-Juin → appliquer à Avr, Mai, Juin
  - Q3 (Été) : Juin-Sept → appliquer à Juil, Août, Sept
  - Q4 (Automne) : Sept-Déc → appliquer à Oct, Nov, Déc
- **ECA&D** : Moyenne mensuelle des valeurs quotidiennes
- **Alternative** : Interpolation temporelle pour avoir des valeurs mensuelles plus précises

### Harmonisation spatiale

**Problème** : Résolutions spatiales très différentes :
- **ERA5** : ~9 km × 9 km
- **Sentinel-2 NDVI** : 80 m × 80 m
- **Ratio** : ~112x différence de résolution (pas 1000x comme estimé initialement)

**Solution** : Reprojection et resampling (exemple dans le notebook)
- **Reprojeter ERA5 sur la grille NDVI** (downscaling) :
  ```python
  reprojected_da = da.rio.write_crs("EPSG:4326").rio.reproject(
      dst_crs=target_crs,  # CRS du NDVI
      shape=(target_height, target_width),
      transform=target_transform,
  )
  ```
- **Alternative** : Agréger NDVI à la résolution ERA5 (upsampling) - perte d'information
- **Recommandation** : Garder la haute résolution NDVI (80m) et downscaler ERA5 pour analyses détaillées

### Couverture géographique

**Zone d'étude** : Probablement Europe (d'après GADM Europe)

**Villes cibles** : Non spécifiées dans les noms de fichiers, mais probablement :
- Paris (mentionné dans notre config)
- Autres grandes villes européennes

---

## 🚀 Exploitation pour le hackathon

### Période 1 - Warm-Up (13-17 novembre)

**Objectif** : Explorer les datasets

**Actions** :
1. ✅ **Télécharger les datasets** (fait, sauf ECA&D et GADM)
2. **Lire les fichiers NetCDF ERA5**
   - Utiliser `xarray` pour charger les données
   - Visualiser la structure (dimensions, variables, coordonnées)
   - Extraire une zone d'intérêt (ex: Paris)
3. **Lire les fichiers GeoTIFF NDVI**
   - Utiliser `rasterio` pour charger les rasters
   - Visualiser la couverture spatiale
   - Vérifier le CRS et la résolution
4. **Analyser la couverture temporelle**
   - Identifier les périodes communes
   - Détecter les gaps dans les données

**Livrables** :
- Notebook Jupyter avec exploration
- Visualisations des données brutes
- Description de la structure

### Période 2 - Visualisation (17-24 novembre)

**Objectif** : Visualiser l'effet UHI

**Actions** :
1. **Harmoniser les données**
   - Reprojeter ERA5 sur la grille NDVI
   - Agréger temporellement (mensuel)
   - Créer une table harmonisée
2. **Calculer des indicateurs**
   - Différence température urbain-rural
   - Corrélation NDVI-température
   - Zones de chaleur (heat maps)
3. **Visualisations interactives**
   - Cartes de chaleur avec overlay NDVI
   - Graphiques temporels
   - Comparaisons spatiales

**Livrables** :
- Visualisations interactives (React frontend)
- Cartes de chaleur
- Graphiques d'évolution temporelle

### Période 3 - Métriques (24 nov - 1 déc)

**Objectif** : Proposer des métriques quantitatives

**Actions** :
1. **Métriques de performance**
   - RMSE, MAE, R² entre ERA5 et stations ECA&D
   - Validation croisée
2. **Métriques de chaleur**
   - Intensité UHI (différence urbain-rural)
   - Durée des vagues de chaleur
   - Étendue spatiale des zones chaudes
3. **Métriques composites**
   - Score combinant température, NDVI, précipitation
   - Indices de stress thermique

**Livrables** :
- Calculs de métriques
- Tableaux de résultats
- Visualisations des métriques

### Période 4 - Modélisation (1-4 décembre)

**Objectif** : Modèles explicatifs

**Actions** :
1. **Modèles de downscaling**
   - U-Net pour downscaling ERA5 → résolution NDVI
   - Features : NDVI, altitude, urbanisation
2. **Modèles prédictifs**
   - Prédiction température à partir de NDVI
   - Ajustements ERA5 basés sur observations
3. **Recommandations**
   - Zones prioritaires pour végétalisation
   - Impact potentiel de mesures

**Livrables** :
- Modèles entraînés
- Prédictions et ajustements
- Rapport final

---

## 🔧 Intégration avec notre pipeline

### Modifications nécessaires dans `src/ingest.py`

**Actuellement** : Génère des données mock  
**Objectif** : Lire les vrais fichiers NetCDF et GeoTIFF

#### Pour ERA5

```python
import xarray as xr
from pathlib import Path

def load_era5_data(
    data_dir: Path,
    variable: str,  # "t2m_max", "precipitation", "u10", "v10"
    year: int,
    bbox: tuple = None  # (lon_min, lat_min, lon_max, lat_max)
) -> xr.Dataset:
    """
    Charge les données ERA5 depuis les fichiers NetCDF
    
    Args:
        data_dir: Répertoire contenant les fichiers .nc
        variable: Variable à charger
        year: Année
        bbox: Bounding box pour extraire une zone
        
    Returns:
        Dataset xarray avec les données
    """
    # Mapper variable → nom de fichier
    file_map = {
        "t2m_max": f"{year}_2m_temperature_daily_maximum.nc",
        "precipitation": f"{year}_total_precipitation_daily_mean.nc",
        "u10": f"{year}_10m_u_component_of_wind_daily_mean.nc",
        "v10": f"{year}_10m_v_component_of_wind_daily_mean.nc",
    }
    
    file_path = data_dir / file_map[variable]
    ds = xr.open_dataset(file_path)
    
    # Extraire zone d'intérêt si bbox fourni
    if bbox:
        lon_min, lat_min, lon_max, lat_max = bbox
        ds = ds.sel(
            longitude=slice(lon_min, lon_max),
            latitude=slice(lat_max, lat_min)  # Inversé car latitude décroît
        )
    
    return ds
```

#### Pour Sentinel-2 NDVI

```python
import rasterio
from rasterio.mask import mask
import numpy as np

def convert_ndvi_to_real_scale(ndvi_img, nodata_value=255):
    """
    Convertit NDVI de int8 (0-254) vers float (-1 à 1)
    
    Args:
        ndvi_img: Array int8 avec valeurs 0-254, nodata=255
        nodata_value: Valeur représentant NoData (défaut: 255)
        
    Returns:
        Array float avec valeurs -1 à 1, NaN pour NoData
    """
    ndvi_img = ndvi_img.astype(float)
    ndvi_img[ndvi_img == nodata_value] = np.nan
    ndvi_img = ndvi_img / 254 * 2 - 1
    return ndvi_img

def load_ndvi_data(
    data_dir: Path,
    start_date: str,  # "2020-03-01"
    end_date: str,    # "2020-06-01"
    city_geometry: gpd.GeoDataFrame = None
) -> tuple[np.ndarray, dict]:
    """
    Charge les données NDVI depuis les fichiers GeoTIFF
    
    Args:
        data_dir: Répertoire contenant les fichiers .tif
        start_date: Date de début (format YYYY-MM-DD)
        end_date: Date de fin
        city_geometry: GeoDataFrame avec géométrie de la ville (optionnel)
        
    Returns:
        Tuple (array NDVI converti, métadonnées)
    """
    file_name = f"ndvi_{start_date}_{end_date}.tif"
    file_path = data_dir / file_name
    
    with rasterio.open(file_path) as src:
        if city_geometry is not None:
            # Clipper par géométrie de la ville
            city_geometry_crs = city_geometry.to_crs(src.crs)
            geometry_list = [city_geometry_crs.geometry.iloc[0]]
            out_image, out_transform = mask(src, geometry_list, crop=True)
            out_meta = src.meta.copy()
            out_meta.update({
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform
            })
        else:
            out_image = src.read(1)
            out_meta = src.meta
        
        # Convertir NDVI vers échelle réelle
        real_ndvi = convert_ndvi_to_real_scale(out_image, out_meta.get("nodata", 255))
    
    return real_ndvi, out_meta
```

### Modifications dans `src/preprocess.py`

**Ajouter** :
- Reprojection ERA5 (EPSG:4326) → grille NDVI (EPSG:3857 ou autre)
- Resampling pour aligner les résolutions
- Agrégation temporelle (quotidien → mensuel)

### Modifications dans `src/features.py`

**Déjà implémenté** : Calcul NDVI  
**À ajouter** :
- Calcul depuis vraies images Sentinel-2 (si nécessaire)
- Validation que les fichiers NDVI fournis sont corrects

---

## 🎨 Recommandations pour le frontend React

### Différenciation avec les autres équipes

**Problème** : Beaucoup d'équipes utilisent Jupyter Notebook  
**Solution** : **Frontend React interactif et visuel**

### Architecture proposée

```
Frontend React
├── Dashboard principal
│   ├── Carte interactive (Mapbox/Leaflet)
│   │   ├── Overlay température (ERA5)
│   │   ├── Overlay NDVI (Sentinel-2)
│   │   ├── Overlay zones de chaleur (calculées)
│   │   └── Stations météo (ECA&D)
│   ├── Contrôles temporels
│   │   ├── Sélecteur de période (2020-2025)
│   │   ├── Animation temporelle (play/pause)
│   │   └── Graphiques temporels
│   └── Panneau d'analyse
│       ├── Métriques en temps réel
│       ├── Comparaisons spatiales
│       └── Export de données
│
├── Page d'exploration des données
│   ├── Visualisation des datasets bruts
│   ├── Statistiques descriptives
│   └── Détection de patterns
│
├── Page d'analyse avancée
│   ├── Calcul de métriques
│   ├── Modèles de prédiction
│   └── Recommandations
│
└── Page de rapports
    ├── Génération de rapports PDF
    ├── Export de visualisations
    └── Partage de résultats
```

### Technologies recommandées

#### Cartographie
- **Mapbox GL JS** ou **Leaflet** : Cartes interactives
- **Deck.gl** : Visualisation de données géospatiales (heatmaps, 3D)
- **Turf.js** : Calculs géospatiaux côté client

#### Visualisation
- **D3.js** : Graphiques personnalisés
- **Recharts** ou **Chart.js** : Graphiques simples
- **Observable Plot** : Visualisations déclaratives

#### Gestion d'état
- **Zustand** ou **Redux Toolkit** : État global
- **React Query** : Gestion des données serveur

#### UI/UX
- **Tailwind CSS** : Styling rapide
- **Shadcn/ui** : Composants React modernes
- **Framer Motion** : Animations fluides

### Fonctionnalités clés à implémenter

#### 1. Carte interactive avec overlays

```typescript
// Exemple de structure
interface MapOverlay {
  id: string;
  type: 'temperature' | 'ndvi' | 'heat' | 'stations';
  data: GeoJSON | RasterData;
  opacity: number;
  visible: boolean;
  colormap: string;
}

// Composant React
<MapContainer>
  <TemperatureOverlay data={era5Data} />
  <NDVIOverlay data={ndviData} />
  <HeatZonesOverlay data={calculatedHeatZones} />
  <WeatherStations data={ecadStations} />
</MapContainer>
```

#### 2. Animation temporelle

```typescript
// Contrôles de lecture
<TimelineControls>
  <PlayButton />
  <DateRangePicker start="2020-01-01" end="2025-12-31" />
  <SpeedControl speed={1 | 2 | 5 | 10} /> // jours/seconde
  <StepControls step="day" | "month" | "quarter" />
</TimelineControls>

// Mise à jour automatique de la carte
useEffect(() => {
  if (isPlaying) {
    const interval = setInterval(() => {
      setCurrentDate(addDays(currentDate, 1));
      updateMapData(currentDate);
    }, 1000 / speed);
    return () => clearInterval(interval);
  }
}, [isPlaying, currentDate, speed]);
```

#### 3. Graphiques interactifs

```typescript
// Graphique temporel avec sélection
<TimeSeriesChart
  data={temperatureData}
  xAxis="date"
  yAxis="temperature"
  onPointClick={(point) => {
    // Mettre à jour la carte pour cette date
    setCurrentDate(point.date);
    centerMapOnPoint(point.location);
  }}
/>

// Graphique de corrélation
<ScatterPlot
  xData={ndviValues}
  yData={temperatureValues}
  xLabel="NDVI"
  yLabel="Température (°C)"
  showRegressionLine={true}
/>
```

#### 4. Calculs en temps réel

```typescript
// Calcul de métriques côté client
const calculateUHI = (urbanTemp: number, ruralTemp: number) => {
  return urbanTemp - ruralTemp;
};

const calculateHeatIndex = (temp: number, humidity: number) => {
  // Formule de l'indice de chaleur
  // ...
};

// Affichage en temps réel
<MetricsPanel>
  <MetricCard
    label="UHI Intensity"
    value={calculateUHI(urbanTemp, ruralTemp)}
    unit="°C"
    trend="increasing"
  />
  <MetricCard
    label="Heat Index"
    value={calculateHeatIndex(temp, humidity)}
    unit="°C"
    alert={heatIndex > 40 ? "danger" : "normal"}
  />
</MetricsPanel>
```

#### 5. Export et partage

```typescript
// Export de visualisations
const exportMapAsImage = () => {
  const mapCanvas = map.getCanvas();
  const dataURL = mapCanvas.toDataURL('image/png');
  downloadImage(dataURL, 'heat-map.png');
};

// Export de données
const exportDataAsCSV = (data: any[]) => {
  const csv = convertToCSV(data);
  downloadFile(csv, 'analysis-results.csv', 'text/csv');
};

// Génération de rapport PDF
const generateReport = async () => {
  const report = await fetch('/api/reports/generate', {
    method: 'POST',
    body: JSON.stringify({
      period: selectedPeriod,
      city: selectedCity,
      metrics: calculatedMetrics,
    }),
  });
  const pdfBlob = await report.blob();
  downloadFile(pdfBlob, 'report.pdf', 'application/pdf');
};
```

### Design recommandé

#### Palette de couleurs

```css
/* Température */
.temperature-cold { color: #0066CC; }  /* Bleu (froid) */
.temperature-mild { color: #00CC66; }  /* Vert (doux) */
.temperature-warm { color: #FFCC00; }  /* Jaune (chaud) */
.temperature-hot { color: #FF6600; }   /* Orange (très chaud) */
.temperature-extreme { color: #CC0000; } /* Rouge (extrême) */

/* NDVI */
.ndvi-water { color: #0000FF; }        /* Bleu (eau) */
.ndvi-bare { color: #CCCCCC; }         /* Gris (sol nu) */
.ndvi-sparse { color: #FFFF00; }       /* Jaune (végétation clairsemée) */
.ndvi-dense { color: #00FF00; }        /* Vert (végétation dense) */

/* UI */
.primary { color: #2563EB; }           /* Bleu primaire */
.secondary { color: #10B981; }         /* Vert secondaire */
.danger { color: #EF4444; }            /* Rouge (alertes) */
.warning { color: #F59E0B; }           /* Orange (avertissements) */
```

#### Layout

```
┌─────────────────────────────────────────────────────────┐
│  Header: Logo | Navigation | User Menu                  │
├──────────────┬──────────────────────────────────────────┤
│              │                                          │
│  Sidebar     │         Carte Interactive                │
│  - Filtres   │         (Mapbox/Leaflet)                 │
│  - Métriques │                                          │
│  - Contrôles │                                          │
│              │                                          │
│  Timeline    │         Graphiques                       │
│  Controls    │         (D3.js/Recharts)                 │
│              │                                          │
└──────────────┴──────────────────────────────────────────┘
```

### Intégration avec le backend

#### API REST à créer

```typescript
// Endpoints nécessaires
interface APIEndpoints {
  // Données
  '/api/data/era5': {
    GET: {
      params: { variable: string; year: number; bbox?: number[] };
      returns: GeoJSON | RasterData;
    };
  };
  '/api/data/ndvi': {
    GET: {
      params: { start: string; end: string; bbox?: number[] };
      returns: RasterData;
    };
  };
  '/api/data/stations': {
    GET: {
      params: { bbox?: number[] };
      returns: GeoJSON;
    };
  };
  
  // Calculs
  '/api/analysis/uhi': {
    POST: {
      body: { period: string; bbox: number[] };
      returns: { intensity: number; zones: GeoJSON };
    };
  };
  '/api/analysis/correlation': {
    POST: {
      body: { variable1: string; variable2: string; period: string };
      returns: { correlation: number; scatterData: Point[] };
    };
  };
  
  // Rapports
  '/api/reports/generate': {
    POST: {
      body: { period: string; city: string; metrics: any };
      returns: PDF blob;
    };
  };
}
```

### Avantages du frontend React vs Jupyter

✅ **Interactivité** : Cartes cliquables, animations, filtres en temps réel  
✅ **Performance** : Calculs côté client, pas besoin de recharger le notebook  
✅ **UX moderne** : Interface professionnelle, responsive  
✅ **Partage facile** : URL partageable, pas besoin d'environnement Python  
✅ **Collaboration** : Plusieurs utilisateurs peuvent explorer simultanément  
✅ **Export** : Génération de rapports PDF, export de données  
✅ **Scalabilité** : Peut gérer de grandes quantités de données avec pagination/virtualisation  

---

## 📝 Checklist d'implémentation

### Phase 1 - Exploration (Semaine 1)

- [x] Télécharger tous les datasets ✅
- [ ] Lire les fichiers NetCDF ERA5 avec xarray
- [ ] Lire les fichiers GeoTIFF NDVI avec rasterio (attention conversion int8 → float)
- [ ] Lire les stations ECA&D et filtrer par zone
- [ ] Charger GADM et identifier les limites de villes
- [ ] Visualiser la structure des données
- [ ] Identifier les zones d'intérêt (ex: Paris, Berlin)

### Phase 2 - Intégration Backend (Semaine 2)

- [ ] Modifier `src/ingest.py` pour lire les vrais fichiers
- [ ] Implémenter harmonisation temporelle (mensuelle)
- [ ] Implémenter harmonisation spatiale (reprojection)
- [ ] Upload des données traitées vers GCS
- [ ] Créer API REST pour servir les données

### Phase 3 - Frontend React (Semaine 2-3)

- [ ] Setup projet React (Vite + TypeScript)
- [ ] Intégration Mapbox/Leaflet
- [ ] Composant de carte avec overlays
- [ ] Contrôles temporels (timeline, animation)
- [ ] Graphiques interactifs
- [ ] Panneau de métriques
- [ ] Export de données/rapports

### Phase 4 - Analyse avancée (Semaine 3-4)

- [ ] Calcul de métriques (UHI, corrélations)
- [ ] Modèles de prédiction
- [ ] Visualisations avancées (3D, animations)
- [ ] Génération de rapports PDF
- [ ] Tests et optimisations

---

## 🔗 Ressources

### Documentation

- **ERA5** : https://www.ecmwf.int/en/forecasts/datasets/reanalysis-datasets/era5
- **Sentinel-2** : https://sentinel.esa.int/web/sentinel/missions/sentinel-2
- **NDVI** : https://en.wikipedia.org/wiki/Normalized_difference_vegetation_index
- **ECA&D** : https://www.ecad.eu/

### Bibliothèques Python

- `xarray` : Manipulation de données NetCDF
- `rasterio` : Lecture/écriture de rasters GeoTIFF
- `geopandas` : Manipulation de données vectorielles
- `rioxarray` : Combinaison xarray + rasterio

### Bibliothèques JavaScript/React

- `mapbox-gl` : Cartes interactives
- `deck.gl` : Visualisation géospatiale
- `d3` : Visualisations personnalisées
- `recharts` : Graphiques React
- `turf.js` : Calculs géospatiaux

---

---

## 📖 User Guide - Guide d'utilisation officiel

### Document officiel

**Fichier** : `GenHack - Kayrros data User Guide.docx`  
**Source** : Kayrros (partenaire du hackathon)  
**Taille** : 370 KB

### Liens utiles

- **Google Drive principal** : https://drive.google.com/drive/folders/1_uMrrq63e0iYCFj8A6ehN58641sJZ2x1
- **Notebook Jupyter** : https://drive.google.com/file/d/1g2hk8rsZlNBmgVuW7Ut6cqfMps5qUiG1/view

### Requirements Python

D'après le User Guide, les dépendances requises sont :
```toml
requires-python = ">=3.12"
dependencies = [
    "dask>=2025.10.0",
    "geopandas>=1.1.1",
    "h5netcdf>=1.6.4",
    "ipykernel>=6.30.1",
    "matplotlib>=3.10.6",
    "rasterio>=1.4.3",
    "rioxarray>=0.19.0",
    "xarray>=2025.9.0",
]
```

**⚠️ Note** : Notre pipeline utilise Python 3.11, mais le User Guide recommande Python 3.12+. Vérifier la compatibilité.

### Résumé des datasets (User Guide)

| Dataset | Format | Résolution spatiale | Résolution temporelle | Période | Taille |
|---------|--------|---------------------|----------------------|---------|--------|
| **ERA5-Land** | NetCDF | ~9 km × 9 km | Quotidien | 2020-2025 | ~2.5 GB |
| **Sentinel-2 NDVI** | GeoTIFF | 80 m × 80 m | Trimestriel | 2020-2023 | ~16 GB |
| **ECA&D Stations** | TXT (ZIP) | Points (stations) | Quotidien | Historique | 736 MB |
| **GADM Europe** | GeoPackage | Vectoriel | Statique | v4.1.0 | 719 MB |

### Points clés du User Guide

1. **GADM** : Version réduite à l'Europe uniquement (~700 MB vs 2.8 GB mondial)
2. **ERA5-Land** : Données dérivées depuis ERA5-Land hourly (agrégation quotidienne)
3. **NDVI** : Stocké en int8 (0-254) pour compression, nécessite conversion
4. **ECA&D** : Données "blended" (harmonisées) pour qualité maximale

---

## 📚 Informations complémentaires

### Document officiel

**Fichier** : `GenHack - Kayrros data User Guide.docx`  
**Source** : Kayrros (partenaire du hackathon)

#### Liens utiles

- **Google Drive principal** : https://drive.google.com/drive/folders/1_uMrrq63e0iYCFj8A6ehN58641sJZ2x1
- **Notebook Jupyter** : https://drive.google.com/file/d/1g2hk8rsZlNBmgVuW7Ut6cqfMps5qUiG1/view

#### Requirements Python

D'après le User Guide, les dépendances requises sont :
```toml
requires-python = ">=3.12"
dependencies = [
    "dask>=2025.10.0",
    "geopandas>=1.1.1",
    "h5netcdf>=1.6.4",
    "ipykernel>=6.30.1",
    "matplotlib>=3.10.6",
    "rasterio>=1.4.3",
    "rioxarray>=0.19.0",
    "xarray>=2025.9.0",
]
```

#### Résumé des datasets

| Dataset | Format | Résolution spatiale | Résolution temporelle | Période | Taille |
|---------|--------|---------------------|----------------------|---------|--------|
| **ERA5-Land** | NetCDF | ~9 km × 9 km | Quotidien | 2020-2025 | ~2.5 GB |
| **Sentinel-2 NDVI** | GeoTIFF | 80 m × 80 m | Trimestriel | 2020-2023 | ~16 GB |
| **ECA&D Stations** | TXT (ZIP) | Points (stations) | Quotidien | Historique | 736 MB |
| **GADM Europe** | GeoPackage | Vectoriel | Statique | v4.1.0 | 719 MB |

---

**Dernière mise à jour** : 9 novembre 2025  
**Statut** : ✅ Tous les datasets téléchargés et analysés

