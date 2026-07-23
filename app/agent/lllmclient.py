import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

def get_llm(model_name: str = "llama-3.1-8b-instant", temperature: float = 0.2):
    """
    Returns an instance of ChatGroq using the specified model.
    Recommended models:
    - llama-3.1-8b-instant (Fast, ideal for intent routing & structured QA)
    - llama-3.3-70b-versatile (More capable, ideal for complex reasoning/RAG)
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from environment variables.")

    llm = ChatGroq(
        model_name=model_name,
        temperature=temperature,
        groq_api_key=api_key
    )
    return llm