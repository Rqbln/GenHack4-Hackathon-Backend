"""
GADM Indicators Calculation

Extracts administrative boundaries from GADM and calculates spatial indicators
(mean temperature, NDVI, etc.) for each administrative zone.

Optimized for performance using GeoPandas and spatial indexing.
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import xarray as xr
import rasterio
from rasterio.mask import mask
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class GADMIndicatorCalculator:
    """Calculate spatial indicators for GADM administrative zones"""
    
    def __init__(
        self,
        gadm_gpkg: Path,
        country_code: str = "FRA",
        admin_level: int = 2
    ):
        """
        Initialize GADM indicator calculator
        
        Args:
            gadm_gpkg: Path to GADM GeoPackage
            country_code: ISO country code (e.g., "FRA", "DEU")
            admin_level: Administrative level (0=country, 1=region, 2=department, etc.)
        """
        self.gadm_gpkg = Path(gadm_gpkg)
        self.country_code = country_code
        self.admin_level = admin_level
        self.gadm_gdf = None
        
    def load_gadm(self) -> gpd.GeoDataFrame:
        """Load GADM boundaries"""
        logger.info(f"Loading GADM boundaries for {self.country_code}, level {self.admin_level}")
        
        self.gadm_gdf = gpd.read_file(self.gadm_gpkg)
        
        # Filter by country
        if 'GID_0' in self.gadm_gdf.columns:
            self.gadm_gdf = self.gadm_gdf[self.gadm_gdf['GID_0'] == self.country_code]
        
        logger.info(f"Loaded {len(self.gadm_gdf)} administrative units")
        return self.gadm_gdf
    
    def extract_zone(
        self,
        zone_name: str,
        name_column: Optional[str] = None
    ) -> gpd.GeoDataFrame:
        """
        Extract a specific administrative zone
        
        Args:
            zone_name: Name of the zone to extract
            name_column: Column name to search in (e.g., 'NAME_2', 'NAME_5')
                        If None, searches in all NAME_* columns
            
        Returns:
            GeoDataFrame with the extracted zone
        """
        if self.gadm_gdf is None:
            self.load_gadm()
        
        if name_column:
            filtered = self.gadm_gdf[self.gadm_gdf[name_column] == zone_name]
        else:
            # Search in all NAME columns
            name_cols = [col for col in self.gadm_gdf.columns if col.startswith('NAME_')]
            mask = pd.Series([False] * len(self.gadm_gdf))
            for col in name_cols:
                mask |= (self.gadm_gdf[col] == zone_name)
            filtered = self.gadm_gdf[mask]
        
        if len(filtered) == 0:
            raise ValueError(f"Zone '{zone_name}' not found in GADM")
        
        return filtered
    
    def calculate_zonal_statistics(
        self,
        raster_path: Path,
        zones: gpd.GeoDataFrame,
        statistic: str = 'mean',
        nodata_value: Optional[float] = None
    ) -> pd.DataFrame:
        """
        Calculate zonal statistics for administrative zones
        
        Args:
            raster_path: Path to raster file (GeoTIFF)
            zones: GeoDataFrame with administrative zones
            statistic: Statistic to calculate ('mean', 'min', 'max', 'std', 'sum')
            nodata_value: NoData value to ignore
            
        Returns:
            DataFrame with zone IDs and calculated statistics
        """
        logger.info(f"Calculating {statistic} for {len(zones)} zones from {raster_path.name}")
        
        results = []
        
        with rasterio.open(raster_path) as src:
            # Ensure zones are in same CRS as raster
            zones_reprojected = zones.to_crs(src.crs)
            
            for idx, zone in zones_reprojected.iterrows():
                try:
                    # Clip raster to zone
                    geometry = [zone.geometry]
                    clipped, transform = mask(src, geometry, crop=True, nodata=nodata_value)
                    
                    # Remove nodata values
                    if nodata_value is not None:
                        clipped = clipped[clipped != nodata_value]
                    else:
                        clipped = clipped[~np.isnan(clipped)]
                    
                    if len(clipped) == 0:
                        value = np.nan
                    else:
                        # Calculate statistic
                        if statistic == 'mean':
                            value = np.nanmean(clipped)
                        elif statistic == 'min':
                            value = np.nanmin(clipped)
                        elif statistic == 'max':
                            value = np.nanmax(clipped)
                        elif statistic == 'std':
                            value = np.nanstd(clipped)
                        elif statistic == 'sum':
                            value = np.nansum(clipped)
                        else:
                            raise ValueError(f"Unknown statistic: {statistic}")
                    
                    # Get zone identifier
                    zone_id = zone.get('GID_2', zone.get('GID_1', zone.get('GID_0', idx)))
                    zone_name = zone.get('NAME_2', zone.get('NAME_1', zone.get('NAME_0', 'Unknown')))
                    
                    results.append({
                        'zone_id': zone_id,
                        'zone_name': zone_name,
                        'statistic': statistic,
                        'value': value,
                        'pixel_count': len(clipped)
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to process zone {idx}: {e}")
                    continue
        
        return pd.DataFrame(results)
    
    def calculate_temperature_indicators(
        self,
        era5_ds: xr.Dataset,
        zones: gpd.GeoDataFrame,
        variable: str = 't2m',
        time_slice: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Calculate temperature indicators for zones from ERA5 data
        
        Args:
            era5_ds: ERA5 xarray Dataset
            zones: GeoDataFrame with administrative zones
            variable: Variable name (e.g., 't2m')
            time_slice: Optional time index to use (if None, uses first time)
            
        Returns:
            DataFrame with zone temperature statistics
        """
        logger.info(f"Calculating temperature indicators for {len(zones)} zones")
        
        # Select time slice
        if 'valid_time' in era5_ds.dims:
            if time_slice is None:
                time_slice = 0
            data = era5_ds[variable].isel(valid_time=time_slice)
        else:
            data = era5_ds[variable]
        
        results = []
        
        # Get coordinates
        lons = data.longitude.values
        lats = data.latitude.values
        
        # Ensure zones are in WGS84
        zones_wgs84 = zones.to_crs("EPSG:4326")
        
        for idx, zone in zones_wgs84.iterrows():
            try:
                # Get bounding box of zone
                bbox = zone.geometry.bounds  # (minx, miny, maxx, maxy)
                
                # Find pixels within bounding box
                lon_mask = (lons >= bbox[0]) & (lons <= bbox[2])
                lat_mask = (lats >= bbox[1]) & (lats <= bbox[3])
                
                if not (lon_mask.any() and lat_mask.any()):
                    continue
                
                # Extract data for bounding box
                zone_data = data.sel(
                    longitude=lons[lon_mask],
                    latitude=lats[lat_mask]
                ).values
                
                # Filter by actual geometry (more precise than bbox)
                # For now, use bbox approximation (can be improved with point-in-polygon)
                zone_data = zone_data.flatten()
                zone_data = zone_data[~np.isnan(zone_data)]
                
                if len(zone_data) == 0:
                    continue
                
                # Calculate statistics
                zone_id = zone.get('GID_2', zone.get('GID_1', zone.get('GID_0', idx)))
                zone_name = zone.get('NAME_2', zone.get('NAME_1', zone.get('NAME_0', 'Unknown')))
                
                results.append({
                    'zone_id': zone_id,
                    'zone_name': zone_name,
                    'mean_temp': np.nanmean(zone_data),
                    'min_temp': np.nanmin(zone_data),
                    'max_temp': np.nanmax(zone_data),
                    'std_temp': np.nanstd(zone_data),
                    'pixel_count': len(zone_data)
                })
                
            except Exception as e:
                logger.warning(f"Failed to process zone {idx}: {e}")
                continue
        
        return pd.DataFrame(results)
    
    def calculate_ndvi_indicators(
        self,
        ndvi_path: Path,
        zones: gpd.GeoDataFrame
    ) -> pd.DataFrame:
        """
        Calculate NDVI indicators for zones
        
        Args:
            ndvi_path: Path to NDVI GeoTIFF
            zones: GeoDataFrame with administrative zones
            
        Returns:
            DataFrame with zone NDVI statistics
        """
        return self.calculate_zonal_statistics(
            ndvi_path,
            zones,
            statistic='mean',
            nodata_value=255
        )
    
    def calculate_all_indicators(
        self,
        era5_ds: Optional[xr.Dataset] = None,
        ndvi_paths: Optional[List[Path]] = None,
        zones: Optional[gpd.GeoDataFrame] = None,
        output_path: Optional[Path] = None
    ) -> pd.DataFrame:
        """
        Calculate all indicators for zones
        
        Args:
            era5_ds: Optional ERA5 Dataset
            ndvi_paths: Optional list of NDVI file paths
            zones: Optional zones (if None, uses all zones for country)
            output_path: Optional path to save results
            
        Returns:
            DataFrame with all calculated indicators
        """
        if zones is None:
            if self.gadm_gdf is None:
                self.load_gadm()
            zones = self.gadm_gdf
        
        all_results = []
        
        # Calculate temperature indicators
        if era5_ds is not None:
            temp_results = self.calculate_temperature_indicators(era5_ds, zones)
            all_results.append(temp_results)
        
        # Calculate NDVI indicators
        if ndvi_paths:
            for ndvi_path in ndvi_paths:
                ndvi_results = self.calculate_ndvi_indicators(ndvi_path, zones)
                ndvi_results['source_file'] = ndvi_path.name
                all_results.append(ndvi_results)
        
        # Merge all results
        if len(all_results) == 0:
            logger.warning("No indicators calculated")
            return pd.DataFrame()
        
        # Merge on zone_id
        merged = all_results[0]
        for df in all_results[1:]:
            merged = merged.merge(df, on=['zone_id', 'zone_name'], how='outer', suffixes=('', '_new'))
        
        # Save if path provided
        if output_path:
            merged.to_csv(output_path, index=False)
            logger.info(f"Saved indicators to {output_path}")
        
        return merged


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    from pathlib import Path
    
    gadm_path = Path("../../datasets/gadm_410_europe.gpkg")
    calculator = GADMIndicatorCalculator(
        gadm_gpkg=gadm_path,
        country_code="FRA",
        admin_level=2
    )
    
    # Load GADM
    zones = calculator.load_gadm()
    print(f"Loaded {len(zones)} zones")
    
    # Extract Paris
    paris = calculator.extract_zone("Paris", name_column="NAME_2")
    print(f"Extracted Paris: {len(paris)} polygon(s)")

