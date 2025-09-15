async def run_supervisor_agent(message_content: str):
    from src.agents.supervisor import supervisor

    # TODO: Move this to a route handler
    # Consider: supervisor.invoke() for single response or supervisor.stream() for streaming
    # message_content = "[User ID: 2 - Message Date: Sun. 10 September 2025]: Can you assign me in another task please?"

    result = await supervisor.ainvoke(
        input={
            "messages": [
                {
                    "role": "user",
                    "content": message_content,
                }
            ],
        },
        config={
            "run_name": "agent_supervisor",
            "tags": ["debug"],
            "recursion_limit": 100,
        },
    )

    return result
