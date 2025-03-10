from datetime import datetime
from typing import Dict, Any, Optional
from openai import OpenAI
import json
import logging
import ssl
import certifi
from fastapi import HTTPException
import httpx

logger = logging.getLogger(__name__)

class GPTService:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        # Create custom SSL context with proper configuration
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # Configure transport with custom SSL context
        transport = httpx.HTTPTransport(verify=False, retries=3)
        
        # Initialize client with custom transport
        self.client = OpenAI(
            api_key=api_key,
            http_client=httpx.Client(transport=transport)
        )
        self.model = "gpt-4o-mini"
        logger.info("GPT Service initialized with SSL verification disabled")

    def _test_connection(self):
        """Test the connection to OpenAI API"""
        try:
            # Simple test request
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            logger.debug("Connection test successful")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False

    async def generate_activity_suggestion(
        self, 
        weather_data: Dict[str, Any], 
        preferences: Optional[Dict[str, Any]] = None,
        datetime_str: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate personalized activity suggestions"""
        try:
            # Parse datetime or use current time
            if datetime_str:
                current_time = datetime.fromisoformat(datetime_str)
            else:
                current_time = datetime.now()

            prompt = self._build_prompt(weather_data, preferences, current_time)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a local activity expert."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "text"},
                temperature=0.7,
                max_tokens=2048,
                top_p=0.9,
                frequency_penalty=0,
                presence_penalty=0
            )

            suggestion_text = response.choices[0].message.content
            try:
                return json.loads(suggestion_text)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse GPT response: {suggestion_text}")
                return {"error": "Invalid response format", "raw": suggestion_text}

        except Exception as e:
            logger.error(f"GPT API error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def _build_prompt(
        self, 
        weather_data: Dict[str, Any], 
        preferences: Optional[Dict[str, Any]] = None,
        current_time: datetime = None
    ) -> str:
        # Format time information
        time_info = current_time.strftime("%A, %H:%M")
        day_part = self._get_day_part(current_time.hour)
        
        return f"""
        Based on these conditions in {weather_data['location']['city']}, {weather_data['location']['country']}:
        
        Time:
        - Current: {time_info}
        - Part of day: {day_part}
        
        Weather:
        - Temperature: {weather_data['weather']['temperature']}°C
        - Conditions: {weather_data['weather']['description']}
        - Wind: {weather_data['weather']['wind_speed']} m/s
        - Humidity: {weather_data['weather']['humidity']}%
        
        User Preferences: {json.dumps(preferences) if preferences else 'None provided'}

        Return response in this JSON format:
        {{
            "summary": "Brief description of conditions and time",
            "activities": [
                {{
                    "name": "Activity name",
                    "type": "indoor/outdoor",
                    "description": "Why this is suitable now",
                    "tips": "Practical advice",
                    "timing": "Best timing information"
                }}
            ]
        }}
        """

    def _get_day_part(self, hour: int) -> str:
        """Determine the part of the day based on hour"""
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"