import json
import math
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types


# ========================================
# Paths
# ========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

CHUNKS_FILE = DATA_DIR / "chunks.json"
EMBEDDINGS_FILE = DATA_DIR / "embeddings.json"


# ========================================
# Configuration
# ========================================

EMBEDDING_MODEL = "gemini-embedding-001"
LLM_MODEL = "gemini-3.5-flash-lite"

TOP_K = 5


# ========================================
# Load environment
# ========================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing")


# ========================================
# Gemini
# ========================================

gemini_client = genai.Client(
    api_key=API_KEY
)


# ========================================
# Load RAG data
# ========================================

with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)


with open(EMBEDDINGS_FILE, "r", encoding="utf-8") as f:
    embeddings = json.load(f)


# ========================================
# Cosine similarity
# ========================================

def cosine_similarity(vector_a, vector_b):
    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(
        sum(a * a for a in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(b * b for b in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0

    return dot_product / (
        magnitude_a * magnitude_b
    )


# ========================================
# Vercel API handler
# ========================================

def handler(request):
    try:

        # --------------------------------
        # CORS
        # --------------------------------

        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
            "Content-Type": "application/json",
        }

        # --------------------------------
        # OPTIONS
        # --------------------------------

        if request.method == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": headers,
                "body": "",
            }

        # --------------------------------
        # Only POST
        # --------------------------------

        if request.method != "POST":
            return {
                "statusCode": 405,
                "headers": headers,
                "body": json.dumps({
                    "error": "Method not allowed"
                }),
            }

        # --------------------------------
        # Read request
        # --------------------------------

        body = request.get_json()

        question = (
            body.get("question", "")
            .strip()
        )

        if not question:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({
                    "error": "Question is required"
                }),
            }

        # --------------------------------
        # Query embedding
        # --------------------------------

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
            embedding_response
            .embeddings[0]
            .values
        )

        # --------------------------------
        # Similarity search
        # --------------------------------

        scored_chunks = []

        for chunk, embedding in zip(
            chunks,
            embeddings
        ):

            score = cosine_similarity(
                query_embedding,
                embedding
            )

            scored_chunks.append(
                {
                    "chunk": chunk,
                    "score": score,
                }
            )

        scored_chunks.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        top_chunks = scored_chunks[:TOP_K]

        # --------------------------------
        # Build context
        # --------------------------------

        context_parts = []

        for index, item in enumerate(
            top_chunks,
            start=1
        ):

            chunk = item["chunk"]

            context_parts.append(
                f"""
SOURCE {index}
Page: {chunk["page"]}
Chunk ID: {chunk["chunk_id"]}

{chunk["text"]}
"""
            )

        context = "\n".join(context_parts)

        # --------------------------------
        # RAG prompt
        # --------------------------------

        prompt = f"""
You are ABS Support AI.

You answer questions about the
Artist/Talent Booking Software (ABS/TBS)
using ONLY the retrieved ABS User Manual
context provided below.

RULES:

1. Use only the provided context.
2. Do not invent information.
3. If the answer cannot be found in the
   provided context, say:

"I couldn't find this information in the
ABS User Manual."

4. Give a clear and concise answer.
5. Mention relevant manual page numbers
   when appropriate.
6. Do not claim access to private user data.
7. Do not invent booking status, payment
   information, Artist IDs, or personal
   account information.

USER QUESTION:

{question}

RETRIEVED CONTEXT:

{context}

Answer the question using only the
retrieved documentation.
"""

        # --------------------------------
        # Generate answer
        # --------------------------------

        response = (
            gemini_client.models.generate_content(
                model=LLM_MODEL,
                contents=prompt,
            )
        )

        answer = response.text.strip()

        # --------------------------------
        # Sources
        # --------------------------------

        sources = []

        seen_pages = set()

        for item in top_chunks:

            chunk = item["chunk"]

            page = chunk["page"]

            if page not in seen_pages:

                sources.append(
                    {
                        "page": page,
                        "source": "ABS User Manual",
                        "score": round(
                            item["score"],
                            4
                        ),
                    }
                )

                seen_pages.add(page)

        # --------------------------------
        # Response
        # --------------------------------

        result = {
            "answer": answer,
            "sources": sources,
        }

        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(result),
        }

    except Exception as error:

        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({
                "error": str(error)
            }),
        }
