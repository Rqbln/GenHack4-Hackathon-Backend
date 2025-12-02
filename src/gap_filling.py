"""
Gap Filling Algorithm for Sentinel-2 NDVI Data

Implements Random Forest-based gap filling to reconstruct missing NDVI pixels
caused by cloud cover. Based on research from 2024-2025 showing Random Forest
superiority over harmonic methods (HANTS) for complex gaps.

Reference: Reconstruction of a Monthly 1 km NDVI Time Series Product in China 
Using Random Forest Methodology (MDPI, 2025)
"""

import numpy as np
import rasterio
from rasterio.transform import from_bounds
from pathlib import Path
from typing import Tuple, Optional, Dict
import logging
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import joblib

logger = logging.getLogger(__name__)


class NDVIGapFiller:
    """Random Forest-based gap filling for Sentinel-2 NDVI data"""
    
    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 20,
        min_samples_split: int = 5,
        random_state: int = 42,
        n_jobs: int = -1
    ):
        """
        Initialize Random Forest gap filler
        
        Args:
            n_estimators: Number of trees in the forest
            max_depth: Maximum depth of trees
            min_samples_split: Minimum samples required to split a node
            random_state: Random seed for reproducibility
            n_jobs: Number of parallel jobs (-1 = all cores)
        """
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            random_state=random_state,
            n_jobs=n_jobs,
            verbose=0
        )
        self.is_fitted = False
        
    def extract_features(
        self,
        ndvi_array: np.ndarray,
        nodata_value: float = np.nan,
        window_size: int = 5
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract spatial features for gap filling
        
        Features include:
        - Neighboring pixel values (spatial context)
        - Local statistics (mean, std, min, max in window)
        - Distance to nearest valid pixel
        
        Args:
            ndvi_array: NDVI array (may contain NaN for missing values)
            nodata_value: Value representing NoData
            window_size: Size of neighborhood window (must be odd)
            
        Returns:
            Tuple of (features, target_mask) where:
            - features: Array of shape (n_samples, n_features)
            - target_mask: Boolean mask of pixels to predict
        """
        if window_size % 2 == 0:
            raise ValueError("window_size must be odd")
        
        # Create mask for valid and missing pixels
        valid_mask = ~np.isnan(ndvi_array)
        missing_mask = np.isnan(ndvi_array)
        
        # Pad array for window operations
        pad = window_size // 2
        padded = np.pad(ndvi_array, pad, mode='constant', constant_values=np.nan)
        
        # Extract features for missing pixels
        missing_coords = np.where(missing_mask)
        n_missing = len(missing_coords[0])
        
        if n_missing == 0:
            logger.warning("No missing pixels found")
            return np.array([]), np.array([])
        
        features = []
        targets = []
        
        for i, j in zip(missing_coords[0], missing_coords[1]):
            # Get window around pixel (accounting for padding)
            window = padded[i:i+window_size, j:j+window_size]
            window_center = window[pad, pad]  # Should be NaN
            
            # Feature 1-9: Neighboring pixel values (3x3 window)
            neighbor_values = window.flatten()
            neighbor_features = neighbor_values.copy()
            neighbor_features[pad * window_size + pad] = 0  # Remove center pixel
            
            # Feature 10-13: Local statistics (excluding center)
            window_valid = window[~np.isnan(window)]
            if len(window_valid) > 0:
                local_mean = np.nanmean(window_valid)
                local_std = np.nanstd(window_valid)
                local_min = np.nanmin(window_valid)
                local_max = np.nanmax(window_valid)
            else:
                local_mean = local_std = local_min = local_max = 0.0
            
            # Feature 14: Distance to nearest valid pixel
            # Use Manhattan distance for efficiency
            distances = []
            for vi, vj in zip(*np.where(valid_mask)):
                dist = abs(vi - i) + abs(vj - j)
                if dist > 0:
                    distances.append(dist)
            min_distance = min(distances) if distances else window_size
            
            # Feature 15-16: Position in image (normalized)
            norm_i = i / ndvi_array.shape[0]
            norm_j = j / ndvi_array.shape[1]
            
            # Combine all features
            feature_vector = np.concatenate([
                neighbor_features,  # 9 features
                [local_mean, local_std, local_min, local_max],  # 4 features
                [min_distance],  # 1 feature
                [norm_i, norm_j]  # 2 features
            ])
            
            # Replace NaN in features with 0
            feature_vector = np.nan_to_num(feature_vector, nan=0.0)
            
            features.append(feature_vector)
        
        return np.array(features), missing_mask
    
    def extract_training_data(
        self,
        ndvi_arrays: list,
        nodata_value: float = np.nan,
        window_size: int = 5
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract training data from multiple NDVI arrays
        
        Uses valid pixels from all arrays to train the model
        
        Args:
            ndvi_arrays: List of NDVI arrays (some may have gaps)
            nodata_value: Value representing NoData
            window_size: Size of neighborhood window
            
        Returns:
            Tuple of (X_train, y_train)
        """
        all_features = []
        all_targets = []
        
        for ndvi_array in ndvi_arrays:
            # Create mask for valid pixels
            valid_mask = ~np.isnan(ndvi_array)
            
            if np.sum(valid_mask) == 0:
                continue
            
            # Pad array
            pad = window_size // 2
            padded = np.pad(ndvi_array, pad, mode='constant', constant_values=np.nan)
            
            # Sample valid pixels for training
            valid_coords = np.where(valid_mask)
            n_valid = len(valid_coords[0])
            
            # Sample up to 10000 pixels per image to avoid memory issues
            sample_size = min(10000, n_valid)
            sample_indices = np.random.choice(n_valid, sample_size, replace=False)
            
            for idx in sample_indices:
                i, j = valid_coords[0][idx], valid_coords[1][idx]
                target_value = ndvi_array[i, j]
                
                # Get window
                window = padded[i:i+window_size, j:j+window_size]
                
                # Extract features (same as in extract_features)
                neighbor_values = window.flatten()
                neighbor_features = neighbor_values.copy()
                neighbor_features[pad * window_size + pad] = 0
                
                window_valid = window[~np.isnan(window)]
                if len(window_valid) > 0:
                    local_mean = np.nanmean(window_valid)
                    local_std = np.nanstd(window_valid)
                    local_min = np.nanmin(window_valid)
                    local_max = np.nanmax(window_valid)
                else:
                    local_mean = local_std = local_min = local_max = 0.0
                
                # Distance to nearest valid pixel (excluding self)
                distances = []
                for vi, vj in zip(*np.where(valid_mask)):
                    dist = abs(vi - i) + abs(vj - j)
                    if dist > 0:
                        distances.append(dist)
                min_distance = min(distances) if distances else window_size
                
                norm_i = i / ndvi_array.shape[0]
                norm_j = j / ndvi_array.shape[1]
                
                feature_vector = np.concatenate([
                    neighbor_features,
                    [local_mean, local_std, local_min, local_max],
                    [min_distance],
                    [norm_i, norm_j]
                ])
                
                feature_vector = np.nan_to_num(feature_vector, nan=0.0)
                
                all_features.append(feature_vector)
                all_targets.append(target_value)
        
        return np.array(all_features), np.array(all_targets)
    
    def train(
        self,
        ndvi_arrays: list,
        test_size: float = 0.2,
        window_size: int = 5
    ) -> Dict[str, float]:
        """
        Train the Random Forest model on NDVI data
        
        Args:
            ndvi_arrays: List of NDVI arrays for training
            test_size: Proportion of data for testing
            window_size: Size of neighborhood window
            
        Returns:
            Dictionary with training metrics (R², RMSE)
        """
        logger.info(f"Training Random Forest gap filler on {len(ndvi_arrays)} NDVI arrays")
        
        # Extract training data
        X, y = self.extract_training_data(ndvi_arrays, window_size=window_size)
        
        if len(X) == 0:
            raise ValueError("No training data extracted")
        
        logger.info(f"Extracted {len(X)} training samples")
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Train model
        logger.info("Training Random Forest...")
        self.model.fit(X_train, y_train)
        self.is_fitted = True
        
        # Evaluate
        y_pred_train = self.model.predict(X_train)
        y_pred_test = self.model.predict(X_test)
        
        train_r2 = r2_score(y_train, y_pred_train)
        test_r2 = r2_score(y_test, y_pred_test)
        train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
        test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
        
        metrics = {
            "train_r2": train_r2,
            "test_r2": test_r2,
            "train_rmse": train_rmse,
            "test_rmse": test_rmse,
            "n_samples": len(X),
            "n_features": X.shape[1]
        }
        
        logger.info(f"Training complete:")
        logger.info(f"  Train R²: {train_r2:.4f}, RMSE: {train_rmse:.4f}")
        logger.info(f"  Test R²: {test_r2:.4f}, RMSE: {test_rmse:.4f}")
        
        return metrics
    
    def fill_gaps(
        self,
        ndvi_array: np.ndarray,
        window_size: int = 5
    ) -> np.ndarray:
        """
        Fill gaps in NDVI array using trained model
        
        Args:
            ndvi_array: NDVI array with missing values (NaN)
            window_size: Size of neighborhood window
            
        Returns:
            NDVI array with gaps filled
        """
        if not self.is_fitted:
            raise ValueError("Model must be trained before filling gaps")
        
        # Create copy
        filled_array = ndvi_array.copy()
        
        # Extract features for missing pixels
        features, missing_mask = self.extract_features(ndvi_array, window_size=window_size)
        
        if len(features) == 0:
            logger.info("No gaps to fill")
            return filled_array
        
        # Predict missing values
        logger.info(f"Filling {len(features)} missing pixels...")
        predictions = self.model.predict(features)
        
        # Fill gaps
        missing_coords = np.where(missing_mask)
        for idx, (i, j) in enumerate(zip(missing_coords[0], missing_coords[1])):
            filled_array[i, j] = predictions[idx]
        
        logger.info(f"Filled {len(predictions)} pixels")
        
        return filled_array
    
    def save_model(self, path: Path):
        """Save trained model to disk"""
        if not self.is_fitted:
            raise ValueError("Model must be trained before saving")
        joblib.dump(self.model, path)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: Path):
        """Load trained model from disk"""
        self.model = joblib.load(path)
        self.is_fitted = True
        logger.info(f"Model loaded from {path}")


