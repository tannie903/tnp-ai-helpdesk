from dotenv import load_dotenv
import os

from utils.rag_chain import load_vectorstore, get_retriever

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

vectorstore = load_vectorstore(api_key)
retriever = get_retriever(vectorstore, k=3)