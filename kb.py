# kb_builder_faiss_full.py
import os
import time
import random
import pickle
from dotenv import load_dotenv
import pandas as pd
from azure.cosmos import CosmosClient, exceptions
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
import requests

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()

# -------------------------------
# Groq Embeddings
# -------------------------------
class GroqEmbeddings:
    def __init__(self, api_key=None, model="llama-3.1-8b-instant", base_url="https://api.groq.com/openai/v1"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("❌ OPENAI_API_KEY environment variable not found")
        self.model = model
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        self.last_call_time = 0
        self.min_call_interval = 0.1  # 100ms
        print(f"✅ Using Groq with model: {model}")

    def embed_documents(self, texts):
        embeddings = []
        for i, text in enumerate(texts):
            if i % 10 == 0:
                print(f"   Embedding document {i+1}/{len(texts)}")
            elapsed = time.time() - self.last_call_time
            if elapsed < self.min_call_interval:
                time.sleep(self.min_call_interval - elapsed)
            embeddings.append(self.embed_query(text))
            self.last_call_time = time.time()
        return embeddings

    def embed_query(self, text):
        text = text[:2000] + "..." if len(text) > 2000 else text
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an embedding generator. Return a dense numerical vector."},
                {"role": "user", "content": f"Create a numerical embedding vector for this text: {text}"}
            ],
            "max_tokens": 100,
            "temperature": 0.1
        }
        for attempt in range(3):
            try:
                resp = requests.post(url, headers=self.headers, json=payload, timeout=30)
                resp.raise_for_status()
                result = resp.json()
                embedding_text = result['choices'][0]['message']['content'].strip()
                return self._text_to_embedding(embedding_text)
            except Exception as e:
                print(f"⚠ Attempt {attempt+1} failed: {str(e)}")
                time.sleep(2)
        return self._create_simple_embedding(text)

    def _text_to_embedding(self, text):
        emb = [ord(c)/1000.0 for c in text[:768]]
        emb.extend([0.0]*(768-len(emb)))
        return emb[:768]

    def _create_simple_embedding(self, text):
        words = text.lower().split()
        emb = [0.0]*768
        for i, w in enumerate(words[:768]):
            emb[i] = hash(w) % 1000 / 1000.0
        return emb

# -------------------------------
# Cosmos DB Loader
# -------------------------------
def load_cosmos_data(database_name, container_names, queries=None):
    endpoint = os.getenv("COSMOS_ENDPOINT")
    key = os.getenv("COSMOS_KEY")
    if not endpoint or not key:
        raise ValueError("❌ Missing COSMOS_ENDPOINT or COSMOS_KEY in .env")

    client = CosmosClient(endpoint, credential=key)
    try:
        db = client.get_database_client(database_name)
    except exceptions.CosmosResourceNotFoundError:
        print(f"❌ Database '{database_name}' not found")
        return {}

    all_containers = [c['id'] for c in db.list_containers()]
    print(f"🔹 Existing containers in '{database_name}': {all_containers}")

    results = {}
    queries = queries or {}

    for container_name in container_names:
        if container_name not in all_containers:
            print(f"⚠ Container '{container_name}' does not exist, skipping")
            continue
        try:
            print(f"   📦 Loading container: {container_name}")
            container = db.get_container_client(container_name)
            query = queries.get(container_name, "SELECT * FROM c")
            items = list(container.query_items(query=query, enable_cross_partition_query=True))
            results[container_name] = pd.DataFrame(items) if items else pd.DataFrame()
            print(f"   ✅ Loaded {len(items)} items from '{container_name}'")
        except Exception as e:
            print(f"   ❌ Error loading container '{container_name}': {str(e)}")
    return results

# -------------------------------
# DataFrame -> Documents
# -------------------------------
def df_to_documents(df, source=""):
    docs = []
    if df.empty:
        return docs
    for _, row in df.iterrows():
        text_parts = []
        for col in df.columns:
            val = row[col]

            # Skip if value is NaN (works for scalar only)
            if pd.api.types.is_scalar(val) and pd.isnull(val):
                continue

            # Handle lists, tuples, sets, or arrays
            if isinstance(val, (list, tuple, set)):
                val_str = ", ".join(str(v) for v in val)
            elif hasattr(val, '__iter__') and not isinstance(val, str):
                val_str = ", ".join(str(v) for v in val)
            else:
                val_str = str(val).strip()

            if val_str:
                text_parts.append(f"{col}: {val_str}")

        if text_parts:
            text = "\n".join(text_parts)
            docs.append(Document(page_content=text, metadata={"source": source}))
    return docs

