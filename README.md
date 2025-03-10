# Local Activity Explorer


A FastAPI application that suggests personalized activities based on weather conditions and location, powered by GPT.

```bash
siwar/
├── services/           # Service modules
│   ├── __init__.py
│   └── gpt_service.py
├── static/            # Frontend assets
│   ├── view.html
│   ├── style.css
│   └── script.js
├── tests/            # Test files
│   └── test_gpt_service.py
├── .env              # Environment variables
├── .gitignore       # Git ignore rules
├── api.py           # API utilities
├── Dockerfile       # Docker configuration
├── gptapi.py        # GPT API endpoints
├── requirements.txt  # Python dependencies
└── server.py        # Main server file
```

## Prerequisites
- Docker
- Git
- Text editor (VS Code recommended)

## Step 1: Clone the Repository
```bash
git clone <repository-url>
cd siwar
```

## Step 2: Set Up Environment Variables
Create a `.env` file:
```bash
# filepath: .env
WEATHER_API_KEY=your_weather_api_key
IPINFO_API_KEY=your_ipinfo_api_key
OPENAI_API_KEY=your_openai_api_key
HOST=0.0.0.0
PORT=8000
```

## Step 3: Create Docker Configuration
```dockerfile
# filepath: Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Step 4: Update Requirements
```txt
# filepath: requirements.txt
fastapi==0.115.8
python-dotenv==1.0.1
uvicorn==0.34.0
openai==1.65.5
httpx==0.28.1
pydantic==2.10.6
python-multipart==0.0.20
starlette==0.45.3
requests==2.31.0
```

## Step 5: Build Docker Image
```bash
# Build the image
docker build -t local-explorer .

# Check if image was created
docker images | grep local-explorer
```

## Step 6: Run Docker Container
```bash
# Run container with environment variables
docker run -p 8000:8000 \
  --env-file .env \
  local-explorer
```

## Step 7: Verify Installation
1. Open your browser to `http://localhost:8000`
2. Check API endpoint: `http://localhost:8000/explore`

## Development Commands

### Start Development Server
```bash
# Run with hot reload
uvicorn server:app --reload
```

### Run Tests
```bash
python -m pytest tests/
```

### Docker Development
```bash
# Build with no cache
docker build --no-cache -t local-explorer .

# Run with volume mount
docker run -p 8000:8000 \
  --env-file .env \
  -v $(pwd):/app \
  local-explorer
```

## API Documentation

### GET /explore
Returns activity suggestions based on current conditions.

**Parameters:**
- `datetime_str` (optional): ISO format datetime
- `preferences` (optional): JSON preferences object

**Example Response:**
```json
{
  "current_conditions": {
    "location": {
      "city": "Milan",
      "country": "IT"
    },
    "weather": {
      "temperature": 10.14,
      "description": "moderate rain",
      "wind_speed": 3.6,
      "humidity": 86
    }
  },
  "suggestions": {
    "summary": "Weather conditions summary",
    "activities": [
      {
        "name": "Activity name",
        "type": "indoor/outdoor",
        "description": "Activity description",
        "tips": "Useful tips",
        "timing": "Timing information"
      }
    ]
  }
}
```

## Troubleshooting

### Missing Modules
If you encounter module errors:
```bash
# Update requirements
pip install requests
pip freeze > requirements.txt

# Rebuild Docker image
docker build --no-cache -t local-explorer .
```

### Permission Issues
```bash
# Fix permission issues
sudo chown -R $USER:$USER .
```

### Docker Issues
```bash
# Remove old containers
docker rm $(docker ps -a -q)

# Clean up images
docker system prune -a
```

## Deployment

### Local Testing
```bash
# Test with local IP
curl "http://localhost:8000/explore"
```
