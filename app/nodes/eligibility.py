import re
from app.state import HelpdeskState
from app.agent.lllmclient import get_llm
from app.rag.retriever_singleton import get_shared_retriever
from utils.eligibility import get_company_names


def _extract_cgpa(text: str):
    text = text.lower()
    # number before keyword: "8 cgpa" / "8.5 gpa"
    match = re.search(r'(\d(?:\.\d{1,2})?)\s*(?:cgpa|gpa)', text)
    if not match:
        # keyword before number: "cgpa is 8" / "cgpa: 8.5" / "cgpa of 8"
        match = re.search(r'(?:cgpa|gpa)\D{0,10}?(\d(?:\.\d{1,2})?)', text)
    if match:
        val = float(match.group(1))
        if 0 <= val <= 10:
            return val
    return None


def _extract_company(text: str, companies: list):
    text_low = text.lower()
    for name in companies:
        if name.lower() in text_low:
            return name
    return None


def eligibility_node(state: HelpdeskState):
    retriever = get_shared_retriever(k=4)
    user_query = state["user_query"]
    history = state.get("chat_history", [])
    companies = get_company_names()

    # 1. Try to find CGPA in the current message first
    user_cgpa = _extract_cgpa(user_query)
    # ...and the company name too
    company = _extract_company(user_query, companies)

    # 2. If not found, fall back to scanning chat history (most recent turn first)
    #    so a bare follow-up like "9" or a follow-up company name still resolves.
    if user_cgpa is None:
        for role, content in reversed(history):
            if role == "human":
                found = _extract_cgpa(content)
                if found is not None:
                    user_cgpa = found
                    break

    if company is None:
        for role, content in reversed(history):
            if role == "human":
                found = _extract_company(content, companies)
                if found is not None:
                    company = found
                    break

    # 3. Build the retrieval query from the *resolved* company name, not just
    #    the raw current-turn text — otherwise a follow-up like "9" searches
    #    the vector store for "9" and loses the company context entirely.
    retrieval_query = f"{company} eligibility criteria" if company else user_query

    docs = retriever.invoke(retrieval_query)
    context = "\n\n".join(d.page_content for d in docs)

    llm = get_llm()

    if company is None:
        prompt = f"""
You are an eligibility-checking assistant for a college TNP cell.
The student hasn't mentioned which company/role they're asking about yet.
Using ONLY the context below, ask them which company they mean (and their CGPA,
if they haven't shared it either).

Context:
{context}

Question: {user_query}

Answer:
"""
    elif user_cgpa is not None:
        prompt = f"""
You are an eligibility-checking assistant for a college TNP cell.

The student is asking about {company}. Their CGPA is {user_cgpa}.

Use ONLY the context below to find the CGPA cutoff for {company}.
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
The student is asking about {company} but hasn't shared their CGPA yet.
Using ONLY the context below, tell them the CGPA cutoff for {company},
and ask them to share their CGPA so you can confirm eligibility.

Context:
{context}

Question: {user_query}

Answer:
"""

    result = llm.invoke(prompt)
    response = result.content if hasattr(result, "content") else str(result)

    return {"response": response.strip()}
