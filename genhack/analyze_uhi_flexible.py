#!/usr/bin/env python3
"""
Flexible Urban Heat Island Analysis Script

Analyze UHI effects for any city, country, and time period.
Uses urban-rural buffer methodology with statistical validation.

Usage:
    python analyze_uhi_flexible.py --city "Paris" --country FR --date 2020-06-15
    python analyze_uhi_flexible.py --city "Berlin" --country DE --date 2021-07-20 --inner-buffer 3 --outer-buffer 12
    python analyze_uhi_flexible.py --city "Stockholm" --country SE --start 2020-06-01 --end 2020-06-30
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from shapely.geometry import Point
import warnings
warnings.filterwarnings('ignore')


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Flexible Urban Heat Island Analysis for any city/country/period',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single date analysis
  python analyze_uhi_flexible.py --city "Paris" --country FR --date 2020-06-15
  
  # Custom buffer distances
  python analyze_uhi_flexible.py --city "Berlin" --country DE --date 2021-07-20 --inner-buffer 3 --outer-buffer 12
  
  # Time series analysis (multiple dates)
  python analyze_uhi_flexible.py --city "Madrid" --country ES --start 2020-06-01 --end 2020-06-30
  
  # Specify custom GADM name if city name doesn't match
  python analyze_uhi_flexible.py --city "New York" --country US --gadm-name "New York City" --date 2020-07-15
        """
    )
    
    # Required arguments
    parser.add_argument('--city', required=True, help='City name (e.g., "Paris", "Berlin", "Stockholm")')
    parser.add_argument('--country', required=True, help='ISO 3166-1 Alpha-2 country code (e.g., FR, DE, SE)')
    
    # Date arguments (either --date or --start/--end)
    date_group = parser.add_mutually_exclusive_group(required=True)
    date_group.add_argument('--date', help='Single date for analysis (YYYY-MM-DD)')
    date_group.add_argument('--start', help='Start date for time series (YYYY-MM-DD)')
    
    parser.add_argument('--end', help='End date for time series (YYYY-MM-DD, required if --start is used)')
    
    # Optional arguments
    parser.add_argument('--gadm-name', help='Custom GADM city name if different from --city')
    parser.add_argument('--inner-buffer', type=float, default=2.0, 
                        help='Inner buffer distance in km (default: 2.0)')
    parser.add_argument('--outer-buffer', type=float, default=10.0,
                        help='Outer buffer distance in km (default: 10.0)')
    parser.add_argument('--data-dir', default='datasets/main',
                        help='Path to data directory (default: datasets/main)')
    parser.add_argument('--output-dir', default='outputs/urban_analysis',
                        help='Path to output directory (default: outputs/urban_analysis)')
    parser.add_argument('--highres-dir', default='outputs/highres_maps',
                        help='Path to high-res temperature maps (default: outputs/highres_maps)')
    parser.add_argument('--generate-maps', action='store_true',
                        help='Generate high-res maps if they don\'t exist')
    parser.add_argument('--training-start', help='Training period start (default: first day of analysis month)')
    parser.add_argument('--training-end', help='Training period end (default: day before analysis start)')
    
    args = parser.parse_args()
    
    # Validation
    if args.start and not args.end:
        parser.error('--end is required when using --start')
    
    return args


