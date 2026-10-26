from sentence_transformers import SentenceTransformer, util
from sentence_transformers.util import cos_sim
from chatbot.knowledge_database import get_all_topics
from chatbot.knowledge_database import get_search_records

model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text):

    return model.encode(text)

def calculate_similarity(text1, text2):
    embedding1 = get_embedding(text1)
    embedding2 = get_embedding(text2)

    similarity = cos_sim(embedding1, embedding2)

    return float(similarity[0][0])

def find_best_topic(user_question):
    records = get_search_records()

    best_topic = None
    highest_score = 0

    for topic_id, topic_name, field_name, field_value in records:
        searchable_text = f"{topic_name} {field_name} {field_value}"

        score = calculate_similarity(user_question, searchable_text)

        if score > highest_score:
            highest_score = score
            best_topic = (topic_id, topic_name)

    return best_topic, highest_score
