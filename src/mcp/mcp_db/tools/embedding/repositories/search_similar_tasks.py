from mcp_init import mcp, get_db_connection
from typing import List, Optional
import json
from ..vector import TiDBVectorManager


@mcp.tool()
def search_similar_tasks(
    query: str,
    k: Optional[int] = 5,
    min_distance_threshold: Optional[float] = None,
    max_distance_threshold: Optional[float] = None,
) -> str:
    """
    Search for tasks that are semantically similar to the given query.

    This tool performs vector-based semantic search to find tasks that match
    the intent, content, or requirements described in the query. Useful for
    finding related tasks, estimating effort based on similar past tasks,
    or discovering task patterns.

    PARAMETERS:
    - query: Search query describing the task or requirements (str, required)
    - k: Number of results to return (int, optional, default=5, max=20)
    - min_distance_threshold: Minimum similarity threshold (float, optional, 0.0-1.0)
    - max_distance_threshold: Maximum similarity threshold (float, optional, 0.0-1.0)

    RETURN:
    JSON with search results including task metadata and similarity distances.

    EXAMPLE QUERIES:
    - "electrical repair in office building"
    - "plumbing maintenance bathroom"
    - "painting exterior walls"
    - "HVAC installation commercial building"
    - "lighting fixtures replacement"
    - "emergency roof repair"

    EXAMPLE USAGE:
    search_similar_tasks(
        query="Need to fix electrical lighting in office",
        k=3,
        max_distance_threshold=0.8
    )
    """

    # Validate required parameters
    if not query or not query.strip():
        return json.dumps(
            {"success": False, "error": "❌ query is required and cannot be empty"}
        )

    # Validate optional parameters
    if k is not None:
        if not isinstance(k, int) or k <= 0 or k > 20:
            return json.dumps(
                {"success": False, "error": "❌ k must be an integer between 1 and 20"}
            )
    else:
        k = 5

    if min_distance_threshold is not None:
        if not isinstance(min_distance_threshold, (int, float)) or not (
            0.0 <= min_distance_threshold <= 1.0
        ):
            return json.dumps(
                {
                    "success": False,
                    "error": "❌ min_distance_threshold must be a number between 0.0 and 1.0",
                }
            )

    if max_distance_threshold is not None:
        if not isinstance(max_distance_threshold, (int, float)) or not (
            0.0 <= max_distance_threshold <= 1.0
        ):
            return json.dumps(
                {
                    "success": False,
                    "error": "❌ max_distance_threshold must be a number between 0.0 and 1.0",
                }
            )

    if (
        min_distance_threshold is not None
        and max_distance_threshold is not None
        and min_distance_threshold > max_distance_threshold
    ):
        return json.dumps(
            {
                "success": False,
                "error": "❌ min_distance_threshold cannot be greater than max_distance_threshold",
            }
        )

    try:
        # Initialize vector manager
        vector_manager = TiDBVectorManager()

        # Perform search
        results = vector_manager.search_similar_tasks(query.strip(), k=k)

        # Filter by distance thresholds if provided
        filtered_results = []
        for result in results:
            distance = result.distance

            # Apply distance filters
            if min_distance_threshold is not None and distance < min_distance_threshold:
                continue
            if max_distance_threshold is not None and distance > max_distance_threshold:
                continue

            filtered_results.append(
                {
                    "task_id": result.metadata.get("task_id"),
                    "title": result.metadata.get("title", ""),
                    "trade_category": result.metadata.get("trade_category", ""),
                    "priority": result.metadata.get("priority", 0),
                    "status": result.metadata.get("status", ""),
                    "distance": round(distance, 4),
                    "similarity_score": round(
                        (1 - distance) * 100, 2
                    ),  # Convert to percentage
                    "vector_doc_id": result.id,
                    "matched_content": (
                        result.text[:200] + "..."
                        if len(result.text) > 200
                        else result.text
                    ),
                }
            )

        return json.dumps(
            {
                "success": True,
                "query": query,
                "total_results": len(filtered_results),
                "max_requested": k,
                "filters_applied": {
                    "min_distance_threshold": min_distance_threshold,
                    "max_distance_threshold": max_distance_threshold,
                },
                "results": filtered_results,
                "message": f"✅ Found {len(filtered_results)} similar tasks for query: '{query}'",
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {"success": False, "error": f"❌ Error searching similar tasks: {str(e)}"}
        )
