import re
from app.state import HelpdeskState
from app.agent.lllmclient import get_llm
from app.rag.retriever_singleton import get_shared_retriever
from utils.eligibility import get_company_names


def _clean_text(text: str) -> str:
    """Strips category keywords prepended by UI wrappers and normalizes whitespace."""
    if not text:
        return ""
    text = text.lower().strip()
    return re.sub(r'^(eligibility|guideline|guidelines|placement|placements|general)\s+', '', text).strip()


def _extract_cgpa(text: str):
    if not text:
        return None

    clean_text = _clean_text(text)

    # Scans for any standalone CGPA value between 0.0 and 10.0
    # Works for: "7.5", "eligibility 7.5", "my cgpa is 7.5", "8.2 cgpa"
    matches = re.findall(r'\b(10(?:\.0{1,2})?|[0-9](?:\.[0-9]{1,2})?)\b', clean_text)

    for num in matches:
        try:
            val = float(num)
            if 0.0 <= val <= 10.0:
                return val
        except ValueError:
            continue

    return None


def _get_role_and_content(item):
    """Normalizes both dict and tuple chat history items."""
    if isinstance(item, (tuple, list)):
        return item[0], item[1]
    elif isinstance(item, dict):
        role = "human" if item.get("role") in ["user", "human"] else "ai"
        return role, item.get("content", "")
    return "", ""


def eligibility_node(state: HelpdeskState):
    retriever = get_shared_retriever(k=4)
    raw_user_query = state.get("user_query", "")
    user_query = _clean_text(raw_user_query)
    chat_history = state.get("chat_history", [])

    # 1. Extract CGPA: Check current message first, then search history backward
    user_cgpa = _extract_cgpa(raw_user_query)
    if user_cgpa is None:
        for item in reversed(chat_history):
            role, content = _get_role_and_content(item)
            if role == "human":
                found = _extract_cgpa(content)
                if found is not None:
                    user_cgpa = found
                    break

    # 2. Check if current input is just a number / short answer (e.g. "7.5")
    is_bare_answer = (
        _extract_cgpa(raw_user_query) is not None 
        or len(user_query.split()) <= 3
    )

    # 3. If bare answer, pull the last substantive question from history
    retrieval_query = user_query
    if is_bare_answer:
        for item in reversed(chat_history):
            role, content = _get_role_and_content(item)
            cleaned_content = _clean_text(content)
            
            # Find last human question that wasn't a pure CGPA answer
            if role == "human" and _extract_cgpa(cleaned_content) is None and len(cleaned_content.split()) > 3:
                retrieval_query = cleaned_content
                break

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
Use ONLY the context below to find the CGPA cutoff for the company/role asked about in the question.
Compare {user_cgpa} against that cutoff yourself and state clearly: ELIGIBLE or NOT ELIGIBLE,
plus the cutoff you found. If no cutoff is mentioned in the context, say you don't have that data.
Only answer about the specific company/role the student asked about — do not list other companies.

Context:
{context}

Question: {retrieval_query}

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

Question: {retrieval_query}

Answer:
"""

    result = llm.invoke(prompt)
    response = result.content if hasattr(result, "content") else str(result)

    return {"response": response.strip()}
