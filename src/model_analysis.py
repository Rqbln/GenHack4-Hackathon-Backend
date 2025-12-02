"""
Model Analysis and Hyperparameter Tuning

Analyzes fine-tuning results, performs hyperparameter optimization,
and validates model performance with spatial cross-validation.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
import numpy as np

logger = logging.getLogger(__name__)

try:
    import torch
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logger.warning("matplotlib not available. Install with: pip install matplotlib")


class ModelAnalyzer:
    """Analyze and optimize fine-tuned model"""
    
    def __init__(self, model_dir: Path, results_dir: Path):
        """
        Initialize model analyzer
        
        Args:
            model_dir: Directory containing fine-tuned model
            results_dir: Directory to save analysis results
        """
        self.model_dir = Path(model_dir)
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
    def analyze_training_history(
        self,
        history_path: Path
    ) -> Dict:
        """
        Analyze training history and identify convergence
        
        Args:
            history_path: Path to training history JSON
            
        Returns:
            Dictionary with analysis results
        """
        logger.info("Analyzing training history...")
        
        with open(history_path, 'r') as f:
            history = json.load(f)
        
        train_losses = history.get('train_loss', [])
        val_losses = history.get('val_loss', [])
        
        analysis = {
            'final_train_loss': train_losses[-1] if train_losses else None,
            'final_val_loss': val_losses[-1] if val_losses else None,
            'best_val_loss': min(val_losses) if val_losses else None,
            'best_epoch': val_losses.index(min(val_losses)) if val_losses else None,
            'convergence_epoch': self._detect_convergence(val_losses),
            'overfitting_detected': self._detect_overfitting(train_losses, val_losses)
        }
        
        # Plot training curves if matplotlib available
        if MATPLOTLIB_AVAILABLE and train_losses and val_losses:
            self._plot_training_curves(train_losses, val_losses)
        
        logger.info(f"Training analysis complete: Best val loss = {analysis['best_val_loss']:.4f}")
        return analysis
    
    def _detect_convergence(self, losses: List[float], patience: int = 5) -> Optional[int]:
        """Detect convergence epoch (no improvement for patience epochs)"""
        if len(losses) < patience + 1:
            return None
        
        best_loss = min(losses)
        best_idx = losses.index(best_loss)
        
        # Check if no improvement after best epoch
        if best_idx + patience < len(losses):
            subsequent_losses = losses[best_idx + 1:best_idx + patience + 1]
            if all(loss >= best_loss * 1.01 for loss in subsequent_losses):  # 1% tolerance
                return best_idx + patience
        
        return None
    
    def _detect_overfitting(
        self,
        train_losses: List[float],
        val_losses: List[float]
    ) -> bool:
        """Detect overfitting (val loss increasing while train loss decreasing)"""
        if len(train_losses) < 3 or len(val_losses) < 3:
            return False
        
        # Check last 3 epochs
        recent_train = train_losses[-3:]
        recent_val = val_losses[-3:]
        
        train_decreasing = recent_train[0] > recent_train[-1]
        val_increasing = recent_val[0] < recent_val[-1]
        
        return train_decreasing and val_increasing
    
    def _plot_training_curves(
        self,
        train_losses: List[float],
        val_losses: List[float]
    ):
        """Plot training and validation loss curves"""
        plt.figure(figsize=(10, 6))
        epochs = range(1, len(train_losses) + 1)
        
        plt.plot(epochs, train_losses, 'b-', label='Training Loss', linewidth=2)
        plt.plot(epochs, val_losses, 'r-', label='Validation Loss', linewidth=2)
        
        plt.xlabel('Epoch', fontsize=12)
        plt.ylabel('Loss', fontsize=12)
        plt.title('Training History - Loss Convergence', fontsize=14, fontweight='bold')
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        
        output_path = self.results_dir / 'training_curves.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Training curves saved to {output_path}")
    
    def spatial_cross_validation(
        self,
        predictions: np.ndarray,
        ground_truth: np.ndarray,
        spatial_groups: np.ndarray,
        n_folds: int = 5
    ) -> Dict:
        """
        Perform spatial cross-validation
        
        Args:
            predictions: Model predictions
            ground_truth: Ground truth values
            spatial_groups: Spatial group IDs for each sample
            n_folds: Number of folds
            
        Returns:
            Dictionary with CV results
        """
        logger.info(f"Performing {n_folds}-fold spatial cross-validation...")
        
        unique_groups = np.unique(spatial_groups)
        np.random.shuffle(unique_groups)
        
        fold_size = len(unique_groups) // n_folds
        cv_scores = []
        
        for fold in range(n_folds):
            start_idx = fold * fold_size
            end_idx = start_idx + fold_size if fold < n_folds - 1 else len(unique_groups)
            
            test_groups = unique_groups[start_idx:end_idx]
            train_groups = np.setdiff1d(unique_groups, test_groups)
            
            # Split data
            test_mask = np.isin(spatial_groups, test_groups)
            train_mask = np.isin(spatial_groups, train_groups)
            
            test_pred = predictions[test_mask]
            test_true = ground_truth[test_mask]
            
            # Calculate metrics for this fold
            rmse = np.sqrt(np.mean((test_pred - test_true) ** 2))
            mae = np.mean(np.abs(test_pred - test_true))
            
            cv_scores.append({
                'fold': fold + 1,
                'rmse': rmse,
                'mae': mae,
                'n_test_samples': len(test_pred)
            })
        
        # Aggregate results
        mean_rmse = np.mean([s['rmse'] for s in cv_scores])
        std_rmse = np.std([s['rmse'] for s in cv_scores])
        mean_mae = np.mean([s['mae'] for s in cv_scores])
        std_mae = np.std([s['mae'] for s in cv_scores])
        
        results = {
            'n_folds': n_folds,
            'mean_rmse': mean_rmse,
            'std_rmse': std_rmse,
            'mean_mae': mean_mae,
            'std_mae': std_mae,
            'fold_scores': cv_scores
        }
        
        logger.info(f"CV Results: RMSE = {mean_rmse:.4f} ± {std_rmse:.4f}")
        return results
    
    def hyperparameter_sensitivity(
        self,
        results: List[Dict]
    ) -> Dict:
        """
        Analyze hyperparameter sensitivity
        
        Args:
            results: List of results dictionaries with different hyperparameters
            
        Returns:
            Sensitivity analysis results
        """
        logger.info("Analyzing hyperparameter sensitivity...")
        
        # Extract hyperparameters and metrics
        analysis = {
            'learning_rate': {},
            'lora_r': {},
            'batch_size': {}
        }
        
        for result in results:
            lr = result.get('learning_rate')
            lora_r = result.get('lora_r')
            batch = result.get('batch_size')
            val_loss = result.get('val_loss')
            
            if lr and val_loss:
                if lr not in analysis['learning_rate']:
                    analysis['learning_rate'][lr] = []
                analysis['learning_rate'][lr].append(val_loss)
            
            if lora_r and val_loss:
                if lora_r not in analysis['lora_r']:
                    analysis['lora_r'][lora_r] = []
                analysis['lora_r'][lora_r].append(val_loss)
            
            if batch and val_loss:
                if batch not in analysis['batch_size']:
                    analysis['batch_size'][batch] = []
                analysis['batch_size'][batch].append(val_loss)
        
        # Compute means
        for param_name in analysis:
            for param_value in analysis[param_name]:
                losses = analysis[param_name][param_value]
                analysis[param_name][param_value] = {
                    'mean': np.mean(losses),
                    'std': np.std(losses),
                    'n_runs': len(losses)
                }
        
        return analysis
    
    def save_analysis_report(self, analysis: Dict, output_path: Path):
        """Save analysis report to JSON"""
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        logger.info(f"Analysis report saved to {output_path}")


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    analyzer = ModelAnalyzer(
        model_dir=Path("./models/finetuned_prithvi"),
        results_dir=Path("./results/analysis")
    )
    
    print("Model analyzer initialized")

