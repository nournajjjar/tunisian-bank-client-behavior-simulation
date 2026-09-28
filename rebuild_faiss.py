from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
import json

# --- Load your documents ---
docs = []
with open("corporate_profiles.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    for item in data:
        docs.append(Document(page_content=item))  # if JSON is array of strings

# --- Create embeddings ---
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# --- Build FAISS index ---
vectorstore = FAISS.from_documents(docs, embeddings)

# --- Save index locally ---
vectorstore.save_local("kb_faiss")
print("✅ FAISS index rebuilt successfully!")
