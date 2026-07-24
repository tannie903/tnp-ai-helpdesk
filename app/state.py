 

from typing import TypedDict, Literal, List, Dict, Optional

class HelpdeskState(TypedDict, total=False):
    user_query: str
    category_hint: Optional[str]
    route: Literal["placement_stats", "guidelines", "eligibility", "general"]
    response: str
    chat_history: List[Dict[str, str]]
    student: Optional[Dict[str, str]]