from typing import TypedDict, Literal, List, Dict

class HelpdeskState(TypedDict, total=False):
    user_query: str
    route: Literal["placement_stats", "guidelines", "eligibility", "general"]
    response: str
    chat_history: List[Dict[str, str]]  