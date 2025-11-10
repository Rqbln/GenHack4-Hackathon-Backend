"""
GenHack Climate - Pipeline Orchestrator

Main entry point for the heat downscaling pipeline.
Executes stages sequentially: ingest → preprocess → features → 
train → evaluate → indicators → publish → report
"""

import sys
import logging
import yaml
import click
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Import pipeline stages
from src.models import Manifest, Period, Grid, Mode, Paths
from src.ingest import ingest_stage
from src.preprocess import preprocess_stage
from src.features import features_stage
from src.train import train_stage
from src.evaluate import evaluate_stage
from src.indicators import indicators_stage
from src.publish import publish_stage
from src.report import report_stage

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load YAML configuration file"""
    logger.info(f"Loading configuration: {config_path}")
    with open(config_path) as f:
        config = yaml.safe_load(f)
    return config


def create_manifest(config: Dict[str, Any]) -> Manifest:
    """Create initial pipeline manifest from configuration"""
    manifest = Manifest(
        city=config["city"],
        period=Period(**config["period"]),
        grid=Grid(**config["grid"]),
        variables=config["variables"],
        stage="init",
        tiles=[],
        mode=Mode(**config.get("mode", {}))
    )
    
    # Setup GCS paths if PROJECT_ID is available
    import os
    project_id = os.getenv("PROJECT_ID", "genhack-heat-dev")
    
    # Replace {project} placeholder in paths
    gcs_config = config.get("gcs", {})
    manifest.paths = Paths(
        raw=gcs_config.get("raw", "").format(project=project_id),
        intermediate=gcs_config.get("intermediate", "").format(project=project_id),
        features=gcs_config.get("features", "").format(project=project_id),
        exports=gcs_config.get("exports", "").format(project=project_id)
    )
    
    return manifest


def run_pipeline(config_path: Path, stages: list = None) -> Manifest:
    """
    Run the complete pipeline
    
    Args:
        config_path: Path to YAML configuration
        stages: List of stages to run (None = all stages)
        
    Returns:
        Final manifest after all stages
    """
    logger.info("=" * 60)
    logger.info("GenHack Climate Heat Downscaling Pipeline")
    logger.info("=" * 60)
    
    # Load configuration
    config = load_config(config_path)
    
    # Create initial manifest
    manifest = create_manifest(config)
    
    logger.info(f"City: {manifest.city}")
    logger.info(f"Period: {manifest.period.start} to {manifest.period.end}")
    logger.info(f"Resolution: {manifest.grid.resolution_m}m")
    logger.info(f"Variables: {', '.join(manifest.variables)}")
    logger.info(f"Mode: {'DRY RUN (mock data)' if manifest.mode.dry_run else 'PRODUCTION'}")
    logger.info("-" * 60)
    
    # Define pipeline stages
    all_stages = [
        ("ingest", lambda: ingest_stage(config, manifest)),
        ("preprocess", lambda: preprocess_stage(config, manifest)),
        ("features", lambda: features_stage(config, manifest)),
        ("train", lambda: train_stage(config, manifest)),
        ("evaluate", lambda: evaluate_stage(config, manifest)),
        ("indicators", lambda: indicators_stage(config, manifest)),
        ("publish", lambda: publish_stage(config, manifest)),
        ("report", lambda: report_stage(config, manifest))
    ]
    
    # Filter stages if specified
    if stages:
        all_stages = [(name, func) for name, func in all_stages if name in stages]
    
    # Execute pipeline
    start_time = datetime.now()
    
    for stage_name, stage_func in all_stages:
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"Stage: {stage_name.upper()}")
            logger.info(f"{'='*60}")
            
            stage_start = datetime.now()
            manifest = stage_func()
            stage_duration = (datetime.now() - stage_start).total_seconds()
            
            logger.info(f"✅ {stage_name.upper()} complete ({stage_duration:.1f}s)")
            
        except Exception as e:
            logger.error(f"❌ {stage_name.upper()} failed: {e}")
            logger.exception("Full traceback:")
            sys.exit(1)
    
    # Pipeline complete
    total_duration = (datetime.now() - start_time).total_seconds()
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ PIPELINE COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total duration: {total_duration:.1f}s")
    logger.info(f"Final stage: {manifest.stage}")
    logger.info(f"Output: {manifest.paths.exports if manifest.paths else 'N/A'}")
    
    return manifest


@click.command()
@click.option(
    '--config',
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help='Path to YAML configuration file'
)
@click.option(
    '--stages',
    multiple=True,
    help='Specific stages to run (default: all)'
)
@click.option(
    '--dry-run',
    is_flag=True,
    help='Force dry-run mode (mock data)'
)
def main(config: Path, stages: tuple, dry_run: bool):
    """GenHack Climate Heat Downscaling Pipeline"""
    
    # Override dry-run if flag is set
    if dry_run:
        logger.info("⚠️  Forcing DRY-RUN mode (mock data)")
        import os
        os.environ['FORCE_DRY_RUN'] = 'true'
    
    try:
        manifest = run_pipeline(config, list(stages) if stages else None)
        logger.info("\n🎉 Success! Check outputs at:")
        if manifest.paths and manifest.paths.exports:
            logger.info(f"   {manifest.paths.exports}")
        sys.exit(0)
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Pipeline interrupted by user")
        sys.exit(130)
        
    except Exception as e:
        logger.error(f"\n❌ Pipeline failed: {e}")
        logger.exception("Full traceback:")
        sys.exit(1)


if __name__ == "__main__":
    main()
