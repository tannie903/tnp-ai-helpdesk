from typing import TypedDict, Literal

class HelpdeskState(TypedDict,total=False):
    user_query: str
    route: Literal["placement_stats","guidelines","eligibility","general"]
    response: str