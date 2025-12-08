#!/bin/bash
# Script pour exécuter l'ETL avec l'environnement virtuel

cd "$(dirname "$0")/.."

# Activer l'environnement virtuel
if [ ! -d "venv" ]; then
    echo "❌ Environnement virtuel non trouvé. Création..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel
    pip install xarray geopandas rasterio zarr netcdf4 fsspec
else
    source venv/bin/activate
fi

# Exécuter l'ETL
echo "🚀 Exécution de l'ETL avec les vraies données..."
python3 scripts/run_etl_real_data.py


