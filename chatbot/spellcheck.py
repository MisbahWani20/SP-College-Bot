import sqlite3
import re
from difflib import SequenceMatcher

DATABASE_NAME = "chatbot/knowledge.db"

def get_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def normalize_text(text):
    text = (text or "").lower().strip()
    text = text.replace("&", " and ")
    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )
    text = re.sub(
        r"\s+",
        " ",
        text
    )
    return text.strip()

def get_subjects():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT specialization
        FROM academic_programmes
        WHERE specialization IS NOT NULL
          AND TRIM(specialization) != ''
    """)
    rows = cursor.fetchall()
    conn.close()
    subjects = []
    seen = set()
    for row in rows:
        subject = (
            row["specialization"] or ""
        ).strip()
        key = subject.lower()
        if subject and key not in seen:

            seen.add(key)
            subjects.append(subject)

    return subjects
def similarity(word1, word2):
    return SequenceMatcher(
        None,
        word1.lower(),
        word2.lower()
    ).ratio()

def word_similarity(user_word, subject_word):

    return similarity(
        user_word,
        subject_word
    )

def calculate_subject_score(user_text, subject):

    user_text = normalize_text(user_text)
    subject = normalize_text(subject)

    if not user_text or not subject:
        return 0
    if user_text == subject:
        return 1.0
    user_words = user_text.split()
    subject_words = subject.split()

    if (
        len(user_words) == 1
        and len(subject_words) == 1
    ):
        return similarity(
            user_words[0],
            subject_words[0]
        )

    matched_scores = []

    for user_word in user_words:

        best_word_score = 0

        for subject_word in subject_words:

            score = similarity(
                user_word,
                subject_word
            )

            if score > best_word_score:
                best_word_score = score
        matched_scores.append(
            best_word_score
        )
    if not matched_scores:
        return 0
    if min(matched_scores) < 0.70:
        return 0
    return (
        sum(matched_scores)
        / len(matched_scores)
    )
def abbreviation_match(user_text, subject):
    user_text = normalize_text(user_text)
    subject = normalize_text(subject)
    abbreviations = {
        "chem": "chemistry",
        "phy": "physics",
        "phys": "physics",
        "math": "mathematics",
        "geo": "geography",
        "hist": "history",
        "econ": "economics",
        "eng": "english",
        "soc": "sociology",
        "psych": "psychology",
        "edu" : "education",

        "bot": "botany",
        "zoo": "zoology",
        "stats": "statistics",
        "philo": "philosphy",
        "geol": "geology",
        "biochem": "biochemistry",
        "biotech": "biotechnology",
    }
    if user_text in abbreviations:
        if subject == abbreviations[user_text]:
            return 1.0
    return 0

def find_closest_subject(word, threshold=0.70):
    word = normalize_text(word)
    if not word:
        return None, 0
    subjects = get_subjects()
    best_subject = None
    best_score = 0
    for subject in subjects:
        abbreviation_score = abbreviation_match(
            word,
            subject
        )
        if abbreviation_score > 0:
            score = abbreviation_score
        else:
            score = calculate_subject_score(
                word,
                subject
            )
        if score > best_score:
            best_score = score
            best_subject = subject
    if best_score >= threshold:
        return best_subject, best_score
    return None, best_score