def fill_ndvi_gaps_batch(
    input_dir: Path,
    output_dir: Path,
    model_path: Optional[Path] = None,
    train_on_all: bool = True
) -> Path:
    """
    Fill gaps in all NDVI files in a directory
    
    Args:
        input_dir: Directory containing NDVI GeoTIFF files
        output_dir: Directory to save filled NDVI files
        model_path: Optional path to save/load model
        train_on_all: If True, train on all files; if False, use existing model
        
    Returns:
        Path to output directory
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all NDVI files
    ndvi_files = list(input_dir.glob("*.tif"))
    logger.info(f"Found {len(ndvi_files)} NDVI files")
    
    if len(ndvi_files) == 0:
        raise ValueError(f"No NDVI files found in {input_dir}")
    
    # Initialize gap filler
    gap_filler = NDVIGapFiller()
    
    # Train or load model
    if train_on_all or model_path is None or not model_path.exists():
        # Load all NDVI arrays for training
        ndvi_arrays = []
        for ndvi_file in ndvi_files:
            with rasterio.open(ndvi_file) as src:
                data = src.read(1).astype(float)
                # Convert from int8 to float scale
                data[data == 255] = np.nan
                data = data / 254 * 2 - 1
                ndvi_arrays.append(data)
        
        # Train model
        metrics = gap_filler.train(ndvi_arrays)
        logger.info(f"Training metrics: {metrics}")
        
        # Save model if path provided
        if model_path:
            gap_filler.save_model(model_path)
    else:
        # Load existing model
        gap_filler.load_model(model_path)
    
    # Fill gaps in all files
    for ndvi_file in ndvi_files:
        logger.info(f"Processing {ndvi_file.name}...")
        
        with rasterio.open(ndvi_file) as src:
            # Read and convert NDVI
            data = src.read(1).astype(float)
            nodata_mask = data == 255
            data[data == 255] = np.nan
            data = data / 254 * 2 - 1
            
            # Fill gaps
            filled_data = gap_filler.fill_gaps(data)
            
            # Convert back to int8 scale for storage
            filled_int8 = ((filled_data + 1) / 2 * 254).astype(np.int8)
            filled_int8[nodata_mask] = 255  # Preserve original nodata
            
            # Write output
            output_path = output_dir / f"filled_{ndvi_file.name}"
            with rasterio.open(
                output_path,
                'w',
                driver='GTiff',
                height=src.height,
                width=src.width,
                count=1,
                dtype=filled_int8.dtype,
                crs=src.crs,
                transform=src.transform,
                compress='lzw',
                tiled=True,
                nodata=255
            ) as dst:
                dst.write(filled_int8, 1)
        
        logger.info(f"Saved filled NDVI to {output_path}")
    
    return output_dir


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    from pathlib import Path
    
    input_dir = Path("../../datasets/main/sentinel2_ndvi")
    output_dir = Path("../../datasets/processed/ndvi_filled")
    model_path = Path("../../datasets/processed/gap_filling_model.joblib")
    
    fill_ndvi_gaps_batch(
        input_dir=input_dir,
        output_dir=output_dir,
        model_path=model_path,
        train_on_all=True
    )

