"""
Fine-Tuning Prithvi WxC with QLoRA

Implements QLoRA (Quantized Low-Rank Adaptation) for efficient fine-tuning
of the Prithvi WxC foundation model. This allows fine-tuning with minimal
GPU memory while preserving model performance.

Reference: QLoRA: Efficient Finetuning of Quantized LLMs (Dettmers et al., 2023)
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json

logger = logging.getLogger(__name__)

try:
    import torch
    from transformers import TrainingArguments, Trainer
    from peft import LoraConfig, get_peft_model, TaskType
    from peft import prepare_model_for_kbit_training
    from transformers import BitsAndBytesConfig
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("transformers/peft not available. Install with: pip install transformers peft bitsandbytes accelerate")


class PrithviFineTuner:
    """Fine-tune Prithvi WxC using QLoRA"""
    
    def __init__(
        self,
        model_path: Optional[Path] = None,
        output_dir: Path = Path("./models/finetuned"),
        lora_r: int = 16,
        lora_alpha: int = 32,
        lora_dropout: float = 0.1,
        target_modules: Optional[List[str]] = None,
        use_4bit: bool = True
    ):
        """
        Initialize fine-tuner
        
        Args:
            model_path: Path to base Prithvi model (if None, uses Hugging Face)
            output_dir: Directory to save fine-tuned model
            lora_r: LoRA rank (lower = fewer parameters)
            lora_alpha: LoRA alpha scaling parameter
            lora_dropout: LoRA dropout rate
            target_modules: Modules to apply LoRA to (if None, auto-detects)
            use_4bit: Use 4-bit quantization
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "transformers and peft are required. "
                "Install with: pip install transformers peft bitsandbytes accelerate"
            )
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.lora_config = LoraConfig(
            r=lora_r,
            lora_alpha=lora_alpha,
            target_modules=target_modules or ["query", "value", "key", "dense"],
            lora_dropout=lora_dropout,
            bias="none",
            task_type=TaskType.FEATURE_EXTRACTION,  # Adjust based on actual task
        )
        
        self.use_4bit = use_4bit
        self.model = None
        self.processor = None
        
        logger.info(f"Prithvi Fine-Tuner initialized (LoRA r={lora_r}, alpha={lora_alpha})")
    
    def setup_model(
        self,
        model_name: str = "ibm-granite/granite-geospatial-wxc",
        cache_dir: Optional[Path] = None
    ):
        """
        Setup model with quantization and LoRA
        
        Args:
            model_name: Hugging Face model name
            cache_dir: Cache directory for model weights
        """
        from transformers import AutoModel, AutoProcessor
        
        logger.info(f"Loading model: {model_name}")
        
        # Configure quantization if using 4-bit
        if self.use_4bit:
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
        else:
            quantization_config = None
        
        # Load model with quantization
        self.model = AutoModel.from_pretrained(
            model_name,
            cache_dir=str(cache_dir) if cache_dir else None,
            quantization_config=quantization_config,
            device_map="auto",
            torch_dtype=torch.float16
        )
        
        # Prepare for k-bit training
        self.model = prepare_model_for_kbit_training(self.model)
        
        # Apply LoRA
        self.model = get_peft_model(self.model, self.lora_config)
        
        # Load processor
        self.processor = AutoProcessor.from_pretrained(
            model_name,
            cache_dir=str(cache_dir) if cache_dir else None
        )
        
        logger.info("✅ Model setup complete with QLoRA")
        self.model.print_trainable_parameters()
    
    def create_composite_loss(
        self,
        pixel_weight: float = 1.0,
        perceptual_weight: float = 0.1,
        pinn_weight: float = 0.01
    ):
        """
        Create composite loss function
        
        Loss = λ_MSE * L_pixel + λ_percep * L_VGG + λ_phys * L_PINN
        
        Args:
            pixel_weight: Weight for pixel-wise MSE loss
            perceptual_weight: Weight for perceptual (VGG) loss
            pinn_weight: Weight for physics-informed loss
            
        Returns:
            Loss function
        """
        def composite_loss(predictions, targets, inputs=None):
            # Pixel-wise MSE loss
            pixel_loss = torch.nn.functional.mse_loss(predictions, targets)
            
            # Perceptual loss (VGG features) - simplified
            # In production, would use VGG features
            perceptual_loss = torch.tensor(0.0, device=predictions.device)
            if perceptual_weight > 0:
                # Placeholder - would compute VGG features
                perceptual_loss = pixel_loss * 0.1  # Simplified
            
            # Physics-informed loss (PINN) - simplified
            # In production, would enforce physical constraints
            pinn_loss = torch.tensor(0.0, device=predictions.device)
            if pinn_weight > 0 and inputs is not None:
                # Placeholder - would compute physics constraints
                pinn_loss = pixel_loss * 0.01  # Simplified
            
            total_loss = (
                pixel_weight * pixel_loss +
                perceptual_weight * perceptual_loss +
                pinn_weight * pinn_loss
            )
            
            return total_loss, {
                'pixel_loss': pixel_loss.item(),
                'perceptual_loss': perceptual_loss.item(),
                'pinn_loss': pinn_loss.item(),
                'total_loss': total_loss.item()
            }
        
        return composite_loss
    
    def train(
        self,
        train_dataset,
        val_dataset,
        num_epochs: int = 10,
        batch_size: int = 4,
        learning_rate: float = 2e-4,
        warmup_steps: int = 100,
        save_steps: int = 500,
        logging_steps: int = 50
    ) -> Dict:
        """
        Train the fine-tuned model
        
        Args:
            train_dataset: Training dataset
            val_dataset: Validation dataset
            num_epochs: Number of training epochs
            batch_size: Batch size
            learning_rate: Learning rate
            warmup_steps: Warmup steps
            save_steps: Steps between saves
            logging_steps: Steps between logging
            
        Returns:
            Training history dictionary
        """
        if self.model is None:
            raise ValueError("Model not setup. Call setup_model() first.")
        
        logger.info("Starting fine-tuning...")
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=str(self.output_dir),
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            learning_rate=learning_rate,
            warmup_steps=warmup_steps,
            logging_steps=logging_steps,
            save_steps=save_steps,
            evaluation_strategy="steps",
            eval_steps=save_steps,
            save_total_limit=3,
            load_best_model_at_end=True,
            metric_for_best_model="loss",
            greater_is_better=False,
            fp16=True,
            gradient_accumulation_steps=4,
            report_to="none"  # Disable wandb/tensorboard for now
        )
        
        # Create composite loss
        loss_fn = self.create_composite_loss()
        
        # Custom trainer with composite loss
        class CustomTrainer(Trainer):
            def compute_loss(self, model, inputs, return_outputs=False):
                # This is simplified - actual implementation needs proper data handling
                outputs = model(**inputs)
                loss, loss_dict = loss_fn(outputs.logits, inputs['labels'], inputs)
                return (loss, outputs) if return_outputs else loss
        
        trainer = CustomTrainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
        )
        
        # Train
        train_result = trainer.train()
        
        # Save model
        trainer.save_model()
        self.model.save_pretrained(self.output_dir / "lora_adapter")
        
        logger.info("✅ Fine-tuning complete")
        
        return {
            "train_loss": train_result.training_loss,
            "train_runtime": train_result.metrics.get("train_runtime", 0),
            "output_dir": str(self.output_dir)
        }
    
    def save_config(self, config_path: Path):
        """Save fine-tuning configuration"""
        config = {
            "lora_r": self.lora_config.r,
            "lora_alpha": self.lora_config.lora_alpha,
            "lora_dropout": self.lora_config.lora_dropout,
            "target_modules": self.lora_config.target_modules,
            "use_4bit": self.use_4bit
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Configuration saved to {config_path}")


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    fine_tuner = PrithviFineTuner(
        output_dir=Path("./models/finetuned_prithvi"),
        lora_r=16,
        lora_alpha=32
    )
    
    print("Fine-tuner initialized. Call setup_model() and train() to start.")

