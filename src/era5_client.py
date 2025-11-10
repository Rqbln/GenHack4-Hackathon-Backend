"""
GenHack Climate - ERA5 Data Client (Phase 2)

Client for downloading ERA5 reanalysis data from Copernicus CDS.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import xarray as xr
import numpy as np

logger = logging.getLogger(__name__)


class ERA5Client:
    """
    Client for ERA5 climate reanalysis data via Copernicus CDS API
    
    Requires:
    - CDS API key configured in ~/.cdsapirc
    - Account at https://cds.climate.copernicus.eu/
    """
    
    # ERA5 variable mapping
    VARIABLE_MAP = {
        "t2m": "2m_temperature",           # 2-meter temperature (K)
        "tx": "maximum_2m_temperature_since_previous_post_processing",  # Daily max temp
        "tn": "minimum_2m_temperature_since_previous_post_processing",  # Daily min temp
        "rh": "2m_relative_humidity",      # Relative humidity (%)
        "u10": "10m_u_component_of_wind",  # 10m U wind (m/s)
        "v10": "10m_v_component_of_wind",  # 10m V wind (m/s)
        "tp": "total_precipitation",       # Total precipitation (m)
        "sp": "surface_pressure"           # Surface pressure (Pa)
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize ERA5 client
        
        Args:
            api_key: CDS API key (optional, reads from ~/.cdsapirc if not provided)
        """
        self.api_key = api_key
        self._client = None
    
    @property
    def client(self):
        """Lazy-load CDS API client"""
        if self._client is None:
            try:
                import cdsapi
                self._client = cdsapi.Client()
                logger.info("✅ CDS API client initialized")
            except ImportError:
                raise ImportError(
                    "cdsapi not installed. Install with: pip install cdsapi"
                )
            except Exception as e:
                raise RuntimeError(
                    f"Failed to initialize CDS client. "
                    f"Make sure you have a valid ~/.cdsapirc file. "
                    f"Error: {e}"
                )
        return self._client
    
    def download_era5(
        self,
        variables: List[str],
        bbox: List[float],
        start_date: str,
        end_date: str,
        output_dir: Path,
        dataset: str = "reanalysis-era5-single-levels"
    ) -> Dict[str, Path]:
        """
        Download ERA5 data for specified variables and region
        
        Args:
            variables: List of variable codes (t2m, tx, tn, etc.)
            bbox: Bounding box [west, south, east, north] in degrees
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            output_dir: Output directory
            dataset: ERA5 dataset name
            
        Returns:
            Dict mapping variable names to output file paths
        """
        logger.info(f"🌍 Downloading ERA5 data from Copernicus CDS")
        logger.info(f"   Variables: {', '.join(variables)}")
        logger.info(f"   Period: {start_date} to {end_date}")
        logger.info(f"   Bbox: {bbox}")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        downloaded_files = {}
        
        # Convert dates to datetime
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Generate list of dates
        dates = []
        current = start_dt
        while current <= end_dt:
            dates.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)
        
        for var_code in variables:
            if var_code not in self.VARIABLE_MAP:
                logger.warning(f"⚠️  Unknown variable: {var_code}, skipping")
                continue
            
            era5_var = self.VARIABLE_MAP[var_code]
            output_file = output_dir / f"{var_code}_era5.nc"
            
            logger.info(f"📥 Downloading {var_code} ({era5_var})...")
            
            try:
                # CDS API request
                request = {
                    'product_type': 'reanalysis',
                    'variable': era5_var,
                    'year': [start_dt.strftime("%Y")],
                    'month': [d.split('-')[1] for d in dates],
                    'day': [d.split('-')[2] for d in dates],
                    'time': [f"{h:02d}:00" for h in range(0, 24, 3)],  # Every 3 hours
                    'area': [bbox[3], bbox[0], bbox[1], bbox[2]],  # N, W, S, E
                    'format': 'netcdf',
                }
                
                # Download
                self.client.retrieve(dataset, request, str(output_file))
                
                logger.info(f"✅ Downloaded: {output_file}")
                downloaded_files[var_code] = output_file
                
            except Exception as e:
                logger.error(f"❌ Failed to download {var_code}: {e}")
                continue
        
        return downloaded_files
    
    def convert_to_geotiff(
        self,
        netcdf_path: Path,
        output_path: Path,
        variable: str,
        time_aggregation: str = "mean"
    ) -> Path:
        """
        Convert NetCDF to GeoTIFF with temporal aggregation
        
        Args:
            netcdf_path: Input NetCDF file
            output_path: Output GeoTIFF path
            variable: Variable name
            time_aggregation: How to aggregate over time (mean, max, min)
            
        Returns:
            Path to output GeoTIFF
        """
        logger.info(f"🔄 Converting {netcdf_path.name} to GeoTIFF...")
        
        # Open NetCDF with xarray
        ds = xr.open_dataset(netcdf_path)
        
        # Get the data variable (ERA5 uses different names)
        data_var = list(ds.data_vars)[0]
        data = ds[data_var]
        
        # Detect time dimension name (ERA5 uses 'valid_time' or 'time')
        time_dim = None
        for dim in ["valid_time", "time"]:
            if dim in data.dims:
                time_dim = dim
                break
        
        # Temporal aggregation
        if time_dim and len(data[time_dim]) > 1:
            if time_aggregation == "mean":
                aggregated = data.mean(dim=time_dim)
            elif time_aggregation == "max":
                aggregated = data.max(dim=time_dim)
            elif time_aggregation == "min":
                aggregated = data.min(dim=time_dim)
            else:
                aggregated = data.isel({time_dim: 0})  # First timestep
        else:
            # No time dimension or single timestep
            aggregated = data.isel({time_dim: 0}) if time_dim else data
        
        # Convert to numpy array
        arr = aggregated.values
        
        # Get spatial coordinates
        lats = aggregated.latitude.values
        lons = aggregated.longitude.values
        
        # Create GeoTIFF
        import rasterio
        from rasterio.transform import from_bounds
        
        transform = from_bounds(
            lons.min(), lats.min(), lons.max(), lats.max(),
            arr.shape[1], arr.shape[0]
        )
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with rasterio.open(
            output_path,
            'w',
            driver='GTiff',
            height=arr.shape[0],
            width=arr.shape[1],
            count=1,
            dtype=arr.dtype,
            crs='EPSG:4326',
            transform=transform,
            compress='lzw',
            tiled=True
        ) as dst:
            dst.write(arr, 1)
            dst.set_band_description(1, variable)
        
        logger.info(f"✅ Created GeoTIFF: {output_path}")
        
        # Close dataset
        ds.close()
        
        return output_path


if __name__ == "__main__":
    # Test ERA5 client
    client = ERA5Client()
    
    # Test with small area and short period
    test_output = Path("/tmp/era5_test")
    
    files = client.download_era5(
        variables=["t2m"],
        bbox=[2.2, 48.8, 2.5, 48.9],  # Small Paris area
        start_date="2022-07-15",
        end_date="2022-07-15",  # Single day
        output_dir=test_output
    )
    
    # Convert to GeoTIFF
    for var, nc_file in files.items():
        tif_file = test_output / f"{var}.tif"
        client.convert_to_geotiff(nc_file, tif_file, var)
    
    print(f"✅ Test complete: {len(files)} files downloaded")
