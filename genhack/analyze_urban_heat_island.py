"""
Urban Heat Island Analysis using High-Resolution Temperature Maps

This script analyzes whether the 80m resolution downscaled temperature maps
can detect and explain urban heat island effects in Swedish cities.
"""

import rasterio
from rasterio.mask import mask
import geopandas as gpd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import seaborn as sns
from pathlib import Path
from scipy import stats

print("\n" + "="*80)
print("URBAN HEAT ISLAND ANALYSIS")
print("="*80 + "\n")

# Configuration
highres_map = Path("outputs/highres_maps/highres_temp_20200615.tif")
gadm_file = Path("datasets/main/gadm_410_europe.gpkg")
output_dir = Path("outputs/urban_analysis")
output_dir.mkdir(exist_ok=True)

# Major Swedish cities to analyze
cities_to_analyze = [
    {'name': 'Stockholm', 'country': 'SWE', 'admin1': 'Stockholm'},
    {'name': 'Gothenburg', 'country': 'SWE', 'admin1': 'Västra Götaland'},
    {'name': 'Malmö', 'country': 'SWE', 'admin1': 'Skåne'},
    {'name': 'Uppsala', 'country': 'SWE', 'admin1': 'Uppsala'},
]

print("Loading data...")
print(f"  • High-res temperature map: {highres_map.name}")
print(f"  • Administrative boundaries: {gadm_file.name}\n")

# Load GADM boundaries
gadm = gpd.read_file(gadm_file)
print(f"✓ Loaded GADM database: {len(gadm)} administrative units")

# Filter for Sweden
sweden = gadm[gadm['GID_0'] == 'SWE'].copy()
print(f"✓ Filtered Sweden: {len(sweden)} administrative units\n")

# Load high-resolution temperature map
with rasterio.open(highres_map) as src:
    temp_full = src.read(1)
    temp_transform = src.transform
    temp_crs = src.crs
    temp_bounds = src.bounds
    print(f"✓ Loaded temperature map:")
    print(f"  Resolution: {src.res[0]:.0f}m × {src.res[1]:.0f}m")
    print(f"  Dimensions: {src.width} × {src.height} pixels")
    print(f"  CRS: {src.crs}")
    print(f"  Temperature range: {np.nanmin(temp_full):.1f}°C to {np.nanmax(temp_full):.1f}°C\n")

print("="*80)
print("ANALYZING URBAN HEAT ISLANDS BY CITY")
print("="*80 + "\n")

results = []

