from typing import Optional
from services.gmaps_init import maps_client
from services.logger_init import logger
from services.fastmcp_init import mcp
from . import types

types = types.place_types


@mcp.tool()
def places(
    query: Optional[str] = None,
    location: Optional[str] = None,
    radius: Optional[int] = 1000,
    type: Optional[types] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    open_now: Optional[bool] = False,
    page_token: Optional[str] = None,
) -> list:
    """
    Google Places API tool for broad, exploratory searches to discover multiple places matching criteria.

    WHEN TO USE:
        Discovery searches: "Find Italian restaurants in downtown"
        Type-based searches: "Show me all gas stations nearby"
        Area exploration: "What cafes are within 2km of Central Park?"
        Filtered searches: "Find cheap restaurants that are open now"

        NOT for finding specific businesses by name (use find_place instead)

    PARAMETERS:
        - query: Free-text search ("pizza", "coffee shop near Times Square")
        - location: Center point (lat,lng or address)
        - radius: Search radius in meters (default 1000, max 50,000)
        - type: Business category (restaurant, gas_station, hospital, etc.)
        - min_price/max_price: Price level 0-4 (0=cheapest, 4=most expensive)
        - open_now: Only return currently open businesses
        - page_token: For retrieving additional results

    RETURNS: Multiple results with pagination support

    KEY DIFFERENCES:
        - places(): Broad searches, discovery, "what's nearby"
        - place_nearby: Specific type within radius
        - find_place: Known business/address lookup
    """
    try:
        result = maps_client.places(  # type: ignore
            query=query,
            location=location,
            radius=radius,
            type=type,
            min_price=min_price,
            max_price=max_price,
            open_now=open_now,
            page_token=page_token,
        )

        cleaned_result = clean_response(result)
        logger.info(f"✅ Reverse Geocoding result: {cleaned_result}")
        return cleaned_result

    except ValueError as e:
        logger.error(f"❌ Places API validation error: {str(e)}")
        return [{"error": str(e), "status": "ERROR"}]
    except Exception as e:
        logger.error(f"❌ Places API error: {str(e)}")
        return [{"error": f"Exception occurred: {str(e)}", "status": "ERROR"}]


def clean_response(result) -> list:
    """
    Clean the Places API response to a simpler format for the LLM.
    """
    logger.info(
        f"Cleaning places response with status: {result.get('status', 'UNKNOWN')}"
    )

    try:
        if result["status"] == "OK":
            places = result.get("results", [])
            logger.info(f"Processing {len(places)} places")

            places_filtered = []
            for i, place in enumerate(places):
                logger.debug(f"Processing place {i+1}: {place.get('name', 'Unknown')}")

                cleaned_place = {
                    "place_id": place.get("place_id", ""),
                    "name": place.get("name", ""),
                    "formatted_address": place.get("formatted_address", ""),
                    "rating": place.get("rating", ""),
                    "user_ratings_total": place.get("user_ratings_total", ""),
                    "types": place.get("types", []),
                    "business_status": place.get("business_status", ""),
                    "geometry": place.get("geometry", {}).get("location", {}),
                    "viewport": place.get("geometry", {}).get("viewport", {}),
                    "opening_hours": place.get("opening_hours", {}),
                    "plus_code": place.get("plus_code", {}),
                }
                places_filtered.append(cleaned_place)

            # Include pagination info if available
            # response = {
            # "places": places_filtered,
            # "next_page_token": result.get("next_page_token"),
            # }

            logger.info(f"Cleaned {len(places_filtered)} places successfully")
            return places_filtered
        else:
            error_msg = f"No results found - API status: {result['status']}"
            logger.warning(f"{error_msg}")
            return [{"error": error_msg, "status": "ERROR"}]

    except (KeyError, TypeError) as e:
        error_msg = f"Response parsing error: {str(e)}"
        logger.error(f"{error_msg}")
        return [{"error": error_msg, "status": "ERROR"}]


# run(
#     latlng={"latitude": 48.860901643473504, "longitude": 2.3376543790775197},
# )  # Example usage, can be removed later
