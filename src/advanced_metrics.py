"""
Advanced Metrics: Perkins Skill Score and Spectral Analysis

Implements advanced validation metrics for climate downscaling:
- Perkins Skill Score (S-score) for extreme event validation
- Spectral Analysis (Power Spectral Density) for spatial structure preservation
- Comparison with baseline model
"""

import numpy as np
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

try:
    from scipy import stats
    from scipy.signal import welch
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logger.warning("scipy not available. Install with: pip install scipy")


class AdvancedMetrics:
    """Calculate advanced validation metrics"""
    
    def __init__(self, n_bins: int = 50):
        """
        Initialize advanced metrics calculator
        
        Args:
            n_bins: Number of bins for PDF estimation
        """
        self.n_bins = n_bins
        
    def perkins_skill_score(
        self,
        predicted: np.ndarray,
        observed: np.ndarray,
        bins: Optional[np.ndarray] = None
    ) -> float:
        """
        Calculate Perkins Skill Score (S-score)
        
        Measures overlap between predicted and observed probability distributions.
        Range: [0, 1], where 1 = perfect match
        
        Formula: S = Σ min(Z_pred, Z_obs)
        
        Args:
            predicted: Predicted values
            observed: Observed values (ground truth)
            bins: Optional bin edges for PDF estimation
            
        Returns:
            Perkins Skill Score (0-1)
        """
        if not SCIPY_AVAILABLE:
            raise ImportError("scipy is required for Perkins Skill Score")
        
        # Remove NaN values
        valid_mask = ~(np.isnan(predicted) | np.isnan(observed))
        predicted = predicted[valid_mask]
        observed = observed[valid_mask]
        
        if len(predicted) == 0 or len(observed) == 0:
            return np.nan
        
        # Determine bin range
        if bins is None:
            min_val = min(np.nanmin(predicted), np.nanmin(observed))
            max_val = max(np.nanmax(predicted), np.nanmax(observed))
            bins = np.linspace(min_val, max_val, self.n_bins + 1)
        
        # Calculate PDFs
        pred_pdf, _ = np.histogram(predicted, bins=bins, density=True)
        obs_pdf, _ = np.histogram(observed, bins=bins, density=True)
        
        # Normalize PDFs
        pred_pdf = pred_pdf / np.sum(pred_pdf) if np.sum(pred_pdf) > 0 else pred_pdf
        obs_pdf = obs_pdf / np.sum(obs_pdf) if np.sum(obs_pdf) > 0 else obs_pdf
        
        # Calculate S-score (overlap)
        s_score = np.sum(np.minimum(pred_pdf, obs_pdf))
        
        return float(s_score)
    
    def spectral_analysis(
        self,
        predicted: np.ndarray,
        observed: np.ndarray,
        sample_rate: float = 1.0
    ) -> Dict:
        """
        Perform spectral analysis (Power Spectral Density)
        
        Analyzes spatial frequency content to verify preservation of
        high-frequency structures in downscaled data.
        
        Args:
            predicted: 2D predicted array
            observed: 2D observed array (ground truth)
            sample_rate: Sampling rate (pixels per unit)
            
        Returns:
            Dictionary with spectral analysis results
        """
        if not SCIPY_AVAILABLE:
            raise ImportError("scipy is required for spectral analysis")
        
        # Flatten 2D arrays
        if predicted.ndim == 2:
            pred_1d = predicted.flatten()
            obs_1d = observed.flatten()
        else:
            pred_1d = predicted
            obs_1d = observed
        
        # Remove NaN
        valid_mask = ~(np.isnan(pred_1d) | np.isnan(obs_1d))
        pred_1d = pred_1d[valid_mask]
        obs_1d = obs_1d[valid_mask]
        
        if len(pred_1d) < 100:  # Need sufficient data
            return {
                'frequencies': None,
                'pred_psd': None,
                'obs_psd': None,
                'correlation': np.nan
            }
        
        # Calculate Power Spectral Density using Welch's method
        freqs_pred, psd_pred = welch(pred_1d, fs=sample_rate, nperseg=min(256, len(pred_1d)//4))
        freqs_obs, psd_obs = welch(obs_1d, fs=sample_rate, nperseg=min(256, len(obs_1d)//4))
        
        # Interpolate to common frequency grid
        common_freqs = np.linspace(
            max(freqs_pred[0], freqs_obs[0]),
            min(freqs_pred[-1], freqs_obs[-1]),
            min(len(freqs_pred), len(freqs_obs))
        )
        
        psd_pred_interp = np.interp(common_freqs, freqs_pred, psd_pred)
        psd_obs_interp = np.interp(common_freqs, freqs_obs, psd_obs)
        
        # Calculate correlation between PSDs
        correlation = np.corrcoef(psd_pred_interp, psd_obs_interp)[0, 1]
        
        return {
            'frequencies': common_freqs.tolist(),
            'pred_psd': psd_pred_interp.tolist(),
            'obs_psd': psd_obs_interp.tolist(),
            'correlation': float(correlation) if not np.isnan(correlation) else np.nan
        }
    
    def compare_with_baseline(
        self,
        prithvi_metrics: Dict,
        baseline_metrics: Dict
    ) -> Dict:
        """
        Compare Prithvi WxC metrics with baseline
        
        Args:
            prithvi_metrics: Metrics from Prithvi model
            baseline_metrics: Metrics from baseline model
            
        Returns:
            Comparison dictionary
        """
        comparison = {
            'rmse_improvement': None,
            'mae_improvement': None,
            'r2_improvement': None,
            'perkins_improvement': None,
            'spectral_correlation_improvement': None
        }
        
        # RMSE improvement (negative = better)
        if 'rmse' in prithvi_metrics and 'rmse' in baseline_metrics:
            improvement = baseline_metrics['rmse'] - prithvi_metrics['rmse']
            improvement_pct = (improvement / baseline_metrics['rmse']) * 100
            comparison['rmse_improvement'] = {
                'absolute': float(improvement),
                'percentage': float(improvement_pct)
            }
        
        # MAE improvement
        if 'mae' in prithvi_metrics and 'mae' in baseline_metrics:
            improvement = baseline_metrics['mae'] - prithvi_metrics['mae']
            improvement_pct = (improvement / baseline_metrics['mae']) * 100
            comparison['mae_improvement'] = {
                'absolute': float(improvement),
                'percentage': float(improvement_pct)
            }
        
        # R² improvement (positive = better)
        if 'r2' in prithvi_metrics and 'r2' in baseline_metrics:
            improvement = prithvi_metrics['r2'] - baseline_metrics['r2']
            comparison['r2_improvement'] = {
                'absolute': float(improvement),
                'percentage': float(improvement * 100)
            }
        
        # Perkins Score improvement
        if 'perkins_score' in prithvi_metrics and 'perkins_score' in baseline_metrics:
            improvement = prithvi_metrics['perkins_score'] - baseline_metrics['perkins_score']
            comparison['perkins_improvement'] = {
                'absolute': float(improvement),
                'percentage': float(improvement * 100)
            }
        
        # Spectral correlation improvement
        if 'spectral_correlation' in prithvi_metrics and 'spectral_correlation' in baseline_metrics:
            improvement = prithvi_metrics['spectral_correlation'] - baseline_metrics['spectral_correlation']
            comparison['spectral_correlation_improvement'] = {
                'absolute': float(improvement),
                'percentage': float(improvement * 100)
            }
        
        return comparison
    
    def calculate_all_metrics(
        self,
        predicted: np.ndarray,
        observed: np.ndarray,
        baseline_predicted: Optional[np.ndarray] = None
    ) -> Dict:
        """
        Calculate all advanced metrics
        
        Args:
            predicted: Prithvi model predictions
            observed: Ground truth observations
            baseline_predicted: Optional baseline predictions for comparison
            
        Returns:
            Dictionary with all metrics
        """
        logger.info("Calculating advanced metrics...")
        
        metrics = {}
        
        # Basic metrics (from baseline module)
        from src.baseline import BaselineDownscaler
        baseline_calc = BaselineDownscaler()
        
        metrics['rmse'] = baseline_calc.calculate_rmse(predicted, observed)
        metrics['mae'] = baseline_calc.calculate_mae(predicted, observed)
        metrics['r2'] = baseline_calc.calculate_r2(predicted, observed)
        
        # Perkins Skill Score
        try:
            metrics['perkins_score'] = self.perkins_skill_score(predicted, observed)
            logger.info(f"Perkins Score: {metrics['perkins_score']:.4f}")
        except Exception as e:
            logger.warning(f"Failed to calculate Perkins Score: {e}")
            metrics['perkins_score'] = np.nan
        
        # Spectral Analysis
        try:
            spectral = self.spectral_analysis(predicted, observed)
            metrics['spectral_correlation'] = spectral['correlation']
            metrics['spectral_analysis'] = spectral
            logger.info(f"Spectral Correlation: {metrics['spectral_correlation']:.4f}")
        except Exception as e:
            logger.warning(f"Failed spectral analysis: {e}")
            metrics['spectral_correlation'] = np.nan
        
        # Comparison with baseline if provided
        if baseline_predicted is not None:
            baseline_metrics = {
                'rmse': baseline_calc.calculate_rmse(baseline_predicted, observed),
                'mae': baseline_calc.calculate_mae(baseline_predicted, observed),
                'r2': baseline_calc.calculate_r2(baseline_predicted, observed),
                'perkins_score': self.perkins_skill_score(baseline_predicted, observed) if SCIPY_AVAILABLE else np.nan
            }
            
            metrics['baseline_comparison'] = self.compare_with_baseline(metrics, baseline_metrics)
        
        logger.info("✅ Advanced metrics calculation complete")
        return metrics


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    metrics_calc = AdvancedMetrics()
    
    # Create dummy data
    np.random.seed(42)
    predicted = np.random.randn(1000) * 5 + 20
    observed = predicted + np.random.randn(1000) * 1  # Add noise
    
    # Calculate metrics
    results = metrics_calc.calculate_all_metrics(predicted, observed)
    print(f"RMSE: {results['rmse']:.4f}")
    print(f"Perkins Score: {results['perkins_score']:.4f}")

