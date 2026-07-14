import os
from dotenv import load_dotenv
from utils.rag_chain import load_vectorstore, get_retriever

load_dotenv()
_api_key = os.getenv("GOOGLE_API_KEY")

_vectorstore = None
_retriever = None

def get_shared_retriever(k=3):
    global _vectorstore, _retriever
    if _retriever is None:
        _vectorstore = load_vectorstore(_api_key)
        _retriever = get_retriever(_vectorstore, k=k)
    return _retriever