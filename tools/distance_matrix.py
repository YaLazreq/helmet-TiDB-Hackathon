from datetime import datetime
import logging

# Import centralized Google Maps client
from services.google_maps_client import maps_client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# class DistanceMatrixArgs(BaseModel):
#     origin: str = Field(description="Starting location address")
#     destination: str = Field(description="Destination location address")
#     mode: str = Field(
#         default="driving",
#         description="Mode of transportation (e.g., driving, walking, bicycling, transit)",
#     )


def run(origin: str, destination: str, mode: str = "driving") -> dict:
    """
    Get the distance and duration between two locations.

    Args:
        origin (str): Starting location address.
        destination (str): Destination location address.
        mode (str): Mode of transportation (default is "driving").
    """
    logger.info(f"🚗 Distance Matrix API called: {origin} → {destination} ({mode})")

    try:
        now: datetime = datetime.now()
        logger.info(f"📍 Making API request with departure time: {now}")

        result = maps_client.distance_matrix(  # type: ignore
            origins=origin,
            destinations=destination,
            mode=mode,
            departure_time=now,
        )

        logger.info(f"📡 API response status: {result.get('status', 'UNKNOWN')}")
        logger.debug(f"📊 Full API response: {result}")

        # Extract the relevant data from the complex response
        cleaned_result = clean_response(result, mode)
        logger.info(f"✅ Distance Matrix result: {cleaned_result}")
        return cleaned_result

    except Exception as e:
        logger.error(f"❌ Distance Matrix API error: {str(e)}")
        return {"error": f"Exception occurred: {str(e)}", "status": "ERROR"}


def clean_response(result, mode: str) -> dict:
    """
    Clean the Distance Matrix API response to a simpler format for the llm.
    """
    logger.info(f"🧹 Cleaning response with status: {result.get('status', 'UNKNOWN')}")

    if result["status"] == "OK":
        try:
            element = result["rows"][0]["elements"][0]
            logger.info(f"🎯 Element status: {element.get('status', 'UNKNOWN')}")

            if element["status"] == "OK":
                cleaned = {
                    "origin": result["origin_addresses"][0],
                    "destination": result["destination_addresses"][0],
                    "distance": {
                        "text": element["distance"]["text"],
                        "value": element["distance"]["value"],  # in meters
                    },
                    "duration": {
                        "text": element["duration"]["text"],
                        "value": element["duration"]["value"],  # in seconds
                    },
                    "mode": mode,
                    "status": "OK",
                }
                logger.info(
                    f"✨ Cleaned successfully: {cleaned['distance']['text']}, {cleaned['duration']['text']}"
                )
                return cleaned
            else:
                error_msg = f"Route not found: {element['status']}"
                logger.warning(f"⚠️ {error_msg}")
                return {
                    "error": error_msg,
                    "status": "ERROR",
                }
        except (KeyError, IndexError) as e:
            error_msg = f"Response parsing error: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {"error": error_msg, "status": "ERROR"}

    else:
        error_msg = f"API error: {result['status']}"
        logger.error(f"❌ {error_msg}")
        return {"error": error_msg, "status": "ERROR"}
