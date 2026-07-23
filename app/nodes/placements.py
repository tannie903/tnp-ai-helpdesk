from app.state import HelpdeskState
from app.agent.lllmclient import get_llm
from app.rag.retriever_singleton import get_shared_retriever


def placementstats_node(state: HelpdeskState):
    retriever = get_shared_retriever(k=4)

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
You are a placement statistics assistant for a college TNP cell.

Review the chat history below for context (e.g. if the user is following up on a
company/role mentioned earlier without repeating its name).

---
[Chat History]
{history_str}
---

Use ONLY the context below to answer. If the numbers or company aren't in the
context, say clearly that you don't have that data — do not guess or make up numbers.

Context:
{context}

Question: {user_query}

Answer concisely, citing specific numbers/companies from the context where relevant.
"""

    result = llm.invoke(prompt)
    response = result.content if hasattr(result, "content") else str(result)

    return {"response": response.strip()}