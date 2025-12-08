#!/usr/bin/env python3
"""
Script de vérification des vraies données

Vérifie que tous les fichiers de données sont présents et accessibles
sans nécessiter les dépendances lourdes (xarray, geopandas, etc.)
"""

import sys
from pathlib import Path
import json

def check_files():
    """Vérifie la présence des fichiers de données"""
    
    # Get project root
    project_root = Path(__file__).parent.parent.parent
    datasets_dir = project_root / "datasets"
    
    print("=" * 60)
    print("Vérification des Fichiers de Données")
    print("=" * 60)
    print()
    
    all_ok = True
    
    # 1. ERA5
    print("1. ERA5 Land Daily Statistics")
    era5_dir = datasets_dir / "main" / "derived-era5-land-daily-statistics"
    if era5_dir.exists():
        era5_files = sorted(list(era5_dir.glob("*.nc")))
        print(f"   ✅ Répertoire trouvé: {era5_dir}")
        print(f"   ✅ {len(era5_files)} fichiers NetCDF trouvés")
        
        # Check for key files
        required_vars = ["t2m_max", "precipitation", "u10", "v10"]
        years = [2020, 2021, 2022]
        missing = []
        for year in years:
            for var in required_vars:
                if var == "t2m_max":
                    fname = f"{year}_2m_temperature_daily_maximum.nc"
                elif var == "precipitation":
                    fname = f"{year}_total_precipitation_daily_mean.nc"
                elif var == "u10":
                    fname = f"{year}_10m_u_component_of_wind_daily_mean.nc"
                elif var == "v10":
                    fname = f"{year}_10m_v_component_of_wind_daily_mean.nc"
                
                if not (era5_dir / fname).exists():
                    missing.append(fname)
        
        if missing:
            print(f"   ⚠️  Fichiers manquants pour 2020-2022: {len(missing)}")
            for f in missing[:5]:
                print(f"      - {f}")
            if len(missing) > 5:
                print(f"      ... et {len(missing) - 5} autres")
        else:
            print(f"   ✅ Tous les fichiers requis (2020-2022) sont présents")
    else:
        print(f"   ❌ Répertoire non trouvé: {era5_dir}")
        all_ok = False
    print()
    
    # 2. Sentinel-2 NDVI
    print("2. Sentinel-2 NDVI")
    sentinel2_dir = datasets_dir / "main" / "sentinel2_ndvi"
    if sentinel2_dir.exists():
        ndvi_files = sorted(list(sentinel2_dir.glob("*.tif")))
        print(f"   ✅ Répertoire trouvé: {sentinel2_dir}")
        print(f"   ✅ {len(ndvi_files)} fichiers GeoTIFF trouvés")
        if ndvi_files:
            print(f"   📅 Périodes disponibles:")
            for f in ndvi_files[:4]:
                print(f"      - {f.name}")
            if len(ndvi_files) > 4:
                print(f"      ... et {len(ndvi_files) - 4} autres")
    else:
        print(f"   ❌ Répertoire non trouvé: {sentinel2_dir}")
        all_ok = False
    print()
    
    # 3. ECA&D
    print("3. ECA&D Stations")
    ecad_zip = datasets_dir / "ECA_blend_tx.zip"
    if ecad_zip.exists():
        size_mb = ecad_zip.stat().st_size / 1024 / 1024
        print(f"   ✅ Fichier trouvé: {ecad_zip}")
        print(f"   ✅ Taille: {size_mb:.1f} MB")
    else:
        print(f"   ❌ Fichier non trouvé: {ecad_zip}")
        all_ok = False
    print()
    
    # 4. GADM
    print("4. GADM Boundaries")
    gadm_gpkg = datasets_dir / "main" / "gadm_410_europe.gpkg"
    if not gadm_gpkg.exists():
        gadm_gpkg = datasets_dir / "gadm_410_europe.gpkg"
    
    if gadm_gpkg.exists():
        size_mb = gadm_gpkg.stat().st_size / 1024 / 1024
        print(f"   ✅ Fichier trouvé: {gadm_gpkg}")
        print(f"   ✅ Taille: {size_mb:.1f} MB")
    else:
        print(f"   ❌ Fichier non trouvé")
        all_ok = False
    print()
    
    # Summary
    print("=" * 60)
    if all_ok:
        print("✅ Tous les fichiers de données sont présents!")
        print()
        print("📝 Prochaines étapes:")
        print("   1. Installer les dépendances Python:")
        print("      pip install xarray geopandas rasterio zarr netcdf4")
        print()
        print("   2. Exécuter l'ETL:")
        print("      python3 scripts/run_etl_real_data.py")
    else:
        print("❌ Certains fichiers sont manquants")
        print("   Veuillez télécharger les données manquantes")
    print("=" * 60)
    
    return all_ok


if __name__ == "__main__":
    success = check_files()
    sys.exit(0 if success else 1)


