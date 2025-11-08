"""
GenHack Climate - Model Evaluation (Phase 1: Stub)

Computes metrics comparing model outputs to ground truth.
Phase 1: Placeholder metrics only (no real evaluation)
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

from src.models import Manifest, Metrics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def evaluate_stage(config: Dict[str, Any], manifest: Manifest) -> Manifest:
    """
    Evaluation stage - compute model metrics
    
    Phase 1: Returns placeholder metrics
    Phase 2+: Real evaluation with ground truth
    
    Args:
        config: Pipeline configuration
        manifest: Input manifest
        
    Returns:
        Updated manifest with metrics
    """
    logger.info("🔄 EVALUATE STAGE (PLACEHOLDER)")
    
    # Phase 1: Placeholder metrics
    metrics = Metrics(
        rmse=None,
        mae=None,
        r2=None,
        bias=None,
        correlation=None,
        baseline="bicubic",
        baseline_rmse=None,
        improvement_percent=None,
        spatial_resolution_m=manifest.grid.resolution_m,
        sample_count=None
    )
    
    # Save metrics
    if manifest.paths and manifest.paths.exports:
        exports_dir = Path(manifest.paths.exports.replace("gs://", "/tmp/gcs/"))
        exports_dir.mkdir(parents=True, exist_ok=True)
        
        metrics_path = exports_dir / "metrics.json"
        with open(metrics_path, 'w') as f:
            json.dump(metrics.to_json(), f, indent=2)
        
        logger.info(f"✅ Metrics saved: {metrics_path}")
    
    manifest.stage = "evaluate"
    return manifest


if __name__ == "__main__":
    from models import Manifest, Period, Grid, Paths
    
    test_manifest = Manifest(
        city="paris",
        period=Period(start="2022-07-15", end="2022-07-17"),
        grid=Grid(crs="EPSG:3857", resolution_m=200),
        variables=["t2m"],
        stage="train",
        tiles=[],
        paths=Paths(exports="/tmp/genhack/exports/paris")
    )
    
    result = evaluate_stage({}, test_manifest)
    print(f"✅ Test complete: {result.stage}")
