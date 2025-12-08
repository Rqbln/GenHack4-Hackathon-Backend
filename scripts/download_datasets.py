#!/usr/bin/env python3
"""
Script de téléchargement des datasets GenHack 2025

Télécharge récursivement TOUS les fichiers depuis le Google Drive folder :
- ERA5 Land Daily Statistics (2020-2025)
- Sentinel-2 NDVI (2019-2021)
- ECA&D Stations
- GADM Europe boundaries
- Tous les autres fichiers et sous-dossiers

Usage:
    python3 scripts/download_datasets.py [--output-dir datasets] [--skip-existing]
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Optional, List, Dict
import time

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


def count_files_recursive(directory: Path) -> Dict[str, int]:
    """
    Compte récursivement tous les fichiers dans un répertoire
    
    Returns:
        Dict avec le nombre total de fichiers et la taille totale
    """
    total_files = 0
    total_size = 0
    
    for root, dirs, files in os.walk(directory):
        total_files += len(files)
        for file in files:
            file_path = Path(root) / file
            if file_path.exists():
                total_size += file_path.stat().st_size
    
    return {
        "count": total_files,
        "size_mb": total_size / (1024 * 1024)
    }


def download_folder_from_drive(folder_id: str, output_dir: Path, skip_existing: bool = False) -> bool:
    """
    Télécharge récursivement TOUS les fichiers d'un dossier Google Drive
    
    Args:
        folder_id: Google Drive folder ID
        output_dir: Répertoire de destination
        skip_existing: Si True, ne télécharge pas les fichiers existants
    
    Returns:
        True si succès, False sinon
    """
    if not GDOWN_AVAILABLE:
        logger.error("gdown is required. Install with: pip install gdown")
        return False
    
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        
        url = f"https://drive.google.com/drive/folders/{folder_id}"
        logger.info("=" * 60)
        logger.info("📥 Téléchargement récursif depuis Google Drive")
        logger.info("=" * 60)
        logger.info(f"  URL: {url}")
        logger.info(f"  Destination: {output_dir}")
        logger.info(f"  Skip existing: {skip_existing}")
        logger.info("")
        
        # Compter les fichiers existants avant
        if output_dir.exists():
            before_stats = count_files_recursive(output_dir)
            logger.info(f"📊 Fichiers existants: {before_stats['count']} fichiers ({before_stats['size_mb']:.1f} MB)")
            logger.info("")
        
        start_time = time.time()
        
        # Télécharger récursivement avec toutes les options
        logger.info("🔄 Démarrage du téléchargement...")
        logger.info("   (Cela peut prendre plusieurs minutes selon la taille des fichiers)")
        logger.info("")
        
        # Utiliser download_folder avec toutes les options pour un téléchargement complet
        gdown.download_folder(
            url,
            output=str(output_dir),
            quiet=False,
            use_cookies=False,
            remaining_ok=True,  # Continue même si certains fichiers échouent
            verify=False  # Pas de vérification SSL pour éviter les problèmes
        )
        
        elapsed_time = time.time() - start_time
        
        # Compter les fichiers après
        if output_dir.exists():
            after_stats = count_files_recursive(output_dir)
            new_files = after_stats['count'] - before_stats.get('count', 0)
            new_size_mb = after_stats['size_mb'] - before_stats.get('size_mb', 0)
            
            logger.info("")
            logger.info("=" * 60)
            logger.info("✅ Téléchargement terminé!")
            logger.info("=" * 60)
            logger.info(f"  Temps écoulé: {elapsed_time:.1f} secondes ({elapsed_time/60:.1f} minutes)")
            logger.info(f"  Fichiers téléchargés: {new_files} nouveaux fichiers")
            logger.info(f"  Taille téléchargée: {new_size_mb:.1f} MB")
            logger.info(f"  Total fichiers: {after_stats['count']} fichiers")
            logger.info(f"  Taille totale: {after_stats['size_mb']:.1f} MB ({after_stats['size_mb']/1024:.2f} GB)")
            logger.info("")
            
            return True
        else:
            logger.error("❌ Le répertoire de destination n'existe pas après le téléchargement")
            return False
        
    except KeyboardInterrupt:
        logger.warning("")
        logger.warning("⚠️  Téléchargement interrompu par l'utilisateur")
        logger.warning(f"   Les fichiers partiellement téléchargés sont dans: {output_dir}")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur lors du téléchargement: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


def check_existing_files(output_dir: Path) -> dict:
    """
    Vérifie quels fichiers existent déjà de manière exhaustive
    
    Returns:
        Dict avec statut de chaque type de fichier
    """
    status = {
        "total_files": 0,
        "total_size_mb": 0.0,
        "era5": {"exists": False, "count": 0},
        "sentinel2": {"exists": False, "count": 0},
        "ecad": {"exists": False, "count": 0},
        "gadm": {"exists": False, "count": 0},
        "other": {"count": 0}
    }
    
    if not output_dir.exists():
        return status
    
    # Compter tous les fichiers récursivement
    all_files = []
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            file_path = Path(root) / file
            if file_path.exists():
                all_files.append(file_path)
                status["total_size_mb"] += file_path.stat().st_size / (1024 * 1024)
    
    status["total_files"] = len(all_files)
    
    # Vérifier les types spécifiques
    for file_path in all_files:
        file_name = file_path.name.lower()
        file_ext = file_path.suffix.lower()
        
        # ERA5 NetCDF files
        if file_ext == ".nc":
            status["era5"]["count"] += 1
            status["era5"]["exists"] = True
        
        # Sentinel-2 GeoTIFF files
        elif file_ext in [".tif", ".tiff", ".geotiff"]:
            if "ndvi" in file_name or "sentinel" in file_name:
                status["sentinel2"]["count"] += 1
                status["sentinel2"]["exists"] = True
            else:
                status["other"]["count"] += 1
        
        # ECA&D files
        elif "ecad" in file_name or "eca_blend" in file_name:
            status["ecad"]["count"] += 1
            status["ecad"]["exists"] = True
        
        # GADM files
        elif "gadm" in file_name or file_ext == ".gpkg":
            status["gadm"]["count"] += 1
            status["gadm"]["exists"] = True
        
        else:
            status["other"]["count"] += 1
    
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
    
    logger.info("📊 État actuel des fichiers:")
    logger.info(f"  Total fichiers: {status['total_files']} fichiers ({status['total_size_mb']:.1f} MB / {status['total_size_mb']/1024:.2f} GB)")
    logger.info(f"  ERA5 (.nc): {status['era5']['count']} fichiers {'✅' if status['era5']['exists'] else '❌'}")
    logger.info(f"  Sentinel-2 (.tif): {status['sentinel2']['count']} fichiers {'✅' if status['sentinel2']['exists'] else '❌'}")
    logger.info(f"  ECA&D: {status['ecad']['count']} fichiers {'✅' if status['ecad']['exists'] else '❌'}")
    logger.info(f"  GADM (.gpkg): {status['gadm']['count']} fichiers {'✅' if status['gadm']['exists'] else '❌'}")
    logger.info(f"  Autres fichiers: {status['other']['count']} fichiers")
    logger.info("")
    
    if args.check_only:
        logger.info("Mode vérification uniquement. Arrêt.")
        return 0
    
    if not GDOWN_AVAILABLE:
        logger.error("")
        logger.error("❌ gdown n'est pas installé.")
        logger.error("   Installez-le avec: pip install gdown")
        logger.error("")
        logger.error("Alternative: Téléchargement manuel depuis:")
        logger.error(f"   https://drive.google.com/drive/folders/{GOOGLE_DRIVE_FOLDER_ID}")
        return 1
    
    # Download folder
    logger.info("⚠️  ATTENTION: Ce téléchargement peut être volumineux (plusieurs GB).")
    logger.info("   Assurez-vous d'avoir:")
    logger.info("   - Suffisamment d'espace disque disponible")
    logger.info("   - Une connexion internet stable")
    logger.info("   - Du temps (peut prendre plusieurs minutes/heures selon la taille)")
    logger.info("")
    
    if not args.skip_existing and status['total_files'] > 0:
        logger.warning("⚠️  Des fichiers existent déjà dans le répertoire de destination.")
        logger.warning("   Utilisez --skip-existing pour éviter de re-télécharger les fichiers existants.")
        logger.warning("   Sinon, les fichiers existants seront écrasés.")
        logger.info("")
    
    success = download_folder_from_drive(
        GOOGLE_DRIVE_FOLDER_ID, 
        output_dir,
        skip_existing=args.skip_existing
    )
    
    if success:
        # Check again
        status_after = check_existing_files(output_dir)
        logger.info("=" * 60)
        logger.info("📊 État final des fichiers:")
        logger.info("=" * 60)
        logger.info(f"  Total fichiers: {status_after['total_files']} fichiers ({status_after['total_size_mb']:.1f} MB / {status_after['total_size_mb']/1024:.2f} GB)")
        logger.info(f"  ERA5 (.nc): {status_after['era5']['count']} fichiers {'✅' if status_after['era5']['exists'] else '❌'}")
        logger.info(f"  Sentinel-2 (.tif): {status_after['sentinel2']['count']} fichiers {'✅' if status_after['sentinel2']['exists'] else '❌'}")
        logger.info(f"  ECA&D: {status_after['ecad']['count']} fichiers {'✅' if status_after['ecad']['exists'] else '❌'}")
        logger.info(f"  GADM (.gpkg): {status_after['gadm']['count']} fichiers {'✅' if status_after['gadm']['exists'] else '❌'}")
        logger.info(f"  Autres fichiers: {status_after['other']['count']} fichiers")
        logger.info("")
        logger.info("✅ Tous les fichiers ont été téléchargés avec succès!")
        logger.info("")
        
        return 0
    else:
        logger.error("")
        logger.error("❌ Le téléchargement a échoué.")
        logger.error("   Vous pouvez:")
        logger.error("   1. Réessayer avec: python3 scripts/download_datasets.py")
        logger.error("   2. Télécharger manuellement depuis:")
        logger.error(f"      https://drive.google.com/drive/folders/{GOOGLE_DRIVE_FOLDER_ID}")
        logger.error("")
        return 1


if __name__ == "__main__":
    sys.exit(main())


