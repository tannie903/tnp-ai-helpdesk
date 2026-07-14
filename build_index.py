import os
if os.path.exists("faiss_index/tnp_index/index.faiss"):
    print("FAISS index already exists. Delete the faiss_index/tnp_index folder if you want to rebuild it.")
    exit()
# test_retriever.py
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
import pandas as pd
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# ---------- 1. Load PDF documents ----------
pdf_loader = DirectoryLoader(
    "data/documents/",
    glob="**/*.pdf",
    loader_cls=PyPDFLoader
)
pdf_documents = pdf_loader.load()
print(f"Loaded {len(pdf_documents)} PDF page(s)")

# ---------- 2. Chunk PDF documents ----------
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
    separators=["\n\n", "\n", ".", " "]
)
pdf_chunks = splitter.split_documents(pdf_documents)
print(f"Created {len(pdf_chunks)} chunks from PDF")
print(f"\n=== ALL {len(pdf_chunks)} PDF CHUNKS ===")
for i, chunk in enumerate(pdf_chunks):
    print(f"\n--- Chunk {i+1} (source: {chunk.metadata.get('source')}) ---")
    print(chunk.page_content)

# ---------- 3. Load Excel — one row = one Document ----------
excel_path = "data/TNP_Placement_Data.xlsx"
excel_sheets = pd.read_excel(excel_path, sheet_name=None, header=3)

excel_documents = []
for sheet_name, df in excel_sheets.items():
    df = df.dropna(how="all")
    for _, row in df.iterrows():
        row_text = ", ".join(f"{col}: {val}" for col, val in row.items() if pd.notna(val))
        content = f"[{sheet_name}] {row_text}"
        excel_documents.append(
            Document(page_content=content, metadata={"source": excel_path, "sheet": sheet_name})
        )

print(f"Created {len(excel_documents)} documents from Excel rows")


# ---------- 4. Combine everything ----------
all_documents = pdf_chunks + excel_documents
print(f"Total documents going into FAISS: {len(all_documents)}")

# ---------- 5. Embeddings ----------
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=api_key
)

# ---------- 6. Build FAISS index in batches to respect free-tier rate limits ----------
import time

BATCH_SIZE = 80  # stay safely under the 100/minute free-tier limit
vectorstore = None

for i in range(0, len(all_documents), BATCH_SIZE):
    batch = all_documents[i:i + BATCH_SIZE]
    print(f"Embedding batch {i // BATCH_SIZE + 1} ({len(batch)} documents)...")

    if vectorstore is None:
        vectorstore = FAISS.from_documents(batch, embeddings)
    else:
        vectorstore.add_documents(batch)

    if i + BATCH_SIZE < len(all_documents):
        print("Waiting 60s to respect free-tier rate limit...")
        time.sleep(60)

vectorstore.save_local("faiss_index/tnp_index")
print("FAISS index saved to faiss_index/tnp_index")

# ---------- 7. Quick sanity test ----------
query = "What is the eligibility CGPA for Microsoft?"
results = vectorstore.similarity_search(query, k=3)
for i, doc in enumerate(results):
    print(f"\n--- Result {i+1} ---")
    print(doc.page_content)
    print(f"Source: {doc.metadata.get('source')}")

# ---------- 7. Configure retriever ----------
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 3,          # final number of chunks returned
        "fetch_k": 10,   # considers top 10, then picks 3 diverse ones
        "lambda_mult": 0.7  # 0 = max diversity, 1 = max relevance
    }
)

# ---------- 8. Test the retriever ----------
test_queries = [
    "What is the eligibility CGPA for Microsoft?",
    "What kind of questions does a Product company ask in OA?",
    "Can I sit for a company after rejecting an offer?"
]

for q in test_queries:
    print(f"\n=== Query: {q} ===")
    results = retriever.invoke(q)
    for i, doc in enumerate(results):
        print(f"\n--- Result {i+1} ---")
        print(doc.page_content[:300])
        print(f"Source: {doc.metadata.get('source')}")


# temporarily added
query2 = "What kind of questions does a Product company ask in OA?"
results2 = vectorstore.similarity_search(query2, k=3)
for i, doc in enumerate(results2):
    print(f"\n--- PDF Result {i+1} ---")
    print(doc.page_content)
    print(f"Source: {doc.metadata.get('source')}")

query3 = "Product Companies AWS Microsoft Adobe DSA questions"
results3 = vectorstore.similarity_search(query3, k=6)
for i, doc in enumerate(results3):
    print(f"\n--- Result {i+1} ---")
    print(doc.page_content[:300])
    print(f"Source: {doc.metadata.get('source')}")

