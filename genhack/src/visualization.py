"""
Phase 4: Evaluation & Visualization
Provides tools to assess model performance and visualize results
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import rasterio
from rasterio.plot import show
from pathlib import Path
from typing import Optional, List, Tuple
from matplotlib.colors import LinearSegmentedColormap
import warnings
warnings.filterwarnings('ignore')


class ModelEvaluator:
    """Comprehensive model evaluation tools"""
    
    def __init__(self, test_predictions: pd.DataFrame):
        """
        Initialize evaluator
        
        Args:
            test_predictions: DataFrame with columns:
                [Station_Temp, ERA5_Temp, Predicted_Residual, Predicted_Temp]
        """
        self.df = test_predictions
    
    def plot_residual_distribution(self, save_path: Optional[str] = None):
        """Plot distribution of actual vs predicted residuals"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Actual residuals
        axes[0].hist(self.df['Residual'], bins=50, alpha=0.7, color='blue', edgecolor='black')
        axes[0].axvline(0, color='red', linestyle='--', linewidth=2, label='Zero residual')
        axes[0].set_xlabel('Temperature Residual (°C)', fontsize=12)
        axes[0].set_ylabel('Frequency', fontsize=12)
        axes[0].set_title('Distribution of Actual Residuals\n(Station - ERA5)', fontsize=13, fontweight='bold')
        axes[0].legend()
        axes[0].grid(alpha=0.3)
        
        # Predicted residuals
        axes[1].hist(self.df['Predicted_Residual'], bins=50, alpha=0.7, color='green', edgecolor='black')
        axes[1].axvline(0, color='red', linestyle='--', linewidth=2, label='Zero residual')
        axes[1].set_xlabel('Temperature Residual (°C)', fontsize=12)
        axes[1].set_ylabel('Frequency', fontsize=12)
        axes[1].set_title('Distribution of Predicted Residuals\n(Model Output)', fontsize=13, fontweight='bold')
        axes[1].legend()
        axes[1].grid(alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved to {save_path}")
        
        plt.show()
    
    def plot_scatter_predictions(self, save_path: Optional[str] = None):
        """Scatter plot of predicted vs actual values"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Residual predictions
        axes[0].scatter(self.df['Residual'], self.df['Predicted_Residual'], 
                       alpha=0.3, s=10, color='blue')
        
        # Add perfect prediction line
        min_val = min(self.df['Residual'].min(), self.df['Predicted_Residual'].min())
        max_val = max(self.df['Residual'].max(), self.df['Predicted_Residual'].max())
        axes[0].plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect prediction')
        
        axes[0].set_xlabel('Actual Residual (°C)', fontsize=12)
        axes[0].set_ylabel('Predicted Residual (°C)', fontsize=12)
        axes[0].set_title('Residual Prediction Performance', fontsize=13, fontweight='bold')
        axes[0].legend()
        axes[0].grid(alpha=0.3)
        axes[0].set_aspect('equal', adjustable='box')
        
        # Temperature predictions
        axes[1].scatter(self.df['Station_Temp'], self.df['Predicted_Temp'],
                       alpha=0.3, s=10, color='green')
        
        min_val = min(self.df['Station_Temp'].min(), self.df['Predicted_Temp'].min())
        max_val = max(self.df['Station_Temp'].max(), self.df['Predicted_Temp'].max())
        axes[1].plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect prediction')
        
        axes[1].set_xlabel('Actual Temperature (°C)', fontsize=12)
        axes[1].set_ylabel('Predicted Temperature (°C)', fontsize=12)
        axes[1].set_title('Final Temperature Prediction', fontsize=13, fontweight='bold')
        axes[1].legend()
        axes[1].grid(alpha=0.3)
        axes[1].set_aspect('equal', adjustable='box')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved to {save_path}")
        
        plt.show()
    
    def plot_error_by_feature(self, save_path: Optional[str] = None):
        """Plot prediction error as function of input features"""
        self.df['Error'] = self.df['Predicted_Temp'] - self.df['Station_Temp']
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Error vs NDVI
        axes[0, 0].scatter(self.df['NDVI'], self.df['Error'], alpha=0.3, s=10)
        axes[0, 0].axhline(0, color='red', linestyle='--', linewidth=2)
        axes[0, 0].set_xlabel('NDVI', fontsize=11)
        axes[0, 0].set_ylabel('Prediction Error (°C)', fontsize=11)
        axes[0, 0].set_title('Error vs NDVI', fontsize=12, fontweight='bold')
        axes[0, 0].grid(alpha=0.3)
        
        # Error vs Elevation
        axes[0, 1].scatter(self.df['ELEVATION'], self.df['Error'], alpha=0.3, s=10)
        axes[0, 1].axhline(0, color='red', linestyle='--', linewidth=2)
        axes[0, 1].set_xlabel('Elevation (m)', fontsize=11)
        axes[0, 1].set_ylabel('Prediction Error (°C)', fontsize=11)
        axes[0, 1].set_title('Error vs Elevation', fontsize=12, fontweight='bold')
        axes[0, 1].grid(alpha=0.3)
        
        # Error vs Temperature
        axes[1, 0].scatter(self.df['ERA5_Temp'], self.df['Error'], alpha=0.3, s=10)
        axes[1, 0].axhline(0, color='red', linestyle='--', linewidth=2)
        axes[1, 0].set_xlabel('ERA5 Temperature (°C)', fontsize=11)
        axes[1, 0].set_ylabel('Prediction Error (°C)', fontsize=11)
        axes[1, 0].set_title('Error vs ERA5 Temperature', fontsize=12, fontweight='bold')
        axes[1, 0].grid(alpha=0.3)
        
        # Error vs Day of Year
        axes[1, 1].scatter(self.df['DayOfYear'], self.df['Error'], alpha=0.3, s=10)
        axes[1, 1].axhline(0, color='red', linestyle='--', linewidth=2)
        axes[1, 1].set_xlabel('Day of Year', fontsize=11)
        axes[1, 1].set_ylabel('Prediction Error (°C)', fontsize=11)
        axes[1, 1].set_title('Error vs Day of Year', fontsize=12, fontweight='bold')
        axes[1, 1].grid(alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved to {save_path}")
        
        plt.show()
    
    def plot_comparison_baseline(self, save_path: Optional[str] = None):
        """Compare model performance to ERA5 baseline"""
        # Calculate errors
        model_error = np.abs(self.df['Predicted_Temp'] - self.df['Station_Temp'])
        baseline_error = np.abs(self.df['ERA5_Temp'] - self.df['Station_Temp'])
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Error distributions
        axes[0].hist(baseline_error, bins=50, alpha=0.6, label='ERA5 Baseline', color='red', edgecolor='black')
        axes[0].hist(model_error, bins=50, alpha=0.6, label='Our Model', color='green', edgecolor='black')
        axes[0].set_xlabel('Absolute Error (°C)', fontsize=12)
        axes[0].set_ylabel('Frequency', fontsize=12)
        axes[0].set_title('Error Distribution Comparison', fontsize=13, fontweight='bold')
        axes[0].legend(fontsize=11)
        axes[0].grid(alpha=0.3)
        
        # Cumulative improvement
        improvements = baseline_error - model_error
        axes[1].hist(improvements, bins=50, color='blue', edgecolor='black', alpha=0.7)
        axes[1].axvline(0, color='red', linestyle='--', linewidth=2, label='No improvement')
        axes[1].axvline(improvements.mean(), color='green', linestyle='-', linewidth=2, 
                       label=f'Mean: {improvements.mean():.3f}°C')
        axes[1].set_xlabel('Error Reduction (°C)', fontsize=12)
        axes[1].set_ylabel('Frequency', fontsize=12)
        axes[1].set_title('Per-Sample Improvement over ERA5', fontsize=13, fontweight='bold')
        axes[1].legend(fontsize=10)
        axes[1].grid(alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved to {save_path}")
        
        plt.show()
        
        # Print statistics
        print("\n=== Performance Comparison ===")
        print(f"ERA5 Baseline MAE: {baseline_error.mean():.3f}°C")
        print(f"Our Model MAE:     {model_error.mean():.3f}°C")
        print(f"Average Improvement: {improvements.mean():.3f}°C")
        print(f"Samples improved: {(improvements > 0).sum()} / {len(improvements)} ({100*(improvements > 0).mean():.1f}%)")


class MapVisualizer:
    """Visualize high-resolution temperature maps"""
    
    def __init__(self):
        # Create custom colormap for temperature
        self.temp_cmap = plt.cm.RdYlBu_r  # Red for hot, Blue for cold
    
    def plot_single_map(self, raster_path: str, 
                       title: str = "High-Resolution Temperature",
                       save_path: Optional[str] = None,
                       vmin: Optional[float] = None,
                       vmax: Optional[float] = None):
        """
        Plot a single temperature map
        
        Args:
            raster_path: Path to GeoTIFF file
            title: Plot title
            save_path: Optional path to save figure
            vmin, vmax: Optional temperature range for color scale
        """
        with rasterio.open(raster_path) as src:
            data = src.read(1)
            
            # Determine color scale
            if vmin is None:
                vmin = np.nanpercentile(data, 2)
            if vmax is None:
                vmax = np.nanpercentile(data, 98)
            
            fig, ax = plt.subplots(figsize=(12, 10))
            
            im = ax.imshow(data, cmap=self.temp_cmap, vmin=vmin, vmax=vmax)
            
            cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
            cbar.set_label('Temperature (°C)', fontsize=12, fontweight='bold')
            
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            ax.axis('off')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"Saved to {save_path}")
            
            plt.show()
    
    def plot_comparison(self, era5_path: str, highres_path: str, residual_path: str,
                       save_path: Optional[str] = None):
        """
        Plot side-by-side comparison: ERA5, Residual, High-Res
        
        Args:
            era5_path: Path to upsampled ERA5 map
            highres_path: Path to high-resolution output
            residual_path: Path to predicted residual map
            save_path: Optional path to save figure
        """
        fig, axes = plt.subplots(1, 3, figsize=(20, 6))
        
        # Load data
        with rasterio.open(highres_path) as src:
            highres = src.read(1)
        
        with rasterio.open(residual_path) as src:
            residual = src.read(1)
        
        # Calculate ERA5 from highres and residual
        era5 = highres - residual
        
        # Shared temperature scale for ERA5 and HighRes
        temp_vmin = np.nanpercentile(np.concatenate([era5.ravel(), highres.ravel()]), 2)
        temp_vmax = np.nanpercentile(np.concatenate([era5.ravel(), highres.ravel()]), 98)
        
        # Plot ERA5
        im1 = axes[0].imshow(era5, cmap=self.temp_cmap, vmin=temp_vmin, vmax=temp_vmax)
        axes[0].set_title('ERA5 Baseline\n(~9 km resolution)', fontsize=12, fontweight='bold')
        axes[0].axis('off')
        plt.colorbar(im1, ax=axes[0], fraction=0.046, pad=0.04, label='°C')
        
        # Plot Residual
        residual_abs_max = max(abs(np.nanpercentile(residual, 2)), abs(np.nanpercentile(residual, 98)))
        im2 = axes[1].imshow(residual, cmap='RdBu_r', vmin=-residual_abs_max, vmax=residual_abs_max)
        axes[1].set_title('Predicted Residual\n(Urban Heat Island Effect)', fontsize=12, fontweight='bold')
        axes[1].axis('off')
        plt.colorbar(im2, ax=axes[1], fraction=0.046, pad=0.04, label='°C')
        
        # Plot High-Res
        im3 = axes[2].imshow(highres, cmap=self.temp_cmap, vmin=temp_vmin, vmax=temp_vmax)
        axes[2].set_title('High-Resolution Output\n(~80 m resolution)', fontsize=12, fontweight='bold')
        axes[2].axis('off')
        plt.colorbar(im3, ax=axes[2], fraction=0.046, pad=0.04, label='°C')
        
        plt.suptitle('Temperature Downscaling: ERA5 + Residual = High-Res', 
                    fontsize=14, fontweight='bold', y=1.02)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved to {save_path}")
        
        plt.show()
    
    def create_animation(self, map_files: List[str], output_path: str, fps: int = 2):
        """
        Create animated GIF from sequence of maps
        
        Args:
            map_files: List of GeoTIFF file paths
            output_path: Output GIF path
            fps: Frames per second
        """
        import imageio
        
        images = []
        
        # Determine global vmin/vmax
        all_data = []
        for f in map_files:
            with rasterio.open(f) as src:
                all_data.append(src.read(1).ravel())
        
        combined = np.concatenate(all_data)
        vmin = np.nanpercentile(combined, 2)
        vmax = np.nanpercentile(combined, 98)
        
        # Generate frames
        for f in map_files:
            with rasterio.open(f) as src:
                data = src.read(1)
            
            # Create plot
            fig, ax = plt.subplots(figsize=(10, 8))
            im = ax.imshow(data, cmap=self.temp_cmap, vmin=vmin, vmax=vmax)
            plt.colorbar(im, ax=ax, label='Temperature (°C)')
            
            # Extract date from filename
            date_str = Path(f).stem.split('_')[-1]
            ax.set_title(f'High-Resolution Temperature: {date_str}', fontsize=12, fontweight='bold')
            ax.axis('off')
            
            # Convert plot to image
            fig.canvas.draw()
            image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
            image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
            images.append(image)
            
            plt.close(fig)
        
        # Save as GIF
        imageio.mimsave(output_path, images, fps=fps)
        print(f"Animation saved to {output_path}")


def create_evaluation_report(test_predictions_path: str, output_dir: str):
    """
    Generate complete evaluation report with all visualizations
    
    Args:
        test_predictions_path: Path to test predictions CSV
        output_dir: Directory to save outputs
    """
    print("\n=== Creating Evaluation Report ===")
    
    # Load predictions
    df = pd.read_csv(test_predictions_path)
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize evaluator
    evaluator = ModelEvaluator(df)
    
    # Generate all plots
    print("\n1. Residual distributions...")
    evaluator.plot_residual_distribution(
        save_path=output_path / 'residual_distributions.png'
    )
    
    print("\n2. Scatter predictions...")
    evaluator.plot_scatter_predictions(
        save_path=output_path / 'scatter_predictions.png'
    )
    
    print("\n3. Error by feature...")
    evaluator.plot_error_by_feature(
        save_path=output_path / 'error_by_feature.png'
    )
    
    print("\n4. Baseline comparison...")
    evaluator.plot_comparison_baseline(
        save_path=output_path / 'baseline_comparison.png'
    )
    
    print(f"\nEvaluation report complete! Saved to {output_dir}")


if __name__ == "__main__":
    # Example usage
    create_evaluation_report(
        test_predictions_path='../outputs/test_predictions.csv',
        output_dir='../outputs/evaluation'
    )
