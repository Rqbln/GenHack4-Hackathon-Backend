"""
FastAPI Backend API

Lightweight REST API for serving model predictions and metrics
to the frontend dashboard.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="GenHack 2025 - Chronos-WxC API",
    description="API for climate downscaling predictions and metrics",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load metrics from results file
METRICS_FILE = Path(__file__).parent.parent / "results" / "all_metrics.json"
metrics_data = None

def load_metrics():
    """Load metrics data from JSON file"""
    global metrics_data
    if metrics_data is None:
        if METRICS_FILE.exists():
            try:
                with open(METRICS_FILE, 'r') as f:
                    metrics_data = json.load(f)
                logger.info("Metrics data loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load metrics: {e}")
                metrics_data = {}
        else:
            # Return mock data if file doesn't exist
            logger.warning(f"Metrics file not found at {METRICS_FILE}, using mock data")
            metrics_data = {
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
    return metrics_data

# Pydantic models
class Station(BaseModel):
    staid: int
    staname: str
    country: str
    latitude: float
    longitude: float
    elevation: float

class StationData(BaseModel):
    station: Station
    date: str
    temperature: float
    quality: int

class HealthResponse(BaseModel):
    status: str
    version: str

# API Routes
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return HealthResponse(status="healthy", version="1.0.0")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "chronos-wxc-api"}

@app.get("/api/stations")
async def get_stations():
    """Get list of weather stations"""
    # Mock data - in production, load from database
    stations = [
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
    return {"stations": stations}

@app.get("/api/stations/{station_id}/data")
async def get_station_data(station_id: int, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Get time series data for a specific station"""
    # Mock data - in production, query database
    return {
        "station_id": station_id,
        "data": [],
        "message": "Mock data - implement database query"
    }

@app.get("/api/metrics")
async def get_metrics():
    """Get model metrics"""
    metrics = load_metrics()
    if not metrics:
        raise HTTPException(status_code=404, detail="Metrics not available")
    return metrics

@app.get("/api/metrics/comparison")
async def get_metrics_comparison():
    """Get metrics comparison (Baseline vs Prithvi)"""
    metrics = load_metrics()
    if not metrics:
        raise HTTPException(status_code=404, detail="Metrics not available")
    
    return {
        "baseline": metrics.get("baseline_metrics", {}),
        "prithvi": metrics.get("prithvi_metrics", {}),
        "comparison": metrics.get("model_comparison", {})
    }

@app.get("/api/metrics/advanced")
async def get_advanced_metrics():
    """Get advanced metrics (Perkins Score, Spectral Analysis)"""
    metrics = load_metrics()
    if not metrics:
        raise HTTPException(status_code=404, detail="Metrics not available")
    
    return metrics.get("advanced_metrics", {})

@app.get("/api/validation/physics")
async def get_physics_validation():
    """Get physics validation results"""
    metrics = load_metrics()
    if not metrics:
        raise HTTPException(status_code=404, detail="Metrics not available")
    
    return metrics.get("physics_validation", {})

@app.get("/api/temperature")
async def get_temperature(lat: float, lon: float, date: Optional[str] = None):
    """Get temperature prediction for a specific location and date"""
    # Mock data - in production, query model predictions
    return {
        "latitude": lat,
        "longitude": lon,
        "date": date or "2020-01-01",
        "temperature": 20.5,
        "source": "prithvi_wxc",
        "resolution": "100m"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

