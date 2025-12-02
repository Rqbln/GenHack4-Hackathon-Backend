"""
ETL Pipeline for GenHack 2025 - Data Ingestion and Temporal Alignment

This module handles:
- Loading ERA5 NetCDF files
- Loading Sentinel-2 NDVI GeoTIFF files
- Loading ECA&D station data
- Temporal alignment of all datasets
- Structured storage (Zarr/NetCDF)
"""

import xarray as xr
import rasterio
from rasterio.mask import mask
import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import zipfile
from io import StringIO
import logging
import zarr

logger = logging.getLogger(__name__)


class ETLPipeline:
    """ETL Pipeline for harmonizing ERA5, Sentinel-2, and ECA&D data"""
    
    def __init__(
        self,
        era5_dir: Path,
        sentinel2_dir: Path,
        ecad_zip: Path,
        gadm_gpkg: Path,
        output_dir: Path,
        city_name: str = "Paris",
        country_code: str = "FRA"
    ):
        """
        Initialize ETL Pipeline
        
        Args:
            era5_dir: Directory containing ERA5 NetCDF files
            sentinel2_dir: Directory containing Sentinel-2 NDVI GeoTIFF files
            ecad_zip: Path to ECA_blend_tx.zip
            gadm_gpkg: Path to gadm_410_europe.gpkg
            output_dir: Output directory for processed data
            city_name: Name of the city to analyze
            country_code: ISO country code (e.g., "FRA", "DEU")
        """
        self.era5_dir = Path(era5_dir)
        self.sentinel2_dir = Path(sentinel2_dir)
        self.ecad_zip = Path(ecad_zip)
        self.gadm_gpkg = Path(gadm_gpkg)
        self.output_dir = Path(output_dir)
        self.city_name = city_name
        self.country_code = country_code
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # City boundary (will be loaded from GADM)
        self.city_boundary = None
        
    def load_city_boundary(self) -> gpd.GeoDataFrame:
        """Load city boundary from GADM"""
        logger.info(f"Loading GADM boundaries for {self.city_name}, {self.country_code}")
        
        gadm_gdf = gpd.read_file(self.gadm_gpkg)
        
        # Filter by country and city
        # Note: Administrative level may vary (NAME_2 for Paris, NAME_5 for Lille)
        filtered = gadm_gdf[
            (gadm_gdf.GID_0 == self.country_code) & 
            (gadm_gdf.NAME_2 == self.city_name)
        ]
        
        if len(filtered) == 0:
            # Try NAME_5 for smaller cities
            filtered = gadm_gdf[
                (gadm_gdf.GID_0 == self.country_code) & 
                (gadm_gdf.NAME_5 == self.city_name)
            ]
        
        if len(filtered) == 0:
            raise ValueError(f"City {self.city_name} not found in GADM")
        
        # Dissolve to get unified boundary
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
        """
        Load ERA5 data from NetCDF files
        
        Args:
            variable: Variable name (t2m_max, precipitation, u10, v10)
            year: Year to load
            bbox: Optional bounding box (lon_min, lat_min, lon_max, lat_max)
            
        Returns:
            xarray Dataset with ERA5 data
        """
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
                latitude=slice(lat_max, lat_min)  # Inverted because latitude decreases
            )
        
        # Convert temperature from Kelvin to Celsius
        if variable == "t2m_max" and "t2m" in ds.data_vars:
            ds["t2m"] = ds["t2m"] - 273.15
            ds["t2m"].attrs["units"] = "celsius"
        
        return ds
    
    def load_ndvi_data(
        self,
        start_date: str,
        end_date: str,
        clip_to_boundary: bool = True
    ) -> Tuple[np.ndarray, Dict]:
        """
        Load Sentinel-2 NDVI data from GeoTIFF
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            clip_to_boundary: Whether to clip to city boundary
            
        Returns:
            Tuple of (NDVI array, metadata dict)
        """
        file_name = f"ndvi_{start_date}_{end_date}.tif"
        file_path = self.sentinel2_dir / file_name
        
        if not file_path.exists():
            raise FileNotFoundError(f"NDVI file not found: {file_path}")
        
        logger.info(f"Loading NDVI: {file_name}")
        
        def convert_ndvi_to_real_scale(ndvi_img, nodata_value=255):
            """Convert NDVI from int8 (0-254) to float (-1 to 1)"""
            ndvi_img = ndvi_img.astype(float)
            ndvi_img[ndvi_img == nodata_value] = np.nan
            ndvi_img = ndvi_img / 254 * 2 - 1
            return ndvi_img
        
        with rasterio.open(file_path) as src:
            if clip_to_boundary and self.city_boundary is not None:
                city_geometry_crs = self.city_boundary.to_crs(src.crs)
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
            
            # Convert NDVI to real scale
            real_ndvi = convert_ndvi_to_real_scale(
                out_image, 
                out_meta.get("nodata", 255)
            )
        
        return real_ndvi, out_meta
    
    def load_ecad_stations(self) -> gpd.GeoDataFrame:
        """Load ECA&D station metadata"""
        logger.info("Loading ECA&D station metadata")
        
        def dms_to_decimal(dms_str):
            """Convert DMS (Degrees:Minutes:Seconds) to decimal degrees"""
            dms_str = dms_str.strip()
            sign = 1 if dms_str[0] == '+' else -1
            parts = dms_str[1:].split(':')
            return sign * (float(parts[0]) + float(parts[1])/60 + float(parts[2])/3600)
        
        with zipfile.ZipFile(self.ecad_zip) as z:
            stations_content = z.read('stations.txt').decode('utf-8', errors='ignore')
            stations_df = pd.read_csv(
                StringIO(stations_content),
                skiprows=17,
                skipinitialspace=True
            )
            
            stations_df['LAT_decimal'] = stations_df['LAT'].apply(dms_to_decimal)
            stations_df['LON_decimal'] = stations_df['LON'].apply(dms_to_decimal)
            
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
    
    def load_ecad_station_data(self, station_id: int) -> pd.DataFrame:
        """
        Load temperature data for a specific ECA&D station
        
        Args:
            station_id: Station ID (STAID)
            
        Returns:
            DataFrame with DATE, TX_celsius, Q_TX columns
        """
        with zipfile.ZipFile(self.ecad_zip) as z:
            station_file = f"TX_STAID{station_id:06d}.txt"
            if station_file not in z.namelist():
                raise FileNotFoundError(f"Station file not found: {station_file}")
            
            station_content = z.read(station_file).decode('utf-8', errors='ignore')
            station_data = pd.read_csv(
                StringIO(station_content),
                skiprows=20,
                skipinitialspace=True
            )
            
            # Filter valid data (Q_TX == 0)
            valid_data = station_data[station_data['Q_TX'] == 0].copy()
            valid_data['DATE'] = pd.to_datetime(valid_data['DATE'], format='%Y%m%d')
            valid_data['TX_celsius'] = valid_data['TX'] / 10  # Convert 0.1°C to °C
            
            return valid_data[['DATE', 'TX_celsius', 'Q_TX']]
    
    def align_temporal(
        self,
        era5_ds: xr.Dataset,
        ndvi_data: Dict[str, Tuple[np.ndarray, Dict]],
        ecad_data: Dict[int, pd.DataFrame],
        target_frequency: str = "monthly"
    ) -> xr.Dataset:
        """
        Align all datasets temporally
        
        Args:
            era5_ds: ERA5 xarray Dataset
            ndvi_data: Dict mapping time periods to (NDVI array, metadata)
            ecad_data: Dict mapping station IDs to DataFrames
            target_frequency: Target frequency ('daily', 'monthly', 'quarterly')
            
        Returns:
            Aligned xarray Dataset
        """
        logger.info(f"Aligning datasets to {target_frequency} frequency")
        
        # Resample ERA5 to target frequency
        if target_frequency == "monthly":
            era5_resampled = era5_ds.resample(valid_time='1M').mean()
        elif target_frequency == "quarterly":
            era5_resampled = era5_ds.resample(valid_time='3M').mean()
        else:
            era5_resampled = era5_ds
        
        # TODO: Align NDVI data (quarterly) with ERA5
        # TODO: Align ECA&D station data with ERA5
        
        return era5_resampled
    
    def save_to_zarr(
        self,
        dataset: xr.Dataset,
        output_path: Path,
        chunk_size: Dict[str, int] = None
    ):
        """
        Save xarray Dataset to Zarr format
        
        Args:
            dataset: xarray Dataset to save
            output_path: Output Zarr store path
            chunk_size: Chunk sizes for each dimension
        """
        if chunk_size is None:
            chunk_size = {"valid_time": 30, "latitude": 100, "longitude": 100}
        
        logger.info(f"Saving to Zarr: {output_path}")
        dataset.to_zarr(
            output_path,
            mode='w',
            encoding={var: {'chunks': chunk_size} for var in dataset.data_vars}
        )
    
    def run_etl(
        self,
        years: List[int] = [2020, 2021, 2022],
        variables: List[str] = ["t2m_max", "precipitation", "u10", "v10"],
        output_format: str = "zarr"
    ):
        """
        Run complete ETL pipeline
        
        Args:
            years: Years to process
            variables: ERA5 variables to load
            output_format: Output format ('zarr' or 'netcdf')
        """
        logger.info("=" * 60)
        logger.info("Starting ETL Pipeline")
        logger.info("=" * 60)
        
        # 1. Load city boundary
        self.load_city_boundary()
        bbox = self.city_boundary.total_bounds  # [minx, miny, maxx, maxy]
        bbox_tuple = (bbox[0], bbox[1], bbox[2], bbox[3])  # (lon_min, lat_min, lon_max, lat_max)
        
        # 2. Load ERA5 data for all years and variables
        era5_datasets = {}
        for year in years:
            for variable in variables:
                key = f"{variable}_{year}"
                era5_datasets[key] = self.load_era5_data(variable, year, bbox_tuple)
        
        # 3. Combine ERA5 datasets
        era5_combined = xr.merge(list(era5_datasets.values()))
        
        # 4. Load NDVI data
        ndvi_data = {}
        ndvi_periods = [
            ("2019-12-01", "2020-03-01"),
            ("2020-03-01", "2020-06-01"),
            ("2020-06-01", "2020-09-01"),
            ("2020-09-01", "2020-12-01"),
            ("2020-12-01", "2021-03-01"),
            ("2021-03-01", "2021-06-01"),
            ("2021-06-01", "2021-09-01"),
            ("2021-09-01", "2021-12-01"),
        ]
        
        for start, end in ndvi_periods:
            try:
                ndvi_array, ndvi_meta = self.load_ndvi_data(start, end, clip_to_boundary=True)
                ndvi_data[f"{start}_{end}"] = (ndvi_array, ndvi_meta)
            except FileNotFoundError as e:
                logger.warning(f"Skipping NDVI period {start}-{end}: {e}")
        
        # 5. Load ECA&D stations
        stations_gdf = self.load_ecad_stations()
        
        # 6. Save city boundary
        boundary_path = self.output_dir / "city_boundary.geojson"
        self.city_boundary.to_file(boundary_path, driver='GeoJSON')
        logger.info(f"Saved city boundary to {boundary_path}")
        
        # 7. Save stations
        stations_path = self.output_dir / "stations.geojson"
        stations_gdf.to_file(stations_path, driver='GeoJSON')
        logger.info(f"Saved {len(stations_gdf)} stations to {stations_path}")
        
        # 8. Save ERA5 data
        if output_format == "zarr":
            era5_path = self.output_dir / "era5_aligned.zarr"
            self.save_to_zarr(era5_combined, era5_path)
        else:
            era5_path = self.output_dir / "era5_aligned.nc"
            era5_combined.to_netcdf(era5_path)
        
        logger.info(f"Saved ERA5 data to {era5_path}")
        
        # 9. Save NDVI metadata
        ndvi_meta_path = self.output_dir / "ndvi_metadata.json"
        import json
        with open(ndvi_meta_path, 'w') as f:
            json.dump({
                k: {
                    "shape": v[0].shape,
                    "crs": str(v[1].get("crs", "unknown")),
                    "transform": list(v[1].get("transform", []))
                }
                for k, v in ndvi_data.items()
            }, f, indent=2)
        
        logger.info("=" * 60)
        logger.info("ETL Pipeline completed successfully")
        logger.info("=" * 60)
        
        return {
            "era5": era5_combined,
            "ndvi": ndvi_data,
            "stations": stations_gdf,
            "boundary": self.city_boundary
        }


if __name__ == "__main__":
    # Example usage
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Paths (adjust to your local setup)
    base_dir = Path(__file__).parent.parent.parent / "datasets"
    
    etl = ETLPipeline(
        era5_dir=base_dir / "main" / "derived-era5-land-daily-statistics",
        sentinel2_dir=base_dir / "main" / "sentinel2_ndvi",
        ecad_zip=base_dir / "ECA_blend_tx.zip",
        gadm_gpkg=base_dir / "gadm_410_europe.gpkg",
        output_dir=base_dir / "processed",
        city_name="Paris",
        country_code="FRA"
    )
    
    # Run ETL
    results = etl.run_etl(
        years=[2020, 2021],
        variables=["t2m_max", "precipitation"],
        output_format="zarr"
    )

