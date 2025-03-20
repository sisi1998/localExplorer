import traceback
from fastapi import FastAPI, HTTPException, Request
import httpx
import requests
from typing import Optional
import logging
import certifi
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()




WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
IPINFO_API_KEY = os.getenv("IPINFO_API_KEY")

WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
IPINFO_BASE_URL = "https://ipinfo.io"

# Add middleware to handle CORS and trusted hosts
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Default coordinates for when local IP is detected (Paris coordinates)
DEFAULT_LAT = 48.8566
DEFAULT_LON = 2.3522

def get_client_ip(request: Request) -> str:
    """Get the real client IP from various headers"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    return request.client.host

# Update get_location to use the new IP detection
@app.get("/mylocation")
async def get_location(request: Request, ip: Optional[str] = None):
    try:
        client_ip = ip or get_client_ip(request)
        logger.debug(f"Processing location request for IP: {client_ip}")

        ip_url = f"{IPINFO_BASE_URL}/{client_ip}"
        ip_response = requests.get(
            ip_url,
            params={"token": IPINFO_API_KEY},
            timeout=5,
            verify=False
        )
        ip_response.raise_for_status()
        ip_info = ip_response.json()

        if not ip_info or "loc" not in ip_info:
            raise ValueError("Invalid location data from IPInfo")

        lat, lon = map(float, ip_info["loc"].split(","))
        
        return {
            "ip": client_ip,
            "city": ip_info.get("city", "Unknown"),
            "country": ip_info.get("country", "Unknown"),
            "coordinates": {
                "latitude": lat,
                "longitude": lon
            }
        }
    except Exception as e:
        logger.error(f"Location API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Location API error: {str(e)}")

@app.get("/weather")
async def get_weather(lat: float, lon: float):
    try:
        async with httpx.AsyncClient(verify=False) as client:
            params = {
                "lat": lat,
                "lon": lon,
                "appid": WEATHER_API_KEY,
                "units": "metric"
            }
            response = await client.get(WEATHER_BASE_URL, params=params)
            response.raise_for_status()
            weather_data = response.json()

            return {
                "coordinates": {
                    "latitude": lat,
                    "longitude": lon
                },
                "weather": {
                    "temperature": weather_data["main"]["temp"],
                    "description": weather_data["weather"][0]["description"],
                    "wind_speed": weather_data["wind"]["speed"],
                    "humidity": weather_data["main"]["humidity"]
                }
            }
    except Exception as e:
        logger.error(f"Weather API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}")

@app.get("/weather-by-location")
async def get_weather_by_location(request: Request, ip: Optional[str] = None):
    try:
        # First get location
        location_data = await get_location(request, ip)
        
        # Then get weather using the coordinates
        weather_data = await get_weather(
            lat=location_data["coordinates"]["latitude"],
            lon=location_data["coordinates"]["longitude"]
        )

        # Combine the responses
        return {
            "ip": location_data["ip"],
            "location": {
                "city": location_data["city"],
                "country": location_data["country"],
                "coordinates": location_data["coordinates"]
            },
            "weather": weather_data["weather"]
        }
    except Exception as e:
        logger.error(f"Combined API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Combined API error: {str(e)}")
