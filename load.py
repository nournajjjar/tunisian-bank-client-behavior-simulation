from langchain_community.vectorstores import FAISS

def load_kb(kb_path):
    # Use OpenAIEmbeddings or your custom embeddings class
    from langchain_community.embeddings import OpenAIEmbeddings
    embeddings = OpenAIEmbeddings()  
    vectordb = FAISS.load_local(
        kb_path,
        embeddings=embeddings,
        allow_dangerous_deserialization=True  # <-- add this
    )
    return vectordb