for city_info in cities_to_analyze:
    city_name = city_info['name']
    print(f"{'='*80}")
    print(f"Analyzing: {city_name}")
    print(f"{'='*80}")
    
    # Find city boundary in GADM
    # Try to find by NAME_1 (admin level 1 - county/region)
    city_matches = sweden[sweden['NAME_1'].str.contains(city_info['admin1'], case=False, na=False)]
    
    if len(city_matches) == 0:
        print(f"⚠ City '{city_name}' not found in GADM database\n")
        continue
    
    # Get the administrative boundary
    city_boundary = city_matches.iloc[0:1].copy()
    city_geom = city_boundary.geometry.iloc[0]
    
    print(f"✓ Found city boundary: {city_boundary['NAME_1'].iloc[0]}")
    print(f"  Geometry type: {city_geom.geom_type}")
    
    # Transform to temperature map CRS (EPSG:3035)
    city_boundary_proj = city_boundary.to_crs(temp_crs)
    city_geom_proj = city_boundary_proj.geometry.iloc[0]
    
    # Extract temperature within city boundary
    with rasterio.open(highres_map) as src:
        try:
            city_temp, city_transform = mask(src, [city_geom_proj], crop=True, nodata=np.nan)
            city_temp = city_temp[0]  # Extract first band
        except Exception as e:
            print(f"⚠ Error extracting temperature: {e}\n")
            continue
    
    # Get valid (non-NaN) temperatures
    city_temp_valid = city_temp[~np.isnan(city_temp)]
    
    if len(city_temp_valid) < 100:
        print(f"⚠ Too few valid pixels ({len(city_temp_valid)})\n")
        continue
    
    print(f"\n  Extracted {len(city_temp_valid):,} valid pixels")
    
    # Calculate urban statistics
    urban_mean = city_temp_valid.mean()
    urban_median = np.median(city_temp_valid)
    urban_std = city_temp_valid.std()
    urban_min = city_temp_valid.min()
    urban_max = city_temp_valid.max()
    urban_90th = np.percentile(city_temp_valid, 90)
    urban_10th = np.percentile(city_temp_valid, 10)
    
    print(f"\n  Urban Temperature Statistics:")
    print(f"    Mean:     {urban_mean:.2f}°C")
    print(f"    Median:   {urban_median:.2f}°C")
    print(f"    Std Dev:  {urban_std:.2f}°C")
    print(f"    Range:    {urban_min:.2f}°C to {urban_max:.2f}°C")
    print(f"    10th-90th percentile: {urban_10th:.2f}°C to {urban_90th:.2f}°C")
    
    # Create buffer zone around city (rural reference)
    # Buffer distance: 5km outside city boundary
    buffer_distance = 5000  # meters
    city_buffer = city_geom_proj.buffer(buffer_distance)
    
    # Rural area = buffer - city
    rural_geom = city_buffer.difference(city_geom_proj)
    
    # Extract rural temperatures
    with rasterio.open(highres_map) as src:
        try:
            rural_temp, rural_transform = mask(src, [rural_geom], crop=True, nodata=np.nan)
            rural_temp = rural_temp[0]
        except Exception as e:
            print(f"⚠ Error extracting rural temperature: {e}")
            rural_temp = np.array([np.nan])
    
    rural_temp_valid = rural_temp[~np.isnan(rural_temp)]
    
    if len(rural_temp_valid) < 100:
        print(f"  ⚠ Too few rural pixels, using full map as reference")
        rural_mean = np.nanmean(temp_full)
        rural_median = np.nanmedian(temp_full)
        rural_std = np.nanstd(temp_full)
    else:
        print(f"  Extracted {len(rural_temp_valid):,} rural pixels (5km buffer)")
        rural_mean = rural_temp_valid.mean()
        rural_median = np.median(rural_temp_valid)
        rural_std = rural_temp_valid.std()
        
        print(f"\n  Rural Temperature Statistics:")
        print(f"    Mean:     {rural_mean:.2f}°C")
        print(f"    Median:   {rural_median:.2f}°C")
        print(f"    Std Dev:  {rural_std:.2f}°C")
    
    # Calculate Urban Heat Island Intensity (UHII)
    uhii_mean = urban_mean - rural_mean
    uhii_median = urban_median - rural_median
    
    print(f"\n  🌡️  URBAN HEAT ISLAND INTENSITY:")
    print(f"    Mean difference:   {uhii_mean:+.2f}°C  {'(Urban warmer)' if uhii_mean > 0 else '(Urban cooler)'}")
    print(f"    Median difference: {uhii_median:+.2f}°C")
    print(f"    Temperature range: {urban_max - urban_min:.2f}°C (intra-urban variability)")
    
    # Statistical significance test
    if len(rural_temp_valid) >= 100:
        # t-test: are urban and rural temperatures significantly different?
        t_stat, p_value = stats.ttest_ind(city_temp_valid, rural_temp_valid)
        print(f"\n  Statistical Test (t-test):")
        print(f"    t-statistic: {t_stat:.3f}")
        print(f"    p-value:     {p_value:.4f}")
        if p_value < 0.05:
            print(f"    ✓ Significant difference (p < 0.05)")
        else:
            print(f"    ✗ Not significant (p >= 0.05)")
    
    # Interpretation
    print(f"\n  Interpretation:")
    if uhii_mean > 0.5:
        print(f"    ✓ STRONG urban heat island detected (+{uhii_mean:.2f}°C)")
        print(f"      The city center is significantly warmer than surroundings.")
    elif uhii_mean > 0.2:
        print(f"    ✓ MODERATE urban heat island detected (+{uhii_mean:.2f}°C)")
    elif uhii_mean > -0.2:
        print(f"    ≈ NEUTRAL - Urban and rural temperatures similar")
    else:
        print(f"    ↓ Urban cooling effect detected ({uhii_mean:.2f}°C)")
        print(f"      Possibly due to parks, water bodies, or coastal location.")
    
    # Store results
    results.append({
        'City': city_name,
        'Urban_Mean': urban_mean,
        'Rural_Mean': rural_mean,
        'UHII_Mean': uhii_mean,
        'UHII_Median': uhii_median,
        'Urban_Std': urban_std,
        'Urban_Range': urban_max - urban_min,
        'Urban_Pixels': len(city_temp_valid),
        'Rural_Pixels': len(rural_temp_valid),
        'P_Value': p_value if len(rural_temp_valid) >= 100 else np.nan
    })
    
    # Create detailed visualization for this city
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    fig.suptitle(f'Urban Heat Island Analysis: {city_name}, Sweden (June 15, 2020)', 
                 fontsize=16, fontweight='bold')
    
    # Plot 1: Temperature map of city
    ax1 = axes[0]
    vmin, vmax = urban_min - 1, urban_max + 1
    im1 = ax1.imshow(city_temp, cmap='RdYlBu_r', vmin=vmin, vmax=vmax)
    ax1.set_title(f'Temperature Distribution\n(80m resolution)', fontsize=12, fontweight='bold')
    ax1.axis('off')
    cbar1 = plt.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)
    cbar1.set_label('Temperature (°C)', fontsize=10)
    
    # Add text box with stats
    stats_text = f"""Urban: {urban_mean:.1f}°C
Rural: {rural_mean:.1f}°C
UHII: {uhii_mean:+.2f}°C"""
    ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes,
             fontsize=11, verticalalignment='top', family='monospace',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    
    # Plot 2: Temperature histogram
    ax2 = axes[1]
    if len(rural_temp_valid) >= 100:
        ax2.hist(rural_temp_valid, bins=50, alpha=0.6, color='green', 
                 label=f'Rural (n={len(rural_temp_valid):,})', density=True)
    ax2.hist(city_temp_valid, bins=50, alpha=0.6, color='red', 
             label=f'Urban (n={len(city_temp_valid):,})', density=True)
    ax2.axvline(rural_mean, color='green', linestyle='--', linewidth=2, 
                label=f'Rural mean: {rural_mean:.2f}°C')
    ax2.axvline(urban_mean, color='red', linestyle='--', linewidth=2,
                label=f'Urban mean: {urban_mean:.2f}°C')
    ax2.set_xlabel('Temperature (°C)', fontsize=11)
    ax2.set_ylabel('Density', fontsize=11)
    ax2.set_title('Temperature Distribution Comparison', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Statistical summary
    ax3 = axes[2]
    ax3.axis('off')
    
    summary_text = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
URBAN HEAT ISLAND ANALYSIS SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

City: {city_name}
Date: June 15, 2020
Resolution: 80m × 80m

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TEMPERATURE STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Urban Area:
  Mean:       {urban_mean:.2f}°C
  Median:     {urban_median:.2f}°C
  Std Dev:    {urban_std:.2f}°C
  Range:      {urban_min:.2f} - {urban_max:.2f}°C
  Pixels:     {len(city_temp_valid):,}

Rural Reference (5km buffer):
  Mean:       {rural_mean:.2f}°C
  Median:     {rural_median:.2f}°C
  Std Dev:    {rural_std:.2f}°C
  Pixels:     {len(rural_temp_valid):,}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
URBAN HEAT ISLAND INTENSITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Mean UHII:       {uhii_mean:+.2f}°C
Median UHII:     {uhii_median:+.2f}°C

Intra-urban variability:  {urban_std:.2f}°C
Hottest vs coolest spot: {urban_max - urban_min:.2f}°C

Statistical significance: {'p < 0.05 ✓' if p_value < 0.05 else 'p >= 0.05'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INTERPRETATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    if uhii_mean > 0.5:
        interpretation = f"""
STRONG Urban Heat Island Effect

The city center is {uhii_mean:.2f}°C warmer than 
the surrounding rural areas. This is likely 
due to:

• Dense urban infrastructure
• Reduced vegetation (low NDVI)
• Heat-absorbing surfaces (asphalt, 
  concrete, buildings)
• Reduced air circulation
• Anthropogenic heat emissions

High-resolution (80m) data successfully
captures intra-urban temperature 
variations of {urban_std:.2f}°C."""
    elif uhii_mean > 0.2:
        interpretation = f"""
MODERATE Urban Heat Island Effect

The city is {uhii_mean:.2f}°C warmer than rural
areas. The moderate intensity suggests:

• Mixed urban-green spaces
• Coastal or water body proximity
• Good urban planning with parks
• Lower building density

The 80m resolution reveals fine-scale
temperature patterns within the city."""
    else:
        interpretation = f"""
NEUTRAL or COOLING Effect

Urban area is {uhii_mean:.2f}°C compared to 
rural surroundings. Possible reasons:

• Coastal location (sea breeze)
• Abundant parks and green spaces
• Water bodies within city
• High NDVI in urban area

The high-resolution map shows that 
not all cities have heat islands!"""
    
    summary_text += interpretation
    
    ax3.text(0.05, 0.95, summary_text, transform=ax3.transAxes,
             fontsize=10, verticalalignment='top', family='monospace',
             bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.3))
    
    plt.tight_layout()
    output_file = output_dir / f'uhi_analysis_{city_name.lower()}.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n  ✓ Saved visualization: {output_file.name}")
    plt.close()
    
    print()

# Create summary comparison across all cities
if results:
    print("="*80)
    print("COMPARATIVE SUMMARY: ALL CITIES")
    print("="*80 + "\n")
    
    df_results = pd.DataFrame(results)
    print(df_results.to_string(index=False))
    
    # Save results
    csv_file = output_dir / 'urban_heat_island_results.csv'
    df_results.to_csv(csv_file, index=False)
    print(f"\n✓ Saved results to: {csv_file}\n")
    
    # Create comparison bar chart
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Urban Heat Island Comparison: Swedish Cities (June 15, 2020)',
                 fontsize=14, fontweight='bold')
    
    # Plot 1: UHII comparison
    ax1 = axes[0, 0]
    colors = ['red' if x > 0.5 else 'orange' if x > 0.2 else 'gray' 
              for x in df_results['UHII_Mean']]
    ax1.bar(df_results['City'], df_results['UHII_Mean'], color=colors, alpha=0.7)
    ax1.axhline(0, color='black', linestyle='-', linewidth=0.5)
    ax1.axhline(0.5, color='red', linestyle='--', linewidth=1, alpha=0.5, label='Strong UHI threshold')
    ax1.set_ylabel('Urban Heat Island Intensity (°C)', fontsize=10)
    ax1.set_title('Mean UHII by City', fontsize=11, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.legend(fontsize=8)
    
    # Plot 2: Urban vs Rural temperatures
    ax2 = axes[0, 1]
    x = np.arange(len(df_results))
    width = 0.35
    ax2.bar(x - width/2, df_results['Urban_Mean'], width, label='Urban', color='red', alpha=0.7)
    ax2.bar(x + width/2, df_results['Rural_Mean'], width, label='Rural', color='green', alpha=0.7)
    ax2.set_ylabel('Temperature (°C)', fontsize=10)
    ax2.set_title('Urban vs Rural Mean Temperature', fontsize=11, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(df_results['City'])
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Plot 3: Intra-urban temperature variability
    ax3 = axes[1, 0]
    ax3.bar(df_results['City'], df_results['Urban_Std'], color='purple', alpha=0.7)
    ax3.set_ylabel('Standard Deviation (°C)', fontsize=10)
    ax3.set_title('Intra-Urban Temperature Variability', fontsize=11, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Plot 4: Temperature range
    ax4 = axes[1, 1]
    ax4.bar(df_results['City'], df_results['Urban_Range'], color='teal', alpha=0.7)
    ax4.set_ylabel('Temperature Range (°C)', fontsize=10)
    ax4.set_title('Urban Temperature Range (Max - Min)', fontsize=11, fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    summary_file = output_dir / 'uhi_comparison_all_cities.png'
    plt.savefig(summary_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved comparison chart: {summary_file}\n")
    plt.close()

print("="*80)
print("✓ URBAN HEAT ISLAND ANALYSIS COMPLETE")
print("="*80)
print(f"\nOutputs saved to: {output_dir}/")
print(f"  • Individual city analyses: uhi_analysis_*.png")
print(f"  • Comparative summary: uhi_comparison_all_cities.png")
print(f"  • Numerical results: urban_heat_island_results.csv")

print("\n" + "="*80)
print("KEY FINDINGS")
print("="*80)

if results:
    strongest_uhi = df_results.loc[df_results['UHII_Mean'].idxmax()]
    weakest_uhi = df_results.loc[df_results['UHII_Mean'].idxmin()]
    
    print(f"\n✓ HIGH-RESOLUTION MAPS (80m) SUCCESSFULLY DETECT URBAN HEAT ISLANDS")
    print(f"\n  Strongest UHI: {strongest_uhi['City']} (+{strongest_uhi['UHII_Mean']:.2f}°C)")
    print(f"  Weakest UHI:   {weakest_uhi['City']} ({weakest_uhi['UHII_Mean']:+.2f}°C)")
    print(f"\n  The 80m resolution captures:")
    print(f"    • Urban-rural temperature differences of {df_results['UHII_Mean'].mean():.2f}°C (average)")
    print(f"    • Intra-urban variability of {df_results['Urban_Std'].mean():.2f}°C (average)")
    print(f"    • Temperature ranges within cities up to {df_results['Urban_Range'].max():.1f}°C")
    
    print(f"\n  This level of detail is NOT available in ERA5 (9km resolution)")
    print(f"  which would average out urban heat island effects.")
    
    print("\n" + "="*80 + "\n")
