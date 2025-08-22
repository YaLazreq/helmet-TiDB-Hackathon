from typing import Literal, Optional
import logging

# Import centralized Google Maps client
from services.google_maps_client import maps_client, API_KEY

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

types = Literal[
    "accounting",
    "airport",
    "amusement_park",
    "aquarium",
    "art_gallery",
    "atm",
    "bakery",
    "bank",
    "bar",
    "beauty_salon",
    "bicycle_store",
    "book_store",
    "bowling_alley",
    "bus_station",
    "cafe",
    "campground",
    "car_dealer",
    "car_rental",
    "car_repair",
    "car_wash",
    "casino",
    "cemetery",
    "church",
    "city_hall",
    "clothing_store",
    "convenience_store",
    "courthouse",
    "dentist",
    "department_store",
    "doctor",
    "drugstore",
    "electrician",
    "electronics_store",
    "embassy",
    "fire_station",
    "florist",
    "funeral_home",
    "furniture_store",
    "gas_station",
    "gym",
    "hair_care",
    "hardware_store",
    "hindu_temple",
    "home_goods_store",
    "hospital",
    "insurance_agency",
    "jewelry_store",
    "laundry",
    "lawyer",
    "library",
    "light_rail_station",
    "liquor_store",
    "local_government_office",
    "locksmith",
    "lodging",
    "meal_delivery",
    "meal_takeaway",
    "mosque",
    "movie_rental",
    "movie_theater",
    "moving_company",
    "museum",
    "night_club",
    "painter",
    "park",
    "parking",
    "pet_store",
    "pharmacy",
    "physiotherapist",
    "plumber",
    "police",
    "post_office",
    "primary_school",
    "real_estate_agency",
    "restaurant",
    "roofing_contractor",
    "rv_park",
    "school",
    "secondary_school",
    "shoe_store",
    "shopping_mall",
    "spa",
    "stadium",
    "storage",
    "store",
    "subway_station",
    "supermarket",
    "synagogue",
    "taxi_stand",
    "tourist_attraction",
    "train_station",
    "transit_station",
    "travel_agency",
    "university",
    "veterinary_care",
    "zoo",
]


def run(
    location: str,
    radius: int = 1000,
    type: Optional[types] = None,
    open_now: bool = False,
    language: Optional[str] = None,
):
    """
    A Find Place request takes a text input, and returns a place.
    """
    logger.info(
        f"🗺️ Places Nearby API called: {location} (radius: {radius}m, type: {type})"
    )

    try:
        if not location:
            logger.error("❌ No location provided")
            raise ValueError("No Location provided. Please provide a valid location.")

        logger.info(f"📍 Making API request for places near: {location}")

        result = maps_client.places_nearby(  # type: ignore
            location=location,
            radius=radius,
            keyword="park",
            type=type,
            open_now=open_now,
            language=language,
        )

        logger.info(f"📡 API response status: {result.get('status', 'UNKNOWN')}")
        if result.get("status") == "OK":
            logger.info(f"📋 Found {len(result.get('results', []))} places")

        # Extract the relevant data from the complex response
        cleaned_result = clean_response(result)
        logger.info(
            f"✅ Places Nearby result: {len(cleaned_result) if isinstance(cleaned_result, list) else 'error'}"
        )
        return cleaned_result

    except ValueError as e:
        logger.error(f"❌ Places Nearby validation error: {str(e)}")
        return {"error": str(e), "status": "ERROR"}
    except Exception as e:
        logger.error(f"❌ Places Nearby API error: {str(e)}")
        return {"error": f"Exception occurred: {str(e)}", "status": "ERROR"}


def clean_response(result) -> list:
    """
    Clean the Places Nearby API response to a simpler format for the llm.
    """
    logger.info(
        f"🧹 Cleaning places response with status: {result.get('status', 'UNKNOWN')}"
    )

    try:
        if result["status"] == "OK":
            places = result.get("results", [])
            logger.info(f"🎯 Processing {len(places)} places")

            places_filtered = []
            for i, place in enumerate(places):
                logger.debug(
                    f"🏢 Processing place {i+1}: {place.get('name', 'Unknown')}"
                )

                cleaned_place = {
                    "place_id": place.get("place_id", ""),
                    "name": place.get("name", ""),
                    "vicinity": place.get("vicinity", ""),
                    "rating": place.get("rating", ""),
                    "user_ratings_total": place.get("user_ratings_total", ""),
                    "types": place.get("types", []),
                    "geometry": place.get("geometry", {}).get("location", {}),
                    "viewport": place.get("geometry", {}).get("viewport", {}),
                }
                places_filtered.append(cleaned_place)

            logger.info(f"✨ Cleaned {len(places_filtered)} places successfully")
            return places_filtered
        else:
            error_msg = f"No results found - API status: {result['status']}"
            logger.warning(f"⚠️ {error_msg}")
            return [{"error": error_msg, "status": "ERROR"}]

    except (KeyError, TypeError) as e:
        error_msg = f"Response parsing error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return [{"error": error_msg, "status": "ERROR"}]


# run(
#     location="48.8445722196813,2.3392068760492286",
#     radius=1000,
# )  # Example usage, can be removed later
