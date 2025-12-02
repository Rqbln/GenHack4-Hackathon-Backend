#!/usr/bin/env python3
"""
Simple API Server using only Python standard library
For testing when FastAPI is not available
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load metrics from results file
METRICS_FILE = Path(__file__).parent.parent / "results" / "all_metrics.json"

def load_metrics():
    """Load metrics data from JSON file"""
    if METRICS_FILE.exists():
        try:
            with open(METRICS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load metrics: {e}")
    
    # Return mock data if file doesn't exist
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

class APIHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler for API"""
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        # CORS headers
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Content-Type': 'application/json'
        }
        
        # Route handling
        if path == '/' or path == '/health':
            response = {"status": "healthy", "version": "1.0.0", "service": "chronos-wxc-api"}
        elif path == '/api/stations':
            response = {
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
        elif path == '/api/metrics':
            metrics = load_metrics()
            response = metrics
        elif path == '/api/metrics/comparison':
            metrics = load_metrics()
            response = {
                "baseline": metrics.get("baseline_metrics", {}),
                "prithvi": metrics.get("prithvi_metrics", {}),
                "comparison": metrics.get("model_comparison", {})
            }
        elif path == '/api/metrics/advanced':
            metrics = load_metrics()
            response = metrics.get("advanced_metrics", {})
        elif path == '/api/validation/physics':
            metrics = load_metrics()
            response = metrics.get("physics_validation", {})
        elif path.startswith('/api/temperature'):
            lat = float(query_params.get('lat', [48.8566])[0])
            lon = float(query_params.get('lon', [2.3522])[0])
            date = query_params.get('date', ['2020-01-01'])[0]
            response = {
                "latitude": lat,
                "longitude": lon,
                "date": date,
                "temperature": 20.5,
                "source": "prithvi_wxc",
                "resolution": "100m"
            }
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            for key, value in headers.items():
                if key != 'Content-Type':
                    self.send_header(key, value)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
            return
        
        # Send response
        self.send_response(200)
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def log_message(self, format, *args):
        """Custom log format"""
        logger.info(f"{self.address_string()} - {format % args}")

def run_server(port=8000):
    """Run the API server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, APIHandler)
    logger.info(f"🚀 API Server started on http://localhost:{port}")
    logger.info(f"📊 Health check: http://localhost:{port}/health")
    logger.info(f"📡 Stations: http://localhost:{port}/api/stations")
    logger.info(f"📈 Metrics: http://localhost:{port}/api/metrics")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("\n🛑 Server stopped")
        httpd.server_close()

if __name__ == "__main__":
    run_server()

