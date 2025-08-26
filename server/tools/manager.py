from langchain.tools import StructuredTool
from . import distance_matrix, geocode, places_nearby, reverse_geocode

# distance_matrix_tool = StructuredTool.from_function(
#     name="distance_matrix",
#     description="Get the distance & duration between two locations",
#     func=distance_matrix.run,
#     # args_schema=distance_matrix.DistanceMatrixArgs,
# )

# places_nearby_tool = StructuredTool.from_function(
#     name="places_nearby",
#     description="Get a list of places nearby a location",
#     func=places_nearby.run,
#     # args_schema=places_nearby.PlacesNearbyArgs,
# )

# geocode_tool = StructuredTool.from_function(
#     name="geocode",
#     description="Get the geocoding information for a location",
#     func=geocode.run,
#     # args_schema=geocoding.GeocodingArgs,
# )

# reverse_geocode_tool = StructuredTool.from_function(
#     name="reverse_geocoding",
#     description="Get the reverse geocoding information for a location",
#     func=reverse_geocode.run,
#     # args_schema=reverse_geocoding.ReverseGeocodingArgs,
# )
