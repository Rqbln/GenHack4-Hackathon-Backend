from http.server import BaseHTTPRequestHandler
import json
import logging
import os
import traceback
from pathlib import Path
from urllib.parse import urlparse

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
                response_data = {
                    "data": [
                        {"date": "2020-01-01", "temperature": 5.2, "quality": 0},
                        {"date": "2020-01-02", "temperature": 6.1, "quality": 0},
                        {"date": "2020-01-03", "temperature": 7.3, "quality": 0}
                    ]
                }
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
