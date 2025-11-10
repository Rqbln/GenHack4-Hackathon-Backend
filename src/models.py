"""
GenHack Climate - Common data models and utilities
Pydantic models matching JSON schemas for type safety
"""

from datetime import datetime, UTC
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Period(BaseModel):
    """Time period for analysis"""
    start: str = Field(..., description="Start date (YYYY-MM-DD)")
    end: str = Field(..., description="End date (YYYY-MM-DD)")


class Grid(BaseModel):
    """Target grid specification"""
    crs: str = Field(..., description="Coordinate reference system")
    resolution_m: float = Field(..., description="Spatial resolution in meters")


class Tile(BaseModel):
    """Spatial tile for large area processing"""
    id: str
    bbox: List[float] = Field(..., min_length=4, max_length=4)


class Mode(BaseModel):
    """Processing mode configuration"""
    dry_run: bool = False


class Paths(BaseModel):
    """GCS paths to pipeline data"""
    raw: Optional[str] = None
    intermediate: Optional[str] = None
    features: Optional[str] = None
    exports: Optional[str] = None


class Manifest(BaseModel):
    """Pipeline manifest - passed between stages"""
    city: str
    period: Period
    grid: Grid
    tiles: List[Tile] = []
    variables: List[str]
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    stage: str
    mode: Optional[Mode] = Mode()
    paths: Optional[Paths] = Paths()

    def to_json(self) -> Dict[str, Any]:
        """Export to JSON-serializable dict"""
        return self.model_dump(mode='json')


class Bounds(BaseModel):
    """Geographic bounds"""
    minx: float
    miny: float
    maxx: float
    maxy: float


class RasterMetadata(BaseModel):
    """Raster file metadata"""
    crs: str
    transform: List[float] = Field(..., min_length=6, max_length=6)
    width: int = Field(..., gt=0)
    height: int = Field(..., gt=0)
    nodata: Optional[float] = None
    dtype: str
    units: Optional[str] = None
    spatial_ref: Optional[str] = None
    bounds: Optional[Bounds] = None
    band_count: Optional[int] = 1
    band_names: Optional[List[str]] = None

    def to_json(self) -> Dict[str, Any]:
        """Export to JSON-serializable dict"""
        return self.model_dump(mode='json')


class Metrics(BaseModel):
    """Model evaluation metrics"""
    rmse: Optional[float] = None
    mae: Optional[float] = None
    r2: Optional[float] = None
    bias: Optional[float] = None
    correlation: Optional[float] = None
    baseline: str = "bicubic"
    baseline_rmse: Optional[float] = None
    improvement_percent: Optional[float] = None
    spatial_resolution_m: Optional[float] = None
    sample_count: Optional[int] = None
    evaluation_date: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_json(self) -> Dict[str, Any]:
        """Export to JSON-serializable dict"""
        return self.model_dump(mode='json')


class Indicators(BaseModel):
    """Climate heat indicators"""
    intensity: Optional[float] = None
    duration: Optional[int] = None
    extent_km2: Optional[float] = None
    max_temperature_c: Optional[float] = None
    mean_temperature_c: Optional[float] = None
    threshold_c: float = 30.0
    days_above_threshold: Optional[int] = None
    affected_population_estimate: Optional[int] = None
    urban_heat_island_intensity_c: Optional[float] = None
    percentile_95: Optional[float] = None
    percentile_99: Optional[float] = None
    computed_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_json(self) -> Dict[str, Any]:
        """Export to JSON-serializable dict"""
        return self.model_dump(mode='json')