def load_city_boundary(gadm_path: Path, city_name: str, country_code: str) -> gpd.GeoDataFrame:
    """
    Load city boundary from GADM database.
    
    Args:
        gadm_path: Path to GADM GeoPackage file
        city_name: Name of the city
        country_code: ISO country code (2 or 3 letter)
        
    Returns:
        GeoDataFrame with city boundary in EPSG:3035
    """
    print(f"\n{'='*60}")
    print(f"LOADING CITY BOUNDARY: {city_name}, {country_code}")
    print(f"{'='*60}")
    
    # Map 2-letter to 3-letter ISO codes
    country_map = {
        'FR': 'FRA', 'DE': 'DEU', 'SE': 'SWE', 'NO': 'NOR', 'FI': 'FIN',
        'ES': 'ESP', 'IT': 'ITA', 'UK': 'GBR', 'GB': 'GBR', 'PL': 'POL',
        'NL': 'NLD', 'BE': 'BEL', 'AT': 'AUT', 'CH': 'CHE', 'DK': 'DNK',
        'PT': 'PRT', 'GR': 'GRC', 'CZ': 'CZE', 'RO': 'ROU', 'HU': 'HUN'
    }
    
    # Convert 2-letter to 3-letter if needed
    if len(country_code) == 2:
        country_code_3 = country_map.get(country_code.upper(), country_code.upper())
    else:
        country_code_3 = country_code.upper()
    
    # Load GADM data
    gdf = gpd.read_file(gadm_path)
    gdf_country = gdf[gdf['GID_0'] == country_code_3].copy()
    
    if len(gdf_country) == 0:
        print(f"ERROR: Country code '{country_code}' (ISO3: {country_code_3}) not found in GADM database")
        print(f"\nAvailable country codes: {sorted(gdf['GID_0'].unique())}")
        sys.exit(1)
    
    # Search for city by name in NAME_1 (primary administrative division)
    city_matches = gdf_country[gdf_country['NAME_1'].str.contains(city_name, case=False, na=False)]
    
    if len(city_matches) == 0:
        print(f"ERROR: City '{city_name}' not found in GADM database for country {country_code}")
        print(f"\nAvailable regions in {country_code}:")
        available = gdf_country['NAME_1'].unique()[:20]
        for region in available:
            print(f"  - {region}")
        sys.exit(1)
    
    # If multiple matches, use union of all
    if len(city_matches) > 1:
        print(f"Found {len(city_matches)} regions matching '{city_name}':")
        for idx, row in city_matches.iterrows():
            print(f"  - {row['NAME_1']}")
        print(f"Using union of all matched regions")
        city_boundary = city_matches.dissolve()
    else:
        city_boundary = city_matches.copy()
    
    # Transform to EPSG:3035
    if city_boundary.crs != 'EPSG:3035':
        city_boundary = city_boundary.to_crs('EPSG:3035')
    
    area_km2 = city_boundary.geometry.area.sum() / 1e6
    bounds = city_boundary.total_bounds
    
    print(f"✓ City boundary loaded successfully")
    print(f"  Area: {area_km2:.1f} km²")
    print(f"  Bounds (EPSG:3035): {bounds}")
    
    return city_boundary


def create_buffer_zones(city_boundary: gpd.GeoDataFrame, inner_km: float, outer_km: float):
    """
    Create urban and rural buffer zones.
    
    Args:
        city_boundary: City boundary geometry
        inner_km: Inner buffer distance in km
        outer_km: Outer buffer distance in km
        
    Returns:
        Tuple of (urban_zone, rural_zone) as GeoDataFrames
    """
    print(f"\n{'='*60}")
    print(f"CREATING BUFFER ZONES")
    print(f"{'='*60}")
    
    # Urban zone = city boundary
    urban_zone = city_boundary.copy()
    
    # Rural zone = donut buffer (outer - inner)
    inner_buffer = city_boundary.buffer(inner_km * 1000)  # km to meters
    outer_buffer = city_boundary.buffer(outer_km * 1000)
    rural_zone = gpd.GeoDataFrame(geometry=outer_buffer.difference(inner_buffer), crs='EPSG:3035')
    
    urban_area = urban_zone.geometry.area.sum() / 1e6
    rural_area = rural_zone.geometry.area.sum() / 1e6
    
    print(f"✓ Buffer zones created")
    print(f"  Urban zone: {urban_area:.1f} km² (city boundary)")
    print(f"  Rural zone: {rural_area:.1f} km² (donut buffer {inner_km}-{outer_km} km)")
    
    return urban_zone, rural_zone


