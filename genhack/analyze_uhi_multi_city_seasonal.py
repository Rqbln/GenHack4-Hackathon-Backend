#!/usr/bin/env python3
"""
Multi-City Seasonal Urban Heat Island Analysis

Trains on one year of data, then analyzes UHI for multiple cities
across different seasons (2 days per month throughout the year).

Usage:
    python analyze_uhi_multi_city_seasonal.py --country FR --train-year 2020 --inference-year 2021
    python analyze_uhi_multi_city_seasonal.py --country DE --train-year 2020 --inference-year 2021 --cities "Berlin,Munich,Hamburg"
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
import seaborn as sns
from calendar import month_name
import subprocess
import warnings
warnings.filterwarnings('ignore')


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Multi-city seasonal UHI analysis across the year',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # France: Train on 2020, analyze Paris, Lyon, Marseille in 2021
  python analyze_uhi_multi_city_seasonal.py --country FR --train-year 2020 --inference-year 2021
  
  # Germany: Custom cities
  python analyze_uhi_multi_city_seasonal.py --country DE --train-year 2020 --inference-year 2021 --cities "Berlin,Munich,Hamburg,Cologne"
  
  # Custom sampling (3 days per month, different days)
  python analyze_uhi_multi_city_seasonal.py --country FR --train-year 2020 --inference-year 2021 --days-per-month 3 --sample-days "5,15,25"
        """
    )
    
    # Required arguments
    parser.add_argument('--country', required=True, 
                        help='ISO country code (FR, DE, SE, ES, IT, etc.)')
    parser.add_argument('--train-year', type=int, required=True,
                        help='Year to use for training (e.g., 2020)')
    parser.add_argument('--inference-year', type=int, required=True,
                        help='Year to analyze UHI (e.g., 2021)')
    
    # Optional arguments
    parser.add_argument('--cities', help='Comma-separated list of cities (default: auto-select major cities)')
    parser.add_argument('--days-per-month', type=int, default=2,
                        help='Number of days to sample per month (default: 2)')
    parser.add_argument('--sample-days', default='1,15',
                        help='Day numbers to sample (default: "1,15" for 1st and 15th)')
    parser.add_argument('--inner-buffer', type=float, default=2.0,
                        help='Inner buffer distance in km (default: 2.0)')
    parser.add_argument('--outer-buffer', type=float, default=10.0,
                        help='Outer buffer distance in km (default: 10.0)')
    parser.add_argument('--data-dir', default='datasets/main',
                        help='Data directory path')
    parser.add_argument('--output-dir', default='outputs/seasonal_uhi',
                        help='Output directory path')
    parser.add_argument('--skip-training', action='store_true',
                        help='Skip training if model already exists')
    
    return parser.parse_args()


# Country code mapping (2-letter to 3-letter)
COUNTRY_MAP = {
    'FR': 'FRA', 'DE': 'DEU', 'SE': 'SWE', 'NO': 'NOR', 'FI': 'FIN',
    'ES': 'ESP', 'IT': 'ITA', 'UK': 'GBR', 'GB': 'GBR', 'PL': 'POL',
    'NL': 'NLD', 'BE': 'BEL', 'AT': 'AUT', 'CH': 'CHE', 'DK': 'DNK',
    'PT': 'PRT', 'GR': 'GRC', 'CZ': 'CZE', 'RO': 'ROU', 'HU': 'HUN'
}

# Default major cities for each country
DEFAULT_CITIES = {
    'FR': ['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Lille'],
    'DE': ['Berlin', 'Munich', 'Hamburg', 'Cologne', 'Frankfurt'],
    'SE': ['Stockholm', 'Gothenburg', 'Malmö', 'Uppsala'],
    'ES': ['Madrid', 'Barcelona', 'Valencia', 'Seville'],
    'IT': ['Rome', 'Milan', 'Naples', 'Turin'],
    'UK': ['London', 'Birmingham', 'Manchester', 'Leeds'],
    'GB': ['London', 'Birmingham', 'Manchester', 'Leeds'],
    'NL': ['Amsterdam', 'Rotterdam', 'The Hague', 'Utrecht'],
    'PL': ['Warsaw', 'Krakow', 'Wroclaw', 'Poznan'],
    'BE': ['Brussels', 'Antwerp', 'Ghent', 'Bruges']
}


