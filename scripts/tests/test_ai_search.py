from chatbot.semantic_search import find_best_topic

question = input("Ask your question: ")

topic, score = find_best_topic(question)

print("\nBest Topic Found:")
print(topic)

print("\nSimilarity Score:")
print(score)