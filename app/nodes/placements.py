from app.state import HelpdeskState
from app.agent.lllmclient import get_llm
from app.rag.retriever_singleton import get_shared_retriever
from app.tools.placement_stats import is_aggregate_query, compute_answer


def placementstats_node(state: HelpdeskState):
    user_query = state["user_query"]
    chat_history = state.get("chat_history", [])

    history_str = ""
    for role, content in chat_history:
        speaker = "User" if role == "human" else "Assistant"
        history_str += f"{speaker}: {content}\n"

    # --- STEP 1: Decide whether this is an aggregate/calculation query ---
    if is_aggregate_query(user_query):
        # Ground truth comes from pandas — exact, deterministic, no top-k truncation
        computed_fact = compute_answer(user_query)

        # For long, multi-line breakdowns (full company lists), return the
        # computed text directly. Handing long text to a small/fast LLM
        # "just to phrase nicely" risks it truncating, summarizing, or
        # silently dropping rows and the final total line.
        if computed_fact.count("\n") > 5:
            return {"response": computed_fact.strip()}

        # For short, single-fact answers (a total, an average, a single
        # highest/lowest), it's safe to let the LLM phrase it conversationally.
        llm = get_llm()
        prompt = f"""
You are a placement statistics assistant for a college TNP cell.

The following fact has already been computed exactly from the full dataset.
Do not recalculate, do not change any numbers, do not add numbers that are
not present below. Simply present it clearly and conversationally, using
the chat history only for tone/context (e.g. addressing a follow-up).

---
[Chat History]
{history_str}
---

[Computed Fact]
{computed_fact}

Question: {user_query}

Answer using ONLY the computed fact above.
"""
        result = llm.invoke(prompt)
        response = result.content if hasattr(result, "content") else str(result)
        return {"response": response.strip()}

    # --- STEP 2: Otherwise, treat as a qualitative/lookup query -> existing RAG path ---
    retriever = get_shared_retriever(k=4)
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