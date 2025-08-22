from typing import Optional
import logging

# Import centralized Google Maps client
from services.google_maps_client import maps_client, API_KEY

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run(
    address: str,
    place_id: Optional[str] = None,
):
    """
    A Geocoding request takes an address and returns geocoding information.
    """
    logger.info(f"📏 Geocoding API called: {address} (place_id: {place_id})")

    try:
        if not address:
            logger.error("❌ No address provided")
            raise ValueError("No Address provided. Please provide a valid address.")

        logger.info(f"📍 Making geocoding request for: {address}")

        result = maps_client.geocode(  # type: ignore
            address=address,
            place_id=place_id,
        )

        logger.info(f"📡 API response: Found {len(result) if result else 0} results")
        logger.debug(f"📊 Full API response: {result}")

        # Extract the relevant data from the complex response
        cleaned_result = clean_response(result)
        logger.info(f"✅ Geocoding result: {cleaned_result}")
        return cleaned_result

    except ValueError as e:
        logger.error(f"❌ Geocoding validation error: {str(e)}")
        return {"error": str(e), "status": "ERROR"}
    except Exception as e:
        logger.error(f"❌ Geocoding API error: {str(e)}")
        return {"error": f"Exception occurred: {str(e)}", "status": "ERROR"}


def clean_response(result) -> dict:
    """
    Clean the Geocoding API response to a simpler format for the llm.
    """
    logger.info(
        f"🧹 Cleaning geocoding response: {len(result) if result else 0} results"
    )

    try:
        if result and len(result) > 0:
            place = result[0]
            logger.info(
                f"🎯 Processing first result: {place.get('formatted_address', 'Unknown')}"
            )

            # Try to get navigation points location first
            location = {}
            navigation_points = place.get("navigation_points", [])

            if navigation_points and len(navigation_points) > 0:
                location = navigation_points[0].get("location", {})
                logger.debug(f"📏 Using navigation points location: {location}")
            else:
                # Fallback to geometry location
                geometry = place.get("geometry", {})
                location = geometry.get("location", {})
                logger.debug(f"🗺️ Using geometry location: {location}")

            place_cleaned = {
                "formatted_address": place.get("formatted_address", ""),
                "location": location,
                "place_id": place.get("place_id", ""),
            }

            logger.info(f"✨ Cleaned geocoding result successfully")
            return place_cleaned
        else:
            error_msg = "No results found"
            logger.warning(f"⚠️ {error_msg}")
            return {"error": error_msg, "status": "ERROR"}

    except (KeyError, IndexError, TypeError) as e:
        error_msg = f"Response parsing error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {"error": error_msg, "status": "ERROR"}
