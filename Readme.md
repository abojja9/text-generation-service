# Text Generation Service

A FastAPI-based text generation service using TinyLlama, providing a secure API for text generation with OAuth2 authentication.

## Features

- Text generation using `TinyLlama-1.1B-Chat` model - A lightweight 1.1B parameter model fine-tuned for chat/instruction following
- Model is automatically downloaded from `Hugging Face Hub` on first run
- OAuth2 authentication with JWT tokens
- FastAPI-based REST API
- Docker containerization
- Environment-based configuration
- Comprehensive logging
- Health check endpoints
- Swagger UI documentation

## About the Model

The service uses TinyLlama-1.1B-Chat-v1.0, which is a 1.1 billion parameter language model designed to be a lightweight alternative to larger language models. Key features:

- Compact size (1.1B parameters) making it suitable for deployment on less powerful hardware
- Fine-tuned specifically for chat and instruction following
- Supports various text generation tasks like writing, translation, and Q&A
- Automatically downloaded from Hugging Face Hub on first run
- Model files are cached locally for subsequent runs

## Prerequisites

- Docker and Docker Compose
- Python 3.10+
- Hugging Face account and API token

## Project Structure

```
.
├── Dockerfile
├── README.md
├── docker-compose.yml
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── auth.py
│   ├── config.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── service.py
└── start.sh
```

## Getting Started

1. Clone the repository:
```bash
git clone <repository-url>
cd text-generation-service
```

2. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

3. Update the `.env` file with your configuration:

Replace `hf_...` with your Hugging Face API token.

```plaintext
APP_MODEL_NAME=TinyLlama/TinyLlama-1.1B-Chat-v1.0
APP_MAX_LENGTH=200
APP_TEMPERATURE=0.7
JWT_SECRET_KEY="your-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
HUGGINGFACE_TOKEN=hf_...
APP_HOST=0.0.0.0
APP_PORT=8000
```

4. Build and run using Docker Compose:
```bash
bash start.sh
```
or 
```bash
docker-compose up --build
```

The service will be available at `http://localhost:8002`.

## Authentication

The service uses OAuth2 with JWT tokens for authentication. To get started, use the default admin credentials:

- Username: `agam`
- Password: `StrongPass123!`

or 

- Username: `admin`
- Password: `admin`

or you can register a new user using the `/register` endpoint.

![Authentication](images/authorization.png)

First, obtain an access token using these credentials. The token will be required for all protected endpoints.

## API Endpoints

### Main Endpoints

The service provides several endpoints:

![API Endpoints](images/api_endpoints.png)

- `POST /v1/completions`: Generate text completions
- `GET /v1/models`: List available models
- `POST /token`: Get access token
- `POST /register`: Register new user
- `GET /users/me`: Get current user info
- `GET /health`: Health check endpoint

### Text generation endpoint:

![Text Generation Endpoint](images/completions_api_endpoint.png)

![Request and Response](images/request_and_response.png)

### Example Request and Response

Here's an example of using the API endpoints:

1. First, obtain an authentication token:
```bash
curl -X 'POST' \
  'http://0.0.0.0:8002/token' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=password&username=admin&password=admin&scope=&client_id=string&client_secret=string'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

2. Use the token to make a completion request:
```bash
curl -X 'POST' \
  'http://0.0.0.0:8002/v1/completions' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
  -H 'Content-Type: application/json' \
  -d '{
    "max_tokens": 200,
    "model": "tinyllama-1.1b",
    "prompt": "Write a recipe for chocolate chip cookies. Include ingredients and steps.",
    "temperature": 0.7
  }'
```

Response:
```json
{
  "id": "cmpl-ef45adae-0462-414a-b960-92d10f62bea5",
  "object": "text_completion",
  "created": 1738096236,
  "model": "tinyllama-1.1b",
  "choices": [
    {
      "text": "Of course! Here's a recipe for chocolate chip cookies:\n\nIngredients:\n- 2 cups all-purpose flour\n- 1 teaspoon baking soda\n- 1 teaspoon salt\n- 1 cup unsalted butter, at room temperature\n- 3/4 cup granulated sugar\n- 2 large eggs\n- 3/4 cup granulated sugar\n- 1/2 cup unsweetened cocoa powder\n- 1 teaspoon vanilla extract\n- 1 cup semisweet chocolate chips\n\nInstructions:\n1. Preheat your oven to 35",
      "index": 0,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 11,
    "completion_tokens": 70,
    "total_tokens": 81
  }
}
```



### Running Tests

```bash
pytest
```

## API Documentation

Once the service is running, visit:
- Swagger UI: `http://localhost:8002/docs`
- ReDoc: `http://localhost:8002/redoc`

## Environment Variables

All configuration is managed through environment variables:

- `APP_MODEL_NAME`: Hugging Face model identifier
- `APP_MAX_LENGTH`: Maximum length for generated text
- `APP_TEMPERATURE`: Temperature for text generation
- `JWT_SECRET_KEY`: Secret key for JWT token generation
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `HUGGINGFACE_TOKEN`: Your Hugging Face API token
- `APP_HOST`: Service host
- `APP_PORT`: Service port

## License

This project is licensed under the MIT License - see the LICENSE file for details.
