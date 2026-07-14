from app.nodes.placements import placementstats_node
from app.nodes.eligibility import eligibility_node
from app.nodes.general import generalchatbot_node
from app.nodes.guidelines import guidelines_node
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
    