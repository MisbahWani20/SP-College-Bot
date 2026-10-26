import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(
    api_key=GROQ_API_KEY
)
def ask_groq(question):
    if not GROQ_API_KEY:
        print("Groq API key not found.")
        return None
    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI assistant for Cluster University "
                        "Srinagar. Answer clearly and naturally. "
                        "Do not invent official Cluster University "
                        "information such as programmes, fees, admission "
                        "dates, eligibility, notifications, or results."
                    )
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            temperature=0.3
        )
        if response and response.choices:
            answer = response.choices[0].message.content
            if answer:
                return answer.strip()
    except Exception as error:
        print("Groq error:", error)
    return None