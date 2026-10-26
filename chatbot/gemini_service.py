import os
import json
import re
from google import genai
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(
    api_key=GEMINI_API_KEY
)
def ask_gemini(question):
    if not GEMINI_API_KEY:
        print("Gemini API key not found.")
        return None
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=(
                "You are an AI assistant for Cluster University Srinagar. "
                "Answer the user's question clearly and briefly. "
                "Do not invent official university facts, admission dates, "
                "fees, programmes, notifications, or other CUS-specific "
                "information. If you do not know the answer, say so.\n\n"
                f"User question: {question}"
            )
        )

        if response and response.text:
            return response.text.strip()

    except Exception as error:

        print("Gemini error:", error)
        if "429" in str(error):
            print("Gemini quota exceeded.")
        return None


def classify_question(question):

    if not GEMINI_API_KEY:
        print("Gemini API key not found.")
        return None

    prompt = f"""
You are the intent classifier for a university AI chatbot.

Classify the user's question into exactly ONE of these intents:

1. programme
   Questions about a specific academic programme offered by
   Cluster University Srinagar.

   Examples:
   - What is BSc IT?
   - Tell me about BSc IT
   - What is the fee for BSc IT?
   - What is the eligibility for BSc IT?
   - How long is BSc IT?
   - What is MSc Artificial Intelligence and Machine Learning?

2. college
   Questions about a specific constituent college.

3. university
   Questions about Cluster University Srinagar itself,
   its administration, Vice Chancellor, Registrar, mission,
   vision, establishment, etc.

4. admission
   General university admission questions that are not specifically
   asking for details of one particular programme.

5. pdf
   Questions asking about official documents, prospectus, ordinances,
   policies, regulations, brochures, etc.

6. website
   Questions about latest/current notifications, results,
   examination notices, job notifications, official website updates, etc.

7. general_ai
   General educational or technical questions that are NOT asking
   for Cluster University Srinagar-specific information.

   Examples:
   - What is machine learning?
   - Explain quantum computing.
   - What is artificial intelligence?
   - Explain blockchain in simple words.
   - What is cloud computing?

8. unknown
   Questions that do not clearly belong to any of the above.

IMPORTANT:
A technical subject must NOT automatically be classified as a
university programme.

For example:
"What is machine learning?"
must be general_ai.

"What is quantum computing?"
must be general_ai.

"What is BSc IT?"
must be programme.

"What is the fee for BSc IT?"
must be programme.

Return ONLY valid JSON.
Do not use markdown.
Do not include ```json.

The JSON must have exactly these fields:

{{
    "intent": "...",
    "entity": "...",
    "question_type": "..."
}}

User question:
{question}
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        if not response or not response.text:
            return None

        result = response.text.strip()

        # Remove accidental markdown fences if Gemini adds them
        result = re.sub(
            r"^```json\s*|\s*```$",
            "",
            result,
            flags=re.IGNORECASE
        ).strip()

        classification = json.loads(result)

        print("Gemini Classification:", classification)

        return classification

    except Exception as error:
        print("Gemini classification error:", error)
        if "429" in str(error):
            print("Gemini quota exceeded.")
        return None