# behavioral.py
# Single-file behavioral chat + RAG + LangGraph + RL-friendly hooks + Arabic media sentiment
# - Interactive CLI chat (Groq via langchain_groq)
# - RAG over FAISS KB (loads kb_faiss/ or builds from ./docs)
# - LangGraph pipeline (retrieve -> generate -> memorize -> media sentiment)
# - Persistent memory (JSON)
# - Hooks to integrate with Mesa EventEngine

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, TypedDict
from dotenv import load_dotenv

# ---- LangChain / LangGraph ----
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# -------------------------------
# Config & Folders
# -------------------------------
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("❌ OPENAI_API_KEY not found. Put your Groq key in .env as OPENAI_API_KEY")

BASE_DIR = Path(__file__).parent
KB_DIR = BASE_DIR / "kb_faiss"
DOCS_DIR = BASE_DIR / "docs"
MEM_DIR = BASE_DIR / "memory"
MEM_DIR.mkdir(exist_ok=True)

SESSION_MEM_FILE = MEM_DIR / "session_memory.json"
MEDIA_SIGNAL_FILE = MEM_DIR / "media_signal.json"

# -------------------------------
# Chat Model (Groq - LLaMA3)
# -------------------------------
LLM_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
llm = ChatGroq(api_key=API_KEY, model=LLM_MODEL, temperature=0.2, timeout=60)

# -------------------------------
# Memory (persistent JSON)
# -------------------------------
def _load_memory() -> List[Dict[str, str]]:
    if SESSION_MEM_FILE.exists():
        try:
            return json.loads(SESSION_MEM_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

def _save_memory(history: List[Dict[str, str]]) -> None:
    SESSION_MEM_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")

CHAT_HISTORY: List[Dict[str, str]] = _load_memory()

def memorize_interaction(user: str, bot: str) -> None:
    CHAT_HISTORY.append({"user": user, "bot": bot, "ts": time.time()})
    _save_memory(CHAT_HISTORY)

# -------------------------------
# KB / RAG Loader
# -------------------------------
def _build_embeddings():
    model_name = os.getenv("HF_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    return HuggingFaceEmbeddings(model_name=model_name)

def _ingest_docs_to_faiss(docs_dir: Path, kb_dir: Path) -> Optional[FAISS]:
    txts: List[str] = []
    for pat in ("*.txt", "*.md"):
        for p in docs_dir.glob(pat):
            try:
                txts.append(p.read_text(encoding="utf-8"))
            except Exception:
                pass
    if not txts:
        return None
    emb = _build_embeddings()
    vs = FAISS.from_texts(txts, embedding=emb)
    vs.save_local(str(kb_dir))
    return vs

def load_vectorstore() -> Optional[FAISS]:
    if KB_DIR.exists():
        try:
            emb = _build_embeddings()
            vs = FAISS.load_local(str(KB_DIR), embeddings=emb, allow_dangerous_deserialization=True)
            print("✅ Loaded existing FAISS KB from kb_faiss/")
            return vs
        except Exception as e:
            print(f"⚠️ Failed to load existing FAISS KB: {e}")

    if DOCS_DIR.exists():
        vs = _ingest_docs_to_faiss(DOCS_DIR, KB_DIR)
        if vs is not None:
            print("✅ Built FAISS KB automatically from ./docs")
            return vs
        else:
            print("⚠️ ./docs exists but no text files found to build KB")
    else:
        print("⚠️ ./docs folder not found, cannot build KB automatically")

    return None

VECTORSTORE = load_vectorstore()

# -------------------------------
# LangGraph: State + Nodes
# -------------------------------
class GraphState(TypedDict):
    query: str
    history: List[Dict[str, str]]
    context_docs: List[str]
    answer: str
    media_shock: float

def _retrieve(state: GraphState) -> GraphState:
    query = state["query"]
    docs = []
    if VECTORSTORE is not None:
        retriever = VECTORSTORE.as_retriever(search_kwargs={"k": 5})
        results = retriever.invoke(query)
        for r in results:
            docs.append(r.page_content)
    state["context_docs"] = docs
    return state

def _rag_generate(state: GraphState) -> GraphState:
    query = state["query"]
    history = state["history"]
    docs = state.get("context_docs", [])

    system = """
You are a specialized AI assistant for the geomarketing department of BIAT, a Tunisian bank.
Simulate and analyze the behavior of retail and corporate clients in response to strategic changes.
Provide insights to improve bank attractiveness, competitiveness, and customer experience.
Answer questions on churn, adoption, and client behavior with estimates or factors.
Do not answer unrelated questions. Keep responses clear, concise, and actionable.
"""

    ctx = "\n\n".join([f"- {c}" for c in docs]) if docs else "No context available."
    fewshot_mem = "\n".join([f"User: {h['user']}\nAssistant: {h['bot']}" for h in history[-4:]]) if history else ""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("system", "Context:\n" + ctx),
            ("system", "Recent interactions:\n" + fewshot_mem),
            ("user", "{q}")
        ]
    )

    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"q": query})
    state["answer"] = answer
    return state

# -------------------------------
# Arabic sentiment node
# -------------------------------
def _arabic_media_sentiment_scalar(text: str) -> float:
    sys = (
        "أنت محلّل معنويات ومتخصص في التحليلات الجيوماركتينغ لبنك بي آي آي تي (BIAT) في تونس. "
        "قم بإعطاء رقم واحد فقط بين -0.3 و 0.3 يمثل تأثير هذا النص على سلوك العملاء (المتجزئين والشركات) للبنك، "
        "مع مراعاة التغيرات في المنتجات والخدمات والجغرافيا والعروض الرقمية والعوامل الاقتصادية والاجتماعية الخارجية. "
        "القيمة السالبة تعني تأثيراً سلبياً على سلوك العملاء، والقيمة الموجبة تأثيراً إيجابياً. "
        "أجب بالرقم فقط."
    )
    prompt = ChatPromptTemplate.from_messages([("system", sys), ("user", "{t}")])
    chain = prompt | llm | StrOutputParser()
    try:
        raw = chain.invoke({"t": text}).strip()
        val = float(raw)
        return max(-0.3, min(0.3, val))
    except Exception:
        return 0.0

