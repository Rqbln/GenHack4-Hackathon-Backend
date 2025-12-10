"""
Phase 1: Data Preparation for Climate Downscaling
Handles parsing station metadata, temperature data, and building training cubes
"""

import pandas as pd
import numpy as np
import xarray as xr
import rasterio
from pathlib import Path
from datetime import datetime
from typing import Tuple, List, Dict
import warnings
warnings.filterwarnings('ignore')


class StationMetadataParser:
    """Parse ECA&D station metadata from DMS format to decimal degrees"""
    
    def __init__(self, stations_file: str):
        self.stations_file = Path(stations_file)
    
    @staticmethod
    def dms_to_decimal(dms_string: str) -> float:
        """
        Convert DMS (Degrees:Minutes:Seconds) to decimal degrees
        Formula: Decimal = Deg + Min/60 + Sec/3600
        
        Args:
            dms_string: String in format '+56:52:00' or '-12:34:56'
        
        Returns:
            Decimal degrees (float)
        """
        dms_string = dms_string.strip()
        sign = 1 if dms_string[0] == '+' else -1
        
        # Remove the +/- sign
        dms_string = dms_string[1:]
        
        # Split by ':'
        parts = dms_string.split(':')
        degrees = float(parts[0])
        minutes = float(parts[1])
        seconds = float(parts[2])
        
        decimal = sign * (degrees + minutes / 60.0 + seconds / 3600.0)
        return decimal
    
    def parse_stations(self) -> pd.DataFrame:
        """
        Parse stations.txt file and convert coordinates to decimal degrees
        
        Returns:
            DataFrame with columns: [STAID, STANAME, CN, LAT_DEC, LON_DEC, HGHT]
        """
        # Read the file, skipping header rows
        stations = []
        
        with open(self.stations_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find the start of data (after header)
        data_start = 0
        for i, line in enumerate(lines):
            if 'STAID,STANAME' in line:
                data_start = i + 1
                break
        
        # Parse each station line
        for line in lines[data_start:]:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split(',')
            if len(parts) < 6:
                continue
            
            try:
                staid = int(parts[0].strip())
                staname = parts[1].strip()
                cn = parts[2].strip()
                lat_dms = parts[3].strip()
                lon_dms = parts[4].strip()
                hght = int(parts[5].strip())
                
                # Convert coordinates
                lat_dec = self.dms_to_decimal(lat_dms)
                lon_dec = self.dms_to_decimal(lon_dms)
                
                stations.append({
                    'STAID': staid,
                    'STANAME': staname,
                    'CN': cn,
                    'LAT_DEC': lat_dec,
                    'LON_DEC': lon_dec,
                    'ELEVATION': hght
                })
            except (ValueError, IndexError) as e:
                print(f"Warning: Could not parse line: {line[:50]}... Error: {e}")
                continue
        
        df = pd.DataFrame(stations)
        print(f"Parsed {len(df)} stations from {len(df['CN'].unique())} countries")
        return df


class StationTemperatureLoader:
    """Load and clean station temperature observations"""
    
    def __init__(self, data_dir: str, stations_meta: pd.DataFrame):
        self.data_dir = Path(data_dir)
        self.stations_meta = stations_meta
    
    def load_station_file(self, staid: int) -> pd.DataFrame:
        """
        Load temperature data for a single station
        
        Args:
            staid: Station ID
        
        Returns:
            DataFrame with cleaned temperature data
        """
        filepath = self.data_dir / f"TX_STAID{staid:06d}.txt"
        
        if not filepath.exists():
            return pd.DataFrame()
        
        # Read the file, skipping header
        data = []
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        # Find data start
        data_start = 0
        for i, line in enumerate(lines):
            if 'STAID, SOUID' in line:
                data_start = i + 1
                break
        
        # Parse data lines
        for line in lines[data_start:]:
            parts = line.strip().split(',')
            if len(parts) < 5:
                continue
            
            try:
                staid_val = int(parts[0].strip())
                date_str = parts[2].strip()
                tx_val = int(parts[3].strip())
                q_tx = int(parts[4].strip())
                
                data.append({
                    'STAID': staid_val,
                    'DATE': date_str,
                    'TX': tx_val,
                    'Q_TX': q_tx
                })
            except (ValueError, IndexError):
                continue
        
        return pd.DataFrame(data)
    
    def clean_temperature_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply cleaning rules:
        1. Filter Quality: Keep only Q_TX == 0
        2. Handle Missing: Drop TX == -9999
        3. Convert Units: TX is in 0.1°C, divide by 10
        4. Parse Date: Convert YYYYMMDD to datetime
        
        Args:
            df: Raw temperature dataframe
        
        Returns:
            Cleaned dataframe
        """
        if df.empty:
            return df
        
        # Filter quality
        df = df[df['Q_TX'] == 0].copy()
        
        # Handle missing
        df = df[df['TX'] != -9999].copy()
        
        # Convert units (0.1°C to °C)
        df['TX'] = df['TX'] / 10.0
        
        # Parse date
        df['DATE'] = pd.to_datetime(df['DATE'], format='%Y%m%d')
        
        return df
    
    def load_country_stations(self, country_code: str, 
                             date_range: Tuple[str, str] = None) -> pd.DataFrame:
        """
        Load all stations for a specific country
        
        Args:
            country_code: ISO 3166 country code (e.g., 'SE', 'DE')
            date_range: Optional tuple of (start_date, end_date) in 'YYYY-MM-DD' format
        
        Returns:
            Combined dataframe with all station data for the country
        """
        # Filter stations by country
        country_stations = self.stations_meta[
            self.stations_meta['CN'] == country_code
        ]
        
        print(f"Loading {len(country_stations)} stations for country {country_code}")
        
        all_data = []
        for idx, station in country_stations.iterrows():
            staid = station['STAID']
            df = self.load_station_file(staid)
            
            if not df.empty:
                df = self.clean_temperature_data(df)
                
                # Add station metadata
                df['LAT'] = station['LAT_DEC']
                df['LON'] = station['LON_DEC']
                df['ELEVATION'] = station['ELEVATION']
                df['STANAME'] = station['STANAME']
                
                all_data.append(df)
        
        if not all_data:
            return pd.DataFrame()
        
        combined = pd.concat(all_data, ignore_index=True)
        
        # Apply date range filter if provided
        if date_range:
            start_date, end_date = date_range
            combined = combined[
                (combined['DATE'] >= start_date) & 
                (combined['DATE'] <= end_date)
            ]
        
        print(f"Loaded {len(combined)} observations from {combined['STAID'].nunique()} stations")
        return combined


class TrainingCubeBuilder:
    """Build training cube by merging station data with ERA5 and NDVI"""
    
    def __init__(self, era5_dir: str, ndvi_dir: str):
        self.era5_dir = Path(era5_dir)
        self.ndvi_dir = Path(ndvi_dir)
        self.era5_cache = {}
        self.ndvi_cache = {}
    
    def get_era5_value(self, date: datetime, lat: float, lon: float, 
                       variable: str = '2m_temperature_daily_maximum') -> float:
        """
        Extract ERA5 temperature value at given location and time
        
        Args:
            date: Date to query
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
            variable: ERA5 variable name
        
        Returns:
            Temperature in Celsius (or NaN if not found)
        """
        year = date.year
        cache_key = (year, variable)
        
        # Load ERA5 file if not cached
        if cache_key not in self.era5_cache:
            filepath = self.era5_dir / f"{year}_{variable}.nc"
            
            if not filepath.exists():
                return np.nan
            
            try:
                ds = xr.open_dataset(filepath)
                self.era5_cache[cache_key] = ds
            except Exception as e:
                print(f"Error loading ERA5 file {filepath}: {e}")
                return np.nan
        
        ds = self.era5_cache[cache_key]
        
        # Find nearest point
        try:
            # Select by nearest lat/lon and date
            # ERA5 files use 'valid_time' not 'time'
            point = ds.sel(
                latitude=lat,
                longitude=lon,
                valid_time=date,
                method='nearest'
            )
            
            # Get temperature value (convert K to C if needed)
            # Variable name mapping: 2m_temperature -> t2m
            var_name_map = {
                '2m_temperature': 't2m',
                'total_precipitation': 'tp',
                '10m_u_component_of_wind': 'u10',
                '10m_v_component_of_wind': 'v10'
            }
            var_base = variable.split('_daily_')[0]
            var_name = var_name_map.get(var_base, var_base)
            
            temp_k = point[var_name].values
            temp_c = float(temp_k) - 273.15  # Convert Kelvin to Celsius
            
            return temp_c
        except Exception as e:
            print(f"Error extracting ERA5 value at ({lat}, {lon}, {date}): {e}")
            return np.nan
    
    def get_ndvi_value(self, date: datetime, lat: float, lon: float) -> float:
        """
        Extract NDVI value at given location and time
        
        Args:
            date: Date to query (will find appropriate seasonal file)
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
        
        Returns:
            NDVI value (or NaN if not found)
        """
        # Find appropriate NDVI file for this date
        ndvi_files = list(self.ndvi_dir.glob('ndvi_*.tif'))
        
        # Select file based on date range in filename
        selected_file = None
        for f in ndvi_files:
            # Parse filename: ndvi_YYYY-MM-DD_YYYY-MM-DD.tif
            parts = f.stem.split('_')
            if len(parts) >= 3:
                start_str = parts[1]
                end_str = parts[2]
                
                try:
                    start = datetime.strptime(start_str, '%Y-%m-%d')
                    end = datetime.strptime(end_str, '%Y-%m-%d')
                    
                    if start <= date < end:
                        selected_file = f
                        break
                except ValueError:
                    continue
        
        if selected_file is None:
            return np.nan
        
        # Load NDVI file if not cached
        if selected_file not in self.ndvi_cache:
            try:
                self.ndvi_cache[selected_file] = rasterio.open(selected_file)
            except Exception as e:
                print(f"Error loading NDVI file {selected_file}: {e}")
                return np.nan
        
        src = self.ndvi_cache[selected_file]
        
        # Get pixel value at lat/lon
        try:
            # Import pyproj for coordinate transformation
            from pyproj import Transformer
            
            # Transform WGS84 (EPSG:4326) to raster CRS
            transformer = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
            x, y = transformer.transform(lon, lat)
            
            # Convert to pixel coordinates
            row, col = src.index(x, y)
            
            # Check bounds
            if not (0 <= row < src.height and 0 <= col < src.width):
                return np.nan
            
            # Read the value
            window = rasterio.windows.Window(col, row, 1, 1)
            data = src.read(1, window=window)
            
            if data.size == 0:
                return np.nan
            
            value = float(data[0, 0])
            
            # Check for nodata value (255 for Sentinel-2 NDVI)
            if value == 255:
                return np.nan
            
            # Scale from 0-254 to -1 to 1
            # Formula: (value / 254) * 2 - 1
            value_scaled = (value / 254.0) * 2.0 - 1.0
            
            return value_scaled
            
        except Exception as e:
            print(f"Error extracting NDVI at ({lat}, {lon}): {e}")
            return np.nan
    
    def build_training_cube(self, station_data: pd.DataFrame, 
                           progress_interval: int = 1000) -> pd.DataFrame:
        """
        Build complete training cube by merging all data sources
        
        Args:
            station_data: Cleaned station temperature data
            progress_interval: Print progress every N rows
        
        Returns:
            Training dataframe with columns:
            [DATE, LAT, LON, ELEVATION, NDVI, ERA5_Temp, Station_Temp, Residual]
        """
        print(f"Building training cube from {len(station_data)} station observations...")
        
        training_data = []
        
        for idx, row in station_data.iterrows():
            if idx % progress_interval == 0:
                print(f"Processing row {idx}/{len(station_data)}...")
            
            date = row['DATE']
            lat = row['LAT']
            lon = row['LON']
            elevation = row['ELEVATION']
            station_temp = row['TX']
            
            # Get ERA5 baseline
            era5_temp = self.get_era5_value(date, lat, lon)
            
            # Get NDVI
            ndvi = self.get_ndvi_value(date, lat, lon)
            
            # Skip if we couldn't get both ERA5 and NDVI
            if np.isnan(era5_temp) or np.isnan(ndvi):
                continue
            
            # Calculate residual (the target for ML)
            residual = station_temp - era5_temp
            
            training_data.append({
                'DATE': date,
                'LAT': lat,
                'LON': lon,
                'ELEVATION': elevation,
                'NDVI': ndvi,
                'ERA5_Temp': era5_temp,
                'Station_Temp': station_temp,
                'Residual': residual,
                'STAID': row['STAID'],
                'DayOfYear': date.dayofyear
            })
        
        df = pd.DataFrame(training_data)
        print(f"Built training cube with {len(df)} valid samples")
        
        return df
    
    def close(self):
        """Close all open file handles"""
        for ds in self.era5_cache.values():
            try:
                ds.close()
            except:
                pass
        
        for src in self.ndvi_cache.values():
            try:
                src.close()
            except:
                pass


# Main execution functions
def prepare_training_data(data_dir: str, 
                         country_code: str = 'SE',
                         date_range: Tuple[str, str] = ('2020-01-01', '2023-12-31'),
                         output_path: str = None) -> pd.DataFrame:
    """
    Complete data preparation pipeline
    
    Args:
        data_dir: Base directory containing all data
        country_code: Country to process
        date_range: Date range tuple
        output_path: Optional path to save training data
    
    Returns:
        Training dataframe ready for modeling
    """
    data_path = Path(data_dir)
    
    # Step 1: Parse station metadata
    print("\n=== Step 1: Parsing Station Metadata ===")
    parser = StationMetadataParser(data_path / 'ECA_blend_tx' / 'stations.txt')
    stations_meta = parser.parse_stations()
    
    # Step 2: Load station temperature data
    print("\n=== Step 2: Loading Station Temperature Data ===")
    loader = StationTemperatureLoader(
        data_path / 'ECA_blend_tx',
        stations_meta
    )
    station_data = loader.load_country_stations(country_code, date_range)
    
    if station_data.empty:
        print("No station data loaded!")
        return pd.DataFrame()
    
    # Step 3: Build training cube
    print("\n=== Step 3: Building Training Cube ===")
    builder = TrainingCubeBuilder(
        data_path / 'derived-era5-land-daily-statistics',
        data_path / 'sentinel2_ndvi'
    )
    
    training_data = builder.build_training_cube(station_data)
    builder.close()
    
    # Save if requested
    if output_path and not training_data.empty:
        training_data.to_csv(output_path, index=False)
        print(f"\nTraining data saved to {output_path}")
    
    return training_data


if __name__ == "__main__":
    # Example usage
    training_data = prepare_training_data(
        data_dir='../datasets/main',
        country_code='SE',  # Sweden
        date_range=('2020-01-01', '2023-12-31'),
        output_path='../outputs/training_data.csv'
    )
    
    if not training_data.empty:
        print("\n=== Training Data Summary ===")
        print(training_data.describe())
        print(f"\nShape: {training_data.shape}")
        print(f"Stations: {training_data['STAID'].nunique()}")
