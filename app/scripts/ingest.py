import os
import argparse
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Define paths relative to the project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
JOURNAL_DIR = BASE_DIR / "data" / "journal"
CHROMA_DB_DIR = BASE_DIR / "data" / "chroma_db"

def ingest_journal():
    print(f"Reading journal entries from {JOURNAL_DIR}...")
    
    # Ensure directories exist
    os.makedirs(JOURNAL_DIR, exist_ok=True)
    os.makedirs(CHROMA_DB_DIR, exist_ok=True)
    
    # Load all markdown files
    loader = DirectoryLoader(str(JOURNAL_DIR), glob="**/*.md", loader_cls=TextLoader)
    try:
        documents = loader.load()
    except Exception as e:
        print(f"Error loading documents: {e}")
        return
    
    if not documents:
        print("No markdown files found in data/journal/. Please add some.")
        return
        
    print(f"Loaded {len(documents)} journal entries.")
    if len(documents) > 0:
        print(f"First doc length: {len(documents[0].page_content)}")
        print(f"First doc preview: {documents[0].page_content[:100]}")
    
    # Split text into manageable chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")
    
    # Initialize local HF Embeddings (downloads on first run)
    print("Initializing local HuggingFace Embeddings (all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Create and persist Vector Store
    print(f"Storing embeddings in ChromaDB at {CHROMA_DB_DIR}...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_DB_DIR)
    )
    
    print("Ingestion complete! Database is ready to be queried by the Journal Worker.")

if __name__ == "__main__":
    ingest_journal()
