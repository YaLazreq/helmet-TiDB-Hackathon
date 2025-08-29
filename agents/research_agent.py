# from typing import List, Any, Optional
# from .base_agent import BaseAgent


def web_search(query: str) -> str:
    """Simule une recherche web en renvoyant une chaîne de caractères"""
    return f"Résultats de la recherche pour '{query}' : [Lien1, Lien2, Lien3]"


# class ResearchAgent(BaseAgent):
#     """Agent spécialisé dans la recherche d'informations"""

#     def __init__(
#         self, model, name: str = "research_expert", tools: Optional[List[Any]] = None
#     ):
#         super().__init__(
#             model=model,
#             name=name,
#             description="Expert en recherche avec accès aux outils de recherche web",
#             tools=tools or [],
#         )

#     def get_default_prompt(self) -> str:
#         return (
#             "You are a world class researcher with access to web search and various APIs. "
#             "Do not do any math - delegate mathematical calculations to other agents. "
#             "Focus on gathering accurate, up-to-date information from reliable sources."
#         )

#     def get_tools(self) -> List[Any]:
#         return self.tools
