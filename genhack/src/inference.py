"""
Phase 3: Inference - Generate High-Resolution Temperature Maps
Creates downscaled temperature maps using trained residual learning model
"""

import numpy as np
import pandas as pd
import xarray as xr
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_bounds
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional
from modeling import ResidualLearningModel


class HighResMapGenerator:
    """Generate high-resolution temperature maps from ERA5 + Satellite data"""
    
    def __init__(self, model: ResidualLearningModel, 
                 era5_dir: str, 
                 ndvi_dir: str,
                 elevation_file: Optional[str] = None):
        """
        Initialize map generator
        
        Args:
            model: Trained residual learning model
            era5_dir: Directory containing ERA5 NetCDF files
            ndvi_dir: Directory containing NDVI GeoTIFF files
            elevation_file: Optional elevation raster file
        """
        self.model = model
        self.era5_dir = Path(era5_dir)
        self.ndvi_dir = Path(ndvi_dir)
        self.elevation_file = elevation_file
    
    def load_ndvi_for_date(self, date: datetime, 
                          bbox: Optional[Tuple[float, float, float, float]] = None) -> Tuple[np.ndarray, dict]:
        """
        Load NDVI raster for given date
        
        Args:
            date: Target date
            bbox: Optional bounding box (minx, miny, maxx, maxy) in WGS84
        
        Returns:
            NDVI array and metadata dictionary
        """
        # Find appropriate NDVI file
        ndvi_files = list(self.ndvi_dir.glob('ndvi_*.tif'))
        
        selected_file = None
        for f in ndvi_files:
            parts = f.stem.split('_')
            if len(parts) >= 3:
                try:
                    start = datetime.strptime(parts[1], '%Y-%m-%d')
                    end = datetime.strptime(parts[2], '%Y-%m-%d')
                    
                    if start <= date < end:
                        selected_file = f
                        break
                except ValueError:
                    continue
        
        if selected_file is None:
            raise ValueError(f"No NDVI file found for date {date}")
        
        print(f"Loading NDVI from: {selected_file.name}")
        
        with rasterio.open(selected_file) as src:
            # If bounding box provided, read only that region
            if bbox is not None:
                from pyproj import Transformer
                from rasterio.windows import from_bounds as window_from_bounds
                
                # Transform bbox from WGS84 to raster CRS
                transformer = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
                minx, miny = transformer.transform(bbox[0], bbox[1])
                maxx, maxy = transformer.transform(bbox[2], bbox[3])
                
                # Create window
                window = window_from_bounds(minx, miny, maxx, maxy, src.transform)
                
                # Read windowed data
                ndvi = src.read(1, window=window)
                
                # Update transform for the window
                window_transform = src.window_transform(window)
            else:
                # Read full raster (WARNING: May be very large!)
                print("  WARNING: Reading full NDVI raster (may take several minutes)...")
                ndvi = src.read(1)
                window_transform = src.transform
            
            # Convert nodata (255) to NaN
            ndvi = ndvi.astype(float)
            ndvi[ndvi == 255] = np.nan
            
            # Scale from 0-254 to -1 to 1
            # Formula: (value / 254) * 2 - 1
            ndvi = (ndvi / 254.0) * 2.0 - 1.0
            
            # Clip to valid NDVI range
            ndvi = np.clip(ndvi, -1, 1)
            
            metadata = {
                'transform': window_transform,
                'crs': src.crs,
                'height': ndvi.shape[0],
                'width': ndvi.shape[1],
                'bounds': rasterio.transform.array_bounds(ndvi.shape[0], ndvi.shape[1], window_transform) if bbox else src.bounds
            }
        
        return ndvi, metadata
    
    def load_era5_for_date(self, date: datetime, 
                          variable: str = '2m_temperature_daily_maximum') -> xr.DataArray:
        """
        Load ERA5 temperature for given date
        
        Args:
            date: Target date
            variable: ERA5 variable name
        
        Returns:
            xarray DataArray with temperature data
        """
        year = date.year
        filepath = self.era5_dir / f"{year}_{variable}.nc"
        
        if not filepath.exists():
            raise FileNotFoundError(f"ERA5 file not found: {filepath}")
        
        print(f"Loading ERA5 from: {filepath.name}")
        
        ds = xr.open_dataset(filepath)
        
        # Select the specific date (ERA5 files use 'valid_time' not 'time')
        temp_data = ds.sel(valid_time=date, method='nearest')
        
        # Get temperature variable name mapping
        var_name_map = {
            '2m_temperature': 't2m',
            'total_precipitation': 'tp',
            '10m_u_component_of_wind': 'u10',
            '10m_v_component_of_wind': 'v10'
        }
        var_base = variable.split('_daily_')[0]
        var_name = var_name_map.get(var_base, var_base)
        
        temp_kelvin = temp_data[var_name]
        
        # Convert Kelvin to Celsius
        temp_celsius = temp_kelvin - 273.15
        
        return temp_celsius
    
    def upsample_era5_to_highres(self, era5_temp: xr.DataArray, 
                                 target_metadata: dict) -> np.ndarray:
        """
        Upsample coarse ERA5 grid to match high-resolution NDVI grid
        
        Args:
            era5_temp: ERA5 temperature DataArray
            target_metadata: Metadata from NDVI file (target resolution)
        
        Returns:
            Upsampled temperature array
        """
        print("Upsampling ERA5 to high resolution...")
        
        # Create source array
        src_array = era5_temp.values
        
        # ERA5 coordinates
        lats = era5_temp.latitude.values
        lons = era5_temp.longitude.values
        
        # Create source transform
        lat_res = abs(lats[1] - lats[0])
        lon_res = abs(lons[1] - lons[0])
        
        src_transform = from_bounds(
            lons.min() - lon_res/2,
            lats.min() - lat_res/2,
            lons.max() + lon_res/2,
            lats.max() + lat_res/2,
            len(lons),
            len(lats)
        )
        
        # Prepare destination array
        dst_array = np.empty(
            (target_metadata['height'], target_metadata['width']),
            dtype=np.float32
        )
        
        # Reproject using bilinear interpolation
        reproject(
            source=src_array,
            destination=dst_array,
            src_transform=src_transform,
            src_crs='EPSG:4326',
            dst_transform=target_metadata['transform'],
            dst_crs=target_metadata['crs'],
            resampling=Resampling.bilinear
        )
        
        return dst_array
    
    def create_feature_grid(self, era5_upsampled: np.ndarray,
                           ndvi: np.ndarray,
                           metadata: dict,
                           date: datetime,
                           elevation: Optional[np.ndarray] = None) -> pd.DataFrame:
        """
        Create feature grid for prediction
        
        Args:
            era5_upsampled: Upsampled ERA5 temperature
            ndvi: NDVI array
            metadata: Spatial metadata
            date: Date for day-of-year calculation
            elevation: Optional elevation array
        
        Returns:
            DataFrame with features for each pixel
        """
        print("Creating feature grid...")
        
        height, width = era5_upsampled.shape
        
        # Create coordinate grids
        transform = metadata['transform']
        rows, cols = np.mgrid[0:height, 0:width]
        
        # Convert pixel coordinates to geographic coordinates
        xs, ys = rasterio.transform.xy(transform, rows.ravel(), cols.ravel())
        lons = np.array(xs)
        lats = np.array(ys)
        
        # Flatten all arrays
        era5_flat = era5_upsampled.ravel()
        ndvi_flat = ndvi.ravel()
        
        # Handle elevation
        if elevation is not None:
            elev_flat = elevation.ravel()
        else:
            # Use default elevation if not provided
            elev_flat = np.zeros(len(era5_flat))
        
        # Day of year
        doy = date.timetuple().tm_yday
        doy_flat = np.full(len(era5_flat), doy)
        
        # Create dataframe
        df = pd.DataFrame({
            'ERA5_Temp': era5_flat,
            'NDVI': ndvi_flat,
            'ELEVATION': elev_flat,
            'LAT': lats,
            'LON': lons,
            'DayOfYear': doy_flat,
            'row': rows.ravel(),
            'col': cols.ravel()
        })
        
        # Remove invalid pixels (NaN values)
        df = df.dropna(subset=['ERA5_Temp', 'NDVI'])
        
        return df
    
    def generate_highres_map(self, date: datetime,
                            roi_bounds: Optional[Tuple[float, float, float, float]] = None,
                            output_path: Optional[str] = None) -> Tuple[np.ndarray, dict]:
        """
        Generate complete high-resolution temperature map
        
        Args:
            date: Target date for prediction
            roi_bounds: Optional (min_lon, min_lat, max_lon, max_lat) to crop region
            output_path: Optional path to save output GeoTIFF
        
        Returns:
            High-resolution temperature array and metadata
        """
        print(f"\n=== Generating High-Resolution Map for {date.strftime('%Y-%m-%d')} ===")
        
        # Step 1: Load high-resolution NDVI (defines output grid)
        # Pass bbox to avoid loading full Europe raster
        bbox = roi_bounds if roi_bounds else None
        ndvi, metadata = self.load_ndvi_for_date(date, bbox=bbox)
        
        # Step 2: Load coarse ERA5 temperature
        era5_temp = self.load_era5_for_date(date)
        
        # Step 3: Upsample ERA5 to match NDVI resolution
        era5_upsampled = self.upsample_era5_to_highres(era5_temp, metadata)
        
        # Step 4: Create feature grid
        feature_df = self.create_feature_grid(
            era5_upsampled, ndvi, metadata, date
        )
        
        print(f"Feature grid: {len(feature_df)} valid pixels")
        
        # Step 5: Predict residuals using trained model
        print("Predicting residuals...")
        predicted_residuals = self.model.predict(feature_df)
        
        # Step 6: Reconstruct high-resolution temperature
        # Formula: HighRes Temp = ERA5 + Predicted Residual
        highres_temp = feature_df['ERA5_Temp'].values + predicted_residuals
        
        # Step 7: Reshape back to 2D grid
        height, width = metadata['height'], metadata['width']
        
        # Initialize output arrays with NaN
        residual_map = np.full((height, width), np.nan, dtype=np.float32)
        highres_map = np.full((height, width), np.nan, dtype=np.float32)
        
        # Fill in valid pixels
        rows = feature_df['row'].values.astype(int)
        cols = feature_df['col'].values.astype(int)
        
        residual_map[rows, cols] = predicted_residuals
        highres_map[rows, cols] = highres_temp
        
        print("Map generation complete!")
        print(f"Temperature range: {np.nanmin(highres_map):.1f}°C to {np.nanmax(highres_map):.1f}°C")
        print(f"Mean residual: {np.nanmean(residual_map):.2f}°C")
        
        # Save outputs if requested
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save high-res temperature map
            with rasterio.open(
                output_path,
                'w',
                driver='GTiff',
                height=height,
                width=width,
                count=1,
                dtype=np.float32,
                crs=metadata['crs'],
                transform=metadata['transform'],
                compress='lzw'
            ) as dst:
                dst.write(highres_map, 1)
            
            print(f"Saved to: {output_path}")
            
            # Also save residual map
            residual_path = output_path.parent / f"residual_{output_path.name}"
            with rasterio.open(
                residual_path,
                'w',
                driver='GTiff',
                height=height,
                width=width,
                count=1,
                dtype=np.float32,
                crs=metadata['crs'],
                transform=metadata['transform'],
                compress='lzw'
            ) as dst:
                dst.write(residual_map, 1)
        
        return highres_map, metadata


