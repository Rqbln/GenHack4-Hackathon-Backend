"""
Quick validation script to inspect generated high-resolution temperature map
"""
import rasterio
import numpy as np
from pathlib import Path

output_dir = Path("outputs/highres_maps")
map_file = output_dir / "highres_temp_20200615.tif"

print(f"\n{'='*70}")
print("HIGH-RESOLUTION MAP VALIDATION")
print(f"{'='*70}\n")
print(f"File: {map_file.name}")
print(f"Size: {map_file.stat().st_size / 1024**2:.1f} MB\n")

with rasterio.open(map_file) as src:
    # Metadata
    print(f"{'='*70}")
    print("METADATA")
    print(f"{'='*70}")
    print(f"CRS:        {src.crs}")
    print(f"Dimensions: {src.width} x {src.height} pixels")
    print(f"Resolution: {src.res[0]:.2f} x {src.res[1]:.2f} meters")
    print(f"Bounds:     {src.bounds}")
    print(f"Data type:  {src.dtypes[0]}")
    print(f"NoData:     {src.nodata}\n")
    
    # Read data
    data = src.read(1)
    valid_data = data[~np.isnan(data)]
    
    print(f"{'='*70}")
    print("STATISTICS")
    print(f"{'='*70}")
    print(f"Total pixels:      {data.size:,}")
    print(f"Valid pixels:      {valid_data.size:,} ({valid_data.size/data.size*100:.1f}%)")
    print(f"NaN/NoData pixels: {np.isnan(data).sum():,} ({np.isnan(data).sum()/data.size*100:.1f}%)")
    print()
    print(f"Temperature Range:")
    print(f"  Min:      {valid_data.min():.2f}°C")
    print(f"  Max:      {valid_data.max():.2f}°C")
    print(f"  Mean:     {valid_data.mean():.2f}°C")
    print(f"  Median:   {np.median(valid_data):.2f}°C")
    print(f"  Std Dev:  {valid_data.std():.2f}°C")
    print()
    
    # Temperature distribution
    print(f"{'='*70}")
    print("TEMPERATURE DISTRIBUTION")
    print(f"{'='*70}")
    percentiles = [5, 25, 50, 75, 95]
    for p in percentiles:
        val = np.percentile(valid_data, p)
        print(f"  {p:2d}th percentile: {val:.2f}°C")
    
    print(f"\n{'='*70}")
    print("✓ VALIDATION COMPLETE")
    print(f"{'='*70}\n")
    print("The high-resolution temperature map for June 15, 2020 has been")
    print("successfully generated at 80m resolution for Sweden.")
    print(f"\nExpected temperature range for June in Sweden: 10-25°C")
    print(f"Actual range: {valid_data.min():.1f}°C to {valid_data.max():.1f}°C")
    
    if 8 <= valid_data.min() <= 15 and 20 <= valid_data.max() <= 35:
        print("✓ Temperature range is realistic for Swedish summer conditions.\n")
    else:
        print("⚠ Temperature range may be outside typical Swedish June values.\n")
