from mcp_init import mcp, get_db_connection
from typing import List, Optional
import json
from ..vector import TiDBVectorManager


@mcp.tool()
def find_best_workers_for_task(
    title: str,
    description: str,
    skill_requirements: Optional[List[str]] = None,
    trade_category: Optional[str] = None,
    k: Optional[int] = 3,
    min_similarity_score: Optional[float] = None,
    required_skills: Optional[List[str]] = None,
    preferred_experience_years: Optional[float] = None,
) -> str:
    """
    Find the best workers for a given task based on semantic skill matching.

    This tool uses vector similarity search to match workers' skills, experience,
    and capabilities with task requirements. It combines task fields into a 
    searchable description and finds workers whose skill profiles are most similar.

    PARAMETERS:
    - title: Task title (str, required)
    - description: Task description (str, required)  
    - skill_requirements: List of required skills (list, optional)
    - trade_category: Trade/category of work (str, optional)
    - k: Number of workers to return (int, optional, default=3, max=10)
    - min_similarity_score: Minimum similarity percentage (float, optional, 0-100)
    - required_skills: Must-have skills for filtering (list, optional)
    - preferred_experience_years: Minimum preferred experience years (float, optional)

    RETURN:
    JSON with ranked list of best-matching workers and their skill compatibility.

    EXAMPLE USAGE:
    find_best_workers_for_task(
        title="Office Lighting Repair",
        description="Replace broken fluorescent bulbs in conference room",
        skill_requirements=["electrical_installation", "lighting_maintenance"],
        trade_category="electrical",
        k=3,
        min_similarity_score=70.0
    )
    """

    # Validate required parameters
    if not title or not title.strip():
        return json.dumps(
            {
                "success": False,
                "error": "❌ title is required and cannot be empty",
            }
        )
    
    if not description or not description.strip():
        return json.dumps(
            {
                "success": False,
                "error": "❌ description is required and cannot be empty",
            }
        )
    
    # Build task description by concatenating all fields
    components = []
    components.append(title.strip())
    components.append(description.strip())
    
    if skill_requirements:
        if isinstance(skill_requirements, list):
            components.extend(skill_requirements)
        else:
            components.append(str(skill_requirements))
    
    if trade_category:
        components.append(trade_category.strip())
    
    task_description = " ".join(components)

    # Validate optional parameters
    if k is not None:
        if not isinstance(k, int) or k <= 0 or k > 10:
            return json.dumps(
                {"success": False, "error": "❌ k must be an integer between 1 and 10"}
            )
    else:
        k = 3

    if min_similarity_score is not None:
        if not isinstance(min_similarity_score, (int, float)) or not (
            0.0 <= min_similarity_score <= 100.0
        ):
            return json.dumps(
                {
                    "success": False,
                    "error": "❌ min_similarity_score must be a number between 0 and 100",
                }
            )

    if preferred_experience_years is not None:
        if (
            not isinstance(preferred_experience_years, (int, float))
            or preferred_experience_years < 0
        ):
            return json.dumps(
                {
                    "success": False,
                    "error": "❌ preferred_experience_years must be a non-negative number",
                }
            )

    if required_skills is not None:
        if not isinstance(required_skills, list):
            return json.dumps(
                {
                    "success": False,
                    "error": "❌ required_skills must be a list of strings",
                }
            )

    try:
        # Initialize vector manager
        vector_manager = TiDBVectorManager()

        # Perform vector search for best matching workers
        # We'll search with a higher k first, then filter and rank
        search_k = max(k * 2, 10)  # Get more results for better filtering
        results = vector_manager.find_best_workers_for_task(
            task_description.strip(), k=search_k
        )

        # Process and filter results
        qualified_workers = []
        for result in results:
            distance = result.distance
            similarity_score = (1 - distance) * 100  # Convert to percentage

            # Apply similarity score filter
            if (
                min_similarity_score is not None
                and similarity_score < min_similarity_score
            ):
                continue

            user_metadata = result.metadata
            worker_skills = user_metadata.get("primary_skills", [])
            worker_experience = user_metadata.get("experience_years", 0)

            # Apply experience filter
            if (
                preferred_experience_years is not None
                and worker_experience < preferred_experience_years
            ):
                continue

            # Apply required skills filter
            if required_skills is not None:
                has_required_skills = any(
                    req_skill.lower() in [skill.lower() for skill in worker_skills]
                    for req_skill in required_skills
                )
                if not has_required_skills:
                    continue

            # Calculate skill match details
            skill_matches = []
            if required_skills:
                for req_skill in required_skills:
                    matches = [
                        skill
                        for skill in worker_skills
                        if req_skill.lower() in skill.lower()
                    ]
                    if matches:
                        skill_matches.extend(matches)

            qualified_workers.append(
                {
                    "user_id": user_metadata.get("user_id"),
                    "name": user_metadata.get("name", "Unknown"),
                    "role": user_metadata.get("role", ""),
                    "similarity_score": round(similarity_score, 2),
                    "distance": round(distance, 4),
                    "experience_years": worker_experience,
                    "primary_skills": worker_skills,
                    "trade_categories": user_metadata.get("trade_categories", []),
                    "skill_matches": skill_matches,
                    "vector_doc_id": result.id,
                    "profile_summary": (
                        result.text[:150] + "..."
                        if len(result.text) > 150
                        else result.text
                    ),
                }
            )

        # Sort by similarity score (highest first) and limit to k results
        qualified_workers.sort(key=lambda x: x["similarity_score"], reverse=True)
        final_results = qualified_workers[:k]

        return json.dumps(
            {
                "success": True,
                "task_info": {
                    "title": title,
                    "description": description,
                    "skill_requirements": skill_requirements,
                    "trade_category": trade_category,
                    "combined_description": task_description
                },
                "total_qualified_workers": len(qualified_workers),
                "returned_workers": len(final_results),
                "max_requested": k,
                "filters_applied": {
                    "min_similarity_score": min_similarity_score,
                    "required_skills": required_skills,
                    "preferred_experience_years": preferred_experience_years,
                },
                "best_workers": final_results,
                "message": f"✅ Found {len(final_results)} qualified workers for task: '{task_description[:50]}...'",
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {"success": False, "error": f"❌ Error finding best workers: {str(e)}"}
        )
