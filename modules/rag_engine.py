import streamlit as st
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI

# Initialize API clients exclusively from Streamlit secrets (no .env required)
pinecone_api_key = st.secrets["PINECONE_API_KEY"]
openai_api_key = st.secrets["OPENAI_API_KEY"]

pc = Pinecone(api_key=pinecone_api_key)
# Explicitly initialize OpenAI client to avoid using the older openai.api_key style
openai_client = OpenAI(api_key=openai_api_key)

INDEX_NAME = "athlete-nutrition-rag"

def get_pinecone_index():
    """
    Connects to Pinecone and creates the index if it doesn't exist.
    """
    try:
        existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
        
        if INDEX_NAME not in existing_indexes:
            pc.create_index(
                name=INDEX_NAME,
                dimension=1536, # text-embedding-3-small dimension
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
        return pc.Index(INDEX_NAME)
    except Exception as e:
        print(f"Pinecone connection error: {e}")
        return None

def get_embedding(text):
    """
    Generates embedding for a given text using OpenAI API.
    """
    try:
        response = openai_client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"OpenAI Embedding Error: {e}")
        return None

def get_relevant_papers(profile):
    """
    Queries the Pinecone database to find academic context relevant to the athlete's profile.
    """
    index = get_pinecone_index()
    if not index:
        return ""
        
    sport = profile["sport_type"]
    goal = profile["goal"]
    distance = profile.get("target_distance", "")
    sweat = profile.get("sweat_rate", "")
    
    # Construct a search query reflecting the profile characteristics
    query_text = f"Nutrition, hydration and dietary guidelines for a {sport} athlete aiming for {goal}. Event/Distance: {distance}. Sweat rate: {sweat}."
    query_embedding = get_embedding(query_text)
    
    if not query_embedding:
        return ""
        
    try:
        results = index.query(
            vector=query_embedding,
            top_k=3,
            include_metadata=True
        )
        
        contexts = []
        sources = []
        for match in results.get("matches", []):
            if "metadata" in match and "text" in match["metadata"]:
                contexts.append(match["metadata"]["text"])
                source_name = match["metadata"].get("source", "Bilinmeyen Kaynak")
                if source_name not in sources:
                    sources.append(source_name)
                
        if not contexts:
            return {"text": "", "sources": []}
            
        return {
            "text": "\n\n---\n\n".join(contexts),
            "sources": sources
        }
    except Exception as e:
        print(f"Pinecone query error: {e}")
        return {"text": "", "sources": []}

def add_knowledge_to_index(text_chunks, source_name, batch_size=100):
    """
    Utility function to add documents/chunks to the Pinecone index.
    Not actively used in the app form, but needed when loading PDFs.
    Uploads in batches to avoid Pinecone API size limits.
    """
    index = get_pinecone_index()
    if not index:
        print("Cannot connect to index.")
        return False
        
    vectors_to_upsert = []
    
    for i, chunk in enumerate(text_chunks):
        embedding = get_embedding(chunk)
        if embedding:
            vector_id = f"{source_name}_chunk_{i}"
            # Ensure text metadata is a string and handle potential encoding issues
            text_val = str(chunk)
            # Pinecone metadata limit is 40KB per vector, so usually chunk sizes are fine,
            # but we need to limit the size of the overall upsert payload.
            metadata = {
                "source": source_name,
                "text": text_val
            }
            vectors_to_upsert.append({
                "id": vector_id,
                "values": embedding,
                "metadata": metadata
            })
            
            # Upsert in batches
            if len(vectors_to_upsert) >= batch_size:
                try:
                    index.upsert(vectors=vectors_to_upsert)
                    vectors_to_upsert = [] # Reset batch
                except Exception as e:
                    print(f"Error during batch upsert: {e}")
                    return False
            
    # Upsert remaining vectors
    if vectors_to_upsert:
        try:
            index.upsert(vectors=vectors_to_upsert)
        except Exception as e:
            print(f"Error during final batch upsert: {e}")
            return False
            
    return True
