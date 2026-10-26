import sqlite3
import re
from chatbot.aliases import UNIVERSITY_ALIASES

DATABASE_NAME = "chatbot/knowledge.db"
def normalize_university_question(question):
    question = (question or "").lower().strip()
   
    question = re.sub(r"[^a-z0-9\s-]", " ", question)

    question = re.sub(r"\s+", " ", question).strip()

    for alias, field in sorted(
        UNIVERSITY_ALIASES.items(),
        key=lambda x: len(x[0]),
        reverse=True
    ):
        pattern = rf"\b{re.escape(alias)}\b"

        question = re.sub(
            pattern,
            field,
            question
        )

    return re.sub(r"\s+", " ", question).strip()


def search_university_info(question):

    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM university_info
    """)

    records = cursor.fetchall()
    conn.close()
    original_question = (question or "").lower().strip()
    normalized_question = normalize_university_question(
        original_question
    )
    print(
        "UNIVERSITY SEARCH QUESTION:",
        repr(normalized_question)
    )


    best = None
    best_score = 0

    for record in records:

        field = (record["field"] or "").lower().strip()
        value = (record["value"] or "").lower().strip()

        score = 0

        # Exact field match
        if field in normalized_question:
            score += 200

        if field in UNIVERSITY_ALIASES.values():

            if field in normalized_question:
                score += 300

      
        for word in field.split():
            if len(word) > 2 and word in normalized_question:
                score += 20

    
        for word in value.split():
            if len(word) > 4 and word in normalized_question:
                score += 1

        if score > best_score:
            best_score = score
            best = record
    print(
        "UNIVERSITY BEST FIELD:",
        best["field"] if best else None
    )

    print(
        "UNIVERSITY SCORE:",
        best_score
    )

    return best

def search_all_university_info(question, field_name):

    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM university_info
        WHERE LOWER(field) = LOWER(?)
        ORDER BY university_info_id
    """, (field_name,))
    records = cursor.fetchall()
    conn.close()
    return records
def university_response(question):
    normalized_question = normalize_university_question(question)
    if "constituent colleges" in normalized_question:
        records = search_all_university_info(
            question,
            "College 1"
        )
        conn = sqlite3.connect(DATABASE_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM university_info
            WHERE LOWER(field) LIKE 'college %'
            ORDER BY university_info_id
        """)

        records = cursor.fetchall()
        conn.close()

        if records:
            response = [
                "🏛 <b>Cluster University Srinagar</b>",
                "<b>Constituent Colleges:</b>"
            ]
            for record in records:
                response.append(
                    f"🏛 {record['value']}"
                )
            return "\n".join(response)
    record = search_university_info(question)
    if record is None:
        return None
    field = record["field"]
    value = record["value"]
    source = (
        record["source"]
        if "source" in record.keys()
        else""
    )

    url = (
        record["url"]
        if "url" in record.keys()
        else ""
    )

    email = ""

    if "email" in record.keys():
        email = record["email"] or ""
       
    if field.lower() == "overview":
      response = [
         "🏛 <b>Cluster University Srinagar (CUS)</b>",
         f"{value}"
    ]
    else:
      response = [
         "🏛 <b>Cluster University Srinagar</b>",
         f"<b>{field}:</b> {value}"
    ]

    if email:
        response.append(
            f'<b>Email:</b> '
            f'<a href="mailto:{email}" '
            f'style="color: inherit; text-decoration: underline;">'
            f'{email}'
            f'</a>'
        )

    if url:
        response.append(
            f'<b>Source:</b> '
            f'<a href="{url}" target="_blank">'
            f'{source or "Official University Website"}'
            f'</a>'
        )
    return "\n\n".join(response)