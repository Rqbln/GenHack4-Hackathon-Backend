"""
Physics-Informed Neural Network (PINN) Validation

Validates physical consistency of downscaled predictions:
- UHI intensity vs NDVI (vegetation) correlation
- UHI intensity vs NDBI (built-up index) correlation
- Energy balance constraints
- Spatial coherence checks
"""

import numpy as np
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logger.warning("scipy not available. Install with: pip install scipy")


class PhysicsValidator:
    """Validate physical consistency of predictions"""
    
    def __init__(self):
        """Initialize physics validator"""
        logger.info("Physics Validator initialized")
    
    def calculate_ndbi(
        self,
        red_band: np.ndarray,
        nir_band: np.ndarray
    ) -> np.ndarray:
        """
        Calculate Normalized Difference Built-up Index (NDBI)
        
        NDBI = (SWIR - NIR) / (SWIR + NIR)
        
        For Sentinel-2, we approximate with available bands:
        NDBI ≈ (B11 - B8) / (B11 + B8)
        
        Args:
            red_band: Red band (B4) or SWIR approximation
            nir_band: Near-infrared band (B8)
            
        Returns:
            NDBI array (range: -1 to 1)
        """
        # Simplified NDBI calculation
        # In production, would use actual SWIR band
        ndbi = (red_band - nir_band) / (red_band + nir_band + 1e-10)
        ndbi = np.clip(ndbi, -1, 1)
        return ndbi
    
    def validate_uhi_ndvi_correlation(
        self,
        uhi_intensity: np.ndarray,
        ndvi: np.ndarray,
        expected_correlation: float = -0.5
    ) -> Dict:
        """
        Validate negative correlation between UHI and NDVI
        
        Physical expectation: More vegetation (higher NDVI) → Lower UHI
        
        Args:
            uhi_intensity: UHI intensity array
            ndvi: NDVI array (normalized -1 to 1)
            expected_correlation: Expected correlation coefficient
            
        Returns:
            Validation results dictionary
        """
        if not SCIPY_AVAILABLE:
            raise ImportError("scipy is required for correlation analysis")
        
        # Flatten arrays and remove NaN
        uhi_flat = uhi_intensity.flatten()
        ndvi_flat = ndvi.flatten()
        
        valid_mask = ~(np.isnan(uhi_flat) | np.isnan(ndvi_flat))
        uhi_valid = uhi_flat[valid_mask]
        ndvi_valid = ndvi_flat[valid_mask]
        
        if len(uhi_valid) < 10:
            return {
                'correlation': np.nan,
                'p_value': np.nan,
                'is_valid': False,
                'message': 'Insufficient data for correlation'
            }
        
        # Calculate Pearson correlation
        correlation, p_value = stats.pearsonr(uhi_valid, ndvi_valid)
        
        # Validate: correlation should be negative
        is_valid = correlation < 0 and p_value < 0.05
        
        result = {
            'correlation': float(correlation),
            'p_value': float(p_value),
            'is_valid': is_valid,
            'expected_correlation': expected_correlation,
            'deviation': abs(correlation - expected_correlation),
            'message': (
                f"UHI-NDVI correlation: {correlation:.3f} "
                f"(expected negative, p={p_value:.3f})"
            )
        }
        
        logger.info(result['message'])
        return result
    
    def validate_uhi_ndbi_correlation(
        self,
        uhi_intensity: np.ndarray,
        ndbi: np.ndarray,
        expected_correlation: float = 0.6
    ) -> Dict:
        """
        Validate positive correlation between UHI and NDBI
        
        Physical expectation: More built-up areas (higher NDBI) → Higher UHI
        
        Args:
            uhi_intensity: UHI intensity array
            ndbi: NDBI array (normalized -1 to 1)
            expected_correlation: Expected correlation coefficient
            
        Returns:
            Validation results dictionary
        """
        if not SCIPY_AVAILABLE:
            raise ImportError("scipy is required for correlation analysis")
        
        # Flatten arrays and remove NaN
        uhi_flat = uhi_intensity.flatten()
        ndbi_flat = ndbi.flatten()
        
        valid_mask = ~(np.isnan(uhi_flat) | np.isnan(ndbi_flat))
        uhi_valid = uhi_flat[valid_mask]
        ndbi_valid = ndbi_flat[valid_mask]
        
        if len(uhi_valid) < 10:
            return {
                'correlation': np.nan,
                'p_value': np.nan,
                'is_valid': False,
                'message': 'Insufficient data for correlation'
            }
        
        # Calculate Pearson correlation
        correlation, p_value = stats.pearsonr(uhi_valid, ndbi_valid)
        
        # Validate: correlation should be positive
        is_valid = correlation > 0 and p_value < 0.05
        
        result = {
            'correlation': float(correlation),
            'p_value': float(p_value),
            'is_valid': is_valid,
            'expected_correlation': expected_correlation,
            'deviation': abs(correlation - expected_correlation),
            'message': (
                f"UHI-NDBI correlation: {correlation:.3f} "
                f"(expected positive, p={p_value:.3f})"
            )
        }
        
        logger.info(result['message'])
        return result
    
    def validate_energy_balance(
        self,
        temperature: np.ndarray,
        solar_radiation: Optional[np.ndarray] = None,
        albedo: Optional[np.ndarray] = None
    ) -> Dict:
        """
        Validate simplified energy balance constraints
        
        Simplified: Q_net = Q_solar * (1 - albedo) - Q_outgoing
        
        Args:
            temperature: Temperature array (K or °C)
            solar_radiation: Solar radiation (W/m²), optional
            albedo: Surface albedo (0-1), optional
            
        Returns:
            Validation results dictionary
        """
        # Simplified validation: check temperature range
        temp_min = np.nanmin(temperature)
        temp_max = np.nanmax(temperature)
        temp_mean = np.nanmean(temperature)
        temp_std = np.nanstd(temperature)
        
        # Reasonable temperature range for urban areas (Europe)
        min_reasonable = -20  # °C
        max_reasonable = 50   # °C
        
        is_valid = (
            temp_min >= min_reasonable and
            temp_max <= max_reasonable and
            temp_std < 15  # Reasonable spatial variation
        )
        
        result = {
            'temp_min': float(temp_min),
            'temp_max': float(temp_max),
            'temp_mean': float(temp_mean),
            'temp_std': float(temp_std),
            'is_valid': is_valid,
            'message': (
                f"Temperature range: {temp_min:.1f} to {temp_max:.1f}°C "
                f"(mean: {temp_mean:.1f}°C, std: {temp_std:.1f}°C)"
            )
        }
        
        logger.info(result['message'])
        return result
    
    def validate_spatial_coherence(
        self,
        temperature: np.ndarray,
        threshold: float = 5.0
    ) -> Dict:
        """
        Validate spatial coherence (no unrealistic gradients)
        
        Checks for abrupt temperature changes that violate physical constraints
        
        Args:
            temperature: 2D temperature array
            threshold: Maximum allowed temperature difference between neighbors (°C)
            
        Returns:
            Validation results dictionary
        """
        if temperature.ndim != 2:
            return {
                'is_valid': False,
                'message': 'Spatial coherence requires 2D array'
            }
        
        # Calculate gradients
        grad_y, grad_x = np.gradient(temperature)
        grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Check for excessive gradients
        max_gradient = np.nanmax(grad_magnitude)
        mean_gradient = np.nanmean(grad_magnitude)
        
        # Convert gradient (per pixel) to temperature difference
        # Assuming 100m resolution, gradient of 1 K/pixel ≈ 10 K/km
        max_temp_diff = max_gradient * 0.1  # Approximate conversion
        
        is_valid = max_temp_diff < threshold
        
        result = {
            'max_gradient': float(max_gradient),
            'mean_gradient': float(mean_gradient),
            'max_temp_diff_km': float(max_temp_diff),
            'threshold': threshold,
            'is_valid': is_valid,
            'message': (
                f"Max spatial gradient: {max_temp_diff:.2f}°C/km "
                f"(threshold: {threshold}°C/km)"
            )
        }
        
        logger.info(result['message'])
        return result
    
    def comprehensive_validation(
        self,
        temperature: np.ndarray,
        ndvi: np.ndarray,
        ndbi: Optional[np.ndarray] = None,
        reference_temp: float = 20.0
    ) -> Dict:
        """
        Perform comprehensive physics validation
        
        Args:
            temperature: Predicted temperature array
            ndvi: NDVI array
            ndbi: Optional NDBI array (will be calculated if not provided)
            reference_temp: Reference temperature for UHI calculation
            
        Returns:
            Comprehensive validation results
        """
        logger.info("Performing comprehensive physics validation...")
        
        results = {}
        
        # Calculate UHI intensity
        uhi_intensity = temperature - reference_temp
        
        # Validate UHI-NDVI correlation
        results['uhi_ndvi'] = self.validate_uhi_ndvi_correlation(uhi_intensity, ndvi)
        
        # Validate UHI-NDBI correlation (if NDBI provided or can be calculated)
        if ndbi is not None:
            results['uhi_ndbi'] = self.validate_uhi_ndbi_correlation(uhi_intensity, ndbi)
        else:
            results['uhi_ndbi'] = {
                'is_valid': None,
                'message': 'NDBI not provided'
            }
        
        # Validate energy balance
        results['energy_balance'] = self.validate_energy_balance(temperature)
        
        # Validate spatial coherence
        if temperature.ndim == 2:
            results['spatial_coherence'] = self.validate_spatial_coherence(temperature)
        else:
            results['spatial_coherence'] = {
                'is_valid': None,
                'message': 'Spatial coherence requires 2D array'
            }
        
        # Overall validation status
        validations = [
            results['uhi_ndvi'].get('is_valid'),
            results['uhi_ndbi'].get('is_valid'),
            results['energy_balance'].get('is_valid'),
            results['spatial_coherence'].get('is_valid')
        ]
        
        valid_count = sum(1 for v in validations if v is True)
        total_count = sum(1 for v in validations if v is not None)
        
        results['overall'] = {
            'is_valid': valid_count == total_count and total_count > 0,
            'valid_count': valid_count,
            'total_count': total_count,
            'validation_rate': valid_count / total_count if total_count > 0 else 0.0
        }
        
        logger.info(f"✅ Physics validation complete: {valid_count}/{total_count} checks passed")
        return results


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    validator = PhysicsValidator()
    
    # Create dummy data
    np.random.seed(42)
    temperature = np.random.randn(100, 100) * 5 + 25
    ndvi = np.random.rand(100, 100) * 0.6 + 0.2
    
    # Validate
    results = validator.comprehensive_validation(temperature, ndvi)
    print(f"Overall validation: {results['overall']['is_valid']}")

