"""
Export Results and Figures for Final Report

Generates all necessary outputs for the final hackathon submission:
- Summary statistics
- Comparison figures
- Validation plots
- Metrics tables
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logger.warning("matplotlib not available. Install with: pip install matplotlib")


class ResultsExporter:
    """Export results and figures for final report"""
    
    def __init__(self, output_dir: Path):
        """
        Initialize results exporter
        
        Args:
            output_dir: Directory to save exported files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if MATPLOTLIB_AVAILABLE:
            plt.style.use('seaborn-v0_8-darkgrid')
        
        logger.info(f"Results Exporter initialized: {output_dir}")
    
    def export_metrics_table(
        self,
        metrics: Dict,
        baseline_metrics: Optional[Dict] = None,
        output_path: Path = None
    ) -> Path:
        """
        Export metrics comparison table as JSON
        
        Args:
            metrics: Prithvi model metrics
            baseline_metrics: Baseline model metrics (optional)
            output_path: Output file path (optional)
            
        Returns:
            Path to exported file
        """
        if output_path is None:
            output_path = self.output_dir / 'metrics_comparison.json'
        
        comparison = {
            'export_date': datetime.now().isoformat(),
            'prithvi_metrics': metrics,
            'baseline_metrics': baseline_metrics,
            'improvements': {}
        }
        
        if baseline_metrics:
            # Calculate improvements
            for key in ['rmse', 'mae', 'r2', 'perkins_score']:
                if key in metrics and key in baseline_metrics:
                    if key in ['rmse', 'mae']:
                        # Lower is better
                        improvement = baseline_metrics[key] - metrics[key]
                        improvement_pct = (improvement / baseline_metrics[key]) * 100
                    else:
                        # Higher is better
                        improvement = metrics[key] - baseline_metrics[key]
                        improvement_pct = (improvement / baseline_metrics[key]) * 100 if baseline_metrics[key] != 0 else 0
                    
                    comparison['improvements'][key] = {
                        'absolute': float(improvement),
                        'percentage': float(improvement_pct)
                    }
        
        with open(output_path, 'w') as f:
            json.dump(comparison, f, indent=2)
        
        logger.info(f"✅ Metrics table exported to {output_path}")
        return output_path
    
    def plot_metrics_comparison(
        self,
        metrics: Dict,
        baseline_metrics: Optional[Dict] = None,
        output_path: Path = None
    ) -> Path:
        """
        Create metrics comparison bar chart
        
        Args:
            metrics: Prithvi model metrics
            baseline_metrics: Baseline model metrics (optional)
            output_path: Output file path (optional)
            
        Returns:
            Path to exported figure
        """
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("matplotlib is required for plotting")
        
        if output_path is None:
            output_path = self.output_dir / 'metrics_comparison.png'
        
        # Prepare data
        metric_names = ['RMSE', 'MAE', 'R²', 'Perkins Score']
        prithvi_values = [
            metrics.get('rmse', 0),
            metrics.get('mae', 0),
            metrics.get('r2', 0),
            metrics.get('perkins_score', 0)
        ]
        
        x = np.arange(len(metric_names))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bars1 = ax.bar(x - width/2, prithvi_values, width, label='Prithvi WxC', color='#3b82f6')
        
        if baseline_metrics:
            baseline_values = [
                baseline_metrics.get('rmse', 0),
                baseline_metrics.get('mae', 0),
                baseline_metrics.get('r2', 0),
                baseline_metrics.get('perkins_score', 0)
            ]
            bars2 = ax.bar(x + width/2, baseline_values, width, label='Baseline', color='#ef4444')
        
        ax.set_xlabel('Metrics', fontsize=12, fontweight='bold')
        ax.set_ylabel('Value', fontsize=12, fontweight='bold')
        ax.set_title('Model Performance Comparison', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(metric_names)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"✅ Metrics comparison plot saved to {output_path}")
        return output_path
    
    def plot_training_history(
        self,
        train_losses: List[float],
        val_losses: List[float],
        output_path: Path = None
    ) -> Path:
        """
        Plot training history
        
        Args:
            train_losses: Training loss values
            val_losses: Validation loss values
            output_path: Output file path (optional)
            
        Returns:
            Path to exported figure
        """
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("matplotlib is required for plotting")
        
        if output_path is None:
            output_path = self.output_dir / 'training_history.png'
        
        epochs = range(1, len(train_losses) + 1)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(epochs, train_losses, 'b-', label='Training Loss', linewidth=2)
        ax.plot(epochs, val_losses, 'r-', label='Validation Loss', linewidth=2)
        
        ax.set_xlabel('Epoch', fontsize=12, fontweight='bold')
        ax.set_ylabel('Loss', fontsize=12, fontweight='bold')
        ax.set_title('Training History - Loss Convergence', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"✅ Training history plot saved to {output_path}")
        return output_path
    
    def export_summary_report(
        self,
        metrics: Dict,
        physics_validation: Dict,
        baseline_comparison: Optional[Dict] = None,
        output_path: Path = None
    ) -> Path:
        """
        Export comprehensive summary report
        
        Args:
            metrics: Model metrics
            physics_validation: Physics validation results
            baseline_comparison: Baseline comparison (optional)
            output_path: Output file path (optional)
            
        Returns:
            Path to exported report
        """
        if output_path is None:
            output_path = self.output_dir / 'summary_report.json'
        
        report = {
            'export_date': datetime.now().isoformat(),
            'model_metrics': metrics,
            'physics_validation': physics_validation,
            'baseline_comparison': baseline_comparison,
            'summary': {
                'model_performance': 'Good' if metrics.get('r2', 0) > 0.7 else 'Needs Improvement',
                'physics_consistency': 'Valid' if physics_validation.get('overall', {}).get('is_valid', False) else 'Invalid',
                'baseline_improvement': 'Yes' if baseline_comparison and baseline_comparison.get('rmse_improvement', {}).get('percentage', 0) > 0 else 'No'
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"✅ Summary report exported to {output_path}")
        return output_path
    
    def export_all(
        self,
        metrics: Dict,
        physics_validation: Dict,
        baseline_metrics: Optional[Dict] = None,
        train_losses: Optional[List[float]] = None,
        val_losses: Optional[List[float]] = None
    ) -> Dict[str, Path]:
        """
        Export all results and figures
        
        Args:
            metrics: Model metrics
            physics_validation: Physics validation results
            baseline_metrics: Baseline metrics (optional)
            train_losses: Training losses (optional)
            val_losses: Validation losses (optional)
            
        Returns:
            Dictionary mapping export names to file paths
        """
        logger.info("Exporting all results and figures...")
        
        exports = {}
        
        # Export metrics table
        exports['metrics_table'] = self.export_metrics_table(metrics, baseline_metrics)
        
        # Export metrics comparison plot
        if MATPLOTLIB_AVAILABLE:
            exports['metrics_plot'] = self.plot_metrics_comparison(metrics, baseline_metrics)
            
            # Export training history if available
            if train_losses and val_losses:
                exports['training_history'] = self.plot_training_history(train_losses, val_losses)
        
        # Export summary report
        baseline_comparison = None
        if baseline_metrics:
            from src.advanced_metrics import AdvancedMetrics
            metrics_calc = AdvancedMetrics()
            baseline_comparison = metrics_calc.compare_with_baseline(metrics, baseline_metrics)
        
        exports['summary_report'] = self.export_summary_report(
            metrics,
            physics_validation,
            baseline_comparison
        )
        
        logger.info(f"✅ All exports complete: {len(exports)} files generated")
        return exports


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    exporter = ResultsExporter(Path("./exports"))
    print("Results exporter initialized")

