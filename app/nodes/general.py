from app.state import HelpdeskState
from app.agent.lllmclient import get_llm


def generalchatbot_node(state: HelpdeskState):
    user_query= state["user_query"]

    llm=get_llm()

    prompt = f"""
You are an expert placement mentor.

Answer the question clearly and concisely.

Question: {user_query}

Format:
- Short definition (2-3 lines)
- 3 key bullet points
- 2 practical tips

Keep the answer under 150 words.
"""

    # try:
    #     response = llm.invoke(prompt).strip()
    # except Exception:
    #     response = "Error generating response. Please try again."

    # return {
    #     "response": response
    # }

    result = llm.invoke(prompt)

    if hasattr(result, "content"):
        response = result.content
    else:
        response = str(result)

    response = response.strip()

    return {
        "response": response
    }
        