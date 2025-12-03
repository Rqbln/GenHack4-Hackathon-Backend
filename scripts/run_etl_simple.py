#!/usr/bin/env python3
"""
Script pour exécuter l'ETL simplifié (sans rasterio)

Cette version fonctionne avec uniquement xarray et geopandas.
"""

import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.etl_simple import ETLPipelineSimple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    project_root = Path(__file__).parent.parent.parent
    datasets_dir = project_root / "datasets"
    
    era5_dir = datasets_dir / "main" / "derived-era5-land-daily-statistics"
    sentinel2_dir = datasets_dir / "main" / "sentinel2_ndvi"
    ecad_zip = datasets_dir / "ECA_blend_tx.zip"
    # Try multiple locations for GADM
    gadm_gpkg = None
    for path in [
        datasets_dir / "main" / "gadm_410_europe.gpkg",
        datasets_dir / "gadm_410_europe.gpkg",
    ]:
        if path.exists() and path.stat().st_size > 0:
            gadm_gpkg = path
            break
    
    if gadm_gpkg is None:
        logger.error(f"GADM GeoPackage not found or empty")
        logger.info("Note: GADM file may need to be downloaded separately")
        logger.info("For now, we'll skip GADM and use a default bounding box for Paris")
        gadm_gpkg = None
    
    output_dir = project_root / "GenHack4-Hackathon-Vertex" / "data" / "processed"
    
    # Verify files
    if not era5_dir.exists():
        logger.error(f"ERA5 directory not found: {era5_dir}")
        return 1
    
    if not ecad_zip.exists():
        logger.error(f"ECA&D ZIP not found: {ecad_zip}")
        return 1
    
    # GADM is optional - we can use default bbox
    
    # Initialize ETL
    etl = ETLPipelineSimple(
        era5_dir=era5_dir,
        sentinel2_dir=sentinel2_dir,
        ecad_zip=ecad_zip,
        output_dir=output_dir,
        city_name="Paris",
        country_code="FRA",
        gadm_gpkg=gadm_gpkg
    )
    
    try:
        results = etl.run_etl_simple(
            years=[2020, 2021],
            variables=["t2m_max", "precipitation", "u10", "v10"]
        )
        
        logger.info("\n📊 Résumé des résultats:")
        logger.info(f"   - Stations: {results['summary']['n_stations']}")
        logger.info(f"   - Variables ERA5: {', '.join(results['summary']['era5_variables'])}")
        logger.info(f"   - Dimensions ERA5: {results['summary']['era5_shape']}")
        logger.info(f"   - Fichiers sauvegardés dans: {output_dir}")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Erreur: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())