# -------------------------------
# PDFs
# -------------------------------
def get_pdf_files_from_directory(directory_path="pdfs"):
    if not os.path.exists(directory_path):
        print(f"❌ Directory '{directory_path}' does not exist")
        return []
    pdf_files = [os.path.join(directory_path,f) for f in os.listdir(directory_path) if f.lower().endswith('.pdf')]
    print(f"✅ Found {len(pdf_files)} PDF(s) in '{directory_path}'")
    return pdf_files

# -------------------------------
# Build KB
# -------------------------------
def build_kb(pdf_directory="pdfs", cosmos_configs=None, persist_dir="kb_faiss", sample_size=100):
    embeddings = GroqEmbeddings(model="llama-3.1-8b-instant")
    all_docs = []

    # PDFs
    pdf_files = get_pdf_files_from_directory(pdf_directory)
    for pdf_path in pdf_files:
        try:
            loader = PyPDFLoader(pdf_path)
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = f"PDF/{os.path.basename(pdf_path)}"
            all_docs.extend(docs)
            print(f"📄 Loaded {len(docs)} pages from {os.path.basename(pdf_path)}")
        except Exception as e:
            print(f"❌ Failed loading {pdf_path}: {str(e)}")

    # Cosmos DB
    if cosmos_configs:
        for config in cosmos_configs:
            db_name = config["database"]
            containers = config["containers"]
            queries = config.get("queries", {})
            container_data = load_cosmos_data(db_name, containers, queries)
            for cname, df in container_data.items():
                docs = df_to_documents(df, f"CosmosDB/{cname}")
                all_docs.extend(docs)
                print(f"   ✅ Converted {len(docs)} documents from {cname}")

    if not all_docs:
        print("❌ No documents loaded")
        return

    # Split
    splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=80)
    chunks = splitter.split_documents(all_docs)
    print(f"✂ Split into {len(chunks)} chunks")

    if len(chunks) > sample_size:
        print(f"⚠ Too many chunks ({len(chunks)}), sampling {sample_size}")
        random.seed(42)
        chunks = random.sample(chunks, sample_size)
        print(f"✅ Using {len(chunks)} sample chunks")

    # Embeddings + FAISS
    texts = [c.page_content for c in chunks]
    metadatas = [c.metadata for c in chunks]
    print("🔮 Getting embeddings...")
    embeddings_list = embeddings.embed_documents(texts)

    vectordb = FAISS.from_embeddings(
        text_embeddings=list(zip(texts, embeddings_list)),
        embedding=embeddings,
        metadatas=metadatas
    )

    vectordb.save_local(persist_dir)
    print(f"✅ FAISS KB saved at {persist_dir}, total chunks: {len(chunks)}")

# -------------------------------
# Main
# -------------------------------
if __name__ == "__main__":
    required_vars = ["COSMOS_ENDPOINT", "COSMOS_KEY", "OPENAI_API_KEY"]
    missing = [v for v in required_vars if not os.getenv(v)]
    if missing:
        print(f"❌ Missing environment vars: {missing}")
        exit(1)
    
    print("✅ All required environment variables are set")

    # Automatically discover all Cosmos DB databases and containers, excluding RetailClient & CorporareClient
    endpoint = os.getenv("COSMOS_ENDPOINT")
    key = os.getenv("COSMOS_KEY")
    client = CosmosClient(endpoint, credential=key)
    databases_info = []
    for db in client.list_databases():
        db_name = db['id']
        if db_name in ["RetailClient", "CorporareClient"]:
            print(f"⚠ Skipping database '{db_name}'")
            continue
        database = client.get_database_client(db_name)
        containers = [c['id'] for c in database.list_containers()]
        databases_info.append({"database": db_name, "containers": containers})

    cosmos_configs = databases_info  # Only non-skipped databases

    # Build the KB
    build_kb(
        pdf_directory="pdfs",
        cosmos_configs=cosmos_configs,
        persist_dir="kb_faiss",
        sample_size=50
    )