def train_model(args):
    """Train the downscaling model on a full year of data."""
    print(f"\n{'='*70}")
    print(f"TRAINING MODEL ON {args.train_year} DATA")
    print(f"{'='*70}")
    
    cmd = [
        'python', 'src/main.py',
        '--data-dir', args.data_dir,
        '--output-dir', 'outputs',
        '--country', args.country,
        '--start', f'{args.train_year}-01-01',
        '--end', f'{args.train_year}-12-31'
    ]
    
    print(f"Command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False, text=True)
    
    if result.returncode != 0:
        print(f"ERROR: Training failed")
        sys.exit(1)
    
    print(f"✓ Model trained successfully on {args.train_year} data")


def generate_inference_dates(inference_year: int, sample_days: list):
    """
    Generate list of dates for inference (sampled days across the year).
    
    Args:
        inference_year: Year to analyze
        sample_days: List of day numbers to sample per month
        
    Returns:
        List of datetime objects
    """
    dates = []
    for month in range(1, 13):
        for day in sample_days:
            try:
                date = datetime(inference_year, month, day)
                dates.append(date)
            except ValueError:
                # Handle months with fewer days (e.g., Feb 30)
                continue
    return dates


def generate_highres_maps(args, dates):
    """Generate high-resolution maps for all inference dates."""
    print(f"\n{'='*70}")
    print(f"GENERATING HIGH-RESOLUTION MAPS FOR {len(dates)} DATES")
    print(f"{'='*70}")
    
    # Group dates by month for efficient batch processing
    date_ranges = []
    current_month_start = dates[0]
    
    for i, date in enumerate(dates):
        if i == len(dates) - 1 or date.month != dates[i+1].month:
            date_ranges.append((current_month_start, date))
            if i < len(dates) - 1:
                current_month_start = dates[i+1]
    
    # Generate maps for each month
    for start_date, end_date in date_ranges:
        print(f"\nGenerating maps for {start_date.strftime('%B %Y')}...")
        
        cmd = [
            'python', 'src/main.py',
            '--data-dir', args.data_dir,
            '--output-dir', 'outputs',
            '--country', args.country,
            '--start', f'{args.train_year}-01-01',  # Use training period
            '--end', f'{args.train_year}-12-31',
            '--generate-maps',
            '--inference-start', start_date.strftime('%Y-%m-%d'),
            '--inference-end', end_date.strftime('%Y-%m-%d')
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"ERROR: Failed to generate maps for {start_date.strftime('%B %Y')}")
            continue
    
    print(f"\n✓ High-resolution maps generated for all dates")


def load_city_boundaries(gadm_path: Path, cities: list, country_code: str):
    """Load boundaries for multiple cities."""
    print(f"\n{'='*70}")
    print(f"LOADING CITY BOUNDARIES")
    print(f"{'='*70}")
    
    # Convert country code
    country_code_3 = COUNTRY_MAP.get(country_code.upper(), country_code.upper())
    
    # Load GADM data
    gdf = gpd.read_file(gadm_path)
    gdf_country = gdf[gdf['GID_0'] == country_code_3].copy()
    
    if len(gdf_country) == 0:
        print(f"ERROR: Country code '{country_code}' not found")
        sys.exit(1)
    
    city_boundaries = {}
    
    for city in cities:
        city_matches = gdf_country[gdf_country['NAME_1'].str.contains(city, case=False, na=False)]
        
        if len(city_matches) == 0:
            print(f"WARNING: City '{city}' not found, skipping")
            continue
        
        if len(city_matches) > 1:
            city_boundary = city_matches.dissolve()
        else:
            city_boundary = city_matches.copy()
        
        # Transform to EPSG:3035
        if city_boundary.crs != 'EPSG:3035':
            city_boundary = city_boundary.to_crs('EPSG:3035')
        
        area_km2 = city_boundary.geometry.area.sum() / 1e6
        city_boundaries[city] = city_boundary
        
        print(f"✓ {city}: {area_km2:.1f} km²")
    
    return city_boundaries


def extract_temperatures_filtered(raster_path: Path, zone_gdf: gpd.GeoDataFrame):
    """Extract and filter temperature values from raster."""
    with rasterio.open(raster_path) as src:
        out_image, _ = mask(src, zone_gdf.geometry, crop=True, nodata=src.nodata)
        temps = out_image[0]
        
        # Filter valid and realistic values
        if src.nodata is not None:
            valid = temps[(temps != src.nodata) & ~np.isnan(temps)]
        else:
            valid = temps[~np.isnan(temps)]
        
        # Remove unrealistic temperatures (ocean/water = 0°C, bad data)
        realistic = valid[(valid >= 5) & (valid <= 50)]
        
        return realistic


def analyze_city_date(city_name: str, city_boundary: gpd.GeoDataFrame, 
                     raster_path: Path, inner_buffer: float, outer_buffer: float):
    """Analyze UHI for a single city on a single date."""
    
    # Create buffer zones
    urban_zone = city_boundary.copy()
    inner = city_boundary.buffer(inner_buffer * 1000)
    outer = city_boundary.buffer(outer_buffer * 1000)
    rural_zone = gpd.GeoDataFrame(geometry=outer.difference(inner), crs='EPSG:3035')
    
    # Extract temperatures
    urban_temps = extract_temperatures_filtered(raster_path, urban_zone)
    rural_temps = extract_temperatures_filtered(raster_path, rural_zone)
    
    if len(urban_temps) == 0 or len(rural_temps) == 0:
        return None
    
    # Calculate metrics
    urban_mean = np.mean(urban_temps)
    rural_mean = np.mean(rural_temps)
    uhii = urban_mean - rural_mean
    
    # Statistical test
    t_stat, p_value = stats.ttest_ind(urban_temps, rural_temps)
    
    # Cohen's d
    pooled_std = np.sqrt((np.std(urban_temps)**2 + np.std(rural_temps)**2) / 2)
    cohens_d = uhii / pooled_std
    
    return {
        'urban_mean': urban_mean,
        'urban_std': np.std(urban_temps),
        'urban_n': len(urban_temps),
        'rural_mean': rural_mean,
        'rural_std': np.std(rural_temps),
        'rural_n': len(rural_temps),
        'uhii': uhii,
        't_statistic': t_stat,
        'p_value': p_value,
        'cohens_d': cohens_d,
        'is_significant': p_value < 0.05
    }


def analyze_all_combinations(city_boundaries: dict, dates: list, highres_dir: Path,
                            inner_buffer: float, outer_buffer: float):
    """Analyze UHI for all city-date combinations."""
    print(f"\n{'='*70}")
    print(f"ANALYZING {len(city_boundaries)} CITIES × {len(dates)} DATES")
    print(f"{'='*70}")
    
    results = []
    total = len(city_boundaries) * len(dates)
    count = 0
    
    for city_name, city_boundary in city_boundaries.items():
        for date in dates:
            count += 1
            raster_path = highres_dir / f"highres_temp_{date.strftime('%Y%m%d')}.tif"
            
            if not raster_path.exists():
                print(f"[{count}/{total}] ⚠ {city_name} {date.strftime('%Y-%m-%d')}: Map not found")
                continue
            
            result = analyze_city_date(city_name, city_boundary, raster_path, 
                                      inner_buffer, outer_buffer)
            
            if result is None:
                print(f"[{count}/{total}] ⚠ {city_name} {date.strftime('%Y-%m-%d')}: No valid data")
                continue
            
            result['city'] = city_name
            result['date'] = date
            result['month'] = date.month
            result['month_name'] = month_name[date.month]
            result['season'] = get_season(date.month)
            
            results.append(result)
            
            sig = "✓" if result['is_significant'] else "✗"
            print(f"[{count}/{total}] {sig} {city_name:15s} {date.strftime('%Y-%m-%d')}: "
                  f"UHII = {result['uhii']:+.2f}°C, p={result['p_value']:.2e}")
    
    return pd.DataFrame(results)


def get_season(month: int) -> str:
    """Get season name from month number."""
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Autumn'


def create_visualizations(df: pd.DataFrame, output_dir: Path, country: str, year: int):
    """Create comprehensive visualizations of seasonal UHI patterns."""
    print(f"\n{'='*70}")
    print(f"CREATING VISUALIZATIONS")
    print(f"{'='*70}")
    
    # 1. Heatmap: Cities × Months
    fig, ax = plt.subplots(figsize=(14, 8))
    pivot = df.pivot_table(values='uhii', index='city', columns='month_name', aggfunc='mean')
    month_order = [month_name[i] for i in range(1, 13)]
    pivot = pivot[month_order]
    
    sns.heatmap(pivot, annot=True, fmt='.2f', cmap='RdYlBu_r', center=0,
                cbar_kws={'label': 'UHII (°C)'}, ax=ax, vmin=-1, vmax=1)
    ax.set_title(f'Urban Heat Island Intensity: {country} Cities Across {year}\n(Mean UHII per Month)', 
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('City', fontsize=12)
    plt.tight_layout()
    plt.savefig(output_dir / f'uhi_heatmap_{country}_{year}.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: uhi_heatmap_{country}_{year}.png")
    plt.close()
    
    # 2. Time series: UHII over the year for each city
    fig, ax = plt.subplots(figsize=(14, 6))
    for city in df['city'].unique():
        city_data = df[df['city'] == city].sort_values('month')
        ax.plot(city_data['month'], city_data['uhii'], marker='o', label=city, linewidth=2)
    
    ax.axhline(0, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('UHII (°C)', fontsize=12)
    ax.set_title(f'Seasonal UHI Variation: {country} Cities in {year}', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels([month_name[i][:3] for i in range(1, 13)])
    ax.legend(loc='best')
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / f'uhi_timeseries_{country}_{year}.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: uhi_timeseries_{country}_{year}.png")
    plt.close()
    
    # 3. Box plots: UHII distribution by season
    fig, ax = plt.subplots(figsize=(12, 6))
    season_order = ['Winter', 'Spring', 'Summer', 'Autumn']
    sns.boxplot(data=df, x='season', y='uhii', order=season_order, ax=ax, palette='Set2')
    ax.axhline(0, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax.set_xlabel('Season', fontsize=12)
    ax.set_ylabel('UHII (°C)', fontsize=12)
    ax.set_title(f'Seasonal UHI Distribution: {country} Cities in {year}', 
                 fontsize=14, fontweight='bold')
    ax.grid(alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(output_dir / f'uhi_seasons_{country}_{year}.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: uhi_seasons_{country}_{year}.png")
    plt.close()
    
    # 4. Bar chart: Mean UHII by city
    fig, ax = plt.subplots(figsize=(10, 6))
    city_means = df.groupby('city')['uhii'].mean().sort_values(ascending=False)
    colors = ['red' if x > 0 else 'blue' for x in city_means.values]
    city_means.plot(kind='bar', ax=ax, color=colors, alpha=0.7)
    ax.axhline(0, color='gray', linestyle='--', linewidth=1)
    ax.set_xlabel('City', fontsize=12)
    ax.set_ylabel('Mean UHII (°C)', fontsize=12)
    ax.set_title(f'Mean Urban Heat Island Intensity: {country} Cities ({year})', 
                 fontsize=14, fontweight='bold')
    ax.grid(alpha=0.3, axis='y')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_dir / f'uhi_cities_{country}_{year}.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: uhi_cities_{country}_{year}.png")
    plt.close()


def main():
    args = parse_arguments()
    
    # Setup paths
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    highres_dir = Path('outputs/highres_maps')
    gadm_path = data_dir / 'gadm_410_europe.gpkg'
    
    # Parse sample days
    sample_days = [int(d) for d in args.sample_days.split(',')]
    
    # Get cities list
    if args.cities:
        cities = [c.strip() for c in args.cities.split(',')]
    else:
        cities = DEFAULT_CITIES.get(args.country.upper(), ['Capital'])
    
    print(f"\n{'='*70}")
    print(f"MULTI-CITY SEASONAL UHI ANALYSIS")
    print(f"{'='*70}")
    print(f"Country: {args.country}")
    print(f"Training year: {args.train_year}")
    print(f"Inference year: {args.inference_year}")
    print(f"Cities: {', '.join(cities)}")
    print(f"Sampling: {args.days_per_month} days per month (days: {sample_days})")
    print(f"Buffer: {args.inner_buffer}-{args.outer_buffer} km")
    
    # Step 1: Train model
    if not args.skip_training:
        train_model(args)
    else:
        print(f"\n✓ Skipping training (using existing model)")
    
    # Step 2: Generate inference dates
    dates = generate_inference_dates(args.inference_year, sample_days)
    print(f"\n✓ Generated {len(dates)} inference dates ({len(dates)//12} per month)")
    
    # Step 3: Generate high-resolution maps
    generate_highres_maps(args, dates)
    
    # Step 4: Load city boundaries
    city_boundaries = load_city_boundaries(gadm_path, cities, args.country)
    
    if len(city_boundaries) == 0:
        print("\nERROR: No valid city boundaries found")
        sys.exit(1)
    
    # Step 5: Analyze all combinations
    results_df = analyze_all_combinations(city_boundaries, dates, highres_dir,
                                         args.inner_buffer, args.outer_buffer)
    
    if len(results_df) == 0:
        print("\nERROR: No results generated")
        sys.exit(1)
    
    # Step 6: Save results
    csv_path = output_dir / f'uhi_seasonal_{args.country}_{args.inference_year}.csv'
    results_df.to_csv(csv_path, index=False)
    print(f"\n✓ Results saved to: {csv_path}")
    
    # Step 7: Create visualizations
    create_visualizations(results_df, output_dir, args.country, args.inference_year)
    
    # Step 8: Summary statistics
    print(f"\n{'='*70}")
    print(f"SUMMARY STATISTICS")
    print(f"{'='*70}")
    print(f"Total analyses: {len(results_df)}")
    print(f"Significant UHI detections: {results_df['is_significant'].sum()} ({100*results_df['is_significant'].mean():.1f}%)")
    print(f"\nMean UHII by season:")
    season_summary = results_df.groupby('season')['uhii'].agg(['mean', 'std', 'count'])
    print(season_summary)
    print(f"\nMean UHII by city:")
    city_summary = results_df.groupby('city')['uhii'].agg(['mean', 'std', 'count'])
    print(city_summary)
    
    print(f"\n{'='*70}")
    print(f"✓ ANALYSIS COMPLETE")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
