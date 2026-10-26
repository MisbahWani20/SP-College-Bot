# import os
# from dotenv import load_dotenv
# from groq import Groq

# load_dotenv()

# GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# print("===== GROQ SERVICE TEST =====")

# if not GROQ_API_KEY:
#     print("GROQ_API_KEY not found.")
#     exit()

# client = Groq(api_key=GROQ_API_KEY)

# question = "Explain quantum computing in simple words."

# try:

#     response = client.chat.completions.create(
#         model="qwen/qwen3.8-27b",
#         messages=[
#             {
#                 "role": "user",
#                 "content": question
#             }
#         ],
#         temperature=0.2
#     )

#     answer = response.choices[0].message.content

#     print("\nQUESTION:")
#     print(question)

#     print("\nGROQ ANSWER:")
#     print(answer)

# except Exception as error:

#     print("\nGroq error:")
#     print(error)
from chatbot.groq_service import ask_groq


print("===== GROQ SERVICE TEST =====")

question = "Explain quantum computing in simple words."

answer = ask_groq(question)

print("\nQUESTION:")
print(question)

print("\nGROQ ANSWER:")

if answer:
    print(answer)
else:
    print("No answer received.")