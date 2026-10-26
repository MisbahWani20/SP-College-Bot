from chatbot.llm_service import classify_with_llm

questions = [
    "What is BSc IT?",
    "What is the fee for BSc IT?",
    "How long is BSc IT?",
    "What is the admission process for BSc IT?",
    "Which college offers BSc IT?",
    "What documents do I need for admission?",
    "When will admissions open?",
    "Show me the latest admission notifications.",
    "Tell me about Amar Singh College.",
    "Who is the Vice Chancellor of Cluster University Srinagar?",
    "Show me the prospectus.",
    "What is machine learning?",
    "What is Kashmir University?",
    "Tell me about MSc Data Science.",
    "How many years is Integrated BSc BEd?",
    "What is the selection process?",
]

for question in questions:
    print("\n" + "=" * 70)
    print("QUESTION:", question)

    result = classify_with_llm(question)

    print("CLASSIFICATION:")
    print(result)