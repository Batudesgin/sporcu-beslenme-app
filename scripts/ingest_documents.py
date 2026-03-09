import os
import sys
from PyPDF2 import PdfReader
from dotenv import load_dotenv

# Add the parent directory to the system path so we can import 'modules'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.rag_engine import add_knowledge_to_index

load_dotenv()

# Configuration
CHUNK_SIZE = 800  # Number of words per chunk
CHUNK_OVERLAP = 100 # Number of words to overlap between chunks
PAPERS_DIR = os.path.join(os.path.dirname(__file__), '..', 'papers')

def extract_text_from_pdf(file_path):
    """Extracts text from a PDF file."""
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
    return text

def extract_text_from_txt(file_path):
    """Extracts text from a TXT file."""
    text = ""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        try:
            # Fallback for Windows encoding
            with open(file_path, 'r', encoding='windows-1254') as f:
                text = f.read()
        except Exception as e2:
             print(f"Error reading TXT {file_path}: {e2}")
    return text

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Splits text into chunks of approximately `chunk_size` words with `overlap`."""
    words = text.split()
    chunks = []
    
    if not words:
        return chunks

    i = 0
    while i < len(words):
        # Take chunk_size words
        chunk_words = words[i:i + chunk_size]
        chunk_text = " ".join(chunk_words)
        chunks.append(chunk_text)
        
        # Move forward by chunk_size - overlap
        if i + chunk_size >= len(words):
            break
        i += (chunk_size - overlap)
        
    return chunks

def process_documents():
    """Main function to read, chunk, and upload documents."""
    if not os.path.exists(PAPERS_DIR):
        print(f"Directory not found: {PAPERS_DIR}")
        print("Creating the directory. Please place your PDFs and TXTs there.")
        os.makedirs(PAPERS_DIR)
        return

    files = os.listdir(PAPERS_DIR)
    documents = [f for f in files if f.lower().endswith(('.pdf', '.txt', '.md'))]
    
    if not documents:
        print(f"No PDF, TXT, or MD files found in {PAPERS_DIR}.")
        print("Please place your files there and run this script again.")
        return

    print(f"Found {len(documents)} document(s) to process in {PAPERS_DIR}.")
    
    for filename in documents:
        file_path = os.path.join(PAPERS_DIR, filename)
        print(f"\nProcessing: {filename}")
        
        # 1. Extract Text
        if filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        else:
            text = extract_text_from_txt(file_path)
            
        if not text.strip():
            print(f"Warning: No text could be extracted from {filename}")
            continue
            
        # 2. Chunk Text
        print(f"Extracted {len(text.split())} words. Chunking...")
        chunks = chunk_text(text)
        print(f"Created {len(chunks)} chunks.")
        
        # 3. Upload to Pinecone (via rag_engine.py)
        source_name = filename.replace('.pdf', '').replace('.txt', '').replace('.md', '').replace(' ', '_')
        print(f"Uploading vectors for '{source_name}' to Pinecone...")
        
        success = add_knowledge_to_index(chunks, source_name)
        if success:
             print(f"[SUCCESS] Processed and uploaded: {filename}")
        else:
             print(f"[FAILED] Could not upload: {filename}")
             
    print("\nAll documents processed!")

if __name__ == "__main__":
    print("Starting Document Ingestion Script...")
    process_documents()
