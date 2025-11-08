"""
GenHack Climate - Model Training (Phase 1: Stub/No-op)

Phase 1: Placeholder only (no actual training)
Phase 2+: U-Net/SRGAN training for downscaling
"""

import logging
from typing import Dict, Any

from src.models import Manifest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def train_stage(config: Dict[str, Any], manifest: Manifest) -> Manifest:
    """
    Model training stage (Phase 1: no-op)
    
    Args:
        config: Pipeline configuration
        manifest: Input manifest
        
    Returns:
        Updated manifest
    """
    logger.info("🔄 TRAIN STAGE (NO-OP in Phase 1)")
    logger.info("   Phase 2+ will implement U-Net/SRGAN training")
    
    manifest.stage = "train"
    return manifest


if __name__ == "__main__":
    from models import Manifest, Period, Grid
    
    test_manifest = Manifest(
        city="paris",
        period=Period(start="2022-07-15", end="2022-07-17"),
        grid=Grid(crs="EPSG:3857", resolution_m=200),
        variables=["t2m"],
        stage="features",
        tiles=[]
    )
    
    result = train_stage({}, test_manifest)
    print(f"✅ Test complete: {result.stage}")
