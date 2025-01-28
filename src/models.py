from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedModel, PreTrainedTokenizer
import torch
from typing import Optional, Dict, Any
from src.config import ModelConfig
from loguru import logger

class TextGenerator:
    """Handles text generation using Hugging Face Models."""
    
    def __init__(self, config: ModelConfig):
        """Initialize the text generator with Hugging Face model.
        
        Args:
            config: Model configuration settings
            
        Raises:
            RuntimeError: If model loading fails or device is not available
        """
        self.config = config
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        try:
            # Load tokenizer
            self.tokenizer: PreTrainedTokenizer = AutoTokenizer.from_pretrained(
                config.model_name,
                trust_remote_code=True
            )
            
            # Load model
            self.model: PreTrainedModel = AutoModelForCausalLM.from_pretrained(
                config.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                trust_remote_code=True
            ).to(self.device)
            
            logger.info(f"Successfully loaded model: {config.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise RuntimeError(f"Model initialization failed: {str(e)}")

    def format_prompt(self, prompt: str) -> str:
        """Format the prompt for Hugging Face chat model.
        
        Args:
            prompt: Raw input prompt
            
        Returns:
            str: Formatted prompt with system and user context
        """
        return (
            f"<|system|>You are a helpful AI assistant.\n"
            f"<|user|>{prompt}\n"
            f"<|assistant|>"
        )

    def generate(
        self,
        prompt: str,
        max_length: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Dict[str, Any]
    ) -> str:
        """Generate text based on the input prompt.
        
        Args:
            prompt: Input text prompt
            max_length: Maximum length of generated text
            temperature: Sampling temperature (higher = more creative)
            **kwargs: Additional generation parameters
            
        Returns:
            str: Generated text response
            
        Raises:
            ValueError: If input parameters are invalid
            RuntimeError: If generation fails
        """
        try:
            # Validate and set parameters
            max_length = max_length or self.config.max_length
            temperature = temperature or self.config.temperature
            
            if max_length < 1:
                raise ValueError("max_length must be positive")
            if temperature < 0:
                raise ValueError("temperature must be non-negative")
            
            # Format and encode prompt
            formatted_prompt = self.format_prompt(prompt)
            inputs = self.tokenizer(
                formatted_prompt,
                return_tensors="pt",
                padding=True,
                truncation=True
            ).to(self.device)
            
            # Generate text
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=max_length,
                    temperature=temperature,
                    do_sample=True,
                    top_p=0.95,
                    pad_token_id=self.tokenizer.eos_token_id,
                    **kwargs
                )
            
            # Decode and clean up generated text
            generated_text = self.tokenizer.decode(
                outputs[0],
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True
            )
            
            # Extract assistant's response
            response = generated_text.split("<|assistant|>")[-1].strip()
            
            logger.debug(f"Generated response length: {len(response)}")
            return response
            
        except ValueError as e:
            logger.warning(f"Invalid input parameters: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Generation failed: {str(e)}")
            raise RuntimeError(f"Text generation failed: {str(e)}")