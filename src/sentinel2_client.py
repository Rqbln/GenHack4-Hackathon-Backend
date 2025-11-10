"""
Sentinel-2 Client for downloading satellite imagery via Google Earth Engine.

This module provides functionality to:
- Query Sentinel-2 L2A (atmospherically corrected) imagery
- Filter by cloud cover and date range
- Extract RGB and multispectral bands (B2, B3, B4, B8, B11, B12)
- Export as GeoTIFF with proper georeferencing
- Compute median composites to reduce cloud interference
"""

import ee
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Sentinel2Client:
    """Client for downloading Sentinel-2 imagery from Google Earth Engine."""
    
    # Sentinel-2 band mapping
    BANDS = {
        'B2': 'blue',      # 490nm, 10m resolution
        'B3': 'green',     # 560nm, 10m resolution
        'B4': 'red',       # 665nm, 10m resolution
        'B8': 'nir',       # 842nm, 10m resolution
        'B11': 'swir1',    # 1610nm, 20m resolution
        'B12': 'swir2',    # 2190nm, 20m resolution
    }
    
    def __init__(self, project: Optional[str] = None):
        """
        Initialize Earth Engine client.
        
        Args:
            project: GCP project ID (optional, uses default if not provided)
        """
        try:
            # Try to initialize without project (uses authenticated account)
            if project:
                ee.Initialize(project=project)
            else:
                ee.Initialize()
            logger.info("✅ Earth Engine initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Earth Engine: {e}")
            logger.info("💡 Tip: Make sure Earth Engine API is enabled in your GCP project")
            raise
    
    def download_sentinel2(
        self,
        bbox: List[float],
        start_date: str,
        end_date: str,
        output_dir: Path,
        max_cloud_cover: float = 20.0,
        scale: int = 10,
        bands: Optional[List[str]] = None,
    ) -> Dict[str, Path]:
        """
        Download Sentinel-2 imagery for specified area and period.
        
        Args:
            bbox: Bounding box [west, south, east, north] in WGS84
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            output_dir: Directory to save outputs
            max_cloud_cover: Maximum cloud cover percentage (0-100)
            scale: Output resolution in meters (10, 20, or 60)
            bands: List of bands to download (default: all bands)
        
        Returns:
            Dictionary mapping band names to output file paths
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if bands is None:
            bands = list(self.BANDS.keys())
        
        logger.info(f"📥 Downloading Sentinel-2 data:")
        logger.info(f"  Area: {bbox}")
        logger.info(f"  Period: {start_date} to {end_date}")
        logger.info(f"  Max cloud: {max_cloud_cover}%")
        logger.info(f"  Bands: {bands}")
        
        # Define area of interest
        aoi = ee.Geometry.Rectangle(bbox)
        
        # Query Sentinel-2 L2A collection
        collection = (
            ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
            .filterBounds(aoi)
            .filterDate(start_date, end_date)
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', max_cloud_cover))
        )
        
        # Count available images
        count = collection.size().getInfo()
        logger.info(f"  Found {count} images with <{max_cloud_cover}% cloud cover")
        
        if count == 0:
            logger.warning("⚠️ No images found matching criteria")
            return {}
        
        # Compute median composite to reduce clouds
        composite = collection.median().clip(aoi)
        
        # Download each band
        output_files = {}
        for band in bands:
            band_name = self.BANDS.get(band, band)
            output_file = output_dir / f"{band_name}_s2.tif"
            
            logger.info(f"  Downloading {band} ({band_name})...")
            
            try:
                # Export band
                self._export_band(
                    image=composite,
                    band=band,
                    aoi=aoi,
                    scale=scale,
                    output_file=output_file
                )
                
                output_files[band_name] = output_file
                logger.info(f"    ✅ Saved to {output_file}")
                
            except Exception as e:
                logger.error(f"    ❌ Failed to download {band}: {e}")
        
        return output_files
    
    def _export_band(
        self,
        image: ee.Image,
        band: str,
        aoi: ee.Geometry,
        scale: int,
        output_file: Path
    ) -> None:
        """
        Export a single band as GeoTIFF.
        
        Args:
            image: Earth Engine image
            band: Band name (e.g., 'B4')
            aoi: Area of interest
            scale: Resolution in meters
            output_file: Output file path
        """
        # Select band
        band_image = image.select(band)
        
        # Get download URL
        url = band_image.getDownloadURL({
            'scale': scale,
            'region': aoi,
            'format': 'GEO_TIFF',
            'crs': 'EPSG:4326'
        })
        
        # Download file
        import requests
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    
    def compute_ndvi(
        self,
        nir_file: Path,
        red_file: Path,
        output_file: Path
    ) -> Path:
        """
        Compute NDVI from NIR and Red bands.
        
        NDVI = (NIR - Red) / (NIR + Red)
        
        Args:
            nir_file: Path to NIR band (B8)
            red_file: Path to Red band (B4)
            output_file: Output NDVI file
        
        Returns:
            Path to output file
        """
        import rasterio
        import numpy as np
        
        logger.info(f"🌿 Computing NDVI: {output_file}")
        
        with rasterio.open(nir_file) as nir_ds, rasterio.open(red_file) as red_ds:
            nir = nir_ds.read(1).astype(float)
            red = red_ds.read(1).astype(float)
            
            # Compute NDVI
            denominator = nir + red
            ndvi = np.where(
                denominator != 0,
                (nir - red) / denominator,
                0
            )
            
            # Write output
            profile = nir_ds.profile.copy()
            profile.update(dtype=rasterio.float32, compress='lzw')
            
            with rasterio.open(output_file, 'w', **profile) as dst:
                dst.write(ndvi.astype(np.float32), 1)
        
        logger.info(f"  ✅ NDVI saved to {output_file}")
        return output_file
    
    def compute_ndbi(
        self,
        swir_file: Path,
        nir_file: Path,
        output_file: Path
    ) -> Path:
        """
        Compute NDBI from SWIR and NIR bands.
        
        NDBI = (SWIR - NIR) / (SWIR + NIR)
        
        Args:
            swir_file: Path to SWIR band (B11)
            nir_file: Path to NIR band (B8)
            output_file: Output NDBI file
        
        Returns:
            Path to output file
        """
        import rasterio
        import numpy as np
        
        logger.info(f"🏙️ Computing NDBI: {output_file}")
        
        with rasterio.open(swir_file) as swir_ds, rasterio.open(nir_file) as nir_ds:
            swir = swir_ds.read(1).astype(float)
            nir = nir_ds.read(1).astype(float)
            
            # Compute NDBI
            denominator = swir + nir
            ndbi = np.where(
                denominator != 0,
                (swir - nir) / denominator,
                0
            )
            
            # Write output
            profile = swir_ds.profile.copy()
            profile.update(dtype=rasterio.float32, compress='lzw')
            
            with rasterio.open(output_file, 'w', **profile) as dst:
                dst.write(ndbi.astype(np.float32), 1)
        
        logger.info(f"  ✅ NDBI saved to {output_file}")
        return output_file


# Test function
def test_sentinel2_download():
    """Test Sentinel-2 download for Paris (small area)."""
    client = Sentinel2Client()
    
    # Paris test area (small bbox)
    bbox = [2.2, 48.8, 2.5, 48.9]
    
    # July 2022 (low cloud cover expected)
    start_date = "2022-07-01"
    end_date = "2022-07-31"
    
    output_dir = Path("/tmp/sentinel2_test")
    
    try:
        # Download key bands for NDVI/NDBI
        files = client.download_sentinel2(
            bbox=bbox,
            start_date=start_date,
            end_date=end_date,
            output_dir=output_dir,
            max_cloud_cover=20.0,
            scale=10,
            bands=['B4', 'B8', 'B11']  # Red, NIR, SWIR
        )
        
        print(f"\n✅ Test complete: {len(files)} bands downloaded")
        
        # Compute indices if we have the bands
        if 'nir' in files and 'red' in files:
            ndvi_file = output_dir / "ndvi.tif"
            client.compute_ndvi(files['nir'], files['red'], ndvi_file)
        
        if 'swir1' in files and 'nir' in files:
            ndbi_file = output_dir / "ndbi.tif"
            client.compute_ndbi(files['swir1'], files['nir'], ndbi_file)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_sentinel2_download()
