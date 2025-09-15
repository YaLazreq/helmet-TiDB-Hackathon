# from src.mcp.mcp_db.mcp_init import mcp, get_db_connection
# from typing import Dict, Any, Optional, List
# import json
# from ..vector import TiDBVectorManager


# @mcp.tool()
# def create_user_vector(
#     user_id: int,
#     first_name: str,
#     last_name: str,
#     role: Optional[str] = None,
#     primary_skills: Optional[List[str]] = None,
#     secondary_skills: Optional[List[str]] = None,
#     trade_categories: Optional[List[str]] = None,
#     experience_years: Optional[float] = None,
#     skill_levels: Optional[Dict[str, int]] = None,
#     equipment_mastery: Optional[List[str]] = None,
#     certifications: Optional[List[str]] = None,
#     project_experience: Optional[List[str]] = None,
# ) -> str:
#     """
#     Create a vector embedding for a user to enable semantic search and skill matching.

#     This tool generates vector embeddings based on user attributes like name, role,
#     skills, experience, certifications, and equipment mastery. The vector is stored
#     in TiDB for semantic similarity searches to match workers with tasks.

#     PARAMETERS:
#     - user_id: Unique identifier for the user (int)
#     - first_name: User's first name (str, required)
#     - last_name: User's last name (str, required)
#     - role: User's role (str, optional, e.g., "worker", "supervisor", "team_leader")
#     - primary_skills: Main skills (list, optional, e.g., ["electrical_installation", "maintenance"])
#     - secondary_skills: Additional skills (list, optional, e.g., ["plumbing_repair", "height_work"])
#     - trade_categories: Trade categories (list, optional, e.g., ["electricity", "plumbing"])
#     - experience_years: Years of experience (float, optional)
#     - skill_levels: Skill proficiency levels (dict, optional, e.g., {"electricity": 9, "plumbing": 7})
#     - equipment_mastery: Equipment the user can operate (list, optional, e.g., ["multimeter", "crane"])
#     - certifications: User certifications (list, optional, e.g., ["electrical_permit_B1V"])
#     - project_experience: Types of projects worked on (list, optional, e.g., ["residential", "commercial"])

#     RETURN:
#     JSON with success status and vector document ID, or error message.

#     EXAMPLE USAGE:
#     create_user_vector(
#         user_id=1,
#         first_name="John",
#         last_name="Smith",
#         role="worker",
#         primary_skills=["electrical_installation", "maintenance"],
#         secondary_skills=["plumbing_repair"],
#         trade_categories=["electricity"],
#         experience_years=8.5,
#         skill_levels={"electricity": 9, "maintenance": 7},
#         equipment_mastery=["multimeter", "ladder", "drill"],
#         certifications=["electrical_permit_B1V", "safety_training"]
#     )
#     """

#     # Validate required parameters
#     if not user_id or not isinstance(user_id, int):
#         return json.dumps(
#             {"success": False, "error": "❌ user_id is required and must be an integer"}
#         )

#     if not first_name or not first_name.strip():
#         return json.dumps(
#             {"success": False, "error": "❌ first_name is required and cannot be empty"}
#         )

#     if not last_name or not last_name.strip():
#         return json.dumps(
#             {"success": False, "error": "❌ last_name is required and cannot be empty"}
#         )

#     try:
#         # Initialize vector manager
#         vector_manager = TiDBVectorManager()

#         # Prepare user data
#         user_data = {
#             "first_name": first_name.strip(),
#             "last_name": last_name.strip(),
#         }

#         # Add optional fields if provided
#         if role:
#             user_data["role"] = role.strip()
#         if primary_skills:
#             user_data["primary_skills"] = primary_skills
#         if secondary_skills:
#             user_data["secondary_skills"] = secondary_skills
#         if trade_categories:
#             user_data["trade_categories"] = trade_categories
#         if experience_years is not None:
#             user_data["experience_years"] = experience_years
#         if skill_levels:
#             user_data["skill_levels"] = skill_levels
#         if equipment_mastery:
#             user_data["equipment_mastery"] = equipment_mastery
#         if certifications:
#             user_data["certifications"] = certifications
#         if project_experience:
#             user_data["project_experience"] = project_experience

#         # Create vector
#         doc_id = vector_manager.create_user_vector(user_id, user_data)

#         return json.dumps(
#             {
#                 "success": True,
#                 "message": f"✅ User vector created successfully for user {user_id}",
#                 "user_id": user_id,
#                 "vector_doc_id": doc_id,
#                 "user_name": f"{first_name} {last_name}",
#                 "searchable_content": vector_manager._build_user_searchable_text(
#                     user_data
#                 ),
#             },
#             indent=2,
#         )

#     except Exception as e:
#         return json.dumps(
#             {"success": False, "error": f"❌ Error creating user vector: {str(e)}"}
#         )
