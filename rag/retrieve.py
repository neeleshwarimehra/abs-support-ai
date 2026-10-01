import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types


# ========================================
# Configuration
# ========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHROMA_PATH = PROJECT_ROOT / "chroma_db"

COLLECTION_NAME = "abs_manual"

EMBEDDING_MODEL = "gemini-embedding-001"

TOP_K = 5


# ========================================
# Load environment variables
# ========================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is missing from .env"
    )


# ========================================
# Initialize Gemini
# ========================================

gemini_client = genai.Client(
    api_key=api_key
)


# ========================================
# Initialize ChromaDB
# ========================================

chroma_client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)

collection = chroma_client.get_collection(
    name=COLLECTION_NAME
)


# ========================================
# User question
# ========================================

question = input(
    "\nAsk a question about the ABS User Manual: "
).strip()


if not question:
    raise ValueError(
        "Question cannot be empty."
    )


# ========================================
# Create query embedding
# ========================================

print("\nCreating query embedding...")

response = gemini_client.models.embed_content(
    model=EMBEDDING_MODEL,
    contents=question,
    config=types.EmbedContentConfig(
        task_type="RETRIEVAL_QUERY"
    ),
)

query_embedding = response.embeddings[0].values


# ========================================
# Search ChromaDB
# ========================================

print("Searching ChromaDB...\n")

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=TOP_K,
)


# ========================================
# Display results
# ========================================

print("========================================")
print("RETRIEVAL RESULTS")
print("========================================")

documents = results["documents"][0]

metadatas = results["metadatas"][0]

distances = results["distances"][0]


for index, (
    document,
    metadata,
    distance,
) in enumerate(
    zip(
        documents,
        metadatas,
        distances,
    ),
    start=1,
):

    print()
    print(
        f"Result #{index}"
    )

    print("----------------------------------------")

    print(
        f"Page: {metadata['page']}"
    )

    print(
        f"Chunk ID: {metadata['chunk_id']}"
    )

    print(
        f"Distance: {distance:.4f}"
    )

    print("----------------------------------------")

    print(document[:1500])


print()
print("========================================")
print("Retrieval complete")
print("========================================")
