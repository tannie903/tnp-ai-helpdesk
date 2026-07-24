from app.nodes.placements import placementstats_node
from app.nodes.eligibility import eligibility_node
from app.nodes.general import generalchatbot_node
from app.nodes.guidelines import guidelines_node
from app.state import HelpdeskState

def router_node(state: HelpdeskState):
    user_query = state["user_query"].lower()

    # 1. Eligibility check FIRST (especially since Streamlit prepends 'eligibility')
    if "eligibility" in user_query or "eligible" in user_query or "cutoff" in user_query or "cgpa" in user_query:
        return {"route": "eligibility"}

    # 2. Placement Stats
    elif "placement" in user_query or "stats" in user_query or "salary" in user_query or "package" in user_query or "ctc" in user_query:
        return {"route": "placement_stats"}

    # 3. Guidelines & Policies (removed generic 'company' to avoid false triggers)
    elif "guideline" in user_query or "policy" in user_query or "rule" in user_query or "process" in user_query:
        return {"route": "guidelines"}

    # 4. Fallback General Node
    else:
        return {"route": "general"}