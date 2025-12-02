"""
Baseline Model for Climate Downscaling

Implements interpolation-based baseline methods:
- Bicubic interpolation for spatial downscaling
- Altitude correction using lapse rate
- RMSE calculation for benchmarking against Pentagen

This serves as a baseline to compare against the Prithvi WxC model.
"""

import numpy as np
import xarray as xr
import rasterio
from rasterio.warp import reproject, Resampling, calculate_default_transform
from rasterio.transform import from_bounds
from pathlib import Path
from typing import Tuple, Optional, Dict
import logging
from scipy.interpolate import griddata
from scipy.ndimage import zoom

logger = logging.getLogger(__name__)


class BaselineDownscaler:
    """Baseline downscaling using interpolation and altitude correction"""
    
    def __init__(
        self,
        target_resolution: float = 100.0,  # meters
        lapse_rate: float = -0.0065,  # K/m (standard atmospheric lapse rate)
        interpolation_method: str = 'cubic'
    ):
        """
        Initialize baseline downscaler
        
        Args:
            target_resolution: Target resolution in meters
            lapse_rate: Temperature lapse rate (K/m)
            interpolation_method: Interpolation method ('linear', 'cubic', 'nearest')
        """
        self.target_resolution = target_resolution
        self.lapse_rate = lapse_rate
        self.interpolation_method = interpolation_method
        
    def bicubic_interpolation(
        self,
        low_res_data: np.ndarray,
        low_res_transform: rasterio.Affine,
        target_shape: Tuple[int, int],
        target_transform: rasterio.Affine
    ) -> np.ndarray:
        """
        Perform bicubic interpolation to downscale data
        
        Args:
            low_res_data: Low resolution data array
            low_res_transform: Transform of low resolution data
            target_shape: Target (height, width)
            target_transform: Transform of target grid
            
        Returns:
            Interpolated high resolution array
        """
        # Calculate scale factors
        scale_y = target_shape[0] / low_res_data.shape[0]
        scale_x = target_shape[1] / low_res_data.shape[1]
        
        # Use scipy zoom for bicubic interpolation
        if self.interpolation_method == 'cubic':
            order = 3
        elif self.interpolation_method == 'linear':
            order = 1
        else:
            order = 0
        
        interpolated = zoom(low_res_data, (scale_y, scale_x), order=order, mode='nearest')
        
        # Ensure correct shape
        if interpolated.shape != target_shape:
            # Crop or pad if necessary
            if interpolated.shape[0] > target_shape[0]:
                interpolated = interpolated[:target_shape[0], :]
            if interpolated.shape[1] > target_shape[1]:
                interpolated = interpolated[:, :target_shape[1]]
            if interpolated.shape[0] < target_shape[0] or interpolated.shape[1] < target_shape[1]:
                # Pad with edge values
                pad_y = max(0, target_shape[0] - interpolated.shape[0])
                pad_x = max(0, target_shape[1] - interpolated.shape[1])
                interpolated = np.pad(
                    interpolated,
                    ((0, pad_y), (0, pad_x)),
                    mode='edge'
                )
        
        return interpolated
    
    def altitude_correction(
        self,
        temperature: np.ndarray,
        elevation: np.ndarray,
        reference_elevation: float = 0.0
    ) -> np.ndarray:
        """
        Apply altitude correction to temperature using lapse rate
        
        Formula: T_corrected = T + lapse_rate * (elevation - reference_elevation)
        
        Args:
            temperature: Temperature array (°C)
            elevation: Elevation array (meters)
            reference_elevation: Reference elevation (meters)
            
        Returns:
            Altitude-corrected temperature array
        """
        elevation_diff = elevation - reference_elevation
        correction = self.lapse_rate * elevation_diff
        corrected_temperature = temperature + correction
        
        return corrected_temperature
    
    def downscale_era5_to_ndvi_grid(
        self,
        era5_ds: xr.Dataset,
        ndvi_metadata: Dict,
        variable: str = 't2m',
        apply_altitude_correction: bool = False,
        elevation_data: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Downscale ERA5 data to NDVI grid resolution
        
        Args:
            era5_ds: ERA5 xarray Dataset
            ndvi_metadata: Metadata from NDVI GeoTIFF (transform, crs, shape)
            variable: Variable name to downscale
            apply_altitude_correction: Whether to apply altitude correction
            elevation_data: Optional elevation data for correction
            
        Returns:
            Downscaled array at NDVI resolution
        """
        # Extract ERA5 data for a specific time
        if 'valid_time' in era5_ds.dims:
            # Use first time step for now
            era5_data = era5_ds[variable].isel(valid_time=0).values
        else:
            era5_data = era5_ds[variable].values
        
        # Get ERA5 coordinates
        era5_lat = era5_ds.latitude.values
        era5_lon = era5_ds.longitude.values
        
        # Create ERA5 transform
        lon_min, lon_max = era5_lon.min(), era5_lon.max()
        lat_min, lat_max = era5_lat.min(), era5_lat.max()
        era5_transform = from_bounds(
            lon_min, lat_min, lon_max, lat_max,
            len(era5_lon), len(era5_lat)
        )
        
        # Get target shape and transform
        target_shape = (ndvi_metadata['height'], ndvi_metadata['width'])
        target_transform = ndvi_metadata['transform']
        
        # Perform bicubic interpolation
        downscaled = self.bicubic_interpolation(
            era5_data,
            era5_transform,
            target_shape,
            target_transform
        )
        
        # Apply altitude correction if requested
        if apply_altitude_correction and elevation_data is not None:
            # Calculate mean elevation for reference
            reference_elevation = np.nanmean(elevation_data)
            downscaled = self.altitude_correction(
                downscaled,
                elevation_data,
                reference_elevation
            )
        
        return downscaled
    
    def calculate_rmse(
        self,
        predicted: np.ndarray,
        observed: np.ndarray,
        mask: Optional[np.ndarray] = None
    ) -> float:
        """
        Calculate Root Mean Square Error
        
        Args:
            predicted: Predicted values
            observed: Observed values (ground truth)
            mask: Optional mask to exclude certain pixels
            
        Returns:
            RMSE value
        """
        if mask is not None:
            predicted = predicted[mask]
            observed = observed[mask]
        
        # Remove NaN values
        valid_mask = ~(np.isnan(predicted) | np.isnan(observed))
        predicted = predicted[valid_mask]
        observed = observed[valid_mask]
        
        if len(predicted) == 0:
            return np.nan
        
        mse = np.mean((predicted - observed) ** 2)
        rmse = np.sqrt(mse)
        
        return rmse
    
    def calculate_mae(
        self,
        predicted: np.ndarray,
        observed: np.ndarray,
        mask: Optional[np.ndarray] = None
    ) -> float:
        """
        Calculate Mean Absolute Error
        
        Args:
            predicted: Predicted values
            observed: Observed values (ground truth)
            mask: Optional mask to exclude certain pixels
            
        Returns:
            MAE value
        """
        if mask is not None:
            predicted = predicted[mask]
            observed = observed[mask]
        
        # Remove NaN values
        valid_mask = ~(np.isnan(predicted) | np.isnan(observed))
        predicted = predicted[valid_mask]
        observed = observed[valid_mask]
        
        if len(predicted) == 0:
            return np.nan
        
        mae = np.mean(np.abs(predicted - observed))
        
        return mae
    
    def calculate_r2(
        self,
        predicted: np.ndarray,
        observed: np.ndarray,
        mask: Optional[np.ndarray] = None
    ) -> float:
        """
        Calculate R² (coefficient of determination)
        
        Args:
            predicted: Predicted values
            observed: Observed values (ground truth)
            mask: Optional mask to exclude certain pixels
            
        Returns:
            R² value
        """
        if mask is not None:
            predicted = predicted[mask]
            observed = observed[mask]
        
        # Remove NaN values
        valid_mask = ~(np.isnan(predicted) | np.isnan(observed))
        predicted = predicted[valid_mask]
        observed = observed[valid_mask]
        
        if len(predicted) == 0:
            return np.nan
        
        ss_res = np.sum((observed - predicted) ** 2)
        ss_tot = np.sum((observed - np.mean(observed)) ** 2)
        
        if ss_tot == 0:
            return np.nan
        
        r2 = 1 - (ss_res / ss_tot)
        
        return r2
    
    def evaluate_baseline(
        self,
        predicted: np.ndarray,
        observed: np.ndarray,
        mask: Optional[np.ndarray] = None
    ) -> Dict[str, float]:
        """
        Calculate all baseline metrics
        
        Args:
            predicted: Predicted values
            observed: Observed values (ground truth)
            mask: Optional mask to exclude certain pixels
            
        Returns:
            Dictionary with RMSE, MAE, R²
        """
        metrics = {
            'rmse': self.calculate_rmse(predicted, observed, mask),
            'mae': self.calculate_mae(predicted, observed, mask),
            'r2': self.calculate_r2(predicted, observed, mask)
        }
        
        return metrics


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    downscaler = BaselineDownscaler(
        target_resolution=100.0,
        lapse_rate=-0.0065,
        interpolation_method='cubic'
    )
    
    # Example: Create dummy data
    low_res = np.random.rand(10, 10) * 20 + 15  # 10x10 grid, 15-35°C
    high_res_shape = (100, 100)  # 10x upscaling
    
    # Create dummy transforms
    low_res_transform = from_bounds(2.0, 48.5, 2.5, 49.0, 10, 10)
    high_res_transform = from_bounds(2.0, 48.5, 2.5, 49.0, 100, 100)
    
    # Downscale
    high_res = downscaler.bicubic_interpolation(
        low_res,
        low_res_transform,
        high_res_shape,
        high_res_transform
    )
    
    print(f"Downscaled from {low_res.shape} to {high_res.shape}")
    print(f"RMSE (vs original upsampled): {downscaler.calculate_rmse(high_res, zoom(low_res, 10, order=0)):.4f}")

