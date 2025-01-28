from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional
from datetime import datetime
from enum import Enum

class UserCreate(BaseModel):
    """Schema for user creation."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "johndoe",
                "password": "StrongPass123!"
            }
        }
    )

class User(BaseModel):
    """Schema for user information."""
    username: str = Field(..., min_length=3, max_length=50)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Token(BaseModel):
    """Schema for authentication token."""
    access_token: str
    token_type: str = Field(default="bearer")

class StopReason(str, Enum):
    """Enumeration of possible completion stop reasons."""
    LENGTH = "length"
    STOP = "stop"
    ERROR = "error"

class CompletionRequest(BaseModel):
    """OpenAI-style request format for completions."""
    model: str = Field(..., description="Model name to use for completion")
    prompt: str = Field(..., min_length=1, max_length=4096, description="The prompt to generate completions for")
    max_tokens: Optional[int] = Field(
        default=200,
        ge=1,
        le=2048,
        description="The maximum number of tokens to generate"
    )
    temperature: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Sampling temperature (higher = more creative)"
    )
    stream: Optional[bool] = Field(
        default=False,
        description="Whether to stream responses"
    )
    n: Optional[int] = Field(
        default=1,
        ge=1,
        le=5,
        description="Number of completions to generate"
    )
    stop: Optional[List[str]] = Field(
        default=None,
        max_length=4,
        description="Sequences where the API will stop generating"
    )

    @field_validator('stop')
    def validate_stop_sequences(cls, v):
        """Validate stop sequences length."""
        if v and any(len(s) > 50 for s in v):
            raise ValueError("Stop sequences must be <= 50 characters")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "model": "tinyllama-1.1b",
                "prompt": "Translate to French: Hello, how are you?",
                "max_tokens": 100,
                "temperature": 0.7
            }
        }
    )

class CompletionChoice(BaseModel):
    """Single completion choice in response."""
    text: str = Field(..., description="The generated text")
    index: int = Field(..., ge=0, description="The index of this completion")
    finish_reason: Optional[StopReason] = Field(
        default=None,
        description="The reason the completion stopped"
    )

class CompletionUsage(BaseModel):
    """Token usage information."""
    prompt_tokens: int = Field(..., ge=0, description="Number of tokens in the prompt")
    completion_tokens: int = Field(..., ge=0, description="Number of tokens generated")
    total_tokens: int = Field(..., ge=0, description="Total number of tokens used")

    @field_validator('total_tokens')
    def validate_total_tokens(cls, v, values):
        """Validate total tokens equals sum of prompt and completion tokens."""
        if 'prompt_tokens' in values.data and 'completion_tokens' in values.data:
            expected_total = values.data['prompt_tokens'] + values.data['completion_tokens']
            if v != expected_total:
                raise ValueError("Total tokens must equal prompt_tokens + completion_tokens")
        return v

class CompletionResponse(BaseModel):
    """OpenAI-style response format for completions."""
    id: str = Field(..., description="Unique identifier for the completion")
    object: str = Field("text_completion", description="Object type")
    created: int = Field(default_factory=lambda: int(datetime.utcnow().timestamp()))
    model: str = Field(..., description="Model used for completion")
    choices: List[CompletionChoice] = Field(..., description="Generated completions")
    usage: CompletionUsage = Field(..., description="Token usage statistics")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "cmpl-123abc",
                "object": "text_completion",
                "created": 1677649420,
                "model": "tinyllama-1.1b",
                "choices": [
                    {
                        "text": "Bonjour, comment allez-vous?",
                        "index": 0,
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 8,
                    "total_tokens": 18
                }
            }
        }
    )