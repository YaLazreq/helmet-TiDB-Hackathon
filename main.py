from server.services.logger_init import logger
import pretty_print_message as ppm
from src.agents.supervisor_002 import (
    supervisor,
)  # Add this import or define accordingly


final_chunk = None
for chunk in supervisor.stream(
    {
        "messages": [
            {
                "role": "user",
                "content": "Change l'heure pour l'installation de caméras de sécurité à 15h le lendemain",
            }
        ]
    },
    config={"run_name": "agent_supervisor", "tags": ["debug"]},
    subgraphs=True,
):
    ppm.pretty_print_messages(chunk, last_message=True)
    final_chunk = chunk

# Handle the case where chunk might be a tuple (namespace, update)
if isinstance(final_chunk, tuple):
    _, update = final_chunk
    if "supervisor" in update:
        final_message_history = update["supervisor"]["messages"]
    else:
        final_message_history = None
else:
    final_message_history = (
        final_chunk["supervisor"]["messages"]
        if final_chunk and "supervisor" in final_chunk
        else None
    )
