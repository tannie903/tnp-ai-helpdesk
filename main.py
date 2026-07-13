from langgraph.graph import END , START,StateGraph
from app.state import HelpdeskState

from app.agent.router import router_node
from app.nodes.placements import placementstats_node
from app.nodes.eligibility import eligibility_node
from app.nodes.general import generalchatbot_node
from app.nodes.guidelines import guidelines_node

# from app.agent.router import router_node

def build_graph():

    builder=StateGraph(HelpdeskState)

    builder.add_node("router",router_node)
    builder.add_node("placement_stats",placementstats_node)
    builder.add_node("eligibility",eligibility_node)
    builder.add_node("guidelines",guidelines_node)
    builder.add_node("general",generalchatbot_node)

    builder.add_edge(START,"router")
    builder.add_conditional_edges(
        "router",
        lambda state: state["route"],
        {
        "placement_stats": "placement_stats",
        "guidelines": "guidelines",
        "eligibility": "eligibility",
        "general": "general",
        }
    )
    

    builder.add_edge("placement_stats",END)
    builder.add_edge("guidelines",END)
    builder.add_edge("eligibility",END)
    builder.add_edge("general",END)

    app=builder.compile()
    return app




def start_helpdesk():

    app=build_graph()

    print("Hi! Welcome to the TnP Helpdesk of IGDTUW")
    print("Please provide us your information first")
    
    name=input("Enter your name : ")
    branch=input("Enter your branch : ")
    year=input("Enter your year(1/2/3/4) : ")
    
    print(f"\nGreat! Hi {name} , So you are from {branch} and Year {year}.\n")

    print("So what would you like to know?")
    print("1.Placement Stats")
    print("2.Interview and OA Guidelines")
    print("3.Eligibility Criteria")
    print("4.Would you like to guide us in helping you prepare for the placement season")

    choice=input("Enter choice number: ")
    # add ui option to click and select isme

    if choice == "1":
        query_type="placement"
    elif choice == "2":
        query_type="guidelines"
    elif choice == "3":
        query_type="eligibility"
    else:
        query_type="general"
    

    print(f"\n{name} you can ask your query now !!")
    print("type 'exit' to end the conversation")

    while True:
        user_query=input("\nAsk : ")

        if(user_query.lower()=="exit"):
            print("Goodbye !!")
            break

        full_query=query_type + " " + user_query

        response=app.invoke({"user_query": full_query})
        print(response.get("response"))

if __name__ == "__main__":
    start_helpdesk()






# while True:
#     query=input("Ask your query :")
#     response = router_node(query)
#     print(response)
