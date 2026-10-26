import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai


# Find project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Load .env
load_dotenv(PROJECT_ROOT / ".env")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: GEMINI_API_KEY was not found.")
    exit()

print("Gemini API key found.")

# Create Gemini client
client = genai.Client(api_key=api_key)

try:
    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input="What is Artificial Intelligence? Explain in two sentences."
    )

    print("\n===== GEMINI RESPONSE =====")
    print(interaction.output_text)

except Exception as error:
    print("\n===== GEMINI ERROR =====")
    print(error)