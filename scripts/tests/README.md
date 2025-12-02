# Test Scripts

This directory contains test scripts for validating implementations.

## Structure Tests (No Dependencies Required)

- `test_etl_simple.py` - Tests ETL pipeline structure
- `test_gap_filling_simple.py` - Tests gap filling structure
- `test_baseline_simple.py` - Tests baseline model structure
- `test_syntax.py` - Validates Python syntax

## Full Tests (Require Dependencies)

- `test_etl.py` - Full ETL pipeline test (requires xarray, rasterio, geopandas)
- `test_gap_filling.py` - Full gap filling test (requires numpy, scikit-learn)
- `test_baseline.py` - Full baseline test (requires numpy, scipy)

## Running Tests

```bash
# Run all tests (structure + full if deps available)
python3 scripts/tests/test_all_days_1_4.py

# Run individual tests
python3 scripts/tests/test_etl_simple.py
python3 scripts/tests/test_gap_filling_simple.py
python3 scripts/tests/test_baseline_simple.py
```

## Installing Dependencies

To run full tests, install dependencies:

```bash
pip install -r pipeline/requirements.txt
```

Or use Docker (recommended):

```bash
docker build -f pipeline/Dockerfile.geo -t genhack-pipeline .
docker run --rm genhack-pipeline python scripts/tests/test_all_days_1_4.py
```

