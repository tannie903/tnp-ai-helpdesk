from app.nodes.placements import get_placementstats
from app.nodes.eligibility import get_eligibility
from app.nodes.general import get_generalchatbot
from app.nodes.guidelines import get_guidelines
from app.state import HelpdeskState

def router_node(state: HelpdeskState):
    user_query=state["user_query"].lower()

    if "placement" in user_query or "stats" in user_query:
        return {"route": "placement_stats"}
    
    elif "guideline" in user_query or "company" in user_query:
        return {"route": "guidelines"}
    
    elif "eligibility" in user_query:
        return {"route": "eligibility"}
    
    else:
        return {"route": "general"}
    