#!/usr/bin/env python3
"""
Script de téléchargement des datasets GenHack 2025

Télécharge tous les datasets nécessaires depuis Google Drive :
- ERA5 Land Daily Statistics (2020-2025)
- Sentinel-2 NDVI (2019-2021)
- ECA&D Stations
- GADM Europe boundaries

Usage:
    python3 scripts/download_datasets.py [--output-dir datasets]
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    import gdown
    GDOWN_AVAILABLE = True
except ImportError:
    GDOWN_AVAILABLE = False
    logger.warning("gdown not installed. Install with: pip install gdown")


# Google Drive folder ID
GOOGLE_DRIVE_FOLDER_ID = "1_uMrrq63e0iYCFj8A6ehN58641sJZ2x1"

# Dataset file IDs (from Google Drive)
DATASET_FILES = {
    "ECA_blend_tx.zip": {
        "id": "1abc123...",  # À remplacer par le vrai ID
        "size_mb": 736,
        "description": "ECA&D weather stations data"
    },
    "gadm_410_europe.gpkg": {
        "id": "1def456...",  # À remplacer par le vrai ID
        "size_mb": 719,
        "description": "GADM administrative boundaries"
    }
}

# ERA5 files (24 files)
ERA5_FILES = [
    "2020_2m_temperature_daily_maximum.nc",
    "2020_total_precipitation_daily_mean.nc",
    "2020_10m_u_component_of_wind_daily_mean.nc",
    "2020_10m_v_component_of_wind_daily_mean.nc",
    # ... (autres années 2021-2025)
]

# Sentinel-2 NDVI files (8 files)
SENTINEL2_FILES = [
    "ndvi_2019-12-01_2020-03-01.tif",
    "ndvi_2020-03-01_2020-06-01.tif",
    "ndvi_2020-06-01_2020-09-01.tif",
    "ndvi_2020-09-01_2020-12-01.tif",
    "ndvi_2020-12-01_2021-03-01.tif",
    "ndvi_2021-03-01_2021-06-01.tif",
    "ndvi_2021-06-01_2021-09-01.tif",
    "ndvi_2021-09-01_2021-12-01.tif",
]


def download_file_from_drive(file_id: str, output_path: Path, description: str = "") -> bool:
    """
    Télécharge un fichier depuis Google Drive
    
    Args:
        file_id: Google Drive file ID
        output_path: Chemin de destination
        description: Description du fichier (pour les logs)
    
    Returns:
        True si succès, False sinon
    """
    if not GDOWN_AVAILABLE:
        logger.error("gdown is required. Install with: pip install gdown")
        return False
    
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        url = f"https://drive.google.com/uc?id={file_id}"
        logger.info(f"Downloading {description or output_path.name}...")
        logger.info(f"  URL: {url}")
        logger.info(f"  Destination: {output_path}")
        
        gdown.download(url, str(output_path), quiet=False)
        
        if output_path.exists():
            size_mb = output_path.stat().st_size / (1024 * 1024)
            logger.info(f"✅ Downloaded {output_path.name} ({size_mb:.1f} MB)")
            return True
        else:
            logger.error(f"❌ Download failed: {output_path.name}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error downloading {output_path.name}: {e}")
        return False


def download_folder_from_drive(folder_id: str, output_dir: Path) -> bool:
    """
    Télécharge un dossier complet depuis Google Drive
    
    Args:
        folder_id: Google Drive folder ID
        output_dir: Répertoire de destination
    
    Returns:
        True si succès, False sinon
    """
    if not GDOWN_AVAILABLE:
        logger.error("gdown is required. Install with: pip install gdown")
        return False
    
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        
        url = f"https://drive.google.com/drive/folders/{folder_id}"
        logger.info(f"Downloading folder from Google Drive...")
        logger.info(f"  URL: {url}")
        logger.info(f"  Destination: {output_dir}")
        
        gdown.download_folder(url, output=str(output_dir), quiet=False, use_cookies=False)
        
        logger.info(f"✅ Folder downloaded to {output_dir}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error downloading folder: {e}")
        return False


def check_existing_files(output_dir: Path) -> dict:
    """
    Vérifie quels fichiers existent déjà
    
    Returns:
        Dict avec statut de chaque fichier
    """
    status = {
        "era5": {"exists": False, "count": 0, "expected": 24},
        "sentinel2": {"exists": False, "count": 0, "expected": 8},
        "ecad": {"exists": False},
        "gadm": {"exists": False}
    }
    
    # Check ERA5
    era5_dir = output_dir / "main" / "derived-era5-land-daily-statistics"
    if era5_dir.exists():
        era5_files = list(era5_dir.glob("*.nc"))
        status["era5"]["count"] = len(era5_files)
        status["era5"]["exists"] = len(era5_files) > 0
    
    # Check Sentinel-2
    sentinel2_dir = output_dir / "main" / "sentinel2_ndvi"
    if sentinel2_dir.exists():
        sentinel2_files = list(sentinel2_dir.glob("*.tif"))
        status["sentinel2"]["count"] = len(sentinel2_files)
        status["sentinel2"]["exists"] = len(sentinel2_files) > 0
    
    # Check ECA&D
    ecad_zip = output_dir / "ECA_blend_tx.zip"
    status["ecad"]["exists"] = ecad_zip.exists()
    
    # Check GADM
    gadm_gpkg = output_dir / "gadm_410_europe.gpkg"
    status["gadm"]["exists"] = gadm_gpkg.exists()
    
    return status


def main():
    parser = argparse.ArgumentParser(
        description="Download GenHack 2025 datasets from Google Drive"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="datasets",
        help="Output directory for datasets (default: datasets)"
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip files that already exist"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check which files exist, don't download"
    )
    
    args = parser.parse_args()
    
    project_root = Path(__file__).parent.parent
    output_dir = project_root / args.output_dir
    
    logger.info("=" * 60)
    logger.info("GenHack 2025 - Dataset Downloader")
    logger.info("=" * 60)
    logger.info(f"Output directory: {output_dir}")
    logger.info("")
    
    # Check existing files
    status = check_existing_files(output_dir)
    
    logger.info("📊 Current status:")
    logger.info(f"  ERA5: {status['era5']['count']}/{status['era5']['expected']} files")
    logger.info(f"  Sentinel-2: {status['sentinel2']['count']}/{status['sentinel2']['expected']} files")
    logger.info(f"  ECA&D: {'✅' if status['ecad']['exists'] else '❌'}")
    logger.info(f"  GADM: {'✅' if status['gadm']['exists'] else '❌'}")
    logger.info("")
    
    if args.check_only:
        logger.info("Check-only mode. Exiting.")
        return 0
    
    if not GDOWN_AVAILABLE:
        logger.error("")
        logger.error("❌ gdown is not installed.")
        logger.error("   Install it with: pip install gdown")
        logger.error("")
        logger.error("Alternative: Download manually from:")
        logger.error(f"   https://drive.google.com/drive/folders/{GOOGLE_DRIVE_FOLDER_ID}")
        return 1
    
    # Download folder
    logger.info("📥 Downloading datasets from Google Drive...")
    logger.info("")
    logger.info("⚠️  Note: This will download ~12 GB of data.")
    logger.info("   Make sure you have enough disk space and a stable internet connection.")
    logger.info("")
    
    success = download_folder_from_drive(GOOGLE_DRIVE_FOLDER_ID, output_dir)
    
    if success:
        logger.info("")
        logger.info("=" * 60)
        logger.info("✅ Download completed!")
        logger.info("=" * 60)
        
        # Check again
        status_after = check_existing_files(output_dir)
        logger.info("")
        logger.info("📊 Final status:")
        logger.info(f"  ERA5: {status_after['era5']['count']}/{status_after['era5']['expected']} files")
        logger.info(f"  Sentinel-2: {status_after['sentinel2']['count']}/{status_after['sentinel2']['expected']} files")
        logger.info(f"  ECA&D: {'✅' if status_after['ecad']['exists'] else '❌'}")
        logger.info(f"  GADM: {'✅' if status_after['gadm']['exists'] else '❌'}")
        
        return 0
    else:
        logger.error("")
        logger.error("❌ Download failed. Please try again or download manually.")
        logger.error(f"   Manual download: https://drive.google.com/drive/folders/{GOOGLE_DRIVE_FOLDER_ID}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

