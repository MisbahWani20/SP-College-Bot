import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
from chatbot.sp_college_search import search_sp_college

questions = [
    "Where is SP College located?",
    "What is the phone number of SP College?",
    "What is the official email address?",
    "Where can I find college announcements?",
    "Where can I find the admission brochure?",
    "Tell me the exact hostel admission deadline."
]

for question in questions:
    print("\nQuestion:", question)

    results = search_sp_college(question)

    if not results:
        print("No relevant saved information found.")
        continue

    result = results[0]

    print("Title:", result["title"])
    print("Answer text:", result["chunk_text"])
    print("Official source:", result["source_url"])
