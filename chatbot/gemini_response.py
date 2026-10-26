import os
from google import genai

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def get_gemini_response(question):

    try:

        response = client.models.generate_content(
            model="YOUR_WORKING_MODEL",
            contents=question
        )

        return response.text

    except Exception as error:

        print("Gemini error:", error)

        return None