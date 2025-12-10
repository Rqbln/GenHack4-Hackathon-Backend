#!/bin/bash

# Climate Downscaling Project - Setup Script
# This script sets up the environment and verifies data availability

echo "============================================================"
echo " Climate Downscaling Project - Setup"
echo "============================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check Python version
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_success "Python found: $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    print_success "Python found: $PYTHON_VERSION"
    PYTHON_CMD="python"
else
    print_error "Python not found. Please install Python 3.8 or higher."
    exit 1
fi

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
print_success "pip upgraded"

# Install requirements
echo ""
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        print_success "All dependencies installed"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi
else
    print_error "requirements.txt not found"
    exit 1
fi

# Check data directories
echo ""
echo "Checking data directories..."

DATA_DIRS=(
    "datasets/main/ECA_blend_tx"
    "datasets/main/derived-era5-land-daily-statistics"
    "datasets/main/sentinel2_ndvi"
)

ALL_DATA_PRESENT=true

for dir in "${DATA_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        # Count files
        FILE_COUNT=$(find "$dir" -type f | wc -l)
        print_success "$dir found ($FILE_COUNT files)"
    else
        print_error "$dir not found"
        ALL_DATA_PRESENT=false
    fi
done

# Create output directories
echo ""
echo "Creating output directories..."
mkdir -p outputs/evaluation
mkdir -p outputs/highres_maps
mkdir -p notebooks
mkdir -p src
print_success "Output directories created"

# Verify critical files
echo ""
echo "Checking critical data files..."

CRITICAL_FILES=(
    "datasets/main/ECA_blend_tx/stations.txt"
    "datasets/main/gadm_410_europe.gpkg"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "$file found"
    else
        print_warning "$file not found (optional)"
    fi
done

# Check if source files exist
echo ""
echo "Checking source code files..."

SOURCE_FILES=(
    "src/data_preparation.py"
    "src/modeling.py"
    "src/inference.py"
    "src/visualization.py"
    "src/main.py"
)

for file in "${SOURCE_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "$file found"
    else
        print_error "$file not found"
    fi
done

# Summary
echo ""
echo "============================================================"
echo " Setup Summary"
echo "============================================================"

if [ "$ALL_DATA_PRESENT" = true ]; then
    print_success "All data directories present"
else
    print_warning "Some data directories are missing"
    echo "  Please ensure all datasets are in place before running the pipeline"
fi

echo ""
echo "Next steps:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the pipeline:"
echo "     cd src"
echo "     python main.py --country SE --start 2020-01-01 --end 2023-12-31"
echo ""
echo "  3. Or use the Jupyter notebook:"
echo "     jupyter notebook notebooks/quickstart.ipynb"
echo ""
echo "For more information, see README.md"
echo ""
echo "============================================================"

# Test import of key packages
echo ""
echo "Testing key package imports..."
$PYTHON_CMD -c "
import numpy
import pandas
import sklearn
import xarray
import rasterio
import matplotlib
print('All key packages import successfully!')
" 2>/dev/null

if [ $? -eq 0 ]; then
    print_success "All key packages working"
else
    print_warning "Some packages may have import issues"
    echo "  This is normal if running for the first time"
    echo "  Try importing manually to diagnose"
fi

echo ""
print_success "Setup complete!"
