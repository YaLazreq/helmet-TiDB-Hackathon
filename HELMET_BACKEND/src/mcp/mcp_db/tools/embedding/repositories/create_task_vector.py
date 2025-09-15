# from mcp_init import mcp, get_db_connection
# from typing import Dict, Any, Optional
# import json
# from ..vector import TiDBVectorManager


# @mcp.tool()
# def create_task_vector(
#     task_id: int,
#     title: str,
#     description: str,
#     room: Optional[str] = None,
#     building_section: Optional[str] = None,
#     zone_type: Optional[str] = None,
#     trade_category: Optional[str] = None,
#     skill_requirements: Optional[list] = None,
#     required_materials: Optional[list] = None,
#     required_equipment: Optional[list] = None,
#     notes: Optional[str] = None,
# ) -> str:
#     """
#     Create a vector embedding for a task to enable semantic search and matching.

#     This tool generates vector embeddings based on task attributes like title, description,
#     location, trade category, required skills, materials, and equipment. The vector is
#     stored in TiDB for semantic similarity searches.

#     PARAMETERS:
#     - task_id: Unique identifier for the task (int)
#     - title: Task title (str, required)
#     - description: Task description (str, required)
#     - room: Room location (str, optional, e.g., "A201", "B100")
#     - building_section: Building section (str, optional, e.g., "Wing A", "Block B")
#     - zone_type: Zone type (str, optional, e.g., "office", "warehouse", "technical")
#     - trade_category: Trade category (str, optional, e.g., "electricity", "plumbing")
#     - skill_requirements: Required skills (list, optional, e.g., ["electrician", "plumber"])
#     - required_materials: Materials needed (list, optional)
#     - required_equipment: Equipment needed (list, optional)
#     - notes: Additional notes (str, optional)

#     RETURN:
#     JSON with success status and vector document ID, or error message.

#     EXAMPLE USAGE:
#     create_task_vector(
#         task_id=1,
#         title="Repair electrical lighting in office A201",
#         description="Replace faulty fluorescent lights and check electrical installation",
#         room="A201",
#         building_section="Wing A",
#         zone_type="office",
#         trade_category="electricity",
#         skill_requirements=["electrician"],
#         required_equipment=["ladder", "multimeter"],
#         notes="Urgent - office used daily"
#     )
#     """

#     # Validate required parameters
#     if not task_id or not isinstance(task_id, int):
#         return json.dumps(
#             {"success": False, "error": "❌ task_id is required and must be an integer"}
#         )

#     if not title or not title.strip():
#         return json.dumps(
#             {"success": False, "error": "❌ title is required and cannot be empty"}
#         )

#     if not description or not description.strip():
#         return json.dumps(
#             {
#                 "success": False,
#                 "error": "❌ description is required and cannot be empty",
#             }
#         )

#     try:
#         # Initialize vector manager
#         vector_manager = TiDBVectorManager()

#         # Prepare task data
#         task_data = {
#             "title": title.strip(),
#             "description": description.strip(),
#         }

#         # Add optional fields if provided
#         if room:
#             task_data["room"] = room.strip()
#         if building_section:
#             task_data["building_section"] = building_section.strip()
#         if zone_type:
#             task_data["zone_type"] = zone_type.strip()
#         if trade_category:
#             task_data["trade_category"] = trade_category.strip()
#         if skill_requirements:
#             task_data["skill_requirements"] = skill_requirements
#         if required_materials:
#             task_data["required_materials"] = required_materials
#         if required_equipment:
#             task_data["required_equipment"] = required_equipment
#         if notes:
#             task_data["notes"] = notes.strip()

#         # Create vector
#         doc_id = vector_manager.create_task_vector(task_id, task_data)

#         return json.dumps(
#             {
#                 "success": True,
#                 "message": f"✅ Task vector created successfully for task {task_id}",
#                 "task_id": task_id,
#                 "vector_doc_id": doc_id,
#                 "searchable_content": vector_manager._build_task_searchable_text(
#                     task_data
#                 ),
#             },
#             indent=2,
#         )

#     except Exception as e:
#         return json.dumps(
#             {"success": False, "error": f"❌ Error creating task vector: {str(e)}"}
#         )
