import os
from pathlib import Path
from langchain_core.tools import tool
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CHROMA_DB_DIR = BASE_DIR / "data" / "chroma_db"

# Lazy-load vectorstore to avoid initializing embeddings if not used
_vectorstore = None

def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        _vectorstore = Chroma(
            persist_directory=str(CHROMA_DB_DIR),
            embedding_function=embeddings
        )
    return _vectorstore

@tool
def search_journal(query: str, k: int = 3) -> str:
    """Useful to search your private Markdown journal entries for past memories, work updates, thoughts, and plans.
    Use this when the user asks about something they did, what they remember, or their life events.
    """
    try:
        vs = get_vectorstore()
        docs = vs.similarity_search(query, k=k)
        
        if not docs:
            return "Found no relevant journal entries for this query."
            
        results = []
        for i, doc in enumerate(docs):
            source = Path(doc.metadata.get('source', 'Unknown')).name
            results.append(f"[Entry {i+1} from {source}]:\n{doc.page_content}")
            
        return "\n\n".join(results)
    except Exception as e:
        return f"Error accessing the journal vector database: {str(e)}"
