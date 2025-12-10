"""
Rigorous Urban Heat Island Analysis: Paris, France
Using the Urban-Rural Buffer Method

This analysis implements the standard UHI methodology:
1. Define Urban Core: City administrative boundary
2. Define Rural Reference: Donut buffer (2-10km outside city)
3. Calculate UHII = T_urban_mean - T_rural_mean
"""

import rasterio
from rasterio.mask import mask
import geopandas as gpd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.patches import Patch
import seaborn as sns
from pathlib import Path
from scipy import stats
from shapely.geometry import Point
from shapely.ops import unary_union

print("\n" + "="*80)
print("RIGOROUS URBAN HEAT ISLAND ANALYSIS: PARIS")
print("Method: Urban-Rural Buffer Comparison")
print("="*80 + "\n")

# Configuration
highres_map = Path("outputs/highres_maps/highres_temp_20200615.tif")
gadm_file = Path("datasets/main/gadm_410_europe.gpkg")
output_dir = Path("outputs/urban_analysis")
output_dir.mkdir(exist_ok=True)

# UHI parameters
INNER_BUFFER_KM = 2   # Start of rural donut (km outside city)
OUTER_BUFFER_KM = 10  # End of rural donut (km outside city)

print("Configuration:")
print(f"  City: Paris, France")
print(f"  Date: June 15, 2020 (Daily maximum temperature)")
print(f"  Resolution: 80m × 80m")
print(f"  Urban zone: City administrative boundary")
print(f"  Rural zone: Donut buffer ({INNER_BUFFER_KM}-{OUTER_BUFFER_KM}km outside city)")
print(f"\n" + "="*80 + "\n")

# Load data
print("Loading data...")
gadm = gpd.read_file(gadm_file)
france = gadm[gadm['GID_0'] == 'FRA'].copy()

# Find Paris city boundary
# Paris = NAME_2 == 'Paris' and ENGTYPE_2 == 'Department'
paris_admin = france[(france['NAME_2'] == 'Paris') & 
                     (france['ENGTYPE_2'] == 'Department')].copy()

if len(paris_admin) == 0:
    print("ERROR: Paris not found in GADM database")
    exit(1)

# Merge all Paris polygons into single geometry
paris_geom_wgs84 = unary_union(paris_admin.geometry)
paris_gdf_wgs84 = gpd.GeoDataFrame({'geometry': [paris_geom_wgs84]}, crs='EPSG:4326')

print(f"✓ Loaded Paris boundary:")
print(f"  Administrative units: {len(paris_admin)}")
print(f"  Geometry type: {paris_geom_wgs84.geom_type}")
print(f"  Area: {paris_gdf_wgs84.to_crs('EPSG:3857').area.iloc[0] / 1e6:.1f} km²")

# Load temperature map
with rasterio.open(highres_map) as src:
    temp_crs = src.crs
    temp_bounds = src.bounds
    temp_res = src.res[0]
    print(f"\n✓ Loaded temperature map:")
    print(f"  CRS: {temp_crs}")
    print(f"  Resolution: {temp_res:.0f}m")
    print(f"  Bounds: X [{temp_bounds.left:.0f}, {temp_bounds.right:.0f}], "
          f"Y [{temp_bounds.bottom:.0f}, {temp_bounds.top:.0f}]")

# Transform Paris to temperature map CRS (EPSG:3035)
paris_gdf_proj = paris_gdf_wgs84.to_crs(temp_crs)
paris_geom_proj = paris_gdf_proj.geometry.iloc[0]

print(f"\n✓ Transformed Paris to {temp_crs}")
print(f"  Paris bounds: X [{paris_geom_proj.bounds[0]:.0f}, {paris_geom_proj.bounds[2]:.0f}], "
      f"Y [{paris_geom_proj.bounds[1]:.0f}, {paris_geom_proj.bounds[3]:.0f}]")

