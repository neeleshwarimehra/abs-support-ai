import json
import os
from pathlib import Path
from typing import List

import numpy as np
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types


# --------------------------------------------------
# Configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured")

client = genai.Client(api_key=GEMINI_API_KEY)

EMBEDDING_MODEL = "gemini-embedding-001"
LLM_MODEL = "gemini-3.5-flash-lite"

CHUNKS_FILE = BASE_DIR / "data" / "chunks.json"
EMBEDDINGS_FILE = BASE_DIR / "data" / "embeddings.json"


# --------------------------------------------------
# Load RAG data
# --------------------------------------------------

with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)

with open(EMBEDDINGS_FILE, "r", encoding="utf-8") as f:
    embeddings = json.load(f)


embedding_matrix = np.array(embeddings, dtype=np.float32)


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="ABS Support AI",
    description="RAG API for the ABS/TBS User Manual",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Request / Response models
# --------------------------------------------------

class AskRequest(BaseModel):
    question: str


class Source(BaseModel):
    page: int
    chunk_id: str
    score: float


class AskResponse(BaseModel):
    answer: str
    sources: List[Source]


# --------------------------------------------------
# Utility functions
# --------------------------------------------------

def cosine_similarity(query_vector, matrix):
    query_vector = np.array(query_vector, dtype=np.float32)

    query_norm = np.linalg.norm(query_vector)

    matrix_norms = np.linalg.norm(matrix, axis=1)

    similarities = np.dot(matrix, query_vector) / (
        matrix_norms * query_norm + 1e-10
    )

    return similarities


def get_query_embedding(question: str):
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=question,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY"
        ),
    )

    return response.embeddings[0].values


def generate_answer(question: str, retrieved_chunks):
    context_parts = []

    for item in retrieved_chunks:
        context_parts.append(
            f"""
Page: {item["page"]}
Chunk ID: {item["chunk_id"]}

{item["text"]}
"""
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are ABS Support AI.

You answer questions using ONLY the provided ABS/TBS User Manual context.

Rules:
1. Do not invent information.
2. Do not use outside knowledge.
3. If the answer is not supported by the provided context, say:
   "I couldn't find this information in the ABS User Manual."
4. Keep the answer clear and useful.
5. When possible, mention the relevant page number.
6. Do not claim access to a user's personal booking, profile, payment,
   approval, or account information unless it is explicitly present
   in the provided context.

ABS/TBS USER MANUAL CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:
"""

    response = client.models.generate_content(
        model=LLM_MODEL,
        contents=prompt,
    )

    return response.text.strip()


# --------------------------------------------------
# Routes
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "ABS Support AI API",
        "status": "running",
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "chunks": len(chunks),
        "embedding_dimensions": embedding_matrix.shape[1],
    }


@app.post("/api/ask", response_model=AskResponse)
def ask(request: AskRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:
        # ------------------------------------------
        # 1. Embed user question
        # ------------------------------------------

        query_embedding = get_query_embedding(question)

        # ------------------------------------------
        # 2. Calculate semantic similarity
        # ------------------------------------------

        similarities = cosine_similarity(
            query_embedding,
            embedding_matrix,
        )

        # ------------------------------------------
        # 3. Get Top-K chunks
        # ------------------------------------------

        top_k = min(5, len(chunks))

        top_indices = np.argsort(similarities)[::-1][:top_k]

        retrieved_chunks = []

        for index in top_indices:

            chunk = chunks[index]

            retrieved_chunks.append(
                {
                    "page": int(chunk["page"]),
                    "chunk_id": chunk["chunk_id"],
                    "text": chunk["text"],
                    "score": float(similarities[index]),
                }
            )

        # ------------------------------------------
        # 4. Generate grounded answer
        # ------------------------------------------

        answer = generate_answer(
            question,
            retrieved_chunks,
        )

        # ------------------------------------------
        # 5. Return answer + sources
        # ------------------------------------------

        sources = [
            {
                "page": item["page"],
                "chunk_id": item["chunk_id"],
                "score": round(item["score"], 4),
            }
            for item in retrieved_chunks
        ]

        return {
            "answer": answer,
            "sources": sources,
        }

    except Exception as e:

        print("RAG ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail="Unable to process the question.",
        )
