#!/usr/bin/env python3
"""
Generate Baseline Metrics Report

Calculates baseline metrics for comparison with Prithvi WxC model.
Generates a comprehensive report with RMSE, MAE, R² for baseline interpolation.
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
from src.baseline import BaselineDownscaler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def generate_baseline_metrics_report(output_path: Path):
    """
    Generate baseline metrics report
    
    Args:
        output_path: Path to save the report JSON
    """
    print("=" * 60)
    print("Generating Baseline Metrics Report")
    print("=" * 60)
    
    # Initialize baseline downscaler
    downscaler = BaselineDownscaler(
        target_resolution=100.0,
        lapse_rate=-0.0065,
        interpolation_method='cubic'
    )
    
    # Note: This is a template report structure
    # In production, this would use real data from ETL pipeline
    report = {
        "report_date": datetime.now().isoformat(),
        "baseline_method": "Bicubic Interpolation + Altitude Correction",
        "target_resolution_m": 100.0,
        "lapse_rate_km": -0.0065,
        "metrics": {
            "rmse_celsius": None,  # Would be calculated from real data
            "mae_celsius": None,
            "r2": None,
            "n_samples": None
        },
        "comparison_target": "Pentagen Team Baseline",
        "notes": [
            "Baseline uses bicubic interpolation from ERA5 (9km) to target resolution (100m)",
            "Altitude correction applied using standard atmospheric lapse rate",
            "Metrics calculated against ECA&D ground truth stations",
            "This serves as benchmark for Prithvi WxC fine-tuning"
        ],
        "status": "template",
        "next_steps": [
            "Run on real ERA5/ECA&D aligned data",
            "Calculate metrics for all time periods",
            "Compare with Pentagen baseline results",
            "Use as target for Prithvi WxC improvement"
        ]
    }
    
    # Save report
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Baseline metrics report saved to {output_path}")
    print(f"\nReport Summary:")
    print(f"  Method: {report['baseline_method']}")
    print(f"  Target Resolution: {report['target_resolution_m']}m")
    print(f"  Status: {report['status']}")
    
    return report


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    output_path = project_root / "reports" / "baseline_metrics.json"
    
    report = generate_baseline_metrics_report(output_path)
    print("\n" + "=" * 60)
    print("✅ Baseline metrics report generated successfully")
    print("=" * 60)

