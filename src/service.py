from typing import Optional, Dict, List
import uuid
from loguru import logger

from src.models import TextGenerator
from src.config import ModelConfig
from src.schemas import (
    CompletionRequest, CompletionResponse, CompletionChoice,
    CompletionUsage, StopReason
)

class TextGenerationService:
    """Service class handling text generation business logic."""
    
    def __init__(self):
        self.config: Optional[ModelConfig] = None
        self.generator: Optional[TextGenerator] = None
        
    async def initialize(self) -> None:
        """Initialize the service and load models."""
        try:
            self.config = ModelConfig()
            self.generator = TextGenerator(self.config)
            logger.info("Text generation service initialized successfully")
            logger.info(f"Model: {self.config.model_name}")
            logger.info(f"Device: {self.generator.device}")
        except Exception as e:
            logger.error(f"Failed to initialize service: {str(e)}")
            raise
            
    async def shutdown(self) -> None:
        """Cleanup service resources."""
        if self.generator:
            del self.generator
            self.generator = None
        logger.info("Text generation service shut down successfully")
            
    def is_ready(self) -> bool:
        """Check if service is initialized and ready."""
        return self.config is not None and self.generator is not None
        
    async def generate_completion(
        self,
        request: CompletionRequest,
        user_id: str
    ) -> CompletionResponse:
        """Generate text completion for the given request."""
        if not self.is_ready():
            raise RuntimeError("Service not initialized")
            
        try:
            logger.info(f"Generating completion for user: {user_id}")
            
            generated_text = self.generator.generate(
                prompt=request.prompt,
                max_length=request.max_tokens,
                temperature=request.temperature
            )

            # Calculate token usage (approximate)
            prompt_tokens = len(request.prompt.split())
            completion_tokens = len(generated_text.split())
            total_tokens = prompt_tokens + completion_tokens

            response = CompletionResponse(
                id=f"cmpl-{str(uuid.uuid4())}",
                model=request.model,
                choices=[
                    CompletionChoice(
                        text=generated_text,
                        index=0,
                        finish_reason=StopReason.STOP
                    )
                ],
                usage=CompletionUsage(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens
                )
            )
            
            logger.debug(f"Generated {completion_tokens} tokens for prompt of {prompt_tokens} tokens")
            return response
            
        except Exception as e:
            logger.error(f"Completion generation failed: {str(e)}")
            raise
            
    def get_available_models(self) -> Dict[str, List[Dict[str, str]]]:
        """Get list of available models."""
        if not self.is_ready():
            raise RuntimeError("Service not initialized")
            
        return {
            "data": [
                {
                    "id": "tinyllama-1.1b",
                    "object": "model",
                    "owned_by": "default",
                    "permission": []
                }
            ]
        }
        
    def get_health_status(self) -> Dict[str, str]:
        """Get service health status."""
        if not self.is_ready():
            raise RuntimeError("Service not initialized")
            
        return {
            "status": "healthy",
            "model": self.config.model_name,
            "device": self.generator.device
        }