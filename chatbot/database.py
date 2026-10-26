import sqlite3
from difflib import SequenceMatcher

DATABASE_NAME = "chatbot/faq.db"

DATABASE = DATABASE_NAME

def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    return connection

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
         CREATE TABLE IF NOT EXISTS answers (
            answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            answer TEXT NOT NULL,
            intent TEXT NOT NULL,
            category TEXT,
            source TEXT,
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions(
                   question_id INTEGER PRIMARY KEY AUTOINCREMENT,
                   answer_id INTEGER,
                   question TEXT NOT NULL,
                   keywords TEXT,
                   FOREIGN KEY (answer_id) REFERENCES answers(answer_id)
            )
    ''')
    cursor.execute('''
           CREATE TABLE IF NOT EXISTS chat_history(
                   chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                   user_question TEXT,
                   bot_answer TEXT,
                   timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                   language TEXT
            )
    ''')
    conn.commit()
    conn.close()

def add_answer(answer, intent, category, source, last_updated):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO answers (answer, intent, category, source, last_updated)
        VALUES (?, ?, ?, ?, ?)
    ''', (answer, intent, category, source, last_updated))

    conn.commit()
    answer_id = cursor.lastrowid
    conn.close()
    return answer_id

def add_question(answer_id, question, keywords):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO questions (answer_id, question, keywords)
        VALUES (?, ?, ?)
    ''', (answer_id, question, keywords))

    conn.commit()
    conn.close() 

def search_question(user_question):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT questions.question, answers.answer
        FROM questions
        JOIN answers
        ON questions.answer_id = answers.answer_id
    """)

    rows = cursor.fetchall()
    conn.close()

    best_match = None
    highest_score = 0

    user_question = user_question.lower()

    for question, answer in rows:

        score = SequenceMatcher(
            None,
            user_question,
            question.lower()
        ).ratio()

        if score > highest_score:
            highest_score = score
            best_match = answer

    # Minimum similarity required
    if highest_score >= 0.60:
        return best_match

    return None

def create_web_knowledge_table():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS web_knowledge(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        college TEXT NOT NULL,

        page_title TEXT,

        url TEXT UNIQUE,

        content TEXT NOT NULL,

        crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_college
    ON web_knowledge(college)
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_title
    ON web_knowledge(page_title)
    """)

    conn.commit()

    conn.close()

def insert_web_knowledge(
    college,
    page_title,
    url,
    content
):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO web_knowledge(
        college,
        page_title,
        url,
        content
    )
    VALUES(?,?,?,?)
    """,(
        college,
        page_title,
        url,
        content
    ))
    conn.commit()
    conn.close()

def get_all_web_pages():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            college,
            page_title,
            url,
            content
        FROM web_knowledge
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows
def create_web_chunks_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS web_chunks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        college TEXT,
        page_title TEXT,
        url TEXT,
        chunk_no INTEGER,
        chunk_text TEXT
    )
    """)
    conn.commit()
    conn.close()

def insert_web_chunk(
    college,
    page_title,
    url,
    chunk_no,
    chunk_text
):

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""

    INSERT INTO web_chunks(

        college,
        page_title,
        url,
        chunk_no,
        chunk_text
    )
    VALUES(?,?,?,?,?)
    """,(
       college,
        page_title,
        url,
        chunk_no,
        chunk_text
    ))
    conn.commit()
    conn.close()

def get_all_chunks():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT
        college,
        page_title,
        url,
        chunk_no,
        chunk_text
    FROM web_chunks
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows