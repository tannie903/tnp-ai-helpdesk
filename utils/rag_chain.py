from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings


def load_vectorstore(api_key):
    """
    Loads the pre-built FAISS index from disk.
    Person 2: call this once at app startup, then use .as_retriever()
    on the result to plug into your chain.
    """
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=api_key
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