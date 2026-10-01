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

LLM_MODEL = "gemini-3.5-flash-lite"

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
# Get user question
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

print("\nSearching ABS documentation...")

embedding_response = (
    gemini_client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=question,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY"
        ),
    )
)

query_embedding = (
    embedding_response.embeddings[0].values
)


# ========================================
# Retrieve relevant chunks
# ========================================

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=TOP_K,
)


documents = results["documents"][0]

metadatas = results["metadatas"][0]


# ========================================
# Build context
# ========================================

context_parts = []

for index, (
    document,
    metadata,
) in enumerate(
    zip(documents, metadatas),
    start=1,
):

    context_parts.append(
        f"""
SOURCE {index}
Page: {metadata['page']}
Chunk ID: {metadata['chunk_id']}

{document}
"""
    )


context = "\n".join(context_parts)


# ========================================
# RAG prompt
# ========================================

prompt = f"""
You are ABS Support AI.

You answer questions about the
Artist/Talent Booking Software (ABS/TBS)
using ONLY the information provided in
the retrieved ABS User Manual context.

IMPORTANT RULES:

1. Use only the provided context.
2. Do not invent information.
3. If the answer is not available in the
   context, say:

   "I couldn't find this information in
   the ABS User Manual."

4. Give a clear and concise answer.
5. When possible, mention the relevant
   manual page number.
6. Do not answer questions about private
   user data, booking status, payments,
   personal Artist IDs, or other
   transactional information unless the
   provided documentation explicitly
   contains the answer.

USER QUESTION:

{question}

RETRIEVED ABS USER MANUAL CONTEXT:

{context}

Now answer the user's question.
"""


# ========================================
# Generate answer
# ========================================

print("Generating answer...\n")


response = gemini_client.models.generate_content(
    model=LLM_MODEL,
    contents=prompt,
)


answer = response.text


# ========================================
# Display answer
# ========================================

print("========================================")
print("ABS SUPPORT AI")
print("========================================")

print("\nAnswer:")
print("----------------------------------------")

print(answer)

print("\n----------------------------------------")

print("Sources:")

seen_pages = set()

for metadata in metadatas:

    page = metadata["page"]

    if page not in seen_pages:

        print(
            f"- ABS User Manual, page {page}"
        )

        seen_pages.add(page)


print("\n========================================")
print("RAG answer complete")
print("========================================")