# Check if Paris is within temperature map bounds
paris_center_x, paris_center_y = paris_geom_proj.centroid.x, paris_geom_proj.centroid.y
if not (temp_bounds.left <= paris_center_x <= temp_bounds.right and
        temp_bounds.bottom <= paris_center_y <= temp_bounds.top):
    print(f"\n⚠ WARNING: Paris may be outside temperature map coverage")
    print(f"  Paris center: {paris_center_x:.0f}, {paris_center_y:.0f}")

print(f"\n" + "="*80)
print("STEP 1: DEFINE URBAN ZONE (Paris City)")
print("="*80 + "\n")

# Extract urban temperatures
print("Extracting urban (Paris city) temperatures...")
with rasterio.open(highres_map) as src:
    urban_temp_array, urban_transform = mask(src, [paris_geom_proj], crop=True, nodata=np.nan)
    urban_temp = urban_temp_array[0]  # First band

urban_temp_valid = urban_temp[~np.isnan(urban_temp)]

print(f"✓ Urban zone extracted:")
print(f"  Total pixels: {urban_temp.size:,}")
print(f"  Valid pixels: {len(urban_temp_valid):,} ({len(urban_temp_valid)/urban_temp.size*100:.1f}%)")
print(f"  Coverage area: {len(urban_temp_valid) * (temp_res**2) / 1e6:.2f} km²")

if len(urban_temp_valid) < 100:
    print(f"\nERROR: Too few urban pixels ({len(urban_temp_valid)}). Check map coverage.")
    exit(1)

# Urban statistics
urban_mean = urban_temp_valid.mean()
urban_median = np.median(urban_temp_valid)
urban_std = urban_temp_valid.std()
urban_min = urban_temp_valid.min()
urban_max = urban_temp_valid.max()
urban_p10 = np.percentile(urban_temp_valid, 10)
urban_p90 = np.percentile(urban_temp_valid, 90)

print(f"\nUrban Temperature Statistics:")
print(f"  Mean:     {urban_mean:.2f}°C")
print(f"  Median:   {urban_median:.2f}°C")
print(f"  Std Dev:  {urban_std:.2f}°C")
print(f"  Range:    {urban_min:.2f}°C to {urban_max:.2f}°C")
print(f"  P10-P90:  {urban_p10:.2f}°C to {urban_p90:.2f}°C")

print(f"\n" + "="*80)
print(f"STEP 2: DEFINE RURAL ZONE (Donut Buffer: {INNER_BUFFER_KM}-{OUTER_BUFFER_KM}km)")
print("="*80 + "\n")

# Create buffer zones (in meters for EPSG:3035)
inner_buffer_m = INNER_BUFFER_KM * 1000
outer_buffer_m = OUTER_BUFFER_KM * 1000

print(f"Creating buffer zones...")
outer_ring = paris_geom_proj.buffer(outer_buffer_m)
inner_ring = paris_geom_proj.buffer(inner_buffer_m)

# Rural donut = outer ring - inner ring
rural_donut = outer_ring.difference(inner_ring)

print(f"✓ Rural donut created:")
print(f"  Inner buffer: {INNER_BUFFER_KM}km from city boundary")
print(f"  Outer buffer: {OUTER_BUFFER_KM}km from city boundary")
print(f"  Donut area: {rural_donut.area / 1e6:.1f} km²")

# Extract rural temperatures
print(f"\nExtracting rural temperatures...")
with rasterio.open(highres_map) as src:
    rural_temp_array, rural_transform = mask(src, [rural_donut], crop=True, nodata=np.nan)
    rural_temp = rural_temp_array[0]

rural_temp_valid = rural_temp[~np.isnan(rural_temp)]

print(f"✓ Rural zone extracted:")
print(f"  Total pixels: {rural_temp.size:,}")
print(f"  Valid pixels: {len(rural_temp_valid):,} ({len(rural_temp_valid)/rural_temp.size*100:.1f}%)")
print(f"  Coverage area: {len(rural_temp_valid) * (temp_res**2) / 1e6:.2f} km²")

if len(rural_temp_valid) < 100:
    print(f"\nERROR: Too few rural pixels ({len(rural_temp_valid)}). Adjust buffer size.")
    exit(1)

