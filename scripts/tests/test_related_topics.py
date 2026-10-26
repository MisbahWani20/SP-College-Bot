from chatbot.semantic_search import find_related_topics

topics = find_related_topics(
    "How can I get admission in MSc Information Technology?"
)

for topic, score in topics:
    print(topic[1], score)