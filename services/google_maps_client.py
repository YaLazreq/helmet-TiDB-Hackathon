"""
Google Maps Client Singleton
Centralized initialization of Google Maps client to avoid multiple instances
"""

import os
import logging
import googlemaps
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

if not API_KEY:
    logger.error("❌ GOOGLE_MAPS_API_KEY not found in environment variables")
    raise ValueError(
        "Google Maps API key is required. Please set GOOGLE_MAPS_API_KEY in your .env file"
    )

logger.info("🗺️ Initializing Google Maps client...")

try:
    maps_client = googlemaps.Client(key=API_KEY)
    logger.info("✅ Google Maps client initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize Google Maps client: {str(e)}")
    raise

# Export the client and API key
__all__ = [
    "maps_client",
    "API_KEY",
]
