from chatbot.document_search import (
    load_document,
    search_documents
)

load_document(
    "data/official_data/Prospectus.pdf",
    "Prospectus"
)

load_document(
    "data/official_data/admissionnotificationforpgprogrammes202425.pdf",
    "PG Admission"
)

text, source, score = search_documents(
    "What is the eligibility for MSc Information Technology?"
)

print("\nScore:", score)
print("\nSource:", source)
print("\nAnswer:\n")
print(text)