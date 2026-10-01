import json
from pathlib import Path

import chromadb


# ========================================
# Paths
# ========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHROMA_PATH = PROJECT_ROOT / "chroma_db"

DATA_DIR = PROJECT_ROOT / "data"

DATA_DIR.mkdir(
    exist_ok=True
)


# ========================================
# Open ChromaDB
# ========================================

client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)

collection = client.get_collection(
    name="abs_manual"
)


# ========================================
# Get all records
# ========================================

data = collection.get(
    include=[
        "documents",
        "embeddings",
        "metadatas",
    ]
)


documents = data["documents"]

embeddings = data["embeddings"]

metadatas = data["metadatas"]


# ========================================
# Create chunk records
# ========================================

chunks = []

for document, metadata in zip(
    documents,
    metadatas
):

    chunks.append(
        {
            "text": document,
            "page": int(metadata["page"]),
            "chunk_id": metadata["chunk_id"],
            "source": metadata["source"],
        }
    )


# ========================================
# Convert embeddings to normal Python lists
# ========================================

embeddings = [
    embedding.tolist()
    if hasattr(embedding, "tolist")
    else list(embedding)
    for embedding in embeddings
]


# ========================================
# Save chunks
# ========================================

chunks_path = DATA_DIR / "chunks.json"

with open(
    chunks_path,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        chunks,
        f,
        ensure_ascii=False,
        indent=2,
    )


# ========================================
# Save embeddings
# ========================================

embeddings_path = (
    DATA_DIR / "embeddings.json"
)

with open(
    embeddings_path,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        embeddings,
        f,
    )


# ========================================
# Result
# ========================================

print("========================================")
print("RAG data export complete")
print("========================================")

print(
    f"Chunks exported: {len(chunks)}"
)

print(
    f"Embeddings exported: {len(embeddings)}"
)

print(
    f"Embedding dimensions: "
    f"{len(embeddings[0])}"
)

print(
    f"Chunk file: {chunks_path}"
)

print(
    f"Embedding file: {embeddings_path}"
)