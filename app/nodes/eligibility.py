import re
from app.state import HelpdeskState
from app.agent.lllmclient import get_llm
from app.rag.retriever_singleton import get_shared_retriever



def _extract_cgpa(text: str):
    match = re.search(r'(\d(?:\.\d{1,2})?)\s*(?:cgpa|gpa)?', text.lower())
    if match:
        val = float(match.group(1))
        if 0 <= val <= 10:
            return val
    return None

def eligibility_node(state: HelpdeskState):
    retriever = get_shared_retriever(k=4)
    user_query = state["user_query"]

    # Prefer a dedicated cgpa field if you add one to state; else parse from query
    user_cgpa = state.get("cgpa")
    user_cgpa = float(user_cgpa) if user_cgpa else _extract_cgpa(user_query)

    docs = retriever.invoke(user_query)
    context = "\n\n".join(d.page_content for d in docs)

    llm = get_llm()

    if user_cgpa is not None:
        prompt = f"""
You are an eligibility-checking assistant for a college TNP cell.

The student's CGPA is {user_cgpa}.

Use ONLY the context below to find the CGPA cutoff for the company/role asked about.
Compare {user_cgpa} against that cutoff yourself and state clearly: ELIGIBLE or NOT ELIGIBLE,
plus the cutoff you found. If no cutoff is mentioned in the context, say you don't have that data.

Context:
{context}

Question: {user_query}

Answer:
"""
    else:
        prompt = f"""
You are an eligibility-checking assistant for a college TNP cell.
The student didn't provide their CGPA. Using ONLY the context below, tell them
the CGPA cutoff for the company/role they asked about, and ask them to share
their CGPA so you can confirm eligibility.

Context:
{context}

Question: {user_query}

Answer:
"""

    result = llm.invoke(prompt)
    response = result.content if hasattr(result, "content") else str(result)

    return {"response": response.strip()}