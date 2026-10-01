import os
import re
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types


# ========================================
# Paths and configuration
# ========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHUNKS_FILE = PROJECT_ROOT / "rag" / "chunks.txt"
CHROMA_PATH = PROJECT_ROOT / "chroma_db"

COLLECTION_NAME = "abs_manual"

EMBEDDING_MODEL = "gemini-embedding-001"


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
# Check chunks file
# ========================================

if not CHUNKS_FILE.exists():
    raise FileNotFoundError(
        f"Chunks file not found:\n{CHUNKS_FILE}"
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


# Delete old collection if it exists
try:
    chroma_client.delete_collection(
        COLLECTION_NAME
    )
except Exception:
    pass


collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME
)


# ========================================
# Header
# ========================================

print("========================================")
print("ABS Support AI")
print("RAG Ingestion")
print("========================================")

print(f"Chunks file: {CHUNKS_FILE}")
print(f"ChromaDB: {CHROMA_PATH}")
print()


# ========================================
# Read chunks.txt
# ========================================

content = CHUNKS_FILE.read_text(
    encoding="utf-8"
)


# ========================================
# Parse chunks
# ========================================

pattern = re.compile(
    r"========================================\s*"
    r"Chunk ID:\s*(.*?)\s*"
    r"Page:\s*(\d+)\s*"
    r"========================================\s*"
    r"(.*?)(?="
    r"\n========================================"
    r"\s*Chunk ID:|\Z)",
    re.DOTALL,
)

matches = pattern.findall(content)


documents = []
metadatas = []
ids = []


for chunk_id, page_number, text in matches:

    chunk_id = chunk_id.strip()

    page_number = int(page_number)

    text = text.strip()

    if not chunk_id or not text:
        continue

    ids.append(chunk_id)

    documents.append(text)

    metadatas.append(
        {
            "source": "ABS_User_Manual.pdf",
            "page": page_number,
            "chunk_id": chunk_id,
        }
    )


# ========================================
# Show results
# ========================================

print(f"Chunks found: {len(documents)}")


if not documents:
    raise ValueError(
        "No valid chunks were found."
    )


print()

print("First chunk:")
print("----------------------------------------")
print(documents[0][:500])
print("----------------------------------------")

print()


# ========================================
# Generate embeddings
# ========================================

print("Generating Gemini embeddings...")
print()


embeddings = []


for index, document in enumerate(
    documents,
    start=1
):

    response = gemini_client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=document,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT"
        ),
    )

    vector = response.embeddings[0].values

    embeddings.append(vector)

    print(
        f"Embedded {index}/{len(documents)}"
    )


# ========================================
# Store in ChromaDB
# ========================================

print()
print("Storing vectors in ChromaDB...")


collection.add(
    ids=ids,
    documents=documents,
    embeddings=embeddings,
    metadatas=metadatas,
)


# ========================================
# Final result
# ========================================

count = collection.count()


print()

print("========================================")
print("Ingestion complete")
print("========================================")

print(f"Documents stored: {count}")

print(
    f"Embedding dimensions: "
    f"{len(embeddings[0])}"
)

print()

print("ChromaDB collection:")

print(COLLECTION_NAME)

print()