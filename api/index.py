from http.server import BaseHTTPRequestHandler
import json
import logging
import os
import traceback
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta
import math

# Configuration minimale du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chemins des fichiers (lazy loading dans les méthodes)
BASE_DIR = None
METRICS_FILE = None
STATIONS_FILE = None

def get_paths():
    """Initialise les chemins de fichiers de manière lazy"""
    global BASE_DIR, METRICS_FILE, STATIONS_FILE
    if BASE_DIR is None:
        try:
            BASE_DIR = Path(__file__).parent.parent
            METRICS_FILE = BASE_DIR / "results" / "all_metrics.json"
            STATIONS_FILE = BASE_DIR / "data" / "processed" / "stations.geojson"
        except Exception as e:
            logger.warning(f"Path initialization warning: {e}")
            BASE_DIR = Path("/tmp")
            METRICS_FILE = Path("/dev/null")
            STATIONS_FILE = Path("/dev/null")
    return BASE_DIR, METRICS_FILE, STATIONS_FILE

def load_metrics():
    """Load metrics data from JSON file"""
    _, metrics_file, _ = get_paths()
    if metrics_file.exists():
        try:
            with open(metrics_file, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    # Mock Data
    return {
        "baseline_metrics": {"rmse": 2.45, "mae": 1.89, "r2": 0.72},
        "prithvi_metrics": {"rmse": 1.52, "mae": 1.15, "r2": 0.89},
        "model_comparison": {"rmse_improvement": {"absolute": 0.93, "percentage": 38.0}},
        "data_info": {"status": "mock_data_loaded"}
    }

def load_stations():
    """Load stations from GeoJSON file"""
    _, _, stations_file = get_paths()
    if stations_file.exists():
        try:
            with open(stations_file, 'r') as f:
                geojson = json.load(f)
                stations = []
                for feature in geojson.get('features', []):
                    props = feature.get('properties', {})
                    coords = feature.get('geometry', {}).get('coordinates', [])
                    if len(coords) >= 2:
                        stations.append({
                            "staid": props.get('STAID', props.get('staid', 0)),
                            "staname": props.get('STANAME', props.get('staname', 'Unknown')),
                            "country": props.get('CN', props.get('country', 'FRA')),
                            "latitude": coords[1],
                            "longitude": coords[0],
                            "elevation": props.get('HGHT', props.get('elevation', 0))
                        })
                return {"stations": stations}
        except Exception:
            pass
    return {"stations": [{"staid": 1, "staname": "Mock Station Paris"}]}

def generate_realistic_temperature_data(station_id, latitude, longitude, elevation, start_date_str, end_date_str):
    """
    Generate realistic temperature data with seasonal patterns and station-specific variations
    """
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    except:
        start_date = datetime(2020, 1, 1)
        end_date = datetime(2021, 12, 31)
    
    data = []
    current_date = start_date
    
    # Base temperature for Paris area (latitude 48.8°)
    base_temp = 11.0  # Annual mean temperature for Paris
    
    # Station-specific adjustments based on location
    # Urban stations (lower elevation, central) are warmer
    # Rural stations (higher elevation, peripheral) are cooler
    urban_factor = 1.0 if elevation < 100 else 0.7  # Urban heat island effect
    elevation_factor = -0.0065 * elevation  # Lapse rate: -6.5°C per 1000m
    
    # Station-specific base offset (using station_id as seed for consistency)
    station_offset = (station_id % 10) * 0.5 - 2.0  # -2 to +2.5°C variation
    
    day_count = 0
    while current_date <= end_date:
        # Day of year (1-365/366)
        day_of_year = current_date.timetuple().tm_yday
        
        # Seasonal variation (sine wave with peak in summer)
        seasonal_temp = 10.0 * math.sin((day_of_year - 80) * 2 * math.PI / 365.0)
        
        # Daily variation (small random component)
        daily_variation = math.sin(day_count * 0.1) * 2.0  # Slow variation
        
        # Calculate final temperature
        temperature = (
            base_temp +
            seasonal_temp +
            elevation_factor +
            station_offset * urban_factor +
            daily_variation +
            (station_id % 7) * 0.3  # Small station-specific daily variation
        )
        
        # Add some realistic noise
        noise = math.sin(day_count * 0.05 + station_id) * 1.5
        
        final_temp = round(temperature + noise, 1)
        
        data.append({
            "date": current_date.strftime('%Y-%m-%d'),
            "temperature": final_temp,
            "quality": 0
        })
        
        current_date += timedelta(days=1)
        day_count += 1
    
    return data

def generate_heatmap_data(date_str, bbox=None):
    """
    Generate realistic heatmap data with spatial patterns
    """
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    except:
        date = datetime(2020, 1, 1)
    
    # Default Paris bounding box
    if bbox is None:
        lon_min, lat_min, lon_max, lat_max = 2.2, 48.8, 2.5, 49.0
    else:
        lon_min, lat_min, lon_max, lat_max = bbox
    
    # Day of year for seasonal variation
    day_of_year = date.timetuple().tm_yday
    seasonal_base = 11.0 + 10.0 * math.sin((day_of_year - 80) * 2 * math.PI / 365.0)
    
    # Generate grid of points
    n_points = 200  # More points for better heatmap
    n_lon = int(math.sqrt(n_points) * 1.5)
    n_lat = int(math.sqrt(n_points))
    
    step_lon = (lon_max - lon_min) / n_lon
    step_lat = (lat_max - lat_min) / n_lat
    
    data = []
    center_lon = (lon_min + lon_max) / 2
    center_lat = (lat_min + lat_max) / 2
    
    for i in range(n_lon):
        for j in range(n_lat):
            lon = lon_min + i * step_lon
            lat = lat_min + j * step_lat
            
            # Distance from center (Paris center)
            dist = math.sqrt(
                math.pow((lon - center_lon) * 111.0, 2) +  # Convert to km
                math.pow((lat - center_lat) * 111.0, 2)
            )
            
            # Urban heat island effect: warmer in center
            uhi_effect = 4.0 * math.exp(-dist / 10.0)  # Decay over ~10km
            
            # Small spatial variation
            spatial_var = math.sin(lon * 10) * math.cos(lat * 10) * 1.5
            
            # Final temperature
            temperature = seasonal_base + uhi_effect + spatial_var
            
            data.append({
                "position": [lon, lat],
                "weight": round(temperature, 1)
            })
    
    return data

class handler(BaseHTTPRequestHandler):
    """
    Handler Vercel - Classe héritant de BaseHTTPRequestHandler
    Vercel attend une classe, pas une fonction !
    """
    
    def _send_json_response(self, status_code, data):
        """Helper pour envoyer une réponse JSON"""
        try:
            self.send_response(status_code)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
        except Exception as e:
            logger.error(f"Error sending response: {e}")
    
    def _handle_request(self):
        """Gère la requête HTTP"""
        try:
            # Parsing de l'URL
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)
            
            # Routing
            response_data = {}
            status_code = 200
            
            if path == '/' or path == '/health':
                base_dir, _, _ = get_paths()
                response_data = {
                    "status": "healthy", 
                    "python_version": os.sys.version,
                    "base_dir": str(base_dir)
                }
            elif '/api/stations' in path:
                response_data = load_stations()
            elif '/api/metrics/comparison' in path:
                metrics = load_metrics()
                baseline = metrics.get("baseline_metrics", {})
                prithvi = metrics.get("prithvi_metrics", {})
                if baseline.get("rmse") and prithvi.get("rmse"):
                    response_data = {
                       "rmse_improvement": {
                           "absolute": round(baseline["rmse"] - prithvi["rmse"], 2),
                           "percentage": round((baseline["rmse"] - prithvi["rmse"]) / baseline["rmse"] * 100, 1)
                       }
                    }
                else:
                    response_data = metrics.get("model_comparison", {})
            elif '/api/metrics/advanced' in path:
                metrics = load_metrics()
                response_data = metrics.get("advanced_metrics", {})
            elif '/api/validation/physics' in path:
                metrics = load_metrics()
                response_data = metrics.get("physics_validation", {})
            elif '/api/metrics' in path:
                response_data = load_metrics()
            elif '/api/temperature' in path:
                # Get station info
                station_id = int(query_params.get('station_id', ['1'])[0])
                start_date = query_params.get('start_date', ['2020-01-01'])[0]
                end_date = query_params.get('end_date', ['2021-12-31'])[0]
                
                # Load stations to get station coordinates
                stations_data = load_stations()
                stations = stations_data.get('stations', [])
                station = next((s for s in stations if s.get('staid') == station_id), None)
                
                if station:
                    temp_data = generate_realistic_temperature_data(
                        station_id=station_id,
                        latitude=station.get('latitude', 48.8566),
                        longitude=station.get('longitude', 2.3522),
                        elevation=station.get('elevation', 75),
                        start_date_str=start_date,
                        end_date_str=end_date
                    )
                    response_data = {"data": temp_data}
                else:
                    # Fallback if station not found
                    temp_data = generate_realistic_temperature_data(
                        station_id=station_id,
                        latitude=48.8566,
                        longitude=2.3522,
                        elevation=75,
                        start_date_str=start_date,
                        end_date_str=end_date
                    )
                    response_data = {"data": temp_data}
            elif '/api/heatmap' in path or '/api/era5' in path:
                # Get date and bbox from query params
                date_str = query_params.get('date', [query_params.get('start_date', ['2020-01-01'])[0]])[0]
                bbox_str = query_params.get('bbox', [None])[0]
                
                bbox = None
                if bbox_str:
                    try:
                        bbox = [float(x) for x in bbox_str.split(',')]
                        if len(bbox) != 4:
                            bbox = None
                    except:
                        bbox = None
                
                heatmap_data = generate_heatmap_data(date_str, bbox)
                response_data = {"data": heatmap_data}
            else:
                status_code = 404
                response_data = {"error": "Not Found", "path": path}
            
            self._send_json_response(status_code, response_data)
            
        except Exception as e:
            error_details = traceback.format_exc()
            logger.error(f"Handler failed: {e}\n{error_details}")
            self._send_json_response(500, {
                "error": "Internal Server Error", 
                "message": str(e),
                "traceback": error_details.split('\n')
            })
    
    def do_GET(self):
        """Gère les requêtes GET"""
        self._handle_request()
    
    def do_POST(self):
        """Gère les requêtes POST"""
        self._handle_request()
    
    def do_OPTIONS(self):
        """Gère les requêtes OPTIONS (CORS preflight)"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Override pour éviter les logs verbeux"""
        pass
