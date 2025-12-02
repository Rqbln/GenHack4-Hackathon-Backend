"""
Dataset Preparation for Fine-Tuning

Prepares training pairs (LowRes, HighRes, Target) for fine-tuning Prithvi WxC.
Creates aligned datasets from ERA5 (low-res), Sentinel-2/NDVI (high-res features),
and ECA&D ground truth (target).

This module handles:
- Temporal alignment of all data sources
- Spatial alignment and resampling
- Creation of training/validation/test splits
- Data augmentation strategies
"""

import numpy as np
import xarray as xr
import rasterio
from rasterio.warp import reproject, Resampling
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class FineTuningDataset:
    """Prepare dataset for fine-tuning Prithvi WxC"""
    
    def __init__(
        self,
        output_dir: Path,
        target_resolution: float = 100.0,  # meters
        patch_size: int = 256,  # pixels
        overlap: int = 32  # pixels overlap between patches
    ):
        """
        Initialize dataset preparation
        
        Args:
            output_dir: Directory to save prepared dataset
            target_resolution: Target resolution in meters
            patch_size: Size of training patches (square)
            overlap: Overlap between patches for data augmentation
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.target_resolution = target_resolution
        self.patch_size = patch_size
        self.overlap = overlap
        
    def create_training_pairs(
        self,
        era5_data: xr.Dataset,
        ndvi_data: Dict[str, np.ndarray],
        ecad_data: Dict[int, Dict],
        time_periods: List[Tuple[str, str]]
    ) -> Dict[str, List[Dict]]:
        """
        Create training pairs (LowRes, HighRes, Target) for each time period
        
        Args:
            era5_data: ERA5 xarray Dataset (low resolution)
            ndvi_data: Dictionary mapping time periods to NDVI arrays (high resolution)
            ecad_data: Dictionary mapping station IDs to temperature data
            time_periods: List of (start_date, end_date) tuples
            
        Returns:
            Dictionary with 'train', 'val', 'test' splits containing pairs
        """
        logger.info(f"Creating training pairs for {len(time_periods)} time periods")
        
        all_pairs = []
        
        for start_date, end_date in time_periods:
            # Get ERA5 data for this period
            era5_slice = self._extract_era5_slice(era5_data, start_date, end_date)
            
            # Get NDVI data for this period
            period_key = f"{start_date}_{end_date}"
            if period_key not in ndvi_data:
                logger.warning(f"NDVI data not found for period {period_key}")
                continue
            
            ndvi_array = ndvi_data[period_key]
            
            # Get ECA&D ground truth for this period
            ground_truth = self._extract_ground_truth(ecad_data, start_date, end_date)
            
            # Create pairs
            pairs = self._create_pairs_for_period(
                era5_slice,
                ndvi_array,
                ground_truth,
                start_date,
                end_date
            )
            
            all_pairs.extend(pairs)
        
        # Split into train/val/test
        splits = self._split_dataset(all_pairs, train_ratio=0.7, val_ratio=0.15)
        
        logger.info(f"Created {len(all_pairs)} pairs: "
                   f"{len(splits['train'])} train, "
                   f"{len(splits['val'])} val, "
                   f"{len(splits['test'])} test")
        
        return splits
    
    def _extract_era5_slice(
        self,
        era5_data: xr.Dataset,
        start_date: str,
        end_date: str
    ) -> xr.Dataset:
        """Extract ERA5 data for a specific time period"""
        if 'valid_time' in era5_data.dims:
            start = np.datetime64(start_date)
            end = np.datetime64(end_date)
            slice_data = era5_data.sel(valid_time=slice(start, end))
            # Average over time period
            return slice_data.mean(dim='valid_time')
        return era5_data
    
    def _extract_ground_truth(
        self,
        ecad_data: Dict[int, Dict],
        start_date: str,
        end_date: str
    ) -> Dict[int, float]:
        """Extract ground truth temperatures for time period"""
        ground_truth = {}
        
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        for station_id, station_data in ecad_data.items():
            # Filter data for period
            period_data = [
                temp for date, temp in station_data.items()
                if start <= datetime.fromisoformat(date) <= end
            ]
            
            if period_data:
                # Average temperature for period
                ground_truth[station_id] = np.mean(period_data)
        
        return ground_truth
    
    def _create_pairs_for_period(
        self,
        era5_slice: xr.Dataset,
        ndvi_array: np.ndarray,
        ground_truth: Dict[int, float],
        start_date: str,
        end_date: str
    ) -> List[Dict]:
        """Create training pairs for a specific time period"""
        pairs = []
        
        # Extract ERA5 temperature
        if 't2m' in era5_slice.data_vars:
            era5_temp = era5_slice['t2m'].values
        else:
            logger.warning("ERA5 temperature not found")
            return pairs
        
        # Create patches from NDVI array
        h, w = ndvi_array.shape
        stride = self.patch_size - self.overlap
        
        for y in range(0, h - self.patch_size + 1, stride):
            for x in range(0, w - self.patch_size + 1, stride):
                # Extract patch
                ndvi_patch = ndvi_array[y:y+self.patch_size, x:x+self.patch_size]
                
                # Skip if too many NaN values
                if np.sum(np.isnan(ndvi_patch)) > (self.patch_size ** 2 * 0.5):
                    continue
                
                # Get corresponding low-res ERA5 patch
                # (This is simplified - actual implementation needs proper spatial alignment)
                era5_patch = self._extract_corresponding_era5_patch(
                    era5_temp,
                    x, y,
                    self.patch_size
                )
                
                # Get ground truth if available in this region
                target_temp = self._get_target_temperature(
                    ground_truth,
                    x, y,
                    self.patch_size
                )
                
                if target_temp is None:
                    continue  # Skip if no ground truth
                
                pair = {
                    'low_res': era5_patch,
                    'high_res_features': ndvi_patch,
                    'target': target_temp,
                    'period': f"{start_date}_{end_date}",
                    'patch_coords': (x, y)
                }
                
                pairs.append(pair)
        
        return pairs
    
    def _extract_corresponding_era5_patch(
        self,
        era5_data: np.ndarray,
        x: int,
        y: int,
        patch_size: int
    ) -> np.ndarray:
        """Extract corresponding low-res ERA5 patch (simplified)"""
        # This is a simplified version - actual implementation needs proper
        # coordinate transformation and resampling
        h, w = era5_data.shape
        
        # Scale coordinates (assuming NDVI is higher resolution)
        scale_x = w / (x + patch_size)  # Simplified scaling
        scale_y = h / (y + patch_size)
        
        x_low = int(x * scale_x)
        y_low = int(y * scale_y)
        size_low = max(1, int(patch_size * min(scale_x, scale_y)))
        
        # Extract and upsample to patch_size
        patch = era5_data[
            max(0, y_low):min(h, y_low + size_low),
            max(0, x_low):min(w, x_low + size_low)
        ]
        
        # Upsample to patch_size if needed
        if patch.shape != (patch_size, patch_size):
            from scipy.ndimage import zoom
            zoom_factors = (patch_size / patch.shape[0], patch_size / patch.shape[1])
            patch = zoom(patch, zoom_factors, order=1)
        
        return patch
    
    def _get_target_temperature(
        self,
        ground_truth: Dict[int, float],
        x: int,
        y: int,
        patch_size: int
    ) -> Optional[float]:
        """Get target temperature for patch region (simplified)"""
        # This is simplified - actual implementation needs spatial matching
        # with station coordinates
        if not ground_truth:
            return None
        
        # For now, return average of all ground truth values
        # (actual implementation should match to nearest station)
        return np.mean(list(ground_truth.values()))
    
    def _split_dataset(
        self,
        pairs: List[Dict],
        train_ratio: float = 0.7,
        val_ratio: float = 0.15
    ) -> Dict[str, List[Dict]]:
        """Split dataset into train/val/test"""
        np.random.seed(42)
        np.random.shuffle(pairs)
        
        n = len(pairs)
        n_train = int(n * train_ratio)
        n_val = int(n * val_ratio)
        
        return {
            'train': pairs[:n_train],
            'val': pairs[n_train:n_train + n_val],
            'test': pairs[n_train + n_val:]
        }
    
    def save_dataset(
        self,
        splits: Dict[str, List[Dict]],
        format: str = 'numpy'
    ) -> Dict[str, Path]:
        """
        Save prepared dataset to disk
        
        Args:
            splits: Dictionary with train/val/test splits
            format: Format to save ('numpy', 'zarr', 'hdf5')
            
        Returns:
            Dictionary with paths to saved files
        """
        saved_paths = {}
        
        for split_name, pairs in splits.items():
            if len(pairs) == 0:
                continue
            
            # Extract arrays
            low_res = np.array([p['low_res'] for p in pairs])
            high_res = np.array([p['high_res_features'] for p in pairs])
            targets = np.array([p['target'] for p in pairs])
            
            if format == 'numpy':
                # Save as numpy arrays
                split_dir = self.output_dir / split_name
                split_dir.mkdir(exist_ok=True)
                
                np.save(split_dir / 'low_res.npy', low_res)
                np.save(split_dir / 'high_res.npy', high_res)
                np.save(split_dir / 'targets.npy', targets)
                
                # Save metadata
                metadata = {
                    'n_samples': len(pairs),
                    'patch_size': self.patch_size,
                    'target_resolution': self.target_resolution,
                    'periods': list(set(p['period'] for p in pairs))
                }
                
                with open(split_dir / 'metadata.json', 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                saved_paths[split_name] = split_dir
                
            else:
                raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Saved dataset to {self.output_dir}")
        return saved_paths
    
    def load_dataset(self, split: str = 'train') -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Load prepared dataset split
        
        Args:
            split: Split to load ('train', 'val', 'test')
            
        Returns:
            Tuple of (low_res, high_res, targets) arrays
        """
        split_dir = self.output_dir / split
        
        if not split_dir.exists():
            raise FileNotFoundError(f"Dataset split not found: {split_dir}")
        
        low_res = np.load(split_dir / 'low_res.npy')
        high_res = np.load(split_dir / 'high_res.npy')
        targets = np.load(split_dir / 'targets.npy')
        
        logger.info(f"Loaded {split} split: {len(low_res)} samples")
        return low_res, high_res, targets


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    from pathlib import Path
    
    dataset = FineTuningDataset(
        output_dir=Path("../../datasets/processed/finetuning_dataset"),
        target_resolution=100.0,
        patch_size=256
    )
    
    print(f"Dataset preparation initialized: {dataset.output_dir}")

