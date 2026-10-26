from chatbot.response_builder import build_response


questions = [
    # Programme
    "What is BSc IT?",
    "What is the fee for BSc IT?",
    "What is the eligibility for BEd?",
    "Tell me about MSc Data Science",

    # General admission
    "What is the admission process?",
    "How can I apply for admission?",
    "What documents are required for admission?",
    "When does admission start?",
    "What is the application fee?",

    # Programme admission
    "What is the admission process for BSc IT?",
    "What is the selection process for BSc IT?",

    # College
    "Who is the principal of Amar Singh College?",
    "What facilities are available at SP College?",

    # University
    "Who is the Vice Chancellor?",
    "When was Cluster University Srinagar established?",

    # PDF
    "Show me the prospectus",
    "What is on page 20 of the prospectus?",

    # Website
    "What are the latest notifications?",
    "Show latest results",
    "Are there any new job notifications?",

    # General AI
    "What is machine learning?",
    "Explain quantum computing",

    # Unknown
    "Tell me something",
]


for question in questions:

    print("\n")
    print("=" * 80)
    print("QUESTION:", question)
    print("=" * 80)

    try:
        answer = build_response(question)

        print("\nANSWER:")
        print(answer)

    except Exception as error:

        print("\nERROR:")
        print(type(error).__name__, error)