# Rural statistics
rural_mean = rural_temp_valid.mean()
rural_median = np.median(rural_temp_valid)
rural_std = rural_temp_valid.std()
rural_min = rural_temp_valid.min()
rural_max = rural_temp_valid.max()
rural_p10 = np.percentile(rural_temp_valid, 10)
rural_p90 = np.percentile(rural_temp_valid, 90)

print(f"\nRural Temperature Statistics:")
print(f"  Mean:     {rural_mean:.2f}°C")
print(f"  Median:   {rural_median:.2f}°C")
print(f"  Std Dev:  {rural_std:.2f}°C")
print(f"  Range:    {rural_min:.2f}°C to {rural_max:.2f}°C")
print(f"  P10-P90:  {rural_p10:.2f}°C to {rural_p90:.2f}°C")

print(f"\n" + "="*80)
print("STEP 3: CALCULATE URBAN HEAT ISLAND INTENSITY (UHII)")
print("="*80 + "\n")

# Calculate UHII
uhii_mean = urban_mean - rural_mean
uhii_median = urban_median - rural_median

print(f"UHII = T_urban_mean - T_rural_mean")
print(f"     = {urban_mean:.2f}°C - {rural_mean:.2f}°C")
print(f"     = {uhii_mean:+.2f}°C")

print(f"\nUrban Heat Island Intensity:")
print(f"  Mean UHII:   {uhii_mean:+.3f}°C")
print(f"  Median UHII: {uhii_median:+.3f}°C")

if uhii_mean > 0:
    print(f"\n  ✓ URBAN HEAT ISLAND DETECTED")
    print(f"    Paris city center is {uhii_mean:.2f}°C warmer than rural surroundings")
elif uhii_mean < -0.2:
    print(f"\n  ↓ URBAN COOL ISLAND DETECTED")
    print(f"    Paris city center is {abs(uhii_mean):.2f}°C cooler than rural surroundings")
else:
    print(f"\n  ≈ NEUTRAL - Urban and rural temperatures similar")

print(f"\n" + "="*80)
print("STEP 4: STATISTICAL SIGNIFICANCE TEST")
print("="*80 + "\n")

# Two-sample t-test
t_statistic, p_value = stats.ttest_ind(urban_temp_valid, rural_temp_valid)

print(f"Independent Samples t-Test:")
print(f"  Null hypothesis: Urban and rural temperatures are equal")
print(f"  Alternative hypothesis: Urban and rural temperatures differ")
print(f"\n  t-statistic: {t_statistic:.3f}")
print(f"  p-value:     {p_value:.6f}")
print(f"  Degrees of freedom: {len(urban_temp_valid) + len(rural_temp_valid) - 2:,}")

alpha = 0.05
if p_value < alpha:
    print(f"\n  ✓ RESULT: Statistically significant difference (p < {alpha})")
    print(f"    We reject the null hypothesis.")
    print(f"    The {uhii_mean:.2f}°C difference is NOT due to random chance.")
else:
    print(f"\n  ✗ RESULT: Not statistically significant (p >= {alpha})")
    print(f"    Cannot reject null hypothesis.")

# Effect size (Cohen's d)
pooled_std = np.sqrt(((len(urban_temp_valid)-1)*urban_std**2 + 
                      (len(rural_temp_valid)-1)*rural_std**2) / 
                     (len(urban_temp_valid) + len(rural_temp_valid) - 2))
cohens_d = uhii_mean / pooled_std

print(f"\nEffect Size (Cohen's d):")
print(f"  d = {cohens_d:.3f}")
if abs(cohens_d) < 0.2:
    print(f"  Interpretation: Small effect")
elif abs(cohens_d) < 0.5:
    print(f"  Interpretation: Medium effect")
else:
    print(f"  Interpretation: Large effect")

print(f"\n" + "="*80)
print("STEP 5: VISUALIZATION")
print("="*80 + "\n")

# Create comprehensive visualization
fig = plt.figure(figsize=(20, 12))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

