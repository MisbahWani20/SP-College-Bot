import sqlite3
import re

DATABASE_NAME = "chatbot/faq.db"
OFFICIAL_WEBSITE = "https://www.cusrinagar.edu.in/"
SYLLABUS_URL = (
    "https://www.cusrinagar.edu.in/Syllabus/Index/True?pp=UG"
)

def search_web_knowledge(user_question):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    question = user_question.lower().strip()
   
    if (
        "syllabus" in question
        or "syllabi" in question
    ):
        conn.close()
        return (
            "Cluster University Srinagar",
            "Official CUS Syllabus",
            SYLLABUS_URL,
            "View the official CUS syllabus section to find "
            "the required programme, subject and semester syllabus.",
            1
        )

  
    if (
        "official website" in question
        or question in [
            "website",
            "university website",
            "official university website"
        ]
    ):

        conn.close()

        return (
            "Cluster University Srinagar",
            "Official Website",
            OFFICIAL_WEBSITE,
            "Visit the official website of Cluster University Srinagar.",
            1
        )

    if (
        "result" in question
        or "results" in question
        or "date sheet" in question
        or "datesheet" in question
        or "date-sheet" in question
    ):

        if (
            "date sheet" in question
            or "datesheet" in question
            or "date-sheet" in question
        ):
            words = re.findall(
                r"\b[a-zA-Z0-9]+\b",
                question
            )
            stop_words = {
                "show",
                "me",
                "the",
                "what",
                "is",
                "are",
                "latest",
                "current",
                "official",
                "date",
                "sheet",
                "datesheet",
                "date-sheet",
                "of",
                "for",
                "please",
                "give",
                "tell",
                "about",
                "find"
            }

            words = [
                word
                for word in words
                if word not in stop_words
            ]

            if words:

                conditions = " AND ".join(
                    [
                        "LOWER(REPLACE(title, '.', '')) LIKE ?"
                        for _ in words
                    ]
                )

                parameters = [
                    f"%{word}%"
                    for word in words
                ]

                cursor.execute(
                    f"""
                    SELECT
                        item_type,
                        title,
                        item_date,
                        url
                    FROM cus_website_items
                    WHERE item_type = 'notification'
                    AND (
                        LOWER(title) LIKE '%date sheet%'
                        OR LOWER(title) LIKE '%datesheet%'
                        OR LOWER(title) LIKE '%date-sheet%'
                    )
                    AND {conditions}
                    ORDER BY item_date DESC
                    LIMIT 5
                    """,
                    parameters
                )
                rows = cursor.fetchall()
                if rows:
                    conn.close()
                    return {
                        "type": "exam_notifications",
                        "items": rows
                    }

            cursor.execute("""
                SELECT
                    item_type,
                    title,
                    item_date,
                    url
                FROM cus_website_items
                WHERE item_type = 'notification'
                AND (
                    LOWER(title) LIKE '%date sheet%'
                    OR LOWER(title) LIKE '%datesheet%'
                    OR LOWER(title) LIKE '%date-sheet%'
                )
                ORDER BY item_date DESC
                LIMIT 5
            """)

            rows = cursor.fetchall()

            conn.close()

            if rows:
                return {
                    "type": "exam_notifications",
                    "items": rows
                }

            return None

        words = re.findall(
            r"\b[a-zA-Z0-9]+\b",
            question
        )

        stop_words = {
            "show",
            "me",
            "the",
            "what",
            "is",
            "are",
            "latest",
            "current",
            "official",
            "result",
            "results",
            "of",
            "for",
            "please",
            "give",
            "tell",
            "about",
            "find"
        }

        words = [
            word
            for word in words
            if word not in stop_words
        ]

        if words:
            conditions = " AND ".join(
                [
                    "LOWER(REPLACE(title, '.', '')) LIKE ?"
                    for _ in words
                ]
            )
            parameters = [
                f"%{word}%"
                for word in words
            ]
            cursor.execute(
                f"""
                SELECT
                    item_type,
                    title,
                    item_date,
                    url
                FROM cus_website_items
                WHERE item_type = 'result'
                AND {conditions}
                ORDER BY item_date DESC
                LIMIT 5
                """,
                parameters
            )

            rows = cursor.fetchall()

            if rows:
                conn.close()

                return {
                    "type": "results",
                    "items": rows
                }
        cursor.execute("""
            SELECT
                item_type,
                title,
                item_date,
                url
            FROM cus_website_items
            WHERE item_type = 'result'
            ORDER BY item_date DESC
            LIMIT 5
        """)
        rows = cursor.fetchall()
        conn.close()
        if rows:
            return {
                "type": "results",
                "items": rows
            }
        return None
    
    if (
        "exam notification" in question
        or "exam notifications" in question
        or "examination notification" in question
        or "examination notifications" in question
        or "exam notice" in question
        or "examination notice" in question
    ):

        cursor.execute("""
            SELECT
                item_type,
                title,
                item_date,
                url
            FROM cus_website_items
            WHERE item_type = 'notification'
            AND (
                LOWER(title) LIKE '%exam%'
                OR LOWER(title) LIKE '%examination%'
                OR LOWER(title) LIKE '%date sheet%'
                OR LOWER(title) LIKE '%datesheet%'
                OR LOWER(title) LIKE '%admit card%'
                OR LOWER(title) LIKE '%admit cards%'
                OR LOWER(title) LIKE '%examination form%'
                OR LOWER(title) LIKE '%exam form%'
            )
            ORDER BY item_date DESC
            LIMIT 5
        """)

        rows = cursor.fetchall()

        conn.close()

        if rows:

            return {
                "type": "exam_notifications",
                "items": rows
            }

        return None


    if (
        "admission notification" in question
        or "admission notifications" in question
        or "admission notice" in question
        or "admission notices" in question
        or "latest admission" in question
    ):

        cursor.execute("""
          SELECT
             item_type,
             title,
             item_date,
             url
          FROM cus_website_items
          WHERE item_type = 'notification'
          AND (
             LOWER(title) LIKE '%admission%'
             OR LOWER(title) LIKE '%admissions%'
          )
          ORDER BY item_date DESC
          LIMIT 5
        """)
        rows = cursor.fetchall()
        conn.close()
        if rows:
          return {
             "type": "admission_notifications",
             "items": rows
          }
        return None


    if (
        "job notification" in question
        or "job notifications" in question
        or "job notice" in question
        or "job notices" in question
        or "latest jobs" in question
        or "latest job" in question
        or "employment notification" in question
        or "employment notifications" in question
    ):

        cursor.execute("""
          SELECT
             item_type,
             title,
             item_date,
             url
          FROM cus_website_items
          WHERE item_type = 'notification'
          AND (
             LOWER(title) LIKE '%job%'
             OR LOWER(title) LIKE '%employment%'
             OR LOWER(title) LIKE '%recruitment%'
             OR LOWER(title) LIKE '%appointment%'
             OR LOWER(title) LIKE '%interview%'
          )
          ORDER BY item_date DESC
          LIMIT 5
        """)
        rows = cursor.fetchall()
        conn.close()
        if rows:
           return {
             "type": "job_notifications",
             "items": rows
           }
        return None

    if (
        "latest notification" in question
        or "latest notifications" in question
        or "latest notice" in question
        or "latest notices" in question
        or question == "notification"
        or question == "notifications"
        or question == "notice"
        or question == "notices"
    ):

        cursor.execute("""
            SELECT
                item_type,
                title,
                item_date,
                url
            FROM cus_website_items
            WHERE item_type = 'notification'
            ORDER BY item_date DESC
            LIMIT 5
        """)

        rows = cursor.fetchall()

        conn.close()

        if rows:

            return {
                "type": "notifications",
                "items": rows
            }

        return None

  
    if (
        "notification" in question
        or "notifications" in question
        or "notice" in question
        or "notices" in question
        or "circular" in question
        or "circulars" in question
    ):
        words = re.findall(r"\b[a-zA-Z]+\b", question)
        stop_words = {
            "show",
            "me",
            "the",
            "what",
            "are",
            "is",
            "of",
            "for",
            "please",
            "give",
            "tell",
            "about",
            "find",
            "latest",
            "current",
            "official",
            "notification",
            "notifications",
            "notice",
            "notices",
            "circular",
            "circulars"
        }

        words = [
            word
            for word in words
            if word not in stop_words
        ]

        if words:

            conditions = " AND ".join(
                ["LOWER(title) LIKE ?" for _ in words]
            )

            parameters = [
                f"%{word}%"
                for word in words
            ]

            cursor.execute(
                f"""
                SELECT
                    item_type,
                    title,
                    item_date,
                    url
                FROM cus_website_items
                WHERE item_type = 'notification'
                AND {conditions}
                ORDER BY item_date DESC
                LIMIT 5
                """,
                parameters
            )
            rows = cursor.fetchall()
            conn.close()
            if rows:
                return {
                    "type": "notifications",
                    "items": rows
                }

        conn.close()

        return None

  
    words = question.split()

    stop_words = {
        "show",
        "me",
        "the",
        "what",
        "are",
        "is",
        "of",
        "for",
        "please",
        "give",
        "tell",
        "about",
        "find",
        "latest",
        "current",
        "official"
    }

    words = [
        word
        for word in words
        if word not in stop_words
    ]
    if words:
        conditions = " AND ".join(
            ["LOWER(chunk_text) LIKE ?" for _ in words]
        )
        parameters = [
            f"%{word}%"
            for word in words
        ]
        cursor.execute(
            f"""
            SELECT
                college,
                page_title,
                url,
                chunk_text,
                chunk_no
            FROM web_chunks
            WHERE {conditions}
            LIMIT 1
            """,
            parameters
        )
        row = cursor.fetchone()
        if row:
            conn.close()
            return row
    conn.close()
    return None