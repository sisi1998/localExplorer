import os
import sys
import json
import asyncio
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.gpt_service import GPTService

async def test_gpt_connection():
    try:
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            print("Error: OPENAI_API_KEY not found in environment variables")
            return False

        print("\n=== Testing GPT Service ===")
        gpt_service = GPTService(api_key)
        gpt_service._test_connection()

        test_weather_data = {
            "location": {
                "city": "Paris",
                "country": "FR"
            },
            "weather": {
                "temperature": 22,
                "description": "clear sky",
                "wind_speed": 3.1,
                "humidity": 65
            }
        }

        test_preferences = {
            "outdoor_preference": True,
            "activity_level": "moderate"
        }

        print("\nSending request with:")
        print(f"Location: {test_weather_data['location']['city']}, {test_weather_data['location']['country']}")
        print(f"Weather: {test_weather_data['weather']['temperature']}°C, {test_weather_data['weather']['description']}")
        print(f"Preferences: {json.dumps(test_preferences, indent=2)}")

        response = await gpt_service.generate_activity_suggestion(
            test_weather_data,
            test_preferences
        )

        print("\nGPT Response:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        
        return True

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_gpt_connection())
    print(f"\nTest {'succeeded' if success else 'failed'}")