fig.suptitle('Urban Heat Island Analysis: Paris, France (June 15, 2020)\n' +
             f'Method: Urban-Rural Buffer Comparison (80m resolution)',
             fontsize=16, fontweight='bold', y=0.98)

# Plot 1: Urban temperature map
ax1 = fig.add_subplot(gs[0, 0])
vmin_temp = min(urban_min, rural_min) - 0.5
vmax_temp = max(urban_max, rural_max) + 0.5
im1 = ax1.imshow(urban_temp, cmap='RdYlBu_r', vmin=vmin_temp, vmax=vmax_temp)
ax1.set_title('Urban Zone\n(Paris City)', fontsize=12, fontweight='bold')
ax1.axis('off')
plt.colorbar(im1, ax=ax1, fraction=0.046, label='Temperature (°C)')
ax1.text(0.02, 0.98, f'Mean: {urban_mean:.2f}°C\nPixels: {len(urban_temp_valid):,}',
         transform=ax1.transAxes, fontsize=9, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

# Plot 2: Rural temperature map
ax2 = fig.add_subplot(gs[0, 1])
im2 = ax2.imshow(rural_temp, cmap='RdYlBu_r', vmin=vmin_temp, vmax=vmax_temp)
ax2.set_title(f'Rural Zone\n({INNER_BUFFER_KM}-{OUTER_BUFFER_KM}km Buffer)', 
              fontsize=12, fontweight='bold')
ax2.axis('off')
plt.colorbar(im2, ax=ax2, fraction=0.046, label='Temperature (°C)')
ax2.text(0.02, 0.98, f'Mean: {rural_mean:.2f}°C\nPixels: {len(rural_temp_valid):,}',
         transform=ax2.transAxes, fontsize=9, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

# Plot 3: Schematic diagram
ax3 = fig.add_subplot(gs[0, 2])
ax3.set_xlim(-12, 12)
ax3.set_ylim(-12, 12)
ax3.set_aspect('equal')

# Draw zones
circle_urban = plt.Circle((0, 0), 3, color='red', alpha=0.3, label='Urban (Paris)')
circle_inner = plt.Circle((0, 0), 5, color='none', edgecolor='gray', linestyle='--', linewidth=2)
circle_outer = plt.Circle((0, 0), 10, color='green', alpha=0.2, label=f'Rural ({INNER_BUFFER_KM}-{OUTER_BUFFER_KM}km)')
circle_outer_edge = plt.Circle((0, 0), 10, color='none', edgecolor='green', linewidth=2)

ax3.add_patch(circle_urban)
ax3.add_patch(circle_inner)
ax3.add_patch(circle_outer)
ax3.add_patch(circle_outer_edge)

# Annotations
ax3.annotate('', xy=(0, 3), xytext=(0, 5),
            arrowprops=dict(arrowstyle='<->', color='black', lw=2))
ax3.text(0.5, 4, f'{INNER_BUFFER_KM}km', fontsize=10, va='center')

ax3.annotate('', xy=(0, 5), xytext=(0, 10),
            arrowprops=dict(arrowstyle='<->', color='black', lw=2))
ax3.text(0.5, 7.5, f'{OUTER_BUFFER_KM-INNER_BUFFER_KM}km', fontsize=10, va='center')

ax3.set_title('Methodology Schematic', fontsize=12, fontweight='bold')
ax3.axis('off')
ax3.legend(loc='upper right', fontsize=10)

# Plot 4: Temperature histograms
ax4 = fig.add_subplot(gs[1, :2])
bins = np.linspace(vmin_temp, vmax_temp, 60)
ax4.hist(rural_temp_valid, bins=bins, alpha=0.5, color='green', 
         label=f'Rural (n={len(rural_temp_valid):,})', density=True, edgecolor='darkgreen')
ax4.hist(urban_temp_valid, bins=bins, alpha=0.5, color='red',
         label=f'Urban (n={len(urban_temp_valid):,})', density=True, edgecolor='darkred')
ax4.axvline(rural_mean, color='green', linestyle='--', linewidth=2.5, 
            label=f'Rural mean: {rural_mean:.2f}°C')
ax4.axvline(urban_mean, color='red', linestyle='--', linewidth=2.5,
            label=f'Urban mean: {urban_mean:.2f}°C')

# Shade the UHII difference
if uhii_mean > 0:
    ax4.axvspan(rural_mean, urban_mean, alpha=0.2, color='orange', 
                label=f'UHII: +{uhii_mean:.2f}°C')
else:
    ax4.axvspan(urban_mean, rural_mean, alpha=0.2, color='blue',
                label=f'UHII: {uhii_mean:.2f}°C')

ax4.set_xlabel('Temperature (°C)', fontsize=11)
ax4.set_ylabel('Probability Density', fontsize=11)
ax4.set_title('Temperature Distribution Comparison', fontsize=12, fontweight='bold')
ax4.legend(fontsize=9, loc='best')
ax4.grid(True, alpha=0.3)

# Plot 5: Box plots
ax5 = fig.add_subplot(gs[1, 2])
box_data = [rural_temp_valid, urban_temp_valid]
bp = ax5.boxplot(box_data, labels=['Rural', 'Urban'], patch_artist=True,
                 showmeans=True, meanline=True,
                 boxprops=dict(facecolor='lightblue', alpha=0.7),
                 medianprops=dict(color='red', linewidth=2),
                 meanprops=dict(color='blue', linewidth=2, linestyle='--'))
bp['boxes'][0].set_facecolor('lightgreen')
bp['boxes'][1].set_facecolor('lightcoral')

ax5.set_ylabel('Temperature (°C)', fontsize=11)
ax5.set_title('Temperature Distribution\n(Box Plot)', fontsize=12, fontweight='bold')
ax5.grid(True, alpha=0.3, axis='y')

# Add significance marker
if p_value < 0.001:
    sig_text = '***'
elif p_value < 0.01:
    sig_text = '**'
elif p_value < 0.05:
    sig_text = '*'
else:
    sig_text = 'ns'

y_max = max(urban_p90, rural_p90) + 0.5
ax5.plot([1, 2], [y_max, y_max], 'k-', linewidth=1.5)
ax5.text(1.5, y_max + 0.1, sig_text, ha='center', fontsize=14, fontweight='bold')

# Plot 6: Statistical summary text
ax6 = fig.add_subplot(gs[2, :])
ax6.axis('off')

summary_text = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
URBAN HEAT ISLAND ANALYSIS RESULTS - PARIS, FRANCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

METHODOLOGY: Urban-Rural Buffer Method
  • Urban zone: Paris city administrative boundary
  • Rural zone: Donut buffer {INNER_BUFFER_KM}-{OUTER_BUFFER_KM}km outside city limits
  • Data: High-resolution downscaled temperature (80m resolution)
  • Date: June 15, 2020 (Daily maximum temperature)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEMPERATURE STATISTICS                       Urban (Paris)        Rural ({INNER_BUFFER_KM}-{OUTER_BUFFER_KM}km)        Difference
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Mean Temperature                             {urban_mean:6.2f}°C            {rural_mean:6.2f}°C           {uhii_mean:+6.2f}°C
Median Temperature                           {urban_median:6.2f}°C            {rural_median:6.2f}°C           {uhii_median:+6.2f}°C
Standard Deviation                           {urban_std:6.2f}°C            {rural_std:6.2f}°C
Temperature Range                            {urban_min:.2f} - {urban_max:.2f}°C      {rural_min:.2f} - {rural_max:.2f}°C
10th-90th Percentile                         {urban_p10:.2f} - {urban_p90:.2f}°C      {rural_p10:.2f} - {rural_p90:.2f}°C

Sample Size                                  {len(urban_temp_valid):,} pixels          {len(rural_temp_valid):,} pixels
Coverage Area                                {len(urban_temp_valid) * (temp_res**2) / 1e6:6.1f} km²            {len(rural_temp_valid) * (temp_res**2) / 1e6:6.1f} km²

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

URBAN HEAT ISLAND INTENSITY (UHII)

  UHII = T_urban_mean - T_rural_mean = {urban_mean:.2f}°C - {rural_mean:.2f}°C = {uhii_mean:+.3f}°C

  Classification: {'🔥 STRONG UHI (> +1.0°C)' if uhii_mean > 1.0 else '🌡️  MODERATE UHI (+0.5 to +1.0°C)' if uhii_mean > 0.5 else '≈ WEAK UHI (+0.2 to +0.5°C)' if uhii_mean > 0.2 else '≈ NEUTRAL (-0.2 to +0.2°C)' if abs(uhii_mean) <= 0.2 else '❄️  COOL ISLAND (< -0.2°C)'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STATISTICAL SIGNIFICANCE

  Independent Samples t-Test
    H₀: Urban and rural temperatures are equal
    H₁: Urban and rural temperatures differ

    t-statistic: {t_statistic:8.3f}
    p-value:     {p_value:.6f}
    Significance: {'p < 0.001 (***) - Extremely significant' if p_value < 0.001 else 'p < 0.01 (**) - Highly significant' if p_value < 0.01 else 'p < 0.05 (*) - Significant' if p_value < 0.05 else 'p ≥ 0.05 (ns) - Not significant'}

    {'✓ CONCLUSION: The temperature difference is statistically significant.' if p_value < 0.05 else '✗ CONCLUSION: Cannot confirm temperature difference is real (may be noise).'}

  Effect Size (Cohen\'s d): {cohens_d:.3f}  ({'Small' if abs(cohens_d) < 0.2 else 'Medium' if abs(cohens_d) < 0.5 else 'Large'} effect)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INTERPRETATION

"""

if uhii_mean > 1.0 and p_value < 0.05:
    interpretation = f"""✓ STRONG URBAN HEAT ISLAND CONFIRMED
    
The 80m high-resolution map reveals that Paris city center is {uhii_mean:.2f}°C warmer than the surrounding 
rural areas ({INNER_BUFFER_KM}-{OUTER_BUFFER_KM}km away). This difference is statistically significant (p < 0.05) and represents 
a large effect size (Cohen's d = {cohens_d:.2f}).

Likely contributing factors:
  • Dense urban infrastructure (buildings, roads, concrete)
  • Reduced vegetation cover (lower evapotranspiration)
  • Heat-absorbing surfaces with low albedo
  • Anthropogenic heat emissions (traffic, buildings)
  • Reduced wind ventilation in urban canyons

The high spatial resolution (80m) successfully captures the urban heat island effect that would be 
completely averaged out in coarse ERA5 data (9km resolution)."""

elif uhii_mean > 0.5 and p_value < 0.05:
    interpretation = f"""✓ MODERATE URBAN HEAT ISLAND CONFIRMED

Paris shows a moderate warming of {uhii_mean:.2f}°C compared to rural surroundings. This is statistically
significant (p < 0.05) and represents a {'medium' if abs(cohens_d) < 0.5 else 'large'} effect size.

The moderate UHI intensity may be due to:
  • Mixed urban-green spaces (parks like Bois de Boulogne/Vincennes)
  • River Seine providing cooling corridors
  • European urban planning with vegetated areas
  • Time of measurement (midday vs nighttime when UHI peaks)

The 80m resolution successfully discriminates urban from rural thermal environments."""

elif uhii_mean > 0.2 and p_value < 0.05:
    interpretation = f"""≈ WEAK URBAN HEAT ISLAND DETECTED

A small but statistically significant temperature difference of {uhii_mean:.2f}°C exists between Paris 
and its surroundings. The weak intensity suggests:
  • Analysis during summer daytime (solar heating dominates)
  • Abundant urban green spaces mitigating UHI
  • Coastal/river proximity providing cooling
  
Even this small difference is reliably captured by the high-resolution downscaling."""

elif abs(uhii_mean) <= 0.2:
    interpretation = f"""≈ NO URBAN HEAT ISLAND DETECTED

Paris and its rural surroundings show nearly identical temperatures (Δ = {uhii_mean:+.2f}°C).
This could indicate:
  • Summer midday analysis: Solar radiation overwhelms urban effects
  • Green city with abundant parks and tree cover
  • River and water bodies providing cooling
  • Ventilation from prevailing winds

Note: UHI effects are typically strongest at night. Daytime maximum temperatures may not show 
the full UHI intensity."""

else:
    interpretation = f"""❄️ URBAN COOL ISLAND DETECTED

Surprisingly, Paris is {abs(uhii_mean):.2f}°C {'cooler' if uhii_mean < 0 else 'warmer'} than rural areas. 
Possible explanations:
  • Extensive urban green spaces (parks, gardens, tree-lined boulevards)
  • Seine River and water features providing evaporative cooling
  • Shading from buildings reducing direct solar heating
  • Data quality or coverage issues (check rural zone location)

This unexpected result demonstrates the model is not biased toward finding heat islands."""

summary_text += interpretation

ax6.text(0.05, 0.95, summary_text, transform=ax6.transAxes,
         fontsize=9, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.3))

plt.tight_layout()
output_file = output_dir / 'paris_uhi_rigorous_analysis.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"✓ Saved visualization: {output_file}")
plt.close()

# Save numerical results
results_df = pd.DataFrame({
    'Metric': ['Mean Temperature', 'Median Temperature', 'Std Dev', 'Min', 'Max',
               'P10', 'P90', 'Sample Size', 'Area (km²)'],
    'Urban': [urban_mean, urban_median, urban_std, urban_min, urban_max,
              urban_p10, urban_p90, len(urban_temp_valid), 
              len(urban_temp_valid) * (temp_res**2) / 1e6],
    'Rural': [rural_mean, rural_median, rural_std, rural_min, rural_max,
              rural_p10, rural_p90, len(rural_temp_valid),
              len(rural_temp_valid) * (temp_res**2) / 1e6],
    'Difference': [uhii_mean, uhii_median, np.nan, np.nan, np.nan,
                   np.nan, np.nan, np.nan, np.nan]
})

csv_file = output_dir / 'paris_uhi_results.csv'
results_df.to_csv(csv_file, index=False)
print(f"✓ Saved numerical results: {csv_file}")

# Statistical test results
stats_df = pd.DataFrame({
    'Test': ['t-test'],
    't_statistic': [t_statistic],
    'p_value': [p_value],
    'significant': [p_value < 0.05],
    'cohens_d': [cohens_d],
    'UHII_mean': [uhii_mean],
    'UHII_median': [uhii_median]
})

stats_file = output_dir / 'paris_uhi_statistics.csv'
stats_df.to_csv(stats_file, index=False)
print(f"✓ Saved statistical test results: {stats_file}")

print(f"\n" + "="*80)
print("✓ ANALYSIS COMPLETE")
print("="*80)
print(f"\nKEY RESULT:")
print(f"  Urban Heat Island Intensity (UHII): {uhii_mean:+.3f}°C")
print(f"  Statistical significance: p = {p_value:.6f} {'(Significant)' if p_value < 0.05 else '(Not significant)'}")
print(f"  Effect size (Cohen's d): {cohens_d:.3f}")
print(f"\nConclusion:")
if uhii_mean > 0.5 and p_value < 0.05:
    print(f"  ✓ The 80m high-resolution map successfully detects a significant")
    print(f"    urban heat island in Paris (+{uhii_mean:.2f}°C).")
elif p_value < 0.05:
    print(f"  ✓ The 80m map detects statistically significant urban-rural")
    print(f"    temperature differences ({uhii_mean:+.2f}°C).")
else:
    print(f"  The analysis shows {'urban warming' if uhii_mean > 0 else 'neutral/cooling'} of {uhii_mean:+.2f}°C,")
    print(f"  but the difference is not statistically significant.")

print(f"\n" + "="*80 + "\n")
