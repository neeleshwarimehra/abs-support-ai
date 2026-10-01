from pathlib import Path
import re

import pymupdf


# ========================================
# Configuration
# ========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PDF_PATH = (
    PROJECT_ROOT
    / "rag"
    / "documents"
    / "ABS_User_Manual.pdf"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "rag"
    / "chunks.txt"
)

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200


# ========================================
# Validate PDF
# ========================================

if not PDF_PATH.exists():
    raise FileNotFoundError(
        f"PDF not found:\n{PDF_PATH}"
    )


# ========================================
# Text cleaning
# ========================================

def clean_text(text: str) -> str:
    """
    Clean extracted PDF text.
    """

    # Replace multiple spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    return text.strip()


# ========================================
# Create chunks
# ========================================

def create_chunks(text: str):
    """
    Split text into overlapping chunks.
    """

    chunks = []

    start = 0

    while start < len(text):

        end = start + CHUNK_SIZE

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


# ========================================
# Read PDF
# ========================================

print("========================================")
print("ABS Support AI")
print("PDF Chunking")
print("========================================")

print(f"PDF: {PDF_PATH}")


pdf = pymupdf.open(PDF_PATH)

print(f"Total pages: {len(pdf)}")


all_chunks = []


# ========================================
# Process every page
# ========================================

for page_number, page in enumerate(pdf, start=1):

    text = page.get_text("text")

    text = clean_text(text)

    if not text:
        continue

    page_chunks = create_chunks(text)

    for chunk_number, chunk in enumerate(
        page_chunks,
        start=1
    ):

        all_chunks.append(
            {
                "chunk_id": (
                    f"page_{page_number}"
                    f"_chunk_{chunk_number}"
                ),
                "page": page_number,
                "text": chunk,
            }
        )


pdf.close()


# ========================================
# Save chunks
# ========================================

with open(
    OUTPUT_PATH,
    "w",
    encoding="utf-8"
) as file:

    for item in all_chunks:

        file.write(
            "\n========================================\n"
        )

        file.write(
            f"Chunk ID: {item['chunk_id']}\n"
        )

        file.write(
            f"Page: {item['page']}\n"
        )

        file.write(
            "========================================\n"
        )

        file.write(
            item["text"]
        )

        file.write("\n")


# ========================================
# Results
# ========================================

print()
print("========================================")
print("Chunking complete")
print("========================================")

print(f"Total chunks: {len(all_chunks)}")

print(f"Output: {OUTPUT_PATH}")


# Show first chunk
if all_chunks:

    first = all_chunks[0]

    print()
    print("========================================")
    print("FIRST CHUNK")
    print("========================================")

    print(f"Chunk ID: {first['chunk_id']}")
    print(f"Page: {first['page']}")

    print()
    print(first["text"][:1500])
