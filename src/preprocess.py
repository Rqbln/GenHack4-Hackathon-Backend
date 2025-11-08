"""
GenHack Climate - Preprocessing (Phase 1: Stub)

Handles reprojection, resampling, and normalization of rasters.
Phase 1: Simple passthrough with metadata extraction.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling

from src.models import Manifest, RasterMetadata, Bounds

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def preprocess_raster(
    input_path: Path,
    output_path: Path,
    target_crs: str = "EPSG:3857",
    resampling: Resampling = Resampling.bilinear
) -> RasterMetadata:
    """
    Reproject and resample a raster
    
    Args:
        input_path: Source raster
        output_path: Destination raster
        target_crs: Target coordinate system
        resampling: Resampling method
        
    Returns:
        Metadata of output raster
    """
    with rasterio.open(input_path) as src:
        # Calculate transform for target CRS
        transform, width, height = calculate_default_transform(
            src.crs, target_crs, src.width, src.height, *src.bounds
        )
        
        # Prepare output
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': target_crs,
            'transform': transform,
            'width': width,
            'height': height,
            'compress': 'lzw',
            'tiled': True
        })
        
        # Reproject
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with rasterio.open(output_path, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=target_crs,
                    resampling=resampling
                )
        
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
                bounds=Bounds(
                    minx=bounds.left,
                    miny=bounds.bottom,
                    maxx=bounds.right,
                    maxy=bounds.top
                ),
                band_count=dst.count
            )
    
    logger.info(f"✅ Preprocessed: {input_path.name} -> {output_path.name}")
    return metadata


def preprocess_stage(config: Dict[str, Any], manifest: Manifest) -> Manifest:
    """
    Preprocess all rasters from ingest stage
    
    Args:
        config: Pipeline configuration
        manifest: Input manifest (from ingest)
        
    Returns:
        Updated manifest with preprocessed data paths
    """
    logger.info("🔄 PREPROCESS STAGE")
    
    if not manifest.paths or not manifest.paths.raw:
        raise ValueError("No raw data path in manifest")
    
    raw_dir = Path(manifest.paths.raw.replace("gs://", "/tmp/gcs/"))
    intermediate_dir = Path(manifest.paths.intermediate.replace("gs://", "/tmp/gcs/"))
    intermediate_dir.mkdir(parents=True, exist_ok=True)
    
    target_crs = manifest.grid.crs
    metadata_dict = {}
    
    # Process each variable
    for variable in manifest.variables:
        input_path = raw_dir / f"{variable}_mock.tif"
        output_path = intermediate_dir / f"{variable}_reprojected.tif"
        
        if input_path.exists():
            metadata = preprocess_raster(
                input_path=input_path,
                output_path=output_path,
                target_crs=target_crs
            )
            metadata_dict[variable] = metadata.to_json()
        else:
            logger.warning(f"⚠️  Input file not found: {input_path}")
    
    # Update manifest
    manifest.stage = "preprocess"
    
    # Save metadata
    metadata_path = intermediate_dir / "raster_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata_dict, f, indent=2)
    
    # Save updated manifest
    manifest_path = intermediate_dir / "manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest.to_json(), f, indent=2)
    
    logger.info(f"✅ Preprocess complete: {len(metadata_dict)} rasters")
    logger.info(f"   Output: {intermediate_dir}")
    
    return manifest


if __name__ == "__main__":
    # Test stub locally
    import sys
    from src.models import Manifest, Period, Grid, Paths
    
    # First run ingest to have input data
    from src.ingest import ingest_mock_data
    
    test_manifest = Manifest(
        city="paris",
        period=Period(start="2022-07-15", end="2022-07-17"),
        grid=Grid(crs="EPSG:3857", resolution_m=200),
        variables=["t2m", "rh"],
        stage="init",
        tiles=[]
    )
    
    test_config = {
        "extent": {"bbox_wgs84": [2.224, 48.815, 2.470, 48.902]}
    }
    
    # Run ingest first
    manifest_after_ingest = ingest_mock_data(test_config, test_manifest)
    
    # Then preprocess
    result = preprocess_stage(test_config, manifest_after_ingest)
    print(f"✅ Test complete: {result.stage}")
