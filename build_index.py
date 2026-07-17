import os
import time
import pandas as pd
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

if os.path.exists("faiss_index/tnp_index/index.faiss"):
    print("FAISS index already exists. Delete the faiss_index/tnp_index folder if you want to rebuild it.")
    exit()

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
    print(doc.page_content[:300])
    print(f"Source: {doc.metadata.get('source')}")
