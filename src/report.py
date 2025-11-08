"""
GenHack Climate - Report Generation

Generates HTML and PDF reports using Jinja2 templates and Weasyprint.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from src.models import Manifest, Indicators, Metrics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_indicators(exports_dir: Path) -> Optional[Indicators]:
    """Load indicators from JSON file"""
    indicators_path = exports_dir / "indicators.json"
    if indicators_path.exists():
        with open(indicators_path) as f:
            data = json.load(f)
            return Indicators(**data)
    return None


def load_metrics(exports_dir: Path) -> Optional[Metrics]:
    """Load metrics from JSON file"""
    metrics_path = exports_dir / "metrics.json"
    if metrics_path.exists():
        with open(metrics_path) as f:
            data = json.load(f)
            return Metrics(**data)
    return None


def collect_maps(exports_dir: Path) -> List[Dict[str, str]]:
    """Collect PNG map previews"""
    maps = []
    
    map_configs = [
        ("temperature.png", "Temperature Distribution", "2-meter temperature"),
        ("ndvi.png", "Vegetation Index (NDVI)", "Normalized Difference Vegetation Index"),
        ("ndbi.png", "Built-up Index (NDBI)", "Normalized Difference Built-up Index")
    ]
    
    for filename, title, caption in map_configs:
        map_path = exports_dir / f"{exports_dir.parent.parent.name}_{filename}"
        if map_path.exists():
            maps.append({
                "path": str(map_path),
                "title": title,
                "caption": caption
            })
    
    return maps


def generate_report(
    config: Dict[str, Any],
    manifest: Manifest,
    template_dir: Path,
    output_dir: Path
) -> Dict[str, Path]:
    """
    Generate HTML and PDF reports
    
    Args:
        config: Pipeline configuration
        manifest: Pipeline manifest
        template_dir: Directory containing Jinja2 templates
        output_dir: Output directory for reports
        
    Returns:
        Dict mapping format to output path
    """
    logger.info("🔄 Generating report...")
    
    exports_dir = Path(manifest.paths.exports.replace("gs://", "/tmp/gcs/"))
    
    # Load data
    indicators = load_indicators(exports_dir)
    metrics = load_metrics(exports_dir)
    maps = collect_maps(exports_dir)
    
    # Prepare template context
    context = {
        "city": manifest.city,
        "period_start": manifest.period.start,
        "period_end": manifest.period.end,
        "resolution_m": manifest.grid.resolution_m,
        "crs": manifest.grid.crs,
        "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "mode_dry_run": manifest.mode.dry_run if manifest.mode else False,
        "indicators": indicators.model_dump() if indicators else None,
        "metrics": metrics.model_dump() if metrics else None,
        "maps": maps,
        "include_maps": config.get("output", {}).get("report", {}).get("include_maps", True),
        "include_metrics": config.get("output", {}).get("report", {}).get("include_metrics", True),
        "variables": manifest.variables,
        "stage": manifest.stage
    }
    
    # Setup Jinja2
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("report.html.j2")
    
    # Render HTML
    html_content = template.render(**context)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {}
    
    # Save HTML
    html_path = output_dir / f"{manifest.city}_report.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    outputs['html'] = html_path
    logger.info(f"✅ HTML report: {html_path}")
    
    # Generate PDF
    report_formats = config.get("output", {}).get("report", {}).get("format", ["html", "pdf"])
    if "pdf" in report_formats:
        try:
            pdf_path = output_dir / f"{manifest.city}_report.pdf"
            HTML(string=html_content, base_url=str(output_dir)).write_pdf(pdf_path)
            outputs['pdf'] = pdf_path
            logger.info(f"✅ PDF report: {pdf_path}")
        except Exception as e:
            logger.error(f"❌ PDF generation failed: {e}")
            logger.info("   Continuing with HTML only")
    
    return outputs


def report_stage(config: Dict[str, Any], manifest: Manifest) -> Manifest:
    """
    Report generation stage
    
    Args:
        config: Pipeline configuration
        manifest: Input manifest
        
    Returns:
        Updated manifest
    """
    logger.info("🔄 REPORT STAGE")
    
    # Find template directory
    template_dir = Path(__file__).parent.parent / "templates"
    if not template_dir.exists():
        raise FileNotFoundError(f"Template directory not found: {template_dir}")
    
    if not manifest.paths or not manifest.paths.exports:
        raise ValueError("No exports path in manifest")
    
    exports_dir = Path(manifest.paths.exports.replace("gs://", "/tmp/gcs/"))
    
    # Generate reports
    outputs = generate_report(config, manifest, template_dir, exports_dir)
    
    manifest.stage = "report"
    
    logger.info(f"✅ Report complete: {len(outputs)} formats")
    for format_type, path in outputs.items():
        logger.info(f"   {format_type.upper()}: {path}")
    
    return manifest


if __name__ == "__main__":
    from models import Manifest, Period, Grid, Paths, Mode
    from ingest import ingest_mock_data
    from preprocess import preprocess_stage
    from features import features_stage
    from indicators import indicators_stage
    from evaluate import evaluate_stage
    from publish import publish_stage
    
    test_manifest = Manifest(
        city="paris",
        period=Period(start="2022-07-15", end="2022-07-17"),
        grid=Grid(crs="EPSG:3857", resolution_m=200),
        variables=["t2m"],
        stage="init",
        tiles=[],
        mode=Mode(dry_run=True)
    )
    
    test_config = {
        "extent": {"bbox_wgs84": [2.224, 48.815, 2.470, 48.902]},
        "indicators": {"threshold_celsius": 30.0},
        "output": {
            "formats": ["geotiff", "png", "metadata"],
            "report": {
                "format": ["html", "pdf"],
                "include_maps": True,
                "include_metrics": True
            }
        }
    }
    
    # Run full pipeline
    manifest = ingest_mock_data(test_config, test_manifest)
    manifest = preprocess_stage(test_config, manifest)
    manifest = features_stage(test_config, manifest)
    manifest = indicators_stage(test_config, manifest)
    manifest = evaluate_stage(test_config, manifest)
    manifest = publish_stage(test_config, manifest)
    result = report_stage(test_config, manifest)
    
    print(f"✅ Full pipeline test complete: {result.stage}")
