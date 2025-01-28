from datetime import timedelta
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from dotenv import load_dotenv

from src.schemas import (
    CompletionRequest, CompletionResponse, UserCreate, Token
)
from src.auth import (
    authenticate_user, create_access_token, get_current_active_user,
    users_db, get_password_hash, User
)
from src.service import TextGenerationService
import os

# Load environment variables
load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Initialize FastAPI app
app = FastAPI(
    title="Text Generation Service",
    description="A simple text generation service using TinyLlama",
    version="1.0.0",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
        "clientId": "text-generation-client"
    }
)
service = TextGenerationService()
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure OAuth2
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={},
    description="OAuth2 password flow"
)

@app.post("/token", response_model=Token, tags=["authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Get access token using username and password."""
    user = authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed login attempt for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User {user.username} logged in successfully")
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=User, tags=["authentication"])
async def register_user(user: UserCreate):
    """Register a new user."""
    if user.username in users_db:
        logger.warning(f"Registration attempt with existing username: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    users_db[user.username] = {
        "username": user.username,
        "hashed_password": hashed_password,
        "is_active": True
    }
    
    logger.info(f"New user registered: {user.username}")
    return {"username": user.username, "is_active": True}

@app.get("/users/me", response_model=User, tags=["users"])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user

@app.post("/v1/completions", response_model=CompletionResponse, tags=["text-generation"])
async def create_completion(
    request: CompletionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Generate text completion."""
    if not service.is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Text generation service not initialized"
        )
    
    try:
        return await service.generate_completion(request, current_user.username)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/v1/models", tags=["text-generation"])
async def list_models(current_user: User = Depends(get_current_active_user)):
    """List available models."""
    if not service.is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not fully initialized"
        )
    
    return service.get_available_models()

@app.get("/health", tags=["system"])
async def health_check():
    """Health check endpoint (no auth required)."""
    try:
        return service.get_health_status()
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not fully initialized"
        )

@app.on_event("startup")
async def startup_event():
    """Run startup tasks."""
    logger.info("Starting Text Generation Service")
    await service.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """Run shutdown tasks."""
    logger.info("Shutting down Text Generation Service")
    await service.shutdown()