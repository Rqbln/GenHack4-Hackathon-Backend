"""
Vercel Serverless Function for GenHack API
Adapted from api_simple.py for Vercel deployment

Vercel Python functions use BaseHTTPRequestHandler, not AWS Lambda format
"""

import json
from pathlib import Path
import logging
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load metrics from results file
# In Vercel, files are in the deployment package
BASE_DIR = Path(__file__).parent.parent
METRICS_FILE = BASE_DIR / "results" / "all_metrics.json"
STATIONS_FILE = BASE_DIR / "data" / "processed" / "stations.geojson"

def load_metrics():
    """Load metrics data from JSON file"""
    if METRICS_FILE.exists():
        try:
            with open(METRICS_FILE, 'r') as f:
                metrics = json.load(f)
                logger.info("✅ Loaded real metrics from file")
                return metrics
        except Exception as e:
            logger.error(f"Failed to load metrics: {e}")
    
    # Return mock data if file doesn't exist
    logger.warning("Using mock metrics (real metrics file not found)")
    return {
        "baseline_metrics": {"rmse": 2.45, "mae": 1.89, "r2": 0.72},
        "prithvi_metrics": {"rmse": 1.52, "mae": 1.15, "r2": 0.89},
        "advanced_metrics": {
            "perkins_score": 0.84,
            "spectral_correlation": 0.91
        },
        "model_comparison": {
            "rmse_improvement": {"absolute": 0.93, "percentage": 38.0}
        },
        "physics_validation": {
            "overall": {"is_valid": True, "valid_count": 4, "total_count": 4}
        }
    }

def load_stations():
    """Load stations from GeoJSON file"""
    if STATIONS_FILE.exists():
        try:
            with open(STATIONS_FILE, 'r') as f:
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
                logger.info(f"✅ Loaded {len(stations)} stations from file")
                return {"stations": stations}
        except Exception as e:
            logger.error(f"Failed to load stations: {e}")
    
    # Return mock stations if file doesn't exist
    logger.warning("Using mock stations (real stations file not found)")
    return {
        "stations": [
            {
                "staid": 1,
                "staname": "Paris Montsouris",
                "country": "FRA",
                "latitude": 48.8222,
                "longitude": 2.3364,
                "elevation": 75
            },
            {
                "staid": 2,
                "staname": "Paris Orly",
                "country": "FRA",
                "latitude": 48.7233,
                "longitude": 2.3794,
                "elevation": 89
            },
            {
                "staid": 3,
                "staname": "Paris Le Bourget",
                "country": "FRA",
                "latitude": 48.9694,
                "longitude": 2.4414,
                "elevation": 66
            }
        ]
    }

# --- HANDLER VERCEL CORRIGÉ ---

def handler(request):
    """
    Vercel serverless function handler.
    'request' est une instance de http.server.BaseHTTPRequestHandler
    """
    
    # Fonction utilitaire pour envoyer la réponse proprement
    def send_json(status_code, data):
        request.send_response(status_code)
        # Headers CORS
        request.send_header('Access-Control-Allow-Origin', '*')
        request.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        request.send_header('Access-Control-Allow-Headers', 'Content-Type')
        request.send_header('Content-Type', 'application/json')
        request.end_headers()
        # Écriture du corps de la réponse
        request.wfile.write(json.dumps(data, indent=2).encode('utf-8'))

    try:
        # 1. Extraction propre de la méthode et du chemin
        # Sur Vercel (BaseHTTPRequestHandler), la méthode est dans .command
        method = request.command 
        
        # Le path peut contenir des query params (?id=1), on nettoie avec urlparse
        parsed_url = urlparse(request.path)
        path = parsed_url.path

        # 2. Gestion OPTIONS (CORS Preflight)
        if method == 'OPTIONS':
            request.send_response(200)
            request.send_header('Access-Control-Allow-Origin', '*')
            request.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            request.send_header('Access-Control-Allow-Headers', 'Content-Type')
            request.end_headers()
            return # On arrête là, pas de body pour OPTIONS

        # 3. Routing
        response_data = {}
        status = 200

        if path == '/' or path == '/health':
            response_data = {"status": "healthy", "version": "1.0.0", "service": "chronos-wxc-api"}
        
        elif path == '/api/stations':
            response_data = load_stations()
        
        elif path == '/api/metrics':
            metrics = load_metrics()
            response_data = {
                "baseline_metrics": metrics.get("baseline_metrics", {}),
                "prithvi_metrics": metrics.get("prithvi_metrics", {}),
                "advanced_metrics": metrics.get("advanced_metrics", {}),
                "data_info": metrics.get("data_info", {}),
                "calculation_date": metrics.get("calculation_date", "")
            }
        
        elif path == '/api/metrics/comparison':
            metrics = load_metrics()
            baseline = metrics.get("baseline_metrics", {})
            prithvi = metrics.get("prithvi_metrics", {})
            
            if baseline.get("rmse") and prithvi.get("rmse"):
                response_data = {
                    "rmse_improvement": {
                        "absolute": round(baseline["rmse"] - prithvi["rmse"], 2),
                        "percentage": round((baseline["rmse"] - prithvi["rmse"]) / baseline["rmse"] * 100, 1)
                    },
                    "mae_improvement": {
                        "absolute": round(baseline.get("mae", 0) - prithvi.get("mae", 0), 2),
                        "percentage": round((baseline.get("mae", 0) - prithvi.get("mae", 0)) / baseline.get("mae", 1) * 100, 1) if baseline.get("mae") else 0
                    }
                }
            else:
                response_data = metrics.get("model_comparison", {})
        
        elif path == '/api/metrics/advanced':
            metrics = load_metrics()
            response_data = metrics.get("advanced_metrics", {})
        
        elif path == '/api/validation/physics':
            metrics = load_metrics()
            response_data = metrics.get("physics_validation", {})
        
        elif path.startswith('/api/temperature'):
            # Mock temperature data for now
            response_data = {
                "data": [
                    {"date": "2020-01-01", "temperature": 5.2, "quality": 0},
                    {"date": "2020-01-02", "temperature": 6.1, "quality": 0},
                    {"date": "2020-01-03", "temperature": 7.3, "quality": 0}
                ]
            }
        
        else:
            response_data = {"error": f"Path not found: {path}"}
            status = 404

        # 4. Envoi de la réponse finale
        send_json(status, response_data)

    except Exception as e:
        logger.error(f"Error in handler: {e}", exc_info=True)
        # En cas d'erreur fatale, on renvoie une 500 correctement formatée
        send_json(500, {"error": str(e)})
