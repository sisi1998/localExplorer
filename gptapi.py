from fastapi import FastAPI, HTTPException, Request
from typing import Optional
import os
from datetime import datetime  # Import datetime class explicitly
from dotenv import load_dotenv
import logging
from services.gpt_service import GPTService
from api import get_weather_by_location

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize GPT service
gpt_service = GPTService(os.getenv("OPENAI_API_KEY"))

@app.get("/explore")
async def get_local_suggestions(
    request: Request, 
    ip: Optional[str] = None,
    preferences: Optional[dict] = None,
    datetime_str: Optional[str] = None  # Renamed parameter to avoid conflict
):
    """Get personalized local activity suggestions"""
    try:
        # Get weather and location data
        weather_location_data = await get_weather_by_location(request, ip)
        
        # Generate suggestions using GPT
        suggestions = await gpt_service.generate_activity_suggestion(
            weather_location_data,
            preferences,
            datetime_str
        )

        return {
            "current_conditions": weather_location_data,
            "time": datetime_str or datetime.now().isoformat(),
            "suggestions": suggestions
        }

    except Exception as e:
        logger.error(f"Error in local explorer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))