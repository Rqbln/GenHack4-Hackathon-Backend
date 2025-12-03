"""
ETL Pipeline Simplifié - Version sans rasterio pour tester

Cette version simplifiée permet de tester l'ETL sans rasterio
en utilisant uniquement xarray et geopandas.
"""

import xarray as xr
import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import zipfile
from io import StringIO
import logging
import json

logger = logging.getLogger(__name__)

# Try to import rasterio, but make it optional
try:
    import rasterio
    from rasterio.mask import mask
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False
    logger.warning("rasterio not available. NDVI loading will be skipped.")


class ETLPipelineSimple:
    """ETL Pipeline simplifié pour tester sans toutes les dépendances"""
    
    def __init__(
        self,
        era5_dir: Path,
        sentinel2_dir: Path,
        ecad_zip: Path,
        output_dir: Path,
        city_name: str = "Paris",
        country_code: str = "FRA",
        gadm_gpkg: Optional[Path] = None
    ):
        self.era5_dir = Path(era5_dir)
        self.sentinel2_dir = Path(sentinel2_dir)
        self.ecad_zip = Path(ecad_zip)
        self.gadm_gpkg = Path(gadm_gpkg) if gadm_gpkg else None
        self.output_dir = Path(output_dir)
        self.city_name = city_name
        self.country_code = country_code
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.city_boundary = None
    
    def load_city_boundary(self) -> gpd.GeoDataFrame:
        """Load city boundary from GADM or use default bbox"""
        if self.gadm_gpkg is None or not self.gadm_gpkg.exists() or self.gadm_gpkg.stat().st_size == 0:
            logger.warning(f"GADM file not available. Using default bounding box for {self.city_name}")
            # Default bounding box for Paris
            if self.city_name.lower() == "paris":
                bbox_coords = [2.224, 48.815, 2.470, 48.902]  # [lon_min, lat_min, lon_max, lat_max]
            else:
                # Generic bbox - user should provide
                bbox_coords = [2.0, 48.5, 2.5, 49.0]
            
            from shapely.geometry import box
            city_boundary = gpd.GeoDataFrame(
                [1],
                geometry=[box(bbox_coords[0], bbox_coords[1], bbox_coords[2], bbox_coords[3])],
                crs="EPSG:4326"
            )
            self.city_boundary = city_boundary
            logger.info(f"Using default bounding box: {bbox_coords}")
            return city_boundary
        
        logger.info(f"Loading GADM boundaries for {self.city_name}, {self.country_code}")
        
        gadm_gdf = gpd.read_file(self.gadm_gpkg)
        
        # Try different administrative levels
        filtered = gadm_gdf[
            (gadm_gdf.GID_0 == self.country_code) & 
            (gadm_gdf.NAME_2 == self.city_name)
        ]
        
        if len(filtered) == 0:
            filtered = gadm_gdf[
                (gadm_gdf.GID_0 == self.country_code) & 
                (gadm_gdf.NAME_5 == self.city_name)
            ]
        
        if len(filtered) == 0:
            # Try case-insensitive
            filtered = gadm_gdf[
                (gadm_gdf.GID_0 == self.country_code) & 
                (gadm_gdf.NAME_2.str.upper() == self.city_name.upper())
            ]
        
        if len(filtered) == 0:
            raise ValueError(f"City {self.city_name} not found in GADM. Available cities: {gadm_gdf[gadm_gdf.GID_0 == self.country_code]['NAME_2'].unique()[:10]}")
        
        city_boundary = filtered.dissolve()
        self.city_boundary = city_boundary.to_crs("EPSG:4326")
        
        logger.info(f"City boundary loaded: {len(city_boundary)} polygon(s)")
        return city_boundary
    
    def load_era5_data(
        self,
        variable: str,
        year: int,
        bbox: Optional[Tuple[float, float, float, float]] = None
    ) -> xr.Dataset:
        """Load ERA5 data from NetCDF files"""
        variable_map = {
            "t2m_max": f"{year}_2m_temperature_daily_maximum.nc",
            "precipitation": f"{year}_total_precipitation_daily_mean.nc",
            "u10": f"{year}_10m_u_component_of_wind_daily_mean.nc",
            "v10": f"{year}_10m_v_component_of_wind_daily_mean.nc",
        }
        
        file_path = self.era5_dir / variable_map.get(variable)
        if not file_path.exists():
            raise FileNotFoundError(f"ERA5 file not found: {file_path}")
        
        logger.info(f"Loading ERA5: {variable} for year {year}")
        ds = xr.open_dataset(file_path)
        
        # Extract bounding box if provided
        if bbox:
            lon_min, lat_min, lon_max, lat_max = bbox
            ds = ds.sel(
                longitude=slice(lon_min, lon_max),
                latitude=slice(lat_max, lat_min)  # Inverted
            )
        
        # Convert temperature from Kelvin to Celsius
        if variable == "t2m_max" and "t2m" in ds.data_vars:
            ds["t2m"] = ds["t2m"] - 273.15
            ds["t2m"].attrs["units"] = "celsius"
        
        return ds
    
    def load_ecad_stations(self) -> gpd.GeoDataFrame:
        """Load ECA&D station metadata"""
        logger.info("Loading ECA&D station metadata")
        
        def dms_to_decimal(dms_str):
            """Convert DMS to decimal degrees"""
            if pd.isna(dms_str) or dms_str == '':
                return np.nan
            dms_str = str(dms_str).strip()
            if dms_str[0] in ['+', '-']:
                sign = 1 if dms_str[0] == '+' else -1
                parts = dms_str[1:].split(':')
            else:
                sign = 1
                parts = dms_str.split(':')
            
            if len(parts) != 3:
                return np.nan
            
            try:
                return sign * (float(parts[0]) + float(parts[1])/60 + float(parts[2])/3600)
            except:
                return np.nan
        
        with zipfile.ZipFile(self.ecad_zip) as z:
            stations_content = z.read('stations.txt').decode('utf-8', errors='ignore')
            stations_df = pd.read_csv(
                StringIO(stations_content),
                skiprows=17,
                skipinitialspace=True
            )
            
            stations_df['LAT_decimal'] = stations_df['LAT'].apply(dms_to_decimal)
            stations_df['LON_decimal'] = stations_df['LON'].apply(dms_to_decimal)
            
            # Remove rows with invalid coordinates
            stations_df = stations_df.dropna(subset=['LAT_decimal', 'LON_decimal'])
            
            stations_gdf = gpd.GeoDataFrame(
                stations_df,
                geometry=gpd.points_from_xy(
                    stations_df['LON_decimal'],
                    stations_df['LAT_decimal']
                ),
                crs="EPSG:4326"
            )
        
        # Filter stations within city boundary if available
        if self.city_boundary is not None:
            stations_in_city = stations_gdf[stations_gdf.within(
                self.city_boundary.geometry.iloc[0]
            )]
            logger.info(f"Found {len(stations_in_city)} stations in {self.city_name}")
            return stations_in_city
        
        return stations_gdf
    
    def run_etl_simple(
        self,
        years: List[int] = [2020, 2021],
        variables: List[str] = ["t2m_max", "precipitation"]
    ):
        """Run simplified ETL pipeline"""
        logger.info("=" * 60)
        logger.info("Starting Simplified ETL Pipeline")
        logger.info("=" * 60)
        
        # 1. Load city boundary
        self.load_city_boundary()
        bbox = self.city_boundary.total_bounds
        bbox_tuple = (bbox[0], bbox[1], bbox[2], bbox[3])
        
        # 2. Load ERA5 data
        era5_datasets = {}
        for year in years:
            for variable in variables:
                key = f"{variable}_{year}"
                try:
                    era5_datasets[key] = self.load_era5_data(variable, year, bbox_tuple)
                except Exception as e:
                    logger.error(f"Failed to load {key}: {e}")
        
        # 3. Combine ERA5 datasets by year
        era5_by_year = {}
        for year in years:
            year_datasets = [ds for key, ds in era5_datasets.items() if key.endswith(f"_{year}")]
            if year_datasets:
                era5_by_year[year] = xr.merge(year_datasets)
        
        # Concatenate across years
        if len(era5_by_year) > 1:
            era5_combined = xr.concat(
                [era5_by_year[year] for year in sorted(era5_by_year.keys())],
                dim='valid_time'
            )
        elif len(era5_by_year) == 1:
            era5_combined = list(era5_by_year.values())[0]
        else:
            raise ValueError("No ERA5 datasets loaded")
        
        # 4. Load ECA&D stations
        stations_gdf = self.load_ecad_stations()
        
        # 5. Save outputs
        boundary_path = self.output_dir / "city_boundary.geojson"
        self.city_boundary.to_file(boundary_path, driver='GeoJSON')
        logger.info(f"✅ Saved city boundary to {boundary_path}")
        
        stations_path = self.output_dir / "stations.geojson"
        stations_gdf.to_file(stations_path, driver='GeoJSON')
        logger.info(f"✅ Saved {len(stations_gdf)} stations to {stations_path}")
        
        era5_path = self.output_dir / "era5_aligned.nc"
        era5_combined.to_netcdf(era5_path)
        logger.info(f"✅ Saved ERA5 data to {era5_path}")
        
        # Save summary
        summary = {
            "city": self.city_name,
            "years": years,
            "variables": variables,
            "n_stations": len(stations_gdf),
            "era5_shape": dict(era5_combined.dims),
            "era5_variables": list(era5_combined.data_vars),
            "bbox": bbox.tolist()
        }
        
        summary_path = self.output_dir / "etl_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"✅ Saved summary to {summary_path}")
        
        logger.info("=" * 60)
        logger.info("✅ Simplified ETL Pipeline completed successfully")
        logger.info("=" * 60)
        
        return {
            "era5": era5_combined,
            "stations": stations_gdf,
            "boundary": self.city_boundary,
            "summary": summary
        }

