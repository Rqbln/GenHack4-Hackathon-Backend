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

def handler(request):
    """
    Handler Vercel robuste.
    Capture toutes les erreurs pour éviter le crash 'Invocation Failed'.
    """
    
    # 1. Fonction interne pour envoyer la réponse
    def send_response(status, data):
        request.send_response(status)
        request.send_header('Access-Control-Allow-Origin', '*')
        request.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        request.send_header('Access-Control-Allow-Headers', 'Content-Type')
        request.send_header('Content-Type', 'application/json')
        request.end_headers()
        try:
            request.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
        except Exception as write_error:
            # Fallback critique si l'écriture échoue
            print(f"Critical write error: {write_error}")

    # 2. Bloc de sécurité global
    try:
        # --- INITIALISATION LAZY (Pour éviter le crash au boot) ---
        # On calcule les chemins ICI, pas en global
        try:
            # Si le fichier est dans api/index.py, parent.parent = racine
            BASE_DIR = Path(__file__).parent.parent
            METRICS_FILE = BASE_DIR / "results" / "all_metrics.json"
            STATIONS_FILE = BASE_DIR / "data" / "processed" / "stations.geojson"
        except Exception as e:
            # Fallback si le système de fichier est différent
            BASE_DIR = Path("/tmp")
            METRICS_FILE = Path("/dev/null")
            STATIONS_FILE = Path("/dev/null")
            logger.warning(f"Path initialization warning: {e}")

        # --- LOGIQUE HELPER ---
        def load_metrics():
            if METRICS_FILE.exists():
                try:
                    with open(METRICS_FILE, 'r') as f:
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
                        return {"stations": stations}
                except Exception:
                    pass
            return {"stations": [{"staid": 1, "staname": "Mock Station Paris"}]}

        # --- TRAITEMENT DE LA REQUÊTE ---
        
        # Gestion safe de la méthode HTTP
        # request peut être un objet ou un dict selon le contexte de test/prod
        method = getattr(request, 'command', 'GET')
        raw_path = getattr(request, 'path', '/')
        
        # Parsing de l'URL
        parsed_path = urlparse(raw_path).path

        if method == 'OPTIONS':
            send_response(200, {})
            return

        # Routing
        response_data = {}
        status_code = 200

        if parsed_path == '/' or parsed_path == '/health':
            response_data = {
                "status": "healthy", 
                "python_version": os.sys.version,
                "base_dir": str(BASE_DIR)
            }
        elif '/api/stations' in parsed_path:
            response_data = load_stations()
        elif '/api/metrics/comparison' in parsed_path:
            metrics = load_metrics()
            baseline = metrics.get("baseline_metrics", {})
            prithvi = metrics.get("prithvi_metrics", {})
            # Calcul simple si données présentes
            if baseline.get("rmse") and prithvi.get("rmse"):
                response_data = {
                   "rmse_improvement": {
                       "absolute": round(baseline["rmse"] - prithvi["rmse"], 2),
                       "percentage": round((baseline["rmse"] - prithvi["rmse"]) / baseline["rmse"] * 100, 1)
                   }
                }
            else:
                response_data = metrics.get("model_comparison", {})
        elif '/api/metrics/advanced' in parsed_path:
            metrics = load_metrics()
            response_data = metrics.get("advanced_metrics", {})
        elif '/api/validation/physics' in parsed_path:
            metrics = load_metrics()
            response_data = metrics.get("physics_validation", {})
        elif '/api/metrics' in parsed_path:
            response_data = load_metrics()
        elif '/api/temperature' in parsed_path:
            # Mock temperature data for now
            response_data = {
                "data": [
                    {"date": "2020-01-01", "temperature": 5.2, "quality": 0},
                    {"date": "2020-01-02", "temperature": 6.1, "quality": 0},
                    {"date": "2020-01-03", "temperature": 7.3, "quality": 0}
                ]
            }
        else:
            status_code = 404
            response_data = {"error": "Not Found", "path": parsed_path}

        send_response(status_code, response_data)

    except Exception as e:
        # C'est ICI qu'on sauve l'invocation failed
        # On capture l'erreur et on l'affiche au lieu de crasher la fonction
        error_details = traceback.format_exc()
        logger.error(f"Handler failed: {e}\n{error_details}")
        send_response(500, {
            "error": "Internal Server Error", 
            "message": str(e),
            "traceback": error_details.split('\n')
        })
