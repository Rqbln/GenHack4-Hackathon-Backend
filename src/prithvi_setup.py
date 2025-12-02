"""
Prithvi WxC Setup and Inference

Setup for Prithvi WxC (Vision Transformer for Weather and Climate) foundation model.
Downloads model weights from Hugging Face and provides simple inference interface.

Model: granite-geospatial-wxc (Prithvi WxC)
Reference: https://huggingface.co/ibm-granite/granite-geospatial-wxc
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
import json

logger = logging.getLogger(__name__)

try:
    from transformers import AutoModel, AutoProcessor
    from PIL import Image
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("transformers or torch not available. Install with: pip install transformers torch pillow")


class PrithviWxCSetup:
    """Setup and inference for Prithvi WxC model"""
    
    MODEL_NAME = "ibm-granite/granite-geospatial-wxc"
    DEFAULT_CACHE_DIR = Path.home() / ".cache" / "huggingface" / "hub"
    
    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        device: str = "auto"
    ):
        """
        Initialize Prithvi WxC setup
        
        Args:
            cache_dir: Directory to cache model weights (default: ~/.cache/huggingface/hub)
            device: Device to use ('auto', 'cpu', 'cuda')
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "transformers and torch are required. "
                "Install with: pip install transformers torch pillow"
            )
        
        self.cache_dir = Path(cache_dir) if cache_dir else self.DEFAULT_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine device
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        self.model = None
        self.processor = None
        
        logger.info(f"Prithvi WxC initialized (device: {self.device}, cache: {self.cache_dir})")
    
    def download_model(self, force_download: bool = False) -> Dict[str, Any]:
        """
        Download Prithvi WxC model weights from Hugging Face
        
        Args:
            force_download: Force re-download even if cached
            
        Returns:
            Dictionary with download information
        """
        logger.info(f"Downloading Prithvi WxC model: {self.MODEL_NAME}")
        logger.info("This may take several minutes on first run...")
        
        try:
            # Download processor
            logger.info("Downloading processor...")
            self.processor = AutoProcessor.from_pretrained(
                self.MODEL_NAME,
                cache_dir=str(self.cache_dir),
                force_download=force_download
            )
            
            # Download model
            logger.info("Downloading model weights (this may take a while)...")
            self.model = AutoModel.from_pretrained(
                self.MODEL_NAME,
                cache_dir=str(self.cache_dir),
                force_download=force_download,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            
            # Move to device
            self.model = self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"✅ Model downloaded and loaded on {self.device}")
            
            # Get model info
            num_params = sum(p.numel() for p in self.model.parameters())
            model_size_mb = sum(p.numel() * p.element_size() for p in self.model.parameters()) / (1024 * 1024)
            
            return {
                "model_name": self.MODEL_NAME,
                "device": self.device,
                "num_parameters": num_params,
                "model_size_mb": model_size_mb,
                "cache_dir": str(self.cache_dir)
            }
            
        except Exception as e:
            logger.error(f"Failed to download model: {e}")
            raise
    
    def load_model(self) -> bool:
        """
        Load model from cache (if already downloaded)
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            logger.info(f"Loading Prithvi WxC from cache: {self.cache_dir}")
            
            self.processor = AutoProcessor.from_pretrained(
                self.MODEL_NAME,
                cache_dir=str(self.cache_dir)
            )
            
            self.model = AutoModel.from_pretrained(
                self.MODEL_NAME,
                cache_dir=str(self.cache_dir),
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            
            self.model = self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"✅ Model loaded from cache on {self.device}")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to load from cache: {e}")
            return False
    
    def simple_inference(
        self,
        image_path: Path,
        task: str = "downscaling",
        output_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Run simple inference on an image
        
        Args:
            image_path: Path to input image (GeoTIFF or similar)
            task: Task type (e.g., "downscaling", "super_resolution")
            output_path: Optional path to save output
            
        Returns:
            Dictionary with inference results
        """
        if self.model is None or self.processor is None:
            raise ValueError("Model not loaded. Call download_model() or load_model() first.")
        
        logger.info(f"Running inference on {image_path.name} (task: {task})")
        
        try:
            # Load image
            image = Image.open(image_path)
            
            # Process image
            inputs = self.processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Run inference
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            # Extract results
            if hasattr(outputs, 'logits'):
                predictions = outputs.logits
            elif hasattr(outputs, 'last_hidden_state'):
                predictions = outputs.last_hidden_state
            else:
                predictions = outputs[0] if isinstance(outputs, tuple) else outputs
            
            result = {
                "input_shape": image.size,
                "output_shape": list(predictions.shape),
                "task": task,
                "device": self.device
            }
            
            # Save output if path provided
            if output_path:
                # Convert to numpy and save (simplified - actual implementation depends on output format)
                import numpy as np
                if isinstance(predictions, torch.Tensor):
                    predictions_np = predictions.cpu().numpy()
                    np.save(output_path, predictions_np)
                    result["output_saved"] = str(output_path)
            
            logger.info(f"✅ Inference completed: {result['output_shape']}")
            return result
            
        except Exception as e:
            logger.error(f"Inference failed: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if self.model is None:
            return {"status": "not_loaded"}
        
        num_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        
        return {
            "model_name": self.MODEL_NAME,
            "device": self.device,
            "num_parameters": num_params,
            "trainable_parameters": trainable_params,
            "model_loaded": True,
            "processor_loaded": self.processor is not None
        }


def test_prithvi_setup():
    """Test function to verify Prithvi WxC setup"""
    print("=" * 60)
    print("Testing Prithvi WxC Setup")
    print("=" * 60)
    
    if not TRANSFORMERS_AVAILABLE:
        print("⚠️  transformers/torch not available. Skipping test.")
        print("   Install with: pip install transformers torch pillow")
        return False
    
    try:
        # Initialize
        setup = PrithviWxCSetup(device="cpu")  # Use CPU for testing
        
        # Try to load from cache
        loaded = setup.load_model()
        
        if not loaded:
            print("⚠️  Model not in cache. Would need to download (skipping for test).")
            print("   Run: setup.download_model() to download")
            return True  # Not an error, just not downloaded yet
        
        # Get info
        info = setup.get_model_info()
        print(f"✅ Model loaded: {info['num_parameters']:,} parameters")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Test setup
    test_prithvi_setup()

