from dotenv import load_dotenv
from google import genai
import os


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is missing from .env"
    )


client = genai.Client(
    api_key=api_key
)


response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="Explain what RAG means in one sentence."
)


print("\nGemini response:")
print(response.text)