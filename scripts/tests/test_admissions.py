from chatbot.admission_search import search_admission

questions = [
    "How can I apply for UG admission?",
    "What is the PG admission process?",
    "What documents are required for admission?",
    "What is the application fee for PG admission?",
    "What is the admission fee for UG?",
    "How are students selected for UG admission?",
    "What is the reservation policy?",
    "What is the admission portal?",
    "Is migration certificate required?",
    "What is spot admission?"
]

for question in questions:

    print("\nQUESTION:", question)

    result = search_admission(question)

    if result:
        print("TOPIC:", result["topic"])
        print("APPLICABLE TO:", result["applicable_to"])
    else:
        print("NO RESULT")