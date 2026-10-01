from pathlib import Path
import fitz


# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ABS User Manual
PDF_PATH = PROJECT_ROOT / "rag" / "documents" / "ABS_User_Manual.pdf"


if not PDF_PATH.exists():
    raise FileNotFoundError(
        f"ABS User Manual not found at:\n{PDF_PATH}"
    )


print("========================================")
print("ABS Support AI")
print("PDF Extraction Test")
print("========================================")
print(f"PDF: {PDF_PATH}")


# Open PDF
pdf = fitz.open(PDF_PATH)

print(f"Total pages: {len(pdf)}")


# Read first page
page = pdf[0]

text = page.get_text("text")


print("\n========================================")
print("FIRST PAGE")
print("========================================")

print(text[:3000])


pdf.close()

print("\n========================================")
print("PDF extraction successful")
print("========================================")


