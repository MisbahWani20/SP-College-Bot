from chatbot.nlp import preprocess_text
from chatbot.database import search_question
from chatbot.response_builder import build_response

def get_response(message):
    return build_response(message)
