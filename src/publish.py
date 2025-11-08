"""
GenHack Climate - Publish/Export (Phase 1: Stub)

Exports final outputs in standard formats:
- GeoTIFF (Cloud Optimized)
- PNG preview images
- Metadata JSON

Phase 1: Exports mock data with proper formatting
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any
import numpy as np
import rasterio
from rasterio.plot import show
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

from src.models import Manifest, RasterMetadata, Bounds

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def export_geotiff(
    input_path: Path,
    output_path: Path,
    compress: str = "lzw",
    tiled: bool = True
) -> RasterMetadata:
    """
    Export raster as Cloud Optimized GeoTIFF
    
    Args:
        input_path: Source raster
        output_path: Destination COG
        compress: Compression method
        tiled: Whether to tile output
        
    Returns:
        Metadata of exported raster
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with rasterio.open(input_path) as src:
        # Copy with COG-friendly options
        profile = src.profile.copy()
        profile.update({
            'driver': 'GTiff',
            'compress': compress,
            'tiled': tiled,
            'blockxsize': 512,
            'blockysize': 512,
            'interleave': 'band'
        })
        
        with rasterio.open(output_path, 'w', **profile) as dst:
            for i in range(1, src.count + 1):
                dst.write(src.read(i), i)
                if src.descriptions[i-1]:
                    dst.set_band_description(i, src.descriptions[i-1])
        
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
    
    logger.info(f"✅ Exported GeoTIFF: {output_path.name}")
    return metadata


def export_png_preview(
    input_path: Path,
    output_path: Path,
    title: str = "Temperature"
) -> Path:
    """
    Generate PNG preview of raster
    
    Args:
        input_path: Source raster
        output_path: Destination PNG
        title: Title for plot
        
    Returns:
        Path to PNG
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with rasterio.open(input_path) as src:
        data = src.read(1)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        im = ax.imshow(data, cmap='RdYlBu_r')
        ax.set_title(title)
        plt.colorbar(im, ax=ax, label='°C')
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
    
    logger.info(f"✅ Generated preview: {output_path.name}")
    return output_path


def publish_stage(config: Dict[str, Any], manifest: Manifest) -> Manifest:
    """
    Publish/export stage - create final outputs
    
    Args:
        config: Pipeline configuration
        manifest: Input manifest
        
    Returns:
        Updated manifest
    """
    logger.info("🔄 PUBLISH STAGE")
    
    if not manifest.paths or not manifest.paths.intermediate:
        raise ValueError("No intermediate data path in manifest")
    
    intermediate_dir = Path(manifest.paths.intermediate.replace("gs://", "/tmp/gcs/"))
    exports_dir = Path(manifest.paths.exports.replace("gs://", "/tmp/gcs/"))
    exports_dir.mkdir(parents=True, exist_ok=True)
    
    output_formats = config.get("output", {}).get("formats", ["geotiff", "png", "metadata"])
    
    exported_files = []
    metadata_dict = {}
    
    # Export temperature raster
    temp_input = intermediate_dir / "t2m_reprojected.tif"
    if temp_input.exists():
        if "geotiff" in output_formats:
            temp_output = exports_dir / f"{manifest.city}_temperature.tif"
            metadata = export_geotiff(temp_input, temp_output)
            metadata_dict["temperature"] = metadata.to_json()
            exported_files.append(str(temp_output))
        
        if "png" in output_formats:
            png_output = exports_dir / f"{manifest.city}_temperature.png"
            export_png_preview(
                temp_input, 
                png_output, 
                title=f"{manifest.city.title()} - Temperature (°C)"
            )
            exported_files.append(str(png_output))
    
    # Export feature indices if available
    features_dir = Path(manifest.paths.features.replace("gs://", "/tmp/gcs/"))
    
    for feature in ["ndvi", "ndbi"]:
        feature_input = features_dir / f"{feature}.tif"
        if feature_input.exists():
            if "geotiff" in output_formats:
                feature_output = exports_dir / f"{manifest.city}_{feature}.tif"
                metadata = export_geotiff(feature_input, feature_output)
                metadata_dict[feature] = metadata.to_json()
                exported_files.append(str(feature_output))
            
            if "png" in output_formats:
                png_output = exports_dir / f"{manifest.city}_{feature}.png"
                cmap = 'YlGn' if feature == "ndvi" else 'Greys'
                export_png_preview(feature_input, png_output, title=f"{manifest.city.title()} - {feature.upper()}")
                exported_files.append(str(png_output))
    
    # Save metadata
    if "metadata" in output_formats:
        metadata_output = exports_dir / "export_metadata.json"
        with open(metadata_output, 'w') as f:
            json.dump({
                "city": manifest.city,
                "period": manifest.period.model_dump(),
                "grid": manifest.grid.model_dump(),
                "files": exported_files,
                "rasters": metadata_dict
            }, f, indent=2)
        logger.info(f"✅ Metadata saved: {metadata_output}")
    
    manifest.stage = "publish"
    
    logger.info(f"✅ Publish complete: {len(exported_files)} files")
    logger.info(f"   Output: {exports_dir}")
    
    return manifest


if __name__ == "__main__":
    from models import Manifest, Period, Grid, Paths
    from ingest import ingest_mock_data
    from preprocess import preprocess_stage
    from features import features_stage
    
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
        "output": {"formats": ["geotiff", "png", "metadata"]}
    }
    
    # Run full pipeline
    manifest = ingest_mock_data(test_config, test_manifest)
    manifest = preprocess_stage(test_config, manifest)
    manifest = features_stage(test_config, manifest)
    result = publish_stage(test_config, manifest)
    
    print(f"✅ Test complete: {result.stage}")
