from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import streamlit as st
import os

def load_vectorstore(api_key=None):
    """
    Loads the pre-built FAISS index from disk.
    """
    # Fetch key from parameter, or Streamlit secrets, or OS environment
    resolved_key = (
        api_key
        or st.secrets.get("GOOGLE_API_KEY")
        or st.secrets.get("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
    )

    if not resolved_key:
        raise ValueError("Google API key was not found in Streamlit Secrets or function arguments!")

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=resolved_key
    )
    
    vectorstore = FAISS.load_local(
        "faiss_index/tnp_index",
        embeddings,
        allow_dangerous_deserialization=True
    )
    return vectorstore


def get_retriever(vectorstore, k=3):
    """
    Wraps the vectorstore into a retriever using MMR for diverse results.
    Person 2: call this after load_vectorstore() to get something
    you can plug straight into a RetrievalQA / LCEL chain.
    """
    return vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": 10, "lambda_mult": 0.7}
    )