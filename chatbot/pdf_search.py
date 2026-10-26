import sqlite3
import re
DATABASE_NAME = "chatbot/faq.db"
def search_pdf(user_question):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    question = user_question.lower().strip()
    # 1. Detect requested page number
    page_match = re.search(
        r"\bpage\s*(?:no\.?|number)?\s*(\d+)\b",
        question
    )
    requested_page = None
    if page_match:
        requested_page = int(page_match.group(1))
    if requested_page is not None:
        cursor.execute("""
            SELECT
                pdf_name,
                page,
                chunk
            FROM pdf_knowledge
            WHERE page = ?
            ORDER BY pdf_name
            LIMIT 1
        """, (requested_page,))

        row = cursor.fetchone()

        if row:
            conn.close()
            return row

    stop_words = {
        "show",
        "me",
        "the",
        "a",
        "an",
        "what",
        "does",
        "do",
        "is",
        "are",
        "tell",
        "about",
        "please",
        "give",
        "information",
        "information",
        "say",
        "says",
        "page",
        "number",
        "no",
        "prospectus",
        "pdf",
        "document",
        "official",
        "university"
    }

    words = re.findall(r"[a-z0-9]+", question)

    search_words = [
        word
        for word in words
        if word not in stop_words
        and len(word) > 2
    ]

    best_result = None
    best_score = 0

    for word in search_words:

        cursor.execute("""
            SELECT
                pdf_name,
                page,
                chunk
            FROM pdf_knowledge
            WHERE LOWER(chunk) LIKE ?
            ORDER BY page
        """, (f"%{word}%",))

        rows = cursor.fetchall()

        for row in rows:

            chunk = (row[2] or "").lower()

            score = chunk.count(word)

            if score > best_score:
                best_score = score
                best_result = row

    conn.close()

    return best_result