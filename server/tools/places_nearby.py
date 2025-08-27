from typing import Optional

from services.gmaps_init import maps_client
from services.logger_init import logger
from services.fastmcp_init import mcp
from . import types

types = types.place_types


@mcp.tool()
def place_nearby(
    location: str,
    radius: int = 1000,
    type: Optional[types] = None,
    open_now: bool = False,
    language: Optional[str] = None,
) -> list:
    """
    Google Places Nearby Search API tool for finding places of a specific type within a defined radius.

    WHEN TO USE:
        Find all businesses of a specific type nearby: "All hospitals within 5km"
        Location-centered searches: "Gas stations within 2 miles of this address"
        Type-specific discovery: "What parks are around here?"
        Quick proximity checks: "Any pharmacies open nearby?"

        NOT for broad discovery searches (use places() instead)
        NOT for finding specific named businesses (use find_place() instead)
        NOT for complex multi-criteria searches

    PARAMETERS:
        - location: Center point for search (required) - address, lat/lng, or place name
        - radius: Search radius in meters (default 1000, max 50,000)
        - type: Specific business category (restaurant, hospital, gas_station, etc.)
        - open_now: Only return currently open businesses (default False)
        - language: Language for results (optional)

    RETURNS: List of places within the specified radius, ranked by prominence/distance

    KEY DIFFERENCES:
        - place_nearby: Focused radius-based search for specific types
        - places(): Broad discovery with complex filtering and text search
        - find_place: Lookup specific known businesses by name/address

    BEST PRACTICES:
        - Use when you know the area and want a specific type of business
        - Combine with open_now=True for immediate needs
        - Start with smaller radius (500-2000m) for dense urban areas
        - Use larger radius (5000-10000m) for suburban/rural areas
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
        return [{"error": str(e), "status": "ERROR"}]
    except Exception as e:
        logger.error(f"❌ Places Nearby API error: {str(e)}")
        return [{"error": f"Exception occurred: {str(e)}", "status": "ERROR"}]


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
