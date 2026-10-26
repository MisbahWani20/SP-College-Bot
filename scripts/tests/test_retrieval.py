from chatbot.knowledge_database import get_topic, get_topic_fields

topic = get_topic("Cluster University Srinagar")

if topic:

    topic_id = topic[0]

    print("Topic Found:")
    print(topic)

    print("\nKnowledge:\n")

    fields = get_topic_fields(topic_id)

    for field in fields:

        print(field)

else:

    print("Topic Not Found")