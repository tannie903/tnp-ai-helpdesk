from app.state import HelpdeskState
from app.agent.lllmclient import get_llm


def generalchatbot_node(state: HelpdeskState):
    user_query = state.get("user_query", "")
    chat_history = state.get("chat_history", [])

    history_str = ""
    for role, content in chat_history:
        speaker = "User" if role == "human" else "Assistant"
        history_str += f"{speaker}: {content}\n"

    llm = get_llm()

    prompt = f"""
You are an expert placement mentor. 

Review the chat history below for context before answering the user's latest question.

---
[Chat History]
{history_str}
---

Question: {user_query}

Format:
- Short definition (2-3 lines)
- 3 key bullet points
- 2 practical tips

Keep the answer under 150 words.
"""

    result = llm.invoke(prompt)

    if hasattr(result, "content"):
        response = result.content
    else:
        response = str(result)

    response = response.strip()

    return {
        "response": response
    }