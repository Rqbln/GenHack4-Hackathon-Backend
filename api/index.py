"""
Vercel Serverless Function for GenHack API
Adapted from api_simple.py for Vercel deployment

Vercel Python functions receive a request object and return a response dict
"""

import json
from pathlib import Path
import logging

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

# Vercel Python serverless function handler
# Vercel passes request as an object with 'path', 'method', 'headers', 'body', etc.
def handler(request):
    """Vercel serverless function handler"""
    try:
        # Extract path and method from request
        # Vercel passes the request as an object with attributes
        if hasattr(request, 'path'):
            path = request.path
            method = request.method if hasattr(request, 'method') else 'GET'
        elif isinstance(request, dict):
            path = request.get('path', '/')
            method = request.get('method', 'GET')
        else:
            # Try to get from request object attributes
            path = getattr(request, 'path', '/')
            method = getattr(request, 'method', 'GET')
        
        # CORS headers
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Content-Type': 'application/json'
        }
        
        # Handle OPTIONS (CORS preflight)
        if method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': ''
            }
        
        # Route handling
        if path == '/' or path == '/health':
            response = {"status": "healthy", "version": "1.0.0", "service": "chronos-wxc-api"}
        elif path == '/api/stations':
            response = load_stations()
        elif path == '/api/metrics':
            metrics = load_metrics()
            response = {
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
            
            comparison = {}
            if baseline.get("rmse") and prithvi.get("rmse"):
                comparison = {
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
                comparison = metrics.get("model_comparison", {})
            
            response = comparison
        elif path == '/api/metrics/advanced':
            metrics = load_metrics()
            response = metrics.get("advanced_metrics", {})
        elif path == '/api/validation/physics':
            metrics = load_metrics()
            response = metrics.get("physics_validation", {})
        elif path.startswith('/api/temperature'):
            # Mock temperature data for now
            response = {
                "data": [
                    {"date": "2020-01-01", "temperature": 5.2, "quality": 0},
                    {"date": "2020-01-02", "temperature": 6.1, "quality": 0},
                    {"date": "2020-01-03", "temperature": 7.3, "quality": 0}
                ]
            }
        else:
            response = {"error": "Not found"}
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps(response)
            }
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(response, indent=2)
        }
    except Exception as e:
        logger.error(f"Error in handler: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({"error": str(e)})
        }
