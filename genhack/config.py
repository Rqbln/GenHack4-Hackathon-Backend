"""
Configuration file for climate downscaling pipeline
"""

# Data paths
DATA_DIR = './datasets/main'
OUTPUT_DIR = './outputs'

# Data preparation settings
DATA_PREP = {
    'country_code': 'SE',  # ISO 3166 country code
    'date_range': ('2020-01-01', '2023-12-31'),
    'skip_if_exists': True,  # Skip data prep if training_data.csv exists
}

# Model training settings
MODEL = {
    'type': 'random_forest',  # 'random_forest' or 'xgboost'
    'split_type': 'spatial',  # 'spatial' or 'geographic'
    'test_size': 0.2,
    
    # Random Forest parameters
    'rf_params': {
        'n_estimators': 200,
        'max_depth': 15,
        'min_samples_split': 10,
        'min_samples_leaf': 5,
        'n_jobs': -1,
        'random_state': 42
    },
    
    # XGBoost parameters
    'xgb_params': {
        'n_estimators': 200,
        'max_depth': 8,
        'learning_rate': 0.1,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'n_jobs': -1,
        'random_state': 42
    }
}

# Inference settings
INFERENCE = {
    'generate_maps': False,  # Set to True to generate maps
    'start_date': '2023-07-01',
    'end_date': '2023-07-31',
    'roi_bounds': None,  # Optional: (min_lon, min_lat, max_lon, max_lat)
}

# Visualization settings
VISUALIZATION = {
    'create_plots': True,
    'save_plots': True,
    'plot_format': 'png',
    'dpi': 300
}

# Advanced settings
ADVANCED = {
    'progress_interval': 1000,  # Print progress every N rows
    'cache_size': 10,  # Number of ERA5/NDVI files to keep in memory
    'compression': 'lzw',  # GeoTIFF compression method
    'verbose': True
}
