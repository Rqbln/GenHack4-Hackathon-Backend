"""
Main Pipeline Script for Climate Downscaling
Executes the complete workflow from data preparation to evaluation
"""

import argparse
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from data_preparation import prepare_training_data
from modeling import train_and_evaluate_model
from inference import generate_maps_for_period
from visualization import create_evaluation_report


def run_full_pipeline(config: dict):
    """
    Execute the complete climate downscaling pipeline
    
    Pipeline Steps:
    1. Data Preparation: Parse stations, merge with ERA5/NDVI
    2. Model Training: Train residual learning model with spatial CV
    3. Inference: Generate high-resolution temperature maps
    4. Evaluation: Create visualizations and performance reports
    
    Args:
        config: Configuration dictionary with all parameters
    """
    
    print("=" * 70)
    print(" CLIMATE DOWNSCALING PIPELINE - RESIDUAL LEARNING APPROACH")
    print("=" * 70)
    print("\nObjective: Generate high-resolution temperature maps")
    print("Method: ERA5 (9km) + ML Residuals → 80m resolution")
    print("=" * 70)
    
    # Create output directory
    output_dir = Path(config['output_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # ===================================================================
    # PHASE 1: DATA PREPARATION
    # ===================================================================
    print("\n" + "=" * 70)
    print(" PHASE 1: DATA PREPARATION")
    print("=" * 70)
    
    training_data_path = output_dir / 'training_data.csv'
    
    if config.get('skip_data_prep', False) and training_data_path.exists():
        print(f"\nSkipping data preparation. Loading existing data from {training_data_path}")
        import pandas as pd
        training_data = pd.read_csv(training_data_path)
        training_data['DATE'] = pd.to_datetime(training_data['DATE'])
    else:
        training_data = prepare_training_data(
            data_dir=config['data_dir'],
            country_code=config['country_code'],
            date_range=config['date_range'],
            output_path=training_data_path
        )
    
    if training_data.empty:
        print("\nERROR: No training data generated!")
        return
    
    print(f"\n✓ Phase 1 Complete: {len(training_data)} training samples prepared")
    
    # ===================================================================
    # PHASE 2: MODEL TRAINING
    # ===================================================================
    print("\n" + "=" * 70)
    print(" PHASE 2: MODEL TRAINING")
    print("=" * 70)
    
    model, metrics = train_and_evaluate_model(
        training_data=training_data,
        split_type=config.get('split_type', 'spatial'),
        model_type=config.get('model_type', 'random_forest'),
        output_dir=output_dir
    )
    
    print(f"\n✓ Phase 2 Complete: Model trained and evaluated")
    print(f"   - RMSE Improvement: {metrics['Improvement_RMSE']:.3f}°C")
    print(f"   - Model saved to: {output_dir / 'residual_model.pkl'}")
    
    # ===================================================================
    # PHASE 3: INFERENCE (Optional)
    # ===================================================================
    if config.get('generate_maps', False):
        print("\n" + "=" * 70)
        print(" PHASE 3: HIGH-RESOLUTION MAP GENERATION")
        print("=" * 70)
        
        # Define region-specific bounding boxes
        region_bounds = {
            'SE': (10.0, 55.0, 25.0, 70.0),  # Sweden
            'DE': (5.0, 47.0, 15.0, 55.0),    # Germany
            'FR': (-5.0, 41.0, 10.0, 51.0),   # France
            'NO': (4.0, 58.0, 31.0, 71.0),    # Norway
            'FI': (19.0, 59.0, 32.0, 70.0),   # Finland
        }
        
        roi = region_bounds.get(config['country_code'])
        if roi:
            print(f"Using region bounds for {config['country_code']}: LON [{roi[0]}, {roi[2]}], LAT [{roi[1]}, {roi[3]}]")
        else:
            print(f"WARNING: No predefined bounds for {config['country_code']} - will process full Europe (slow!)")
        
        generate_maps_for_period(
            model_path=str(output_dir / 'residual_model.pkl'),
            era5_dir=config['data_dir'] + '/derived-era5-land-daily-statistics',
            ndvi_dir=config['data_dir'] + '/sentinel2_ndvi',
            start_date=config['inference_start_date'],
            end_date=config['inference_end_date'],
            output_dir=str(output_dir / 'highres_maps'),
            roi_bounds=roi
        )
        
        print(f"\n✓ Phase 3 Complete: Maps generated in {output_dir / 'highres_maps'}")
    
    # ===================================================================
    # PHASE 4: EVALUATION & VISUALIZATION
    # ===================================================================
    print("\n" + "=" * 70)
    print(" PHASE 4: EVALUATION & VISUALIZATION")
    print("=" * 70)
    
    create_evaluation_report(
        test_predictions_path=str(output_dir / 'test_predictions.csv'),
        output_dir=str(output_dir / 'evaluation')
    )
    
    print(f"\n✓ Phase 4 Complete: Evaluation report saved to {output_dir / 'evaluation'}")
    
    # ===================================================================
    # PIPELINE COMPLETE
    # ===================================================================
    print("\n" + "=" * 70)
    print(" PIPELINE COMPLETE!")
    print("=" * 70)
    print(f"\nAll outputs saved to: {output_dir}")
    print("\nKey outputs:")
    print(f"  • Training data:        {output_dir / 'training_data.csv'}")
    print(f"  • Trained model:        {output_dir / 'residual_model.pkl'}")
    print(f"  • Test predictions:     {output_dir / 'test_predictions.csv'}")
    print(f"  • Evaluation metrics:   {output_dir / 'evaluation_metrics.csv'}")
    print(f"  • Visualizations:       {output_dir / 'evaluation/'}")
    
    if config.get('generate_maps', False):
        print(f"  • High-res maps:        {output_dir / 'highres_maps/'}")
    
    print("\n" + "=" * 70)


def main():
    """Command-line interface for the pipeline"""
    
    parser = argparse.ArgumentParser(
        description='Climate Downscaling Pipeline - Generate High-Resolution Temperature Maps',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline for Sweden (2020-2023)
  python main.py --country SE --start 2020-01-01 --end 2023-12-31
  
  # Run with map generation for summer 2023
  python main.py --country DE --start 2023-01-01 --end 2023-12-31 \\
                 --generate-maps --inference-start 2023-07-01 --inference-end 2023-07-31
  
  # Quick test run
  python main.py --country SE --start 2023-06-01 --end 2023-08-31
        """
    )
    
    parser.add_argument('--data-dir', type=str, 
                       default='./datasets/main',
                       help='Path to data directory (default: ./datasets/main)')
    
    parser.add_argument('--output-dir', type=str,
                       default='./outputs',
                       help='Path to output directory (default: ./outputs)')
    
    parser.add_argument('--country', type=str, required=True,
                       help='Country code (ISO 3166), e.g., SE, DE, FR')
    
    parser.add_argument('--start', type=str, required=True,
                       help='Start date for training (YYYY-MM-DD)')
    
    parser.add_argument('--end', type=str, required=True,
                       help='End date for training (YYYY-MM-DD)')
    
    parser.add_argument('--model-type', type=str,
                       default='random_forest',
                       choices=['random_forest', 'xgboost'],
                       help='Model type (default: random_forest)')
    
    parser.add_argument('--split-type', type=str,
                       default='spatial',
                       choices=['spatial', 'geographic'],
                       help='Cross-validation split type (default: spatial)')
    
    parser.add_argument('--generate-maps', action='store_true',
                       help='Generate high-resolution maps after training')
    
    parser.add_argument('--inference-start', type=str,
                       help='Start date for map generation (YYYY-MM-DD)')
    
    parser.add_argument('--inference-end', type=str,
                       help='End date for map generation (YYYY-MM-DD)')
    
    parser.add_argument('--skip-data-prep', action='store_true',
                       help='Skip data preparation if training data exists')
    
    args = parser.parse_args()
    
    # Build configuration
    config = {
        'data_dir': args.data_dir,
        'output_dir': args.output_dir,
        'country_code': args.country,
        'date_range': (args.start, args.end),
        'model_type': args.model_type,
        'split_type': args.split_type,
        'generate_maps': args.generate_maps,
        'skip_data_prep': args.skip_data_prep
    }
    
    # Add inference dates if map generation requested
    if args.generate_maps:
        if not args.inference_start or not args.inference_end:
            print("ERROR: --inference-start and --inference-end required when using --generate-maps")
            sys.exit(1)
        
        config['inference_start_date'] = args.inference_start
        config['inference_end_date'] = args.inference_end
    
    # Run pipeline
    try:
        run_full_pipeline(config)
    except Exception as e:
        print(f"\nERROR: Pipeline failed with exception:")
        print(f"{type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
