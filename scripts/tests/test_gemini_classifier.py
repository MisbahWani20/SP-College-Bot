import sys
import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

sys.path.insert(0, PROJECT_ROOT)

from chatbot.gemini_service import classify_question


questions = [
    "What is BSc IT?",
    "What is the fee for BSc IT?",
    "What is machine learning?",
    "Explain quantum computing in simple words.",
    "Which colleges offer BSc IT?",
    "What is the admission process?",
    "Who is the Vice Chancellor?",
    "Show latest notifications."
]


for question in questions:

    print("\n==============================")
    print("QUESTION:", question)

    result = classify_question(question)

    print("GEMINI CLASSIFICATION:")
    print(result)