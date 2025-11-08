"""
GenHack Climate - Generate Mock Test Rasters

Utility script to generate synthetic raster data for testing.
Used by test suites and local development.
"""

import numpy as np
import rasterio
from rasterio.transform import from_bounds
from pathlib import Path
from typing import Tuple


def generate_temperature_raster(
    output_path: Path,
    width: int = 256,
    height: int = 256,
    bbox: Tuple[float, float, float, float] = (2.224, 48.815, 2.470, 48.902),
    base_temp: float = 25.0,
    uhi_intensity: float = 8.0
) -> Path:
    """
    Generate synthetic temperature raster with urban heat island pattern
    
    Args:
        output_path: Destination file path
        width, height: Raster dimensions
        bbox: Bounding box (minx, miny, maxx, maxy) in WGS84
        base_temp: Base temperature (°C)
        uhi_intensity: Urban heat island intensity (°C)
    """
    # Create spatial gradient (urban heat island - warmer in center)
    x = np.linspace(0, 1, width)
    y = np.linspace(0, 1, height)
    xx, yy = np.meshgrid(x, y)
    
    center_x, center_y = 0.5, 0.5
    dist = np.sqrt((xx - center_x)**2 + (yy - center_y)**2)
    
    # Temperature: exponential decay from center
    temperature = base_temp + uhi_intensity * np.exp(-5 * dist)
    
    # Add realistic noise
    noise = np.random.normal(0, 1.5, (height, width))
    temperature += noise
    
    # Affine transform
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
        dtype='float32',
        crs='EPSG:4326',
        transform=transform,
        compress='lzw',
        tiled=True
    ) as dst:
        dst.write(temperature.astype('float32'), 1)
        dst.set_band_description(1, 't2m')
        dst.update_tags(1, units='celsius')
    
    print(f"✅ Generated: {output_path}")
    return output_path


def generate_humidity_raster(
    output_path: Path,
    width: int = 256,
    height: int = 256,
    bbox: Tuple[float, float, float, float] = (2.224, 48.815, 2.470, 48.902)
) -> Path:
    """Generate synthetic relative humidity raster"""
    x = np.linspace(0, 1, width)
    y = np.linspace(0, 1, height)
    xx, yy = np.meshgrid(x, y)
    
    # Humidity: inverse of temperature pattern
    center_x, center_y = 0.5, 0.5
    dist = np.sqrt((xx - center_x)**2 + (yy - center_y)**2)
    humidity = 60.0 - 15.0 * np.exp(-5 * dist) + np.random.normal(0, 5, (height, width))
    humidity = np.clip(humidity, 0, 100)
    
    transform = from_bounds(*bbox, width, height)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(
        output_path,
        'w',
        driver='GTiff',
        height=height,
        width=width,
        count=1,
        dtype='float32',
        crs='EPSG:4326',
        transform=transform,
        compress='lzw',
        tiled=True
    ) as dst:
        dst.write(humidity.astype('float32'), 1)
        dst.set_band_description(1, 'rh')
        dst.update_tags(1, units='percent')
    
    print(f"✅ Generated: {output_path}")
    return output_path


def generate_wind_raster(
    output_path: Path,
    component: str = 'u',
    width: int = 256,
    height: int = 256,
    bbox: Tuple[float, float, float, float] = (2.224, 48.815, 2.470, 48.902)
) -> Path:
    """Generate synthetic wind component raster"""
    x = np.linspace(0, 1, width)
    y = np.linspace(0, 1, height)
    xx, yy = np.meshgrid(x, y)
    
    # Wind: sinusoidal pattern
    if component == 'u':
        wind = 2.0 + 3.0 * np.sin(5 * xx) + np.random.normal(0, 0.5, (height, width))
    else:  # v component
        wind = 1.0 + 2.5 * np.cos(5 * yy) + np.random.normal(0, 0.5, (height, width))
    
    transform = from_bounds(*bbox, width, height)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(
        output_path,
        'w',
        driver='GTiff',
        height=height,
        width=width,
        count=1,
        dtype='float32',
        crs='EPSG:4326',
        transform=transform,
        compress='lzw',
        tiled=True
    ) as dst:
        dst.write(wind.astype('float32'), 1)
        dst.set_band_description(1, f'{component}10')
        dst.update_tags(1, units='m/s')
    
    print(f"✅ Generated: {output_path}")
    return output_path


def generate_test_suite(output_dir: Path) -> None:
    """Generate complete test suite of rasters"""
    print("🔨 Generating test rasters...")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Temperature
    generate_temperature_raster(output_dir / "t2m.tif")
    
    # Humidity
    generate_humidity_raster(output_dir / "rh.tif")
    
    # Wind components
    generate_wind_raster(output_dir / "u10.tif", component='u')
    generate_wind_raster(output_dir / "v10.tif", component='v')
    
    print(f"\n✅ Test suite complete: {output_dir}")
    print(f"   Files: {len(list(output_dir.glob('*.tif')))}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        output_path = Path(sys.argv[1])
    else:
        output_path = Path("/tmp/genhack/test_data")
    
    generate_test_suite(output_path)
    
    print("\nUsage:")
    print("  python tests/generate_mock_rasters.py [output_dir]")
