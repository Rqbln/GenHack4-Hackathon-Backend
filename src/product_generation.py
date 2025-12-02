"""
Product Generation: Complete Time Series

Generates final products (complete time series) for the hackathon period.
Exports downscaled temperature data, NDVI maps, and UHI indicators.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

try:
    import numpy as np
    import xarray as xr
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logger.warning("numpy/xarray not available. Install with: pip install numpy xarray")


class ProductGenerator:
    """Generate final products for hackathon period"""
    
    def __init__(
        self,
        output_dir: Path,
        start_date: datetime,
        end_date: datetime
    ):
        """
        Initialize product generator
        
        Args:
            output_dir: Directory to save generated products
            start_date: Start date for time series
            end_date: End date for time series
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.start_date = start_date
        self.end_date = end_date
        
        logger.info(f"Product Generator initialized: {start_date} to {end_date}")
    
    def generate_time_series(
        self,
        predictions: Dict[str, np.ndarray],
        metadata: Dict
    ) -> Path:
        """
        Generate complete time series NetCDF file
        
        Args:
            predictions: Dictionary with date strings as keys and prediction arrays as values
            metadata: Metadata dictionary (coordinates, variables, etc.)
            
        Returns:
            Path to generated NetCDF file
        """
        if not NUMPY_AVAILABLE:
            raise ImportError("numpy and xarray are required for time series generation")
        
        logger.info("Generating time series NetCDF...")
        
        # Create time dimension
        dates = sorted([datetime.fromisoformat(d) for d in predictions.keys()])
        time_coords = xr.cftime_range(
            start=dates[0],
            end=dates[-1],
            freq='D',
            calendar='gregorian'
        )
        
        # Stack predictions into 3D array (time, lat, lon)
        first_pred = list(predictions.values())[0]
        n_time = len(predictions)
        n_lat, n_lon = first_pred.shape
        
        data_array = np.zeros((n_time, n_lat, n_lon))
        for i, date_str in enumerate(sorted(predictions.keys())):
            data_array[i] = predictions[date_str]
        
        # Create xarray Dataset
        ds = xr.Dataset(
            {
                'temperature': (
                    ['time', 'latitude', 'longitude'],
                    data_array,
                    {
                        'long_name': 'Downscaled 2m Temperature',
                        'units': 'celsius',
                        'standard_name': 'air_temperature'
                    }
                )
            },
            coords={
                'time': time_coords[:n_time],
                'latitude': metadata.get('latitudes', np.linspace(48.8, 49.0, n_lat)),
                'longitude': metadata.get('longitudes', np.linspace(2.2, 2.5, n_lon))
            },
            attrs={
                'title': 'GenHack 2025 - Downscaled Temperature Time Series',
                'description': 'Temperature downscaled from ERA5 using Prithvi WxC',
                'model': 'Prithvi WxC (Fine-tuned)',
                'resolution': '100m',
                'created': datetime.now().isoformat(),
                'hackathon_period': f"{self.start_date.date()} to {self.end_date.date()}"
            }
        )
        
        # Save to NetCDF
        output_path = self.output_dir / 'temperature_timeseries.nc'
        ds.to_netcdf(output_path, format='NETCDF4')
        
        logger.info(f"✅ Time series saved to {output_path}")
        return output_path
    
    def generate_uhi_indicators(
        self,
        temperature_data: np.ndarray,
        reference_temperature: float,
        metadata: Dict
    ) -> Dict:
        """
        Generate UHI intensity indicators
        
        Args:
            temperature_data: 2D temperature array
            reference_temperature: Reference temperature (rural baseline)
            metadata: Metadata dictionary
            
        Returns:
            Dictionary with UHI indicators
        """
        logger.info("Calculating UHI indicators...")
        
        uhi_intensity = temperature_data - reference_temperature
        
        indicators = {
            'mean_uhi': float(np.nanmean(uhi_intensity)),
            'max_uhi': float(np.nanmax(uhi_intensity)),
            'min_uhi': float(np.nanmin(uhi_intensity)),
            'std_uhi': float(np.nanstd(uhi_intensity)),
            'uhi_area_km2': float(np.sum(uhi_intensity > 2.0) * 0.01),  # Assuming 100m resolution
            'hotspot_count': int(np.sum(uhi_intensity > 4.0))
        }
        
        logger.info(f"Mean UHI intensity: {indicators['mean_uhi']:.2f}°C")
        return indicators
    
    def export_summary_report(
        self,
        metrics: Dict,
        indicators: Dict,
        output_path: Path
    ):
        """
        Export summary report as JSON
        
        Args:
            metrics: Model metrics dictionary
            indicators: UHI indicators dictionary
            output_path: Path to save report
        """
        report = {
            'generation_date': datetime.now().isoformat(),
            'period': {
                'start': self.start_date.isoformat(),
                'end': self.end_date.isoformat()
            },
            'model_metrics': metrics,
            'uhi_indicators': indicators,
            'files_generated': [
                'temperature_timeseries.nc',
                'uhi_indicators.json',
                'summary_report.json'
            ]
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"✅ Summary report saved to {output_path}")
    
    def generate_all_products(
        self,
        predictions: Dict[str, np.ndarray],
        metrics: Dict,
        metadata: Dict,
        reference_temp: float = 20.0
    ) -> Dict[str, Path]:
        """
        Generate all final products
        
        Args:
            predictions: Dictionary of predictions by date
            metrics: Model metrics
            metadata: Metadata dictionary
            reference_temp: Reference temperature for UHI calculation
            
        Returns:
            Dictionary mapping product names to file paths
        """
        logger.info("Generating all final products...")
        
        products = {}
        
        # Generate time series
        products['timeseries'] = self.generate_time_series(predictions, metadata)
        
        # Calculate UHI indicators (using mean of all predictions)
        mean_temp = np.mean([pred for pred in predictions.values()], axis=0)
        indicators = self.generate_uhi_indicators(mean_temp, reference_temp, metadata)
        
        # Save indicators
        indicators_path = self.output_dir / 'uhi_indicators.json'
        with open(indicators_path, 'w') as f:
            json.dump(indicators, f, indent=2)
        products['indicators'] = indicators_path
        
        # Generate summary report
        report_path = self.output_dir / 'summary_report.json'
        self.export_summary_report(metrics, indicators, report_path)
        products['report'] = report_path
        
        logger.info("✅ All products generated successfully")
        return products


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    generator = ProductGenerator(
        output_dir=Path("./products"),
        start_date=datetime(2020, 1, 1),
        end_date=datetime(2021, 12, 31)
    )
    
    print("Product generator initialized")