def extract_temperatures(raster_path: Path, zone_gdf: gpd.GeoDataFrame, zone_name: str):
    """
    Extract temperature values from raster within a zone.
    
    Args:
        raster_path: Path to high-res temperature GeoTIFF
        zone_gdf: Zone geometry (GeoDataFrame)
        zone_name: Name of zone for logging
        
    Returns:
        Numpy array of temperature values
    """
    with rasterio.open(raster_path) as src:
        # Check if zone intersects with raster
        raster_bounds = src.bounds
        zone_bounds = zone_gdf.total_bounds
        
        # Simple bounds check
        if (zone_bounds[2] < raster_bounds.left or 
            zone_bounds[0] > raster_bounds.right or
            zone_bounds[3] < raster_bounds.bottom or
            zone_bounds[1] > raster_bounds.top):
            print(f"WARNING: {zone_name} is outside the temperature map extent")
            return np.array([])
        
        # Mask and extract
        out_image, out_transform = mask(src, zone_gdf.geometry, crop=True, nodata=src.nodata)
        temps = out_image[0]
        
        # Filter valid values
        if src.nodata is not None:
            valid_temps = temps[(temps != src.nodata) & ~np.isnan(temps)]
        else:
            valid_temps = temps[~np.isnan(temps)]
        
        # Additional filter: remove unrealistic temperatures (< 5°C or > 50°C for daily max)
        # This filters out ocean/water pixels (often 0°C) and bad data
        realistic_temps = valid_temps[(valid_temps >= 5) & (valid_temps <= 50)]
        
        if len(realistic_temps) < len(valid_temps) * 0.5:
            print(f"WARNING: {zone_name} - filtered out {len(valid_temps) - len(realistic_temps):,} unrealistic temperature values")
        
        return realistic_temps


def calculate_uhi_metrics(urban_temps: np.ndarray, rural_temps: np.ndarray):
    """
    Calculate UHI metrics and statistical tests.
    
    Args:
        urban_temps: Array of urban temperatures
        rural_temps: Array of rural temperatures
        
    Returns:
        Dictionary with UHI metrics and statistics
    """
    print(f"\n{'='*60}")
    print(f"CALCULATING UHI METRICS")
    print(f"{'='*60}")
    
    # Basic statistics
    urban_mean = np.mean(urban_temps)
    urban_std = np.std(urban_temps)
    rural_mean = np.mean(rural_temps)
    rural_std = np.std(rural_temps)
    
    # UHII (Urban Heat Island Intensity)
    uhii = urban_mean - rural_mean
    
    # Statistical tests
    t_stat, p_value = stats.ttest_ind(urban_temps, rural_temps)
    
    # Cohen's d effect size
    pooled_std = np.sqrt((urban_std**2 + rural_std**2) / 2)
    cohens_d = (urban_mean - rural_mean) / pooled_std
    
    # Determine significance
    is_significant = p_value < 0.05
    
    results = {
        'urban_mean': urban_mean,
        'urban_std': urban_std,
        'urban_n': len(urban_temps),
        'rural_mean': rural_mean,
        'rural_std': rural_std,
        'rural_n': len(rural_temps),
        'uhii': uhii,
        't_statistic': t_stat,
        'p_value': p_value,
        'cohens_d': cohens_d,
        'is_significant': is_significant
    }
    
    print(f"Urban zone:  n={results['urban_n']:,} pixels, mean={urban_mean:.2f}°C, std={urban_std:.2f}°C")
    print(f"Rural zone:  n={results['rural_n']:,} pixels, mean={rural_mean:.2f}°C, std={rural_std:.2f}°C")
    print(f"UHII: {uhii:+.3f}°C")
    print(f"t-test: t={t_stat:.3f}, p={p_value:.2e}, {'Significant' if is_significant else 'Not significant'}")
    print(f"Cohen's d: {cohens_d:.3f}")
    
    return results


