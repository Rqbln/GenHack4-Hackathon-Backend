"""
GenHack Climate - Data Ingestion

Phase 1: Generates synthetic rasters (mock mode)
Phase 2: Downloads real ERA5 data from Copernicus CDS

Toggle with manifest.mode.dry_run flag
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any
import numpy as np
import rasterio
from rasterio.transform import from_bounds
from datetime import datetime

from src.models import Manifest, Tile, Paths
from src.era5_client import ERA5Client
from src.sentinel2_client import Sentinel2Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_mock_raster(
    output_path: Path,
    width: int = 128,
    height: int = 128,
    bbox: tuple = (2.224, 48.815, 2.470, 48.902),
    variable: str = "t2m",
    crs: str = "EPSG:4326"
) -> Path:
    """
    Generate a synthetic raster with realistic spatial patterns
    
    Args:
        output_path: Where to save the GeoTIFF
        width, height: Raster dimensions
        bbox: Bounding box (minx, miny, maxx, maxy)
        variable: Variable name (affects pattern)
        crs: Coordinate reference system
        
    Returns:
        Path to created GeoTIFF
    """
    logger.info(f"Generating mock raster: {variable} ({width}x{height})")
    
    # Create synthetic data with spatial pattern
    x = np.linspace(0, 1, width)
    y = np.linspace(0, 1, height)
    xx, yy = np.meshgrid(x, y)
    
    # Base gradient + urban heat island effect (center hotspot)
    center_x, center_y = 0.5, 0.5
    dist = np.sqrt((xx - center_x)**2 + (yy - center_y)**2)
    
    if variable in ["t2m", "tx", "tn"]:
        # Temperature: warmer in center (urban heat island)
        base_temp = 25.0 + 8.0 * np.exp(-5 * dist)
        noise = np.random.normal(0, 1.5, (height, width))
        data = base_temp + noise
    elif variable == "rh":
        # Relative humidity: inverse of temperature
        data = 60.0 - 15.0 * np.exp(-5 * dist) + np.random.normal(0, 5, (height, width))
    elif variable in ["u10", "v10"]:
        # Wind: some spatial variability
        data = 2.0 + 3.0 * np.sin(5 * xx) * np.cos(5 * yy) + np.random.normal(0, 0.5, (height, width))
    else:
        # Default: random field
        data = 20.0 + 10.0 * (xx + yy) / 2 + np.random.normal(0, 2, (height, width))
    
    # Affine transform from bounds
    transform = from_bounds(*bbox, width, height)
    
    # Write GeoTIFF
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(
        output_path,
        'w',
        driver='GTiff',
        height=height,
        width=width,
        count=1,
        dtype=data.dtype,
        crs=crs,
        transform=transform,
        compress='lzw',
        tiled=True
    ) as dst:
        dst.write(data.astype('float32'), 1)
        dst.set_band_description(1, variable)
    
    logger.info(f"✅ Created mock raster: {output_path}")
    return output_path


def ingest_era5_data(config: Dict[str, Any], manifest: Manifest) -> Manifest:
    """
    Real ERA5 data ingestion from Copernicus CDS
    
    Args:
        config: Pipeline configuration
        manifest: Input manifest
        
    Returns:
        Updated manifest with ingested data paths
    """
    logger.info("🔄 INGEST STAGE (ERA5)")
    logger.info(f"City: {manifest.city}")
    logger.info(f"Period: {manifest.period.start} to {manifest.period.end}")
    logger.info(f"Variables: {', '.join(manifest.variables)}")
    
    # Create output directory
    if manifest.paths and manifest.paths.raw:
        output_dir = Path(manifest.paths.raw.replace("gs://", "/tmp/gcs/"))
    else:
        output_dir = Path(f"/tmp/genhack/raw/{manifest.city}")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get bbox from config
    bbox = config.get("extent", {}).get("bbox_wgs84", [2.224, 48.815, 2.470, 48.902])
    
    # Initialize ERA5 client
    client = ERA5Client()
    
    # Download ERA5 data
    netcdf_files = client.download_era5(
        variables=manifest.variables,
        bbox=bbox,
        start_date=manifest.period.start,
        end_date=manifest.period.end,
        output_dir=output_dir
    )
    
    # Convert NetCDF to GeoTIFF
    for var, nc_file in netcdf_files.items():
        tif_file = output_dir / f"{var}_era5.tif"
        client.convert_to_geotiff(
            nc_file, 
            tif_file, 
            var,
            time_aggregation="mean"
        )
    
    # Download Sentinel-2 imagery
    try:
        logger.info("📡 Downloading Sentinel-2 imagery...")
        s2_client = Sentinel2Client()
        s2_files = s2_client.download_sentinel2(
            bbox=bbox,
            start_date=manifest.period.start,
            end_date=manifest.period.end,
            output_dir=output_dir,
            max_cloud_cover=20.0,
            scale=10,
            bands=['B4', 'B8', 'B11']  # Red, NIR, SWIR for NDVI/NDBI
        )
        
        # Compute NDVI and NDBI if we have the required bands
        if 'nir' in s2_files and 'red' in s2_files:
            ndvi_file = output_dir / "ndvi.tif"
            s2_client.compute_ndvi(s2_files['nir'], s2_files['red'], ndvi_file)
        
        if 'swir1' in s2_files and 'nir' in s2_files:
            ndbi_file = output_dir / "ndbi.tif"
            s2_client.compute_ndbi(s2_files['swir1'], s2_files['nir'], ndbi_file)
        
        logger.info(f"✅ Sentinel-2 download complete: {len(s2_files)} bands")
    except Exception as e:
        logger.warning(f"⚠️ Sentinel-2 download failed (continuing with ERA5 only): {e}")
    
    # Update manifest
    manifest.stage = "ingest"
    manifest.paths = Paths(
        raw=str(output_dir),
        intermediate=str(output_dir.parent.parent / "intermediate" / manifest.city),
        features=str(output_dir.parent.parent / "intermediate" / manifest.city / "features"),
        exports=str(output_dir.parent.parent / "exports" / manifest.city)
    )
    
    # Save manifest
    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest.to_json(), f, indent=2)
    
    logger.info(f"✅ ERA5 ingest complete: {len(netcdf_files)} variables")
    logger.info(f"   Output: {output_dir}")
    
    return manifest


def ingest_mock_data(config: Dict[str, Any], manifest: Manifest) -> Manifest:
    """
    Mock data ingestion - generates synthetic rasters
    
    Used when manifest.mode.dry_run is True
    
    Args:
        config: Pipeline configuration
        manifest: Input manifest
        
    Returns:
        Updated manifest with ingested data paths
    """
    logger.info("🔄 INGEST STAGE (MOCK)")
    logger.info(f"City: {manifest.city}")
    logger.info(f"Period: {manifest.period.start} to {manifest.period.end}")
    logger.info(f"Variables: {', '.join(manifest.variables)}")
    
    # Create output directory (local or GCS)
    if manifest.paths and manifest.paths.raw:
        output_dir = Path(manifest.paths.raw.replace("gs://", "/tmp/gcs/"))
    else:
        output_dir = Path(f"/tmp/genhack/raw/{manifest.city}")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate mock rasters for each variable
    bbox = config.get("extent", {}).get("bbox_wgs84", [2.224, 48.815, 2.470, 48.902])
    
    for variable in manifest.variables:
        output_path = output_dir / f"{variable}_mock.tif"
        generate_mock_raster(
            output_path=output_path,
            width=128,
            height=128,
            bbox=tuple(bbox),
            variable=variable,
            crs="EPSG:4326"
        )
    
    # Update manifest
    manifest.stage = "ingest"
    manifest.paths = Paths(
        raw=str(output_dir),
        intermediate=str(output_dir.parent.parent / "intermediate" / manifest.city),
        features=str(output_dir.parent.parent / "intermediate" / manifest.city / "features"),
        exports=str(output_dir.parent.parent / "exports" / manifest.city)
    )
    
    # Save manifest
    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest.to_json(), f, indent=2)
    
    logger.info(f"✅ Ingest complete: {len(manifest.variables)} variables")
    logger.info(f"   Output: {output_dir}")
    
    return manifest


def ingest_stage(config: Dict[str, Any], manifest: Manifest) -> Manifest:
    """
    Main ingestion stage - routes to mock or real data based on dry_run flag
    
    Args:
        config: Pipeline configuration
        manifest: Input manifest
        
    Returns:
        Updated manifest
    """
    if manifest.mode and manifest.mode.dry_run:
        return ingest_mock_data(config, manifest)
    else:
        return ingest_era5_data(config, manifest)


if __name__ == "__main__":
    # Test stub locally
    from src.models import Manifest, Period, Grid
    
    test_manifest = Manifest(
        city="paris",
        period=Period(start="2022-07-15", end="2022-07-17"),
        grid=Grid(crs="EPSG:3857", resolution_m=200),
        variables=["t2m", "tx", "rh"],
        stage="init",
        tiles=[]
    )
    
    test_config = {
        "extent": {"bbox_wgs84": [2.224, 48.815, 2.470, 48.902]}
    }
    
    result = ingest_mock_data(test_config, test_manifest)
    print(f"✅ Test complete: {result.stage}")
