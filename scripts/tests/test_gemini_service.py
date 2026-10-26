from chatbot.gemini_service import ask_gemini


question = "What is Artificial Intelligence?"

result = ask_gemini(question)

print("\n===== GEMINI SERVICE TEST =====")

if result:
    print(result)
else:
    print("Gemini did not return a response.")