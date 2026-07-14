from app.state import HelpdeskState
from app.agent.lllmclient import get_llm
from app.rag.retriever_singleton import get_shared_retriever


def placementstats_node(state: HelpdeskState):
    retriever = get_shared_retriever(k=4)
    
    user_query = state["user_query"]

    docs = retriever.invoke(user_query)
    context = "\n\n".join(d.page_content for d in docs)

    llm = get_llm()

    prompt = f"""
You are a placement statistics assistant for a college TNP cell.

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