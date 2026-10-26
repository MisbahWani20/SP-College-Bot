import sqlite3
import re

DATABASE_NAME = "chatbot/knowledge.db"
LAST_UNIVERSITY_RECORD = None
def search_university(question):
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT *
        FROM university_info
    """)
    records = cursor.fetchall()
    conn.close()
    question = (question or "").lower().strip()

  
    question = re.sub(
        r"[^a-z0-9\s@._-]",
        " ",
        question
    )

    question = re.sub(
        r"\s+",
        " ",
        question
    ).strip()

    best = None
    best_score = 0

    for record in records:

        current = 0

        intent = (
            record["intent"] or ""
        ).lower()

        topic = (
            record["topic"] or ""
        ).lower()

        field = (
            record["field"] or ""
        ).lower()

        value = (
            record["value"] or ""
        ).lower()

        email = (
            record["email"] or ""
        ).lower()

      
        if field and field in question:
            current += 20

       
        if topic and topic in question:
            current += 10


        field_words = re.findall(
            r"[a-z0-9]+",
            field
        )

        for word in field_words:
            if len(word) > 2 and word in question:
                current += 5

   
        value_words = re.findall(
            r"[a-z0-9]+",
            value
        )

        for word in value_words:
            if len(word) > 3 and word in question:
                current += 2

      
        if email and email in question:
            current += 20

      
        if "university" in question:
            current += 2

        if "cus" in question:
            current += 5

        if "cluster" in question and "university" in question:
            current += 5

        if current > best_score:
            best_score = current
            best = record

    global LAST_UNIVERSITY_RECORD
    if best:
        LAST_UNIVERSITY_RECORD = best
    return best

def get_last_university_record():

    global LAST_UNIVERSITY_RECORD

    return LAST_UNIVERSITY_RECORD