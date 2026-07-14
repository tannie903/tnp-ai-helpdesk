from app.state import HelpdeskState
from app.agent.lllmclient import get_llm
from app.rag.retriever_singleton import get_shared_retriever



def guidelines_node(state: HelpdeskState):
    retriever = get_shared_retriever(k=3)
    user_query = state["user_query"]

    docs = retriever.invoke(user_query)
    context = "\n\n".join(d.page_content for d in docs)

    llm = get_llm()

    prompt = f"""
You are an assistant explaining interview and OA (Online Assessment) guidelines
set by companies for a college TNP cell.

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