def create_visualization(raster_path: Path, urban_zone, rural_zone, urban_temps, rural_temps,
                        results: dict, city_name: str, date_str: str, output_path: Path):
    """
    Create comprehensive UHI visualization.
    
    Args:
        raster_path: Path to temperature raster
        urban_zone: Urban zone GeoDataFrame
        rural_zone: Rural zone GeoDataFrame
        urban_temps: Urban temperature array
        rural_temps: Rural temperature array
        results: Dictionary with UHI metrics
        city_name: Name of city
        date_str: Date string for title
        output_path: Path to save figure
    """
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # Load full temperature map
    with rasterio.open(raster_path) as src:
        temp_data = src.read(1)
        temp_data = np.where(temp_data == src.nodata, np.nan, temp_data)
        extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]
    
    # 1. Urban zone map
    ax1 = fig.add_subplot(gs[0, 0])
    im1 = ax1.imshow(temp_data, extent=extent, cmap='RdYlBu_r', origin='upper')
    urban_zone.boundary.plot(ax=ax1, color='red', linewidth=2)
    ax1.set_title(f'Urban Zone\n{city_name}', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Easting (m)')
    ax1.set_ylabel('Northing (m)')
    plt.colorbar(im1, ax=ax1, label='Temperature (°C)', fraction=0.046)
    
    # 2. Rural zone map
    ax2 = fig.add_subplot(gs[0, 1])
    im2 = ax2.imshow(temp_data, extent=extent, cmap='RdYlBu_r', origin='upper')
    rural_zone.boundary.plot(ax=ax2, color='blue', linewidth=2)
    ax2.set_title(f'Rural Zone (Donut Buffer)', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Easting (m)')
    ax2.set_ylabel('Northing (m)')
    plt.colorbar(im2, ax=ax2, label='Temperature (°C)', fraction=0.046)
    
    # 3. Schematic diagram
    ax3 = fig.add_subplot(gs[0, 2])
    urban_zone.plot(ax=ax3, color='red', alpha=0.5, label='Urban')
    rural_zone.plot(ax=ax3, color='blue', alpha=0.3, label='Rural')
    ax3.set_title('Zone Layout', fontsize=12, fontweight='bold')
    ax3.legend(loc='upper right')
    ax3.set_xlabel('Easting (m)')
    ax3.set_ylabel('Northing (m)')
    ax3.set_aspect('equal')
    
    # 4. Temperature histograms
    ax4 = fig.add_subplot(gs[1, :2])
    bins = np.linspace(min(urban_temps.min(), rural_temps.min()),
                       max(urban_temps.max(), rural_temps.max()), 50)
    ax4.hist(rural_temps, bins=bins, alpha=0.5, color='blue', label='Rural', density=True)
    ax4.hist(urban_temps, bins=bins, alpha=0.5, color='red', label='Urban', density=True)
    ax4.axvline(results['rural_mean'], color='blue', linestyle='--', linewidth=2, label=f'Rural Mean: {results["rural_mean"]:.2f}°C')
    ax4.axvline(results['urban_mean'], color='red', linestyle='--', linewidth=2, label=f'Urban Mean: {results["urban_mean"]:.2f}°C')
    ax4.set_xlabel('Temperature (°C)', fontsize=11)
    ax4.set_ylabel('Density', fontsize=11)
    ax4.set_title('Temperature Distribution', fontsize=12, fontweight='bold')
    ax4.legend()
    ax4.grid(alpha=0.3)
    
    # 5. Box plots
    ax5 = fig.add_subplot(gs[1, 2])
    bp = ax5.boxplot([rural_temps, urban_temps], labels=['Rural', 'Urban'],
                      patch_artist=True, widths=0.6)
    bp['boxes'][0].set_facecolor('blue')
    bp['boxes'][1].set_facecolor('red')
    ax5.set_ylabel('Temperature (°C)', fontsize=11)
    ax5.set_title('Temperature Range', fontsize=12, fontweight='bold')
    ax5.grid(alpha=0.3, axis='y')
    
    # 6. Statistical summary
    ax6 = fig.add_subplot(gs[2, :])
    ax6.axis('off')
    
    summary_text = f"""
    URBAN HEAT ISLAND ANALYSIS: {city_name.upper()} - {date_str}
    {'='*90}
    
    CONFIGURATION:
      • Resolution: 80m × 80m
      • Rural buffer: {results.get('inner_buffer', 2):.1f} - {results.get('outer_buffer', 10):.1f} km from city boundary
    
    ZONE STATISTICS:
      Urban Zone:   {results['urban_n']:,} valid pixels  |  Mean: {results['urban_mean']:.2f}°C  |  Std: {results['urban_std']:.2f}°C
      Rural Zone:   {results['rural_n']:,} valid pixels  |  Mean: {results['rural_mean']:.2f}°C  |  Std: {results['rural_std']:.2f}°C
    
    URBAN HEAT ISLAND INTENSITY (UHII):
      UHII = T_urban_mean - T_rural_mean = {results['uhii']:+.3f}°C
      {'Urban area is WARMER' if results['uhii'] > 0 else 'Urban area is COOLER'}
    
    STATISTICAL SIGNIFICANCE:
      Independent samples t-test:  t = {results['t_statistic']:.3f},  p = {results['p_value']:.2e}
      Result: {'STATISTICALLY SIGNIFICANT' if results['is_significant'] else 'NOT SIGNIFICANT'} (α = 0.05)
      Effect size (Cohen's d): {results['cohens_d']:.3f} ({'Small' if abs(results['cohens_d']) < 0.5 else 'Medium' if abs(results['cohens_d']) < 0.8 else 'Large'} effect)
    
    INTERPRETATION:
      {'The urban heat island effect is statistically significant but weak. This is typical for daytime summer conditions.' if results['is_significant'] and abs(results['uhii']) < 0.5 else 'The urban heat island effect is clearly detected.' if results['is_significant'] else 'No significant urban heat island effect detected.'}
    """
    
    ax6.text(0.05, 0.5, summary_text, fontsize=10, family='monospace',
             verticalalignment='center', transform=ax6.transAxes)
    
    plt.suptitle(f'Urban Heat Island Analysis: {city_name} ({date_str})', 
                 fontsize=16, fontweight='bold', y=0.98)
    
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n✓ Visualization saved: {output_path}")


def generate_highres_maps(args, dates):
    """
    Generate high-resolution temperature maps if they don't exist.
    
    Args:
        args: Command line arguments
        dates: List of dates to generate
    """
    import subprocess
    from dateutil.relativedelta import relativedelta
    
    print(f"\n{'='*60}")
    print(f"GENERATING HIGH-RESOLUTION TEMPERATURE MAPS")
    print(f"{'='*60}")
    
    # Determine training period (default: train on previous month)
    inference_start = dates[0]
    inference_end = dates[-1]
    
    if args.training_start and args.training_end:
        training_start = args.training_start
        training_end = args.training_end
    else:
        # Default: train on the month before inference period
        train_end = inference_start - timedelta(days=1)
        train_start = train_end.replace(day=1)  # First day of previous month
        training_start = train_start.strftime('%Y-%m-%d')
        training_end = train_end.strftime('%Y-%m-%d')
    
    inference_start_str = inference_start.strftime('%Y-%m-%d')
    inference_end_str = inference_end.strftime('%Y-%m-%d')
    
    print(f"Training period: {training_start} to {training_end}")
    print(f"Inference period: {inference_start_str} to {inference_end_str}")
    
    cmd = [
        'python', 'src/main.py',
        '--data-dir', args.data_dir,
        '--output-dir', 'outputs',
        '--country', args.country,
        '--start', training_start,
        '--end', training_end,
        '--generate-maps',
        '--inference-start', inference_start_str,
        '--inference-end', inference_end_str
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False, text=True)
    
    if result.returncode != 0:
        print(f"ERROR: Failed to generate high-resolution maps")
        sys.exit(1)
    
    print(f"✓ High-resolution maps generated successfully")


def main():
    args = parse_arguments()
    
    # Setup paths
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    highres_dir = Path(args.highres_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    gadm_path = data_dir / 'gadm_410_europe.gpkg'
    
    # Parse dates
    if args.date:
        dates = [datetime.strptime(args.date, '%Y-%m-%d')]
    else:
        start_date = datetime.strptime(args.start, '%Y-%m-%d')
        end_date = datetime.strptime(args.end, '%Y-%m-%d')
        dates = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
    
    print(f"\n{'='*60}")
    print(f"FLEXIBLE UHI ANALYSIS")
    print(f"{'='*60}")
    print(f"City: {args.city}")
    print(f"Country: {args.country}")
    print(f"Date(s): {dates[0].strftime('%Y-%m-%d')} to {dates[-1].strftime('%Y-%m-%d')} ({len(dates)} days)")
    print(f"Buffer: {args.inner_buffer} - {args.outer_buffer} km")
    
    # Check if high-res maps exist
    missing_dates = []
    for date in dates:
        raster_path = highres_dir / f"highres_temp_{date.strftime('%Y%m%d')}.tif"
        if not raster_path.exists():
            missing_dates.append(date)
    
    if missing_dates:
        if args.generate_maps:
            generate_highres_maps(args, dates)
        else:
            print(f"\nERROR: Missing high-resolution maps for {len(missing_dates)} dates")
            print(f"First missing: {missing_dates[0].strftime('%Y-%m-%d')}")
            print(f"Use --generate-maps flag to create them automatically")
            sys.exit(1)
    
    # Load city boundary
    city_name_for_gadm = args.gadm_name if args.gadm_name else args.city
    city_boundary = load_city_boundary(gadm_path, city_name_for_gadm, args.country)
    
    # Create buffer zones
    urban_zone, rural_zone = create_buffer_zones(city_boundary, args.inner_buffer, args.outer_buffer)
    
    # Process each date
    all_results = []
    
    for date in dates:
        date_str = date.strftime('%Y-%m-%d')
        print(f"\n{'='*60}")
        print(f"PROCESSING DATE: {date_str}")
        print(f"{'='*60}")
        
        raster_path = highres_dir / f"highres_temp_{date.strftime('%Y%m%d')}.tif"
        
        if not raster_path.exists():
            print(f"WARNING: Skipping {date_str} - file not found: {raster_path}")
            continue
        
        # Extract temperatures
        print(f"\nExtracting temperatures...")
        urban_temps = extract_temperatures(raster_path, urban_zone, 'Urban')
        rural_temps = extract_temperatures(raster_path, rural_zone, 'Rural')
        
        if len(urban_temps) == 0 or len(rural_temps) == 0:
            print(f"WARNING: No valid temperatures extracted for {date_str}")
            continue
        
        # Calculate metrics
        results = calculate_uhi_metrics(urban_temps, rural_temps)
        results['date'] = date_str
        results['city'] = args.city
        results['country'] = args.country
        results['inner_buffer'] = args.inner_buffer
        results['outer_buffer'] = args.outer_buffer
        
        all_results.append(results)
        
        # Create visualization
        output_path = output_dir / f"{args.city.lower().replace(' ', '_')}_{args.country.lower()}_uhi_{date.strftime('%Y%m%d')}.png"
        create_visualization(raster_path, urban_zone, rural_zone, urban_temps, rural_temps,
                           results, args.city, date_str, output_path)
    
    # Save results to CSV
    if all_results:
        df_results = pd.DataFrame(all_results)
        csv_path = output_dir / f"{args.city.lower().replace(' ', '_')}_{args.country.lower()}_uhi_results.csv"
        df_results.to_csv(csv_path, index=False)
        print(f"\n✓ Results saved to: {csv_path}")
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"ANALYSIS COMPLETE")
        print(f"{'='*60}")
        print(f"Processed {len(all_results)} dates")
        print(f"Mean UHII: {df_results['uhii'].mean():+.3f}°C (±{df_results['uhii'].std():.3f}°C)")
        print(f"Significant dates: {df_results['is_significant'].sum()}/{len(df_results)}")
    else:
        print("\nERROR: No results generated")
        sys.exit(1)


if __name__ == '__main__':
    main()
