import asyncio
from src.config.llm_init import model
from server.services.logger_init import logger
import pretty_print_message as ppm

from src.mcp.db_client import connect_db_mcp
from src.mcp.api_client import connect_api_mcp


async def main():
    await connect_db_mcp()
    # await connect_api_mcp()

    # Import after initialization
    from src.mcp.db_client import db_mcp_tools, db_mcp_tools_for_prompt

    # from src.mcp.api_client import api_mcp_tools

    # if db_mcp_tools is None or api_mcp_tools is None:
    if db_mcp_tools is None:
        logger.error("MCP tools not initialized properly.")
        return
    else:
        logger.info(f"✅ {len(db_mcp_tools)} DB MCP tool(s) cached")
        # logger.info(f"✅ {len(api_mcp_tools)} API MCP tool(s) cached")

    from langgraph.prebuilt import create_react_agent
    from src.mcp.db_client import get_db_mcp_tools

    prompt = """
        You are an assistant helping to manage tasks and users in a task management system.
        You have access to the following tools:
        {db_mcp_tools_for_prompt}
        
        You can create, read, update row in the database in the following tables: users, tasks.
        CRITICAL: You must use the tools to interact with the database.
        """

    print("🚨🚨🚨")
    print(prompt.format(db_mcp_tools_for_prompt=db_mcp_tools_for_prompt))
    print("🚨🚨🚨")

    print(get_db_mcp_tools())

    database_agent = create_react_agent(
        model=model,
        tools=[*get_db_mcp_tools()],
        prompt=prompt.format(db_mcp_tools_for_prompt=db_mcp_tools_for_prompt),
        name="database_agent",
    )

    result = database_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": """create a new user: user_id, first_name, last_name, email, password_hash, phone, address,
   role, is_active, hire_date,
   primary_skills, secondary_skills, trade_categories, experience_years, skill_levels,
   work_preferences, equipment_mastery, project_experience,
   certifications, safety_training, last_training_date
Values:
   'usr_015', 'Yanis', 'Lazreq', 't.martin@email.com', '$2b$12$hash115', '+33181920212', '42 Boulevard Saint-Michel, Paris 5e',
   'team_leader', TRUE, '2012-04-18',
   '["electrical_installation", "industrial_wiring", "control_panels", "motor_controls"]',
   '["plc_programming", "fiber_optics", "security_systems", "renewable_energy"]',
   '["electricity", "automation"]',
   12.0,
   '{"electrical_installation": 9, "industrial_wiring": 10, "control_panels": 9, "motor_controls": 8}',
   '["indoor", "outdoor", "technical_problem_solving", "precision_work"]',
   '["multimeter", "oscilloscope", "conduit_bender", "wire_pullers", "test_equipment", "laptop"]',
   '["industrial", "commercial", "data_centers", "renewable_energy", "automation"]',
   '["master_electrician", "industrial_controls", "fiber_optic_certification", "solar_installer"]',
   '["electrical_safety", "arc_flash_training", "confined_space", "lockout_tagout", "first_aid"]',
   '2024-02-14'""",
                },
            ]
        }
    )

    print(result["messages"][-1].content)

    # print(db_mcp_tools_for_prompt)
    # from src.agents.supervisor_002 import supervisor

    # final_chunk = None
    # for chunk in supervisor.stream(
    #     {
    #         "messages": [
    #             {
    #                 "role": "user",
    #                 "content": "Change the time for installing security cameras to 3 p.m. the next day",
    #                 # "content": "Changer le numéroe de téléphone du travailleur Yanis Dupont à 0606060606",
    #             }
    #         ]
    #     },
    #     config={"run_name": "agent_supervisor", "tags": ["debug"]},
    #     subgraphs=True,
    # ):
    #     ppm.pretty_print_messages(chunk, last_message=True)
    #     final_chunk = chunk

    # # Handle the case where chunk might be a tuple (namespace, update)
    # if isinstance(final_chunk, tuple):
    #     _, update = final_chunk
    #     if "supervisor" in update:
    #         final_message_history = update["supervisor"]["messages"]
    #     else:
    #         final_message_history = None
    # else:
    #     final_message_history = (
    #         final_chunk["supervisor"]["messages"]
    #         if final_chunk and "supervisor" in final_chunk
    #         else None
    #     )


if __name__ == "__main__":
    asyncio.run(main())
