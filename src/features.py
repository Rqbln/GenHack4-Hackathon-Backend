"""
GenHack Climate - Feature Engineering (Phase 1: Stub)

Computes spectral indices (NDVI, NDBI, etc.) from satellite imagery.
Phase 1: Mock calculations on synthetic data.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any
import numpy as np
import rasterio

from src.models import Manifest, RasterMetadata, Bounds

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def compute_ndvi_mock(
    input_path: Path,
    output_path: Path
) -> RasterMetadata:
    """
    Compute mock NDVI (Normalized Difference Vegetation Index)
    
    NDVI = (NIR - Red) / (NIR + Red)
    Phase 1: Generate synthetic NDVI pattern
    
    Args:
        input_path: Base temperature raster (used for spatial reference)
        output_path: Output NDVI raster
        
    Returns:
        Metadata of NDVI raster
    """
    with rasterio.open(input_path) as src:
        # Read base data for spatial reference
        data = src.read(1)
        
        # Generate mock NDVI: higher in cooler areas (vegetation)
        # Inverse relationship with temperature
        normalized_temp = (data - data.min()) / (data.max() - data.min())
        ndvi = 0.3 + 0.5 * (1 - normalized_temp) + np.random.normal(0, 0.05, data.shape)
        ndvi = np.clip(ndvi, -1, 1)  # NDVI range [-1, 1]
        
        # Write output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with rasterio.open(
            output_path,
            'w',
            driver='GTiff',
            height=src.height,
            width=src.width,
            count=1,
            dtype='float32',
            crs=src.crs,
            transform=src.transform,
            compress='lzw',
            tiled=True
        ) as dst:
            dst.write(ndvi.astype('float32'), 1)
            dst.set_band_description(1, "ndvi")
        
        # Extract metadata
        with rasterio.open(output_path) as dst:
            bounds = dst.bounds
            metadata = RasterMetadata(
                crs=str(dst.crs),
                transform=list(dst.transform)[:6],
                width=dst.width,
                height=dst.height,
                nodata=dst.nodata,
                dtype=str(dst.dtypes[0]),
                units="index",
                bounds=Bounds(
                    minx=bounds.left,
                    miny=bounds.bottom,
                    maxx=bounds.right,
                    maxy=bounds.top
                ),
                band_count=dst.count,
                band_names=["ndvi"]
            )
    
    logger.info(f"✅ Computed NDVI: {output_path.name}")
    return metadata


def compute_ndbi_mock(
    input_path: Path,
    output_path: Path
) -> RasterMetadata:
    """
    Compute mock NDBI (Normalized Difference Built-up Index)
    
    NDBI = (SWIR - NIR) / (SWIR + NIR)
    Phase 1: Generate synthetic NDBI pattern (higher in urban centers)
    
    Args:
        input_path: Base temperature raster
        output_path: Output NDBI raster
        
    Returns:
        Metadata of NDBI raster
    """
    with rasterio.open(input_path) as src:
        data = src.read(1)
        
        # Generate mock NDBI: higher in warmer areas (urban)
        normalized_temp = (data - data.min()) / (data.max() - data.min())
        ndbi = -0.2 + 0.6 * normalized_temp + np.random.normal(0, 0.05, data.shape)
        ndbi = np.clip(ndbi, -1, 1)
        
        # Write output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with rasterio.open(
            output_path,
            'w',
            driver='GTiff',
            height=src.height,
            width=src.width,
            count=1,
            dtype='float32',
            crs=src.crs,
            transform=src.transform,
            compress='lzw',
            tiled=True
        ) as dst:
            dst.write(ndbi.astype('float32'), 1)
            dst.set_band_description(1, "ndbi")
        
        # Extract metadata
        with rasterio.open(output_path) as dst:
            bounds = dst.bounds
            metadata = RasterMetadata(
                crs=str(dst.crs),
                transform=list(dst.transform)[:6],
                width=dst.width,
                height=dst.height,
                nodata=dst.nodata,
                dtype=str(dst.dtypes[0]),
                units="index",
                bounds=Bounds(
                    minx=bounds.left,
                    miny=bounds.bottom,
                    maxx=bounds.right,
                    maxy=bounds.top
                ),
                band_count=dst.count,
                band_names=["ndbi"]
            )
    
    logger.info(f"✅ Computed NDBI: {output_path.name}")
    return metadata


def features_stage(config: Dict[str, Any], manifest: Manifest) -> Manifest:
    """
    Feature engineering stage - compute spectral indices
    
    Args:
        config: Pipeline configuration
        manifest: Input manifest (from preprocess)
        
    Returns:
        Updated manifest with features
    """
    logger.info("🔄 FEATURES STAGE")
    
    if not manifest.paths or not manifest.paths.intermediate:
        raise ValueError("No intermediate data path in manifest")
    
    intermediate_dir = Path(manifest.paths.intermediate.replace("gs://", "/tmp/gcs/"))
    features_dir = Path(manifest.paths.features.replace("gs://", "/tmp/gcs/"))
    features_dir.mkdir(parents=True, exist_ok=True)
    
    # Use temperature raster as base for spatial reference
    base_raster = intermediate_dir / "t2m_reprojected.tif"
    
    if not base_raster.exists():
        logger.warning(f"⚠️  Base raster not found: {base_raster}")
        logger.info("   Skipping feature computation")
        manifest.stage = "features"
        return manifest
    
    # Compute indices
    metadata_dict = {}
    
    ndvi_path = features_dir / "ndvi.tif"
    metadata_dict["ndvi"] = compute_ndvi_mock(base_raster, ndvi_path).to_json()
    
    ndbi_path = features_dir / "ndbi.tif"
    metadata_dict["ndbi"] = compute_ndbi_mock(base_raster, ndbi_path).to_json()
    
    # Update manifest with feature variables
    manifest.variables.extend(["ndvi", "ndbi"])
    manifest.stage = "features"
    
    # Save metadata
    metadata_path = features_dir / "features_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata_dict, f, indent=2)
    
    # Save updated manifest
    manifest_path = features_dir / "manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest.to_json(), f, indent=2)
    
    logger.info(f"✅ Features complete: {len(metadata_dict)} indices")
    logger.info(f"   Output: {features_dir}")
    
    return manifest


if __name__ == "__main__":
    # Test stub locally (requires preprocess output)
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
        "extent": {"bbox_wgs84": [2.224, 48.815, 2.470, 48.902]}
    }
    
    # Run pipeline up to features
    manifest = ingest_mock_data(test_config, test_manifest)
    manifest = preprocess_stage(test_config, manifest)
    result = features_stage(test_config, manifest)
    
    print(f"✅ Test complete: {result.stage}")
    print(f"   Variables: {result.variables}")
