from typing import Optional
from services.gmaps_init import maps_client
from services.logger_init import logger
from services.fastmcp_init import mcp
from . import types

input_types = types.input_types


@mcp.tool()
def find_place(
    input: str,
    input_type: Optional[input_types] = "textquery",
    fields: Optional[list[str]] = [
        "name",
        "formatted_address",
        "place_id",
        "geometry",
        "type",
        "url",
    ],
    location_bias: Optional[str] = None,
    language: Optional[str] = None,
) -> list:
    """
    Google Places Find Place API tool for finding specific places by name, address, or phone number.

    WHEN TO USE:
        Find specific businesses by name: "Starbucks on Main Street"
        Look up places by address: "123 Main St, New York"
        Search by phone number: "+1-555-123-4567"
        Verify/confirm a specific place exists
        Get details about a known location

        NOT for discovery or "what's nearby" searches (use places() instead)
        NOT for browsing multiple options (use place_nearby instead)
        NOT for general category searches like "restaurants"

    PARAMETERS:
        - input: Specific text to search for (business name, address, or phone number)
        - input_type: "textquery" for names/addresses, "phonenumber" for phone searches
        - fields: Specific data fields to return (name, address, rating, etc.)
        - location_bias: Prefer results in specific area (ipbias, point:lat,lng, circle:lat,lng@radius, rectangle:sw_lat,sw_lng|ne_lat,ne_lng)
        - language: Language for results (optional)

    RETURNS: List of candidate places (usually 1-3 results) that match the specific input

    KEY DIFFERENCES:
        - find_place: Lookup specific known places by identifier
        - places(): Broad discovery searches with multiple criteria
        - place_nearby: Type-based searches within radius

    BEST PRACTICES:
        - Use specific, complete business names for best results
        - Include location context when searching common names
        - Use location_bias to narrow results to specific area by specifying either a radius plus lat/lng, or two lat/lng pairs representing the points of a rectangle
        - Combine with address or neighborhood for disambiguation
    """
    try:
        result = maps_client.find_place(  # type: ignore
            input=input,
            input_type=input_type,
            fields=fields,
            location_bias=location_bias,
            language=language,
        )

        logger.info(f"✅ find_place result: {result}")
        return result
        # cleaned_result = clean_response(result)
        # return cleaned_result

    except ValueError as e:
        logger.error(f"❌ find_place validation error: {str(e)}")
        return [{"error": str(e), "status": "ERROR"}]
    except Exception as e:
        logger.error(f"❌ find_place error: {str(e)}")
        return [{"error": f"Exception occurred: {str(e)}", "status": "ERROR"}]


# def clean_response(result) -> list:
#     """
#     Clean the find_place response to a simpler format for the LLM.
#     """
#     logger.info(
#         f"Cleaning find_place response with status: {result.get('status', 'UNKNOWN')}"
#     )

#     try:
#         if result["status"] == "OK":
#             places = result.get("results", [])
#             logger.info(f"Processing {len(places)} places")

#             places_filtered = []
#             for i, place in enumerate(places):
#                 logger.debug(f"Processing place {i+1}: {place.get('name', 'Unknown')}")

#                 cleaned_place = {
#                     "place_id": place.get("place_id", ""),
#                     "name": place.get("name", ""),
#                     "formatted_address": place.get("formatted_address", ""),
#                     "rating": place.get("rating", ""),
#                     "user_ratings_total": place.get("user_ratings_total", ""),
#                     "types": place.get("types", []),
#                     "business_status": place.get("business_status", ""),
#                     "geometry": place.get("geometry", {}).get("location", {}),
#                     "viewport": place.get("geometry", {}).get("viewport", {}),
#                     "opening_hours": place.get("opening_hours", {}),
#                     "plus_code": place.get("plus_code", {}),
#                 }
#                 places_filtered.append(cleaned_place)

#             # Include pagination info if available
#             # response = {
#             # "places": places_filtered,
#             # "next_page_token": result.get("next_page_token"),
#             # }

#             logger.info(f"Cleaned {len(places_filtered)} find_place successfully")
#             return places_filtered
#         else:
#             error_msg = f"No results found - API status: {result['status']}"
#             logger.warning(f"{error_msg}")
#             return [{"error": error_msg, "status": "ERROR"}]

#     except (KeyError, TypeError) as e:
#         error_msg = f"Response parsing error: {str(e)}"
#         logger.error(f"{error_msg}")
#         return [{"error": error_msg, "status": "ERROR"}]


# run(
#     latlng={"latitude": 48.860901643473504, "longitude": 2.3376543790775197},
# )  # Example usage, can be removed later
