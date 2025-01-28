from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class UserCreate(BaseModel):
    """Schema for user creation."""
    username: str
    password: str

class User(BaseModel):
    """Schema for user information."""
    username: str
    is_active: bool = True

class Token(BaseModel):
    """Schema for authentication token."""
    access_token: str
    token_type: str

class CompletionRequest(BaseModel):
    """OpenAI-style request format for completions."""
    model: str = Field(..., description="Model name to use for completion")
    prompt: str = Field(..., description="The prompt to generate completions for")
    max_tokens: Optional[int] = Field(200, description="The maximum number of tokens to generate")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=1.0, description="Sampling temperature")
    stream: Optional[bool] = Field(False, description="Whether to stream responses")
    n: Optional[int] = Field(1, description="Number of completions to generate")
    stop: Optional[List[str]] = Field(None, description="Sequences where the API will stop generating")

class CompletionChoice(BaseModel):
    """Single completion choice in response."""
    text: str = Field(..., description="The generated text")
    index: int = Field(..., description="The index of this completion")
    finish_reason: Optional[str] = Field(None, description="The reason the completion stopped")

class CompletionUsage(BaseModel):
    """Token usage information."""
    prompt_tokens: int = Field(..., description="Number of tokens in the prompt")
    completion_tokens: int = Field(..., description="Number of tokens generated")
    total_tokens: int = Field(..., description="Total number of tokens used")

class CompletionResponse(BaseModel):
    """OpenAI-style response format for completions."""
    id: str = Field(..., description="Unique identifier for the completion")
    object: str = Field("text_completion", description="Object type")
    created: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    model: str = Field(..., description="Model used for completion")
    choices: List[CompletionChoice] = Field(..., description="Generated completions")
    usage: CompletionUsage = Field(..., description="Token usage statistics")