def _media_node(state: GraphState) -> GraphState:
    q = state["query"]
    shock = 0.0
    arabic_hint = any("\u0600" <= ch <= "\u06FF" for ch in q)
    if arabic_hint:
        shock = _arabic_media_sentiment_scalar(q)
    state["media_shock"] = shock
    return state

def _memorize(state: GraphState) -> GraphState:
    q = state["query"]
    a = state.get("answer", "")
    memorize_interaction(q, a)
    write_media_signal(step=None, agent_ctx=None, shock=state.get("media_shock", 0.0))
    return state

# -------------------------------
# Build LangGraph
# -------------------------------
try:
    from langgraph.graph import StateGraph, END
except ModuleNotFoundError:
    raise ModuleNotFoundError("⚠️ Install langgraph: pip install langgraph")

builder = StateGraph(GraphState)
builder.add_node("retrieve", RunnableLambda(_retrieve))
builder.add_node("generate", RunnableLambda(_rag_generate))
builder.add_node("media", RunnableLambda(_media_node))
builder.add_node("memorize", RunnableLambda(_memorize))

builder.set_entry_point("retrieve")
builder.add_edge("retrieve", "generate")
builder.add_edge("generate", "media")
builder.add_edge("media", "memorize")
builder.add_edge("memorize", END)

graph = builder.compile()

# -------------------------------
# Public hooks for Mesa
# -------------------------------
def rag_answer(query: str) -> str:
    state: GraphState = {
        "query": query,
        "history": CHAT_HISTORY,
        "context_docs": [],
        "answer": "",
        "media_shock": 0.0
    }
    out = graph.invoke(state)
    return out["answer"]

def llm_media_shock(arabic_text_or_context: str) -> float:
    return _arabic_media_sentiment_scalar(arabic_text_or_context)

def write_media_signal(step: Optional[int], agent_ctx: Optional[Dict[str, Any]], shock: float) -> None:
    rec = {
        "ts": time.time(),
        "step": step,
        "shock": float(shock),
        "agent_ctx": agent_ctx or {}
    }
    arr = []
    if MEDIA_SIGNAL_FILE.exists():
        try:
            arr = json.loads(MEDIA_SIGNAL_FILE.read_text(encoding="utf-8"))
        except Exception:
            arr = []
    arr.append(rec)
    MEDIA_SIGNAL_FILE.write_text(json.dumps(arr, ensure_ascii=False, indent=2), encoding="utf-8")

# -------------------------------
# CLI Chat
# -------------------------------
HELP = """
Commands:
  /help                 Show help
  /mem                  Show last 5 memory turns
  /clear                Clear session memory
  /buildkb              Build FAISS KB from ./docs if kb_faiss/ missing
  /shock <ar text>      Compute Arabic media shock [-0.3,0.3] and save it
  /exit                 Quit
Just type your question to use RAG + memory.
"""

def _cmd_buildkb():
    if KB_DIR.exists():
        print("ℹ️  kb_faiss/ already exists.")
        return
    if not DOCS_DIR.exists():
        print("❌ ./docs not found. Create it and drop .txt/.md files there.")
        return
    vs = _ingest_docs_to_faiss(DOCS_DIR, KB_DIR)
    if vs is None:
        print("❌ No text files found in ./docs")
    else:
        global VECTORSTORE
        VECTORSTORE = vs
        print("✅ Built FAISS KB from ./docs")

def _cmd_mem():
    for item in CHAT_HISTORY[-5:]:
        print(f"- User: {item['user']}\n  Bot: {item['bot']}\n")

def _cmd_clear():
    global CHAT_HISTORY
    CHAT_HISTORY = []
    _save_memory(CHAT_HISTORY)
    print("🧹 Memory cleared.")

def _interactive_loop():
    print(f"✅ Chat ready (Groq: {LLM_MODEL}). RAG={'ON' if VECTORSTORE else 'OFF (no kb_faiss found)'}")
    print(HELP)
    while True:
        try:
            user = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            break
        if not user:
            continue
        if user.lower() in ("/exit", "exit", "quit"):
            print("👋 Goodbye!")
            break
        if user.lower() in ("/help", "help"):
            print(HELP)
            continue
        if user.lower() in ("/mem", "mem"):
            _cmd_mem()
            continue
        if user.lower() in ("/clear", "clear"):
            _cmd_clear()
            continue
        if user.lower() in ("/buildkb", "buildkb"):
            _cmd_buildkb()
            continue
        if user.lower().startswith("/shock "):
            text = user[7:].strip()
            if not text:
                print("Usage: /shock <arabic-or-english-text>")
                continue
            s = llm_media_shock(text)
            write_media_signal(step=None, agent_ctx={"source": "cli"}, shock=s)
            print(f"🛰️ media_shock = {s:+.3f}  (saved to memory/media_signal.json)")
            continue

        state: GraphState = {
            "query": user,
            "history": CHAT_HISTORY,
            "context_docs": [],
            "answer": "",
            "media_shock": 0.0
        }
        out = graph.invoke(state)
        bot = out["answer"]
        print(f"Bot: {bot}")
        memorize_interaction(user, bot)

# -------------------------------
# Run CLI if script
# -------------------------------
if __name__ == "__main__":
    _interactive_loop()
