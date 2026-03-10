"""
Selective ingestion script: uploads ONLY the Turkish food/drink files to Pinecone.
Runs standalone — does NOT depend on Streamlit (st.secrets).
Reads API keys from .env file or environment variables.
"""
import os
import sys
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not PINECONE_API_KEY:
    print("[ERROR] PINECONE_API_KEY bulunamadi. .env dosyasini kontrol edin.")
    sys.exit(1)
if not OPENAI_API_KEY:
    print("[ERROR] OPENAI_API_KEY bulunamadi. .env dosyasini kontrol edin.")
    sys.exit(1)

pc = Pinecone(api_key=PINECONE_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

INDEX_NAME = "athlete-nutrition-rag"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
PAPERS_DIR = os.path.join(os.path.dirname(__file__), '..', 'papers')

TARGET_FILES = [
    "turk_yemekleri.md",
    "turk_icecekleri.md"
]

def get_pinecone_index():
    try:
        existing = [idx["name"] for idx in pc.list_indexes()]
        if INDEX_NAME not in existing:
            pc.create_index(
                name=INDEX_NAME,
                dimension=1536,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
        return pc.Index(INDEX_NAME)
    except Exception as e:
        print(f"Pinecone baglanti hatasi: {e}")
        return None

def get_embedding(text):
    try:
        response = openai_client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"OpenAI Embedding hatasi: {e}")
        return None

def chunk_text(text):
    words = text.split()
    chunks = []
    if not words:
        return chunks
    i = 0
    while i < len(words):
        chunk_words = words[i:i + CHUNK_SIZE]
        chunks.append(" ".join(chunk_words))
        if i + CHUNK_SIZE >= len(words):
            break
        i += (CHUNK_SIZE - CHUNK_OVERLAP)
    return chunks

def upload_chunks(chunks, source_name):
    index = get_pinecone_index()
    if not index:
        return False
    
    vectors = []
    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)
        if embedding:
            vectors.append({
                "id": f"{source_name}_chunk_{i}",
                "values": embedding,
                "metadata": {
                    "source": source_name,
                    "text": str(chunk)
                }
            })
            
            if len(vectors) >= 100:
                try:
                    index.upsert(vectors=vectors)
                    vectors = []
                except Exception as e:
                    print(f"Upsert hatasi: {e}")
                    return False
    
    if vectors:
        try:
            index.upsert(vectors=vectors)
        except Exception as e:
            print(f"Son upsert hatasi: {e}")
            return False
    
    return True

def main():
    for filename in TARGET_FILES:
        file_path = os.path.join(PAPERS_DIR, filename)
        if not os.path.exists(file_path):
            print(f"[SKIP] Dosya bulunamadi: {file_path}")
            continue
        
        print(f"\nIsleniyor: {filename}")
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        if not text.strip():
            print(f"[SKIP] Bos dosya: {filename}")
            continue
        
        words = text.split()
        print(f"{len(words)} kelime cikarildi. Chunk'lara bolunuyor...")
        chunks = chunk_text(text)
        print(f"{len(chunks)} chunk olusturuldu.")
        
        source_name = filename.replace('.md', '').replace(' ', '_')
        print(f"'{source_name}' icin vektorler Pinecone'a yukleniyor...")
        
        success = upload_chunks(chunks, source_name)
        if success:
            print(f"[BASARILI] Yuklendi: {filename}")
        else:
            print(f"[BASARISIZ] Yuklenemedi: {filename}")
    
    print("\nTamamlandi!")

if __name__ == "__main__":
    print("Turk Mutfagi Verisi Yukleme Baslatiliyor...")
    print(f"Pinecone Index: {INDEX_NAME}")
    print(f"Kaynak klasor: {PAPERS_DIR}")
    main()
