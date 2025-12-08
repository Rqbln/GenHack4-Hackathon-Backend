#!/usr/bin/env python3
"""
Script pour exécuter l'ETL avec les vraies données

Ce script charge les vraies données depuis /datasets/ et exécute
le pipeline ETL complet.
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.etl import ETLPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function to run ETL with real data"""
    
    # Get project root (parent of GenHack4-Hackathon-Vertex)
    project_root = Path(__file__).parent.parent.parent
    datasets_dir = project_root / "datasets"
    
    # Define paths to real data
    era5_dir = datasets_dir / "main" / "derived-era5-land-daily-statistics"
    sentinel2_dir = datasets_dir / "main" / "sentinel2_ndvi"
    ecad_zip = datasets_dir / "ECA_blend_tx.zip"
    gadm_gpkg = datasets_dir / "main" / "gadm_410_europe.gpkg"
    
    # Output directory
    output_dir = project_root / "GenHack4-Hackathon-Vertex" / "data" / "processed"
    
    # Verify all input files exist
    logger.info("=" * 60)
    logger.info("Vérification des fichiers de données")
    logger.info("=" * 60)
    
    missing_files = []
    
    if not era5_dir.exists():
        missing_files.append(f"ERA5 directory: {era5_dir}")
    else:
        era5_files = list(era5_dir.glob("*.nc"))
        logger.info(f"✅ ERA5: {len(era5_files)} fichiers trouvés")
    
    if not sentinel2_dir.exists():
        missing_files.append(f"Sentinel-2 directory: {sentinel2_dir}")
    else:
        ndvi_files = list(sentinel2_dir.glob("*.tif"))
        logger.info(f"✅ Sentinel-2 NDVI: {len(ndvi_files)} fichiers trouvés")
    
    if not ecad_zip.exists():
        # Try alternative location
        ecad_zip_alt = datasets_dir / "ECA_blend_tx" / "ECA_blend_tx.zip"
        if ecad_zip_alt.exists():
            ecad_zip = ecad_zip_alt
            logger.info(f"✅ ECA&D: trouvé à {ecad_zip}")
        else:
            missing_files.append(f"ECA&D ZIP: {ecad_zip} ou {ecad_zip_alt}")
    else:
        logger.info(f"✅ ECA&D: {ecad_zip} ({ecad_zip.stat().st_size / 1024 / 1024:.1f} MB)")
    
    if not gadm_gpkg.exists():
        # Try alternative location
        gadm_gpkg_alt = datasets_dir / "gadm_410_europe.gpkg"
        if gadm_gpkg_alt.exists():
            gadm_gpkg = gadm_gpkg_alt
            logger.info(f"✅ GADM: trouvé à {gadm_gpkg}")
        else:
            missing_files.append(f"GADM GeoPackage: {gadm_gpkg} ou {gadm_gpkg_alt}")
    else:
        logger.info(f"✅ GADM: {gadm_gpkg} ({gadm_gpkg.stat().st_size / 1024 / 1024:.1f} MB)")
    
    if missing_files:
        logger.error("❌ Fichiers manquants:")
        for f in missing_files:
            logger.error(f"   - {f}")
        logger.error("\nVeuillez télécharger les données manquantes.")
        return 1
    
    logger.info("=" * 60)
    logger.info("Tous les fichiers sont présents. Démarrage de l'ETL...")
    logger.info("=" * 60)
    
    # Initialize ETL pipeline
    etl = ETLPipeline(
        era5_dir=era5_dir,
        sentinel2_dir=sentinel2_dir,
        ecad_zip=ecad_zip,
        gadm_gpkg=gadm_gpkg,
        output_dir=output_dir,
        city_name="Paris",
        country_code="FRA"
    )
    
    # Run ETL with a subset of years first (for testing)
    # You can expand to all years later
    try:
        results = etl.run_etl(
            years=[2020, 2021],  # Start with 2 years for testing
            variables=["t2m_max", "precipitation", "u10", "v10"],
            output_format="zarr"
        )
        
        logger.info("=" * 60)
        logger.info("✅ ETL terminé avec succès!")
        logger.info("=" * 60)
        logger.info(f"📁 Résultats sauvegardés dans: {output_dir}")
        logger.info(f"   - ERA5: era5_aligned.zarr")
        logger.info(f"   - Stations: stations.geojson")
        logger.info(f"   - Boundary: city_boundary.geojson")
        logger.info(f"   - NDVI metadata: ndvi_metadata.json")
        
        # Print summary
        logger.info("\n📊 Résumé:")
        logger.info(f"   - Stations trouvées: {len(results['stations'])}")
        logger.info(f"   - Périodes NDVI: {len(results['ndvi'])}")
        logger.info(f"   - Variables ERA5: {list(results['era5'].data_vars)}")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'exécution de l'ETL: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())