def generate_maps_for_period(model_path: str,
                             era5_dir: str,
                             ndvi_dir: str,
                             start_date: str,
                             end_date: str,
                             output_dir: str,
                             roi_bounds: Optional[Tuple[float, float, float, float]] = None):
    """
    Generate high-resolution maps for a date range
    
    Args:
        model_path: Path to trained model
        era5_dir: ERA5 data directory
        ndvi_dir: NDVI data directory
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        output_dir: Output directory
        roi_bounds: Optional (min_lon, min_lat, max_lon, max_lat) for region of interest
                    Example: Sweden (10.0, 55.0, 25.0, 70.0)
    """
    # Load trained model
    print(f"Loading model from {model_path}")
    model = ResidualLearningModel.load(model_path)
    
    # Initialize generator
    generator = HighResMapGenerator(model, era5_dir, ndvi_dir)
    
    # Generate date range
    dates = pd.date_range(start_date, end_date, freq='D')
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Print ROI info
    if roi_bounds:
        print(f"Region of Interest: LON [{roi_bounds[0]}, {roi_bounds[2]}], LAT [{roi_bounds[1]}, {roi_bounds[3]}]")
    else:
        print("WARNING: No ROI specified - will load full Europe NDVI raster (may be very slow)")
    
    # Generate maps
    for date in dates:
        try:
            output_file = output_path / f"highres_temp_{date.strftime('%Y%m%d')}.tif"
            
            generator.generate_highres_map(
                date=date,
                roi_bounds=roi_bounds,
                output_path=output_file
            )
        except Exception as e:
            print(f"Error generating map for {date}: {e}")
            continue


if __name__ == "__main__":
    # Example usage
    generate_maps_for_period(
        model_path='../outputs/residual_model.pkl',
        era5_dir='../datasets/main/derived-era5-land-daily-statistics',
        ndvi_dir='../datasets/main/sentinel2_ndvi',
        start_date='2023-07-01',
        end_date='2023-07-10',
        output_dir='../outputs/highres_maps'
    )
