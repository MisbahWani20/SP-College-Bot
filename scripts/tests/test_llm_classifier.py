from chatbot.llm_service import classify_with_llm


questions = [
    # Programme
    "What is BSc IT?",
    "What is the fee for BSc IT?",
    "What is the eligibility for BEd?",
    "Tell me about MSc Data Science",
    "Which colleges offer BSc IT?",

    # General admission
    "What is the admission process?",
    "How can I apply for admission?",
    "What documents are required for admission?",
    "When does admission start?",
    "What is the application fee?",

    # Programme admission
    "What is the admission process for BSc IT?",
    "What documents are required for BSc IT admission?",

    # College
    "Who is the principal of Amar Singh College?",
    "What facilities are available at SP College?",

    # University
    "Who is the Vice Chancellor?",
    "When was Cluster University Srinagar established?",

    # PDF
    "Show me the prospectus",
    "What does the ordinance say?",
    "What is on page 20 of the prospectus?",

    # Website
    "What are the latest notifications?",
    "Show latest results",
    "Are there any new job notifications?",
    "What is the latest examination notice?",

    # General AI
    "What is machine learning?",
    "Explain quantum computing",
    "What is artificial intelligence?",
    "Explain blockchain",

    # Unknown
    "Hello",
    "Tell me something",
]


for question in questions:

    print("\n" + "=" * 70)
    print("QUESTION:", question)

    result = classify_with_llm(question)

    print("CLASSIFICATION:", result)