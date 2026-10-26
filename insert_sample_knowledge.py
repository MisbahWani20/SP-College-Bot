from chatbot.knowledge_database import add_topic, add_field, add_value

topic_id = add_topic(
    "Cluster University Srinagar",
    "University",
    "General information about Cluster University Srinagar."
)

field_id = add_field(
    topic_id,
    "Established"
)

add_value(
    field_id,
    "2016",
    "Official Cluster University Srinagar Website",
    "https://www.cusrinagar.edu.in/Home/AboutCUS",
    "2026-07-22"
)

print("Sample Knowledge Inserted Successfully!")