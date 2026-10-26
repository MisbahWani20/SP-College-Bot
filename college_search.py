import sqlite3
from chatbot.aliases import COLLEGE_ALIASES

DATABASE_NAME = "chatbot/knowledge.db"
LAST_COLLEGE = None

def search_college(question):
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM college_master")
    colleges = cursor.fetchall()
    conn.close()
    question = question.lower()
    
    question = " "+question+" "
    for short,full in COLLEGE_ALIASES.items():
        question = question.replace(f"{short}", f"{full}")
    question = question.strip()
        
    best = None
    score = 0

    for college in colleges:

        current = 0

        name = (college["college_name"] or "").lower()
        short = (college["short_name"] or "").lower()

        if name in question:
            current += 10

        if short and short in question:
            current += 8

        for word in name.split():
            if len(word) > 2 and word in question:
                current += 2

        if current > score:
            score = current
            best = college
            
    global LAST_COLLEGE
    if best:
        LAST_COLLEGE = best
    return best

def get_last_college():
    global LAST_COLLEGE
    return LAST_COLLEGE