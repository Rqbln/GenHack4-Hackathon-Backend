"""
GenHack Climate - Heat Indicators (Phase 1: Stub)

Computes climate indicators from temperature data:
- Heat intensity, duration, extent
- Urban heat island analysis
- Population exposure estimates

Phase 1: Placeholder calculations on mock data
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any
import numpy as np
import rasterio

from src.models import Manifest, Indicators

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def compute_indicators_mock(
    temperature_path: Path,
    threshold_c: float = 30.0
) -> Indicators:
    """
    Compute heat indicators from temperature raster
    
    Phase 1: Mock calculations
    Phase 2+: Real analysis with multiple timesteps
    
    Args:
        temperature_path: Path to temperature raster
        threshold_c: Heat threshold in Celsius
        
    Returns:
        Heat indicators
    """
    if not temperature_path.exists():
        logger.warning(f"Temperature raster not found: {temperature_path}")
        return Indicators(threshold_c=threshold_c)
    
    with rasterio.open(temperature_path) as src:
        data = src.read(1)
        
        # Mask nodata
        if src.nodata is not None:
            data_masked = np.ma.masked_equal(data, src.nodata)
        else:
            data_masked = np.ma.masked_invalid(data)
        
        # Basic statistics
        max_temp = float(data_masked.max())
        mean_temp = float(data_masked.mean())
        percentile_95 = float(np.percentile(data_masked.compressed(), 95))
        percentile_99 = float(np.percentile(data_masked.compressed(), 99))
        
        # Days above threshold (mock: assume single timestep = 1 day if above)
        days_above = 1 if mean_temp > threshold_c else 0
        
        # Intensity: temperature anomaly above threshold
        intensity = max(0, mean_temp - threshold_c)
        
        # Extent: area with temp > threshold (mock calculation)
        pixels_above = np.sum(data_masked > threshold_c)
        total_pixels = data_masked.count()
        extent_ratio = pixels_above / total_pixels if total_pixels > 0 else 0
        
        # Rough area estimate (assume 200m resolution)
        pixel_area_km2 = (200 * 200) / 1e6  # m² to km²
        extent_km2 = extent_ratio * src.width * src.height * pixel_area_km2
        
        # Urban heat island: mock (difference between max and edge values)
        edge_values = np.concatenate([
            data_masked[0, :].compressed(),
            data_masked[-1, :].compressed(),
            data_masked[:, 0].compressed(),
            data_masked[:, -1].compressed()
        ])
        if len(edge_values) > 0:
            uhi_intensity = max_temp - float(np.mean(edge_values))
        else:
            uhi_intensity = 0.0
        
        indicators = Indicators(
            intensity=intensity,
            duration=days_above,  # Mock: single timestep
            extent_km2=extent_km2,
            max_temperature_c=max_temp,
            mean_temperature_c=mean_temp,
            threshold_c=threshold_c,
            days_above_threshold=days_above,
            affected_population_estimate=None,  # Would need population data
            urban_heat_island_intensity_c=uhi_intensity,
            percentile_95=percentile_95,
            percentile_99=percentile_99
        )
    
    logger.info(f"✅ Computed indicators:")
    logger.info(f"   Max temp: {max_temp:.1f}°C")
    logger.info(f"   Mean temp: {mean_temp:.1f}°C")
    logger.info(f"   UHI intensity: {uhi_intensity:.1f}°C")
    logger.info(f"   Extent: {extent_km2:.1f} km²")
    
    return indicators


def indicators_stage(config: Dict[str, Any], manifest: Manifest) -> Manifest:
    """
    Indicators computation stage
    
    Args:
        config: Pipeline configuration
        manifest: Input manifest
        
    Returns:
        Updated manifest with indicators
    """
    logger.info("🔄 INDICATORS STAGE")
    
    threshold_c = config.get("indicators", {}).get("threshold_celsius", 30.0)
    
    # Find temperature raster
    if manifest.paths and manifest.paths.intermediate:
        intermediate_dir = Path(manifest.paths.intermediate.replace("gs://", "/tmp/gcs/"))
        temp_path = intermediate_dir / "t2m_reprojected.tif"
        
        indicators = compute_indicators_mock(temp_path, threshold_c)
        
        # Save indicators
        if manifest.paths.exports:
            exports_dir = Path(manifest.paths.exports.replace("gs://", "/tmp/gcs/"))
            exports_dir.mkdir(parents=True, exist_ok=True)
            
            indicators_path = exports_dir / "indicators.json"
            with open(indicators_path, 'w') as f:
                json.dump(indicators.to_json(), f, indent=2)
            
            logger.info(f"✅ Indicators saved: {indicators_path}")
    else:
        logger.warning("⚠️  No intermediate path in manifest")
    
    manifest.stage = "indicators"
    return manifest


if __name__ == "__main__":
    from models import Manifest, Period, Grid, Paths
    from ingest import ingest_mock_data
    from preprocess import preprocess_stage
    
    test_manifest = Manifest(
        city="paris",
        period=Period(start="2022-07-15", end="2022-07-17"),
        grid=Grid(crs="EPSG:3857", resolution_m=200),
        variables=["t2m"],
        stage="init",
        tiles=[]
    )
    
    test_config = {
        "extent": {"bbox_wgs84": [2.224, 48.815, 2.470, 48.902]},
        "indicators": {"threshold_celsius": 30.0}
    }
    
    # Run pipeline up to indicators
    manifest = ingest_mock_data(test_config, test_manifest)
    manifest = preprocess_stage(test_config, manifest)
    result = indicators_stage(test_config, manifest)
    
    print(f"✅ Test complete: {result.stage}")
