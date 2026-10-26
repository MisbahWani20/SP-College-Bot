from chatbot.response_builder import build_response

while True:

    question = input("\nAsk: ")

    if question.lower() == "exit":
        break

    print("\n")
    print(build_response(question))
    