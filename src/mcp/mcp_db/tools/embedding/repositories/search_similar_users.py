from mcp_init import mcp, get_db_connection
from typing import List, Optional
import json
from ..vector import TiDBVectorManager


@mcp.tool()
def search_similar_users(
    query: str,
    k: Optional[int] = 5,
    min_similarity_score: Optional[float] = None,
    role_filter: Optional[str] = None,
    min_experience_years: Optional[float] = None,
    trade_category_filter: Optional[str] = None,
) -> str:
    """
    Search for users with skills and profiles similar to the given query.
    
    This tool performs vector-based semantic search to find workers whose
    skills, experience, and capabilities match the query. Useful for finding
    workers with specific expertise, building teams, or identifying skill gaps.
    
    PARAMETERS:
    - query: Search query describing desired skills or profile (str, required)
    - k: Number of results to return (int, optional, default=5, max=15)
    - min_similarity_score: Minimum similarity percentage (float, optional, 0-100)
    - role_filter: Filter by specific role (str, optional, e.g., "worker", "supervisor")
    - min_experience_years: Minimum years of experience (float, optional)
    - trade_category_filter: Filter by trade category (str, optional, e.g., "electricity")
    
    RETURN:
    JSON with search results including user profiles and similarity scores.
    
    EXAMPLE QUERIES:
    - "experienced electrician with commercial building experience"
    - "plumber with pipe installation and repair skills"
    - "crane operator with heavy machinery certification"
    - "painter with exterior and interior painting experience"
    - "HVAC technician with troubleshooting skills"
    - "supervisor with safety training and team leadership"
    - "welder with structural and pipeline experience"
    
    EXAMPLE USAGE:
    search_similar_users(
        query="Experienced electrician with troubleshooting skills",
        k=5,
        min_similarity_score=60.0,
        role_filter="worker",
        min_experience_years=5.0,
        trade_category_filter="electricity"
    )
    """
    
    # Validate required parameters
    if not query or not query.strip():
        return json.dumps({
            "success": False,
            "error": "❌ query is required and cannot be empty"
        })
    
    # Validate optional parameters
    if k is not None:
        if not isinstance(k, int) or k <= 0 or k > 15:
            return json.dumps({
                "success": False,
                "error": "❌ k must be an integer between 1 and 15"
            })
    else:
        k = 5
    
    if min_similarity_score is not None:
        if not isinstance(min_similarity_score, (int, float)) or not (0.0 <= min_similarity_score <= 100.0):
            return json.dumps({
                "success": False,
                "error": "❌ min_similarity_score must be a number between 0 and 100"
            })
    
    if min_experience_years is not None:
        if not isinstance(min_experience_years, (int, float)) or min_experience_years < 0:
            return json.dumps({
                "success": False,
                "error": "❌ min_experience_years must be a non-negative number"
            })
    
    valid_roles = ["worker", "team_leader", "supervisor", "site_manager"]
    if role_filter is not None:
        if role_filter not in valid_roles:
            return json.dumps({
                "success": False,
                "error": f"❌ role_filter must be one of: {valid_roles}"
            })
    
    try:
        # Initialize vector manager
        vector_manager = TiDBVectorManager()
        
        # Perform vector search with higher k for filtering
        search_k = max(k * 2, 15)  # Get more results for better filtering
        results = vector_manager.search_similar_users(query.strip(), k=search_k)
        
        # Process and filter results
        qualified_users = []
        for result in results:
            distance = result.distance
            similarity_score = (1 - distance) * 100  # Convert to percentage
            
            # Apply similarity score filter
            if min_similarity_score is not None and similarity_score < min_similarity_score:
                continue
            
            user_metadata = result.metadata
            user_role = user_metadata.get("role", "")
            user_experience = user_metadata.get("experience_years", 0)
            user_trade_categories = user_metadata.get("trade_categories", [])
            
            # Apply role filter
            if role_filter is not None and user_role != role_filter:
                continue
            
            # Apply experience filter
            if min_experience_years is not None and user_experience < min_experience_years:
                continue
            
            # Apply trade category filter
            if trade_category_filter is not None:
                if not any(trade_category_filter.lower() in category.lower() for category in user_trade_categories):
                    continue
            
            # Calculate skill relevance
            primary_skills = user_metadata.get("primary_skills", [])
            query_words = query.lower().split()
            skill_matches = []
            
            for skill in primary_skills:
                if any(word in skill.lower() for word in query_words):
                    skill_matches.append(skill)
            
            qualified_users.append({
                "user_id": user_metadata.get("user_id"),
                "name": user_metadata.get("name", "Unknown"),
                "role": user_role,
                "similarity_score": round(similarity_score, 2),
                "distance": round(distance, 4),
                "experience_years": user_experience,
                "primary_skills": primary_skills,
                "trade_categories": user_trade_categories,
                "relevant_skills": skill_matches,
                "vector_doc_id": result.id,
                "profile_summary": result.text[:150] + "..." if len(result.text) > 150 else result.text
            })
        
        # Sort by similarity score (highest first) and limit to k results
        qualified_users.sort(key=lambda x: x["similarity_score"], reverse=True)
        final_results = qualified_users[:k]
        
        # Calculate statistics
        avg_similarity = sum(user["similarity_score"] for user in final_results) / len(final_results) if final_results else 0
        avg_experience = sum(user["experience_years"] for user in final_results) / len(final_results) if final_results else 0
        
        return json.dumps({
            "success": True,
            "query": query,
            "total_qualified_users": len(qualified_users),
            "returned_users": len(final_results),
            "max_requested": k,
            "statistics": {
                "average_similarity_score": round(avg_similarity, 2),
                "average_experience_years": round(avg_experience, 1)
            },
            "filters_applied": {
                "min_similarity_score": min_similarity_score,
                "role_filter": role_filter,
                "min_experience_years": min_experience_years,
                "trade_category_filter": trade_category_filter
            },
            "users": final_results,
            "message": f"✅ Found {len(final_results)} users matching: '{query[:50]}...'"
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"❌ Error searching similar users: {str(e)}"
        })