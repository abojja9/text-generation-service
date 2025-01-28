from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
import os

class ModelConfig(BaseSettings):
    """Configuration settings for the text generation service."""
    
    # Model settings
    model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # HF model identifier
    model_path: Optional[str] = None  # Optional local path to model
    max_length: int = 200
    temperature: float = 0.7
    
    # Cache settings
    cache_dir: Optional[str] = None  # Optional cache directory for downloaded models
    
    # API settings
    host: str = os.getenv("APP_HOST")
    port: int = os.getenv("APP_PORT")
    
    class Config:
        env_prefix = "APP_"  # Environment variables prefix