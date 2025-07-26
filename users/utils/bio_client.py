import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class BioGenerator:
    FASTAPI_URL = "http://localhost:8000/generate"  # Default, override in settings.py

    @staticmethod
    def generate_from_fastapi(name, age, hobbies, profession):
        try:
            # Include API key in headers (matches FastAPI's X-API-KEY)
            headers = {
                "X-API-KEY": settings.FASTAPI_SECRET_KEY,  # Key from Django settings
                "Content-Type": "application/json"
            }

            response = requests.post(
                settings.BIO_GENERATOR_URL or BioGenerator.FASTAPI_URL,
                json={
                    "name": name,
                    "age": age,
                    "hobbies": hobbies,
                    "profession": profession
                },
                headers=headers,  # Pass API key
                timeout=10
            )
            response.raise_for_status()  # Raise HTTP errors (4xx/5xx)

            # Handle FastAPI's structured response
            data = response.json()
            if data.get("success"):
                return data.get("bio", "")
            else:
                logger.error(f"Bio generation failed: {data.get('error')}")
                return ""

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            return ""