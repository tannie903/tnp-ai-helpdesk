from app.state import HelpdeskState
from app.agent.lllmclient import get_llm
from app.rag.retriever_singleton import get_shared_retriever


def guidelines_node(state: HelpdeskState):
    retriever = get_shared_retriever(k=3)
    user_query = state["user_query"]
    chat_history = state.get("chat_history", [])

    history_str = ""
    for role, content in chat_history:
        speaker = "User" if role == "human" else "Assistant"
        history_str += f"{speaker}: {content}\n"

    docs = retriever.invoke(user_query)
    context = "\n\n".join(d.page_content for d in docs)

    llm = get_llm()

    prompt = f"""
You are an assistant explaining interview and OA (Online Assessment) guidelines
set by companies for a college TNP cell.

Review the chat history below for context (e.g. if the user is following up on a
company mentioned earlier without repeating its name).

---
[Chat History]
{history_str}
---

Use ONLY the context below. If the guideline isn't covered in the context,
say you don't have that information rather than guessing.

Context:
{context}

Question: {user_query}

Answer in a short, clear, rule-like format (bullet points where relevant).
"""

    result = llm.invoke(prompt)
    response = result.content if hasattr(result, "content") else str(result)

    return {"response": response.strip()}