import os
from dotenv import load_dotenv
from utils.rag_chain import load_vectorstore, get_retriever

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

vectorstore = load_vectorstore(api_key)
retriever = get_retriever(vectorstore, k=3)

result = retriever.invoke("What kind of questions does a Product company ask in OA?")
for doc in result:
    print(doc.page_content[:200])
    print("---")