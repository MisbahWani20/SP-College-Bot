import re
import sqlite3
from pathlib import Path
PROJECT_DIR = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_DIR / "spcollege_data.db"
STOP_WORDS = {
    "the", "is", "a", "an", "of", "for", "to", "in", "on",
    "and", "or", "what", "where", "when", "how", "who",
    "tell", "me", "about", "please", "can", "could", "do",
    "does", "i", "want", "know", "give", "show", "find",
    "which", "are", "was", "were", "my", "your", "their",
    "at", "it", "this", "that", "with", "from", "is",
    "there", "they", "we", "you", "college", "sp"
}
# Map different ways of asking to common searchable terms.
SYNONYMS = {
    "situated": "location",
    "located": "location",
    "location": "location",
    "address": "location",
    "reach": "contact",
    "contact": "contact",
    "call": "phone",
    "telephone": "phone",
    "mobile": "phone",
    "number": "phone",
    "email": "email",
    "mail": "email",
    "e-mail": "email",
    "website": "website",
    "webpage": "website",
    "site": "website",
    "map": "map",
    "direction": "map",
    "directions": "map",
    "route": "map",
    "navigate": "map",
    "establishment": "established",
    "founded": "established",
    "started": "established",
    "notice": "announcement",
    "notices": "announcement",
    "announcements": "announcement",
    "updates": "announcement",
    "deadline": "deadline",
    "lastdate": "deadline",
    "fees": "fee",
    "charges": "fee",
    "examinations": "exam",
    "examination": "exam",
    "timetable": "timetable",
    "schedule": "timetable",
    "brochures": "brochure",
    "admissions": "admission",
    "hostels": "hostel",
    "eligible": "eligibility",
}


def get_words(text):
    """Normalize words and common synonyms for searching."""
    text = (text or "").lower()
    text = text.replace("e-mail", "email")
    text = text.replace("last date", "lastdate")

    words = re.findall(r"[a-z0-9]+", text)
    normalized = set()

    for word in words:
        word = SYNONYMS.get(word, word)

        if len(word) <= 1 or word in STOP_WORDS:
            continue

        if word.endswith("s") and len(word) > 4:
            word = word[:-1]

        normalized.add(word)

    return normalized


def detect_intent(question):
    """Identify the main kind of information requested."""
    q = (question or "").lower()

    if any(term in q for term in (
        "hostel", "deadline", "last date", "lastdate",
        "fee", "fees", "eligibility", "result", "syllabus",
        "exam", "examination", "timetable", "brochure"
    )):
        return "specific"

    if any(term in q for term in (
        "phone", "telephone", "call", "contact number",
        "mobile number", "how do i contact"
    )):
        return "phone"

    if any(term in q for term in (
        "email", "e-mail", "mail address"
    )):
        return "email"

    if any(term in q for term in (
        "where", "location", "located", "situated",
        "address", "how can i get there", "how do i reach"
    )):
        return "location"

    if any(term in q for term in (
        "map", "direction", "directions", "route",
        "navigate", "google maps"
    )):
        return "map"

    if any(term in q for term in (
        "website", "webpage", "web site", "official site"
    )):
        return "website"

    if any(term in q for term in (
        "established", "establishment", "founded", "started"
    )):
        return "established"

    if any(term in q for term in (
        "announcement", "announcements", "notice", "notices",
        "latest update", "latest updates"
    )):
        return "announcement"

    if any(term in q for term in (
        "admission", "admissions", "brochure", "quick links",
        "quick link", "syllabus"
    )):
        return "admission"
    return "general"


def search_sp_college(question, limit=3):
    """Find the most relevant SP College database chunks."""
    if not question or not question.strip():
        return []
    if not DATABASE_PATH.exists():
        print("SP College database not found:", DATABASE_PATH)
        return []
    query_words = get_words(question)
    intent = detect_intent(question)
    question_lower = question.lower()
    department_terms = {
        "it": {"it", "information technology", "msc it", "bsc it"},
        "electronics": {"electronics"},
        "geology": {"geology"},
        "mathematics": {"mathematics", "maths"},
        "human genetics": {"human genetics"},
        "chemistry": {"chemistry"},
        "physics": {"physics"},
        "botany": {"botany"},
        "zoology": {"zoology"},
        "english": {"english"},
        "geography": {"geography"},
    }
    is_hod_query = any(
        term in question_lower
        for term in ("hod", "head of department", "head of the department")
    )

    
    requested_department = next(
        (
            department
            for department, aliases in department_terms.items()
            if any(
                re.search(
                    rf"(?<![a-z0-9]){re.escape(alias.lower())}(?![a-z0-9])",
                    question_lower
                )
                for alias in aliases
            )
        ),
        None
    )

    # Terms that identify the requested information.
    intent_terms = {
        "phone": {"phone", "telephone", "number", "contact"},
        "email": {"email", "mail"},
        "location": {"location", "address", "srinagar", "situated"},
        "map": {"map", "maps", "latitude", "longitude", "direction"},
        "website": {"website", "webpage", "https"},
        "established": {"established", "establishment", "1905", "founded"},
        "announcement": {"announcement", "notice", "alert"},
        "admission": {"admission", "brochure", "quick", "link"},
        "specific": {
            "hostel", "deadline", "fee", "eligibility", "result",
            "syllabus", "exam", "examination", "timetable", "brochure"
        },
    }

    # Remove only generic question words, not the requested topic.
    ignored_words = {
        "where", "when", "what", "which", "who", "how",
        "is", "are", "was", "were", "the", "of", "for",
        "to", "in", "at", "me", "show", "tell", "please",
        "sp", "college"
    }
    useful_words = query_words - ignored_words

    try:
        with sqlite3.connect(str(DATABASE_PATH)) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT p.title, p.url AS source_url, c.chunk_text
                FROM sp_chunks AS c
                JOIN sp_pages AS p ON p.url = c.source_url
            """).fetchall()
    except sqlite3.Error as error:
        print("SP College database search error:", error)
        return []

    matches = []

    for row in rows:
        title = row["title"] or ""
        content = row["chunk_text"] or ""
        source_url = row["source_url"] or ""
        searchable_text = (title + " " + content).lower()

        content_words = get_words(content)
        title_words = get_words(title)

        content_matches = useful_words.intersection(content_words)
        title_matches = useful_words.intersection(title_words)

        # Require evidence of the requested information type.
        if intent == "email" and not (
            "email" in searchable_text or "@" in content
        ):
            continue

        if intent == "phone" and not any(
            term in searchable_text
            for term in ("phone", "telephone", "contact", "0194-")
        ):
            continue

        if intent == "location" and not any(
            term in searchable_text
            for term in ("address", "srinagar", "m.a. road", "ma road")
        ):
            continue

        if intent == "established" and not any(
            term in searchable_text
            for term in ("1905", "established", "establishment", "founded")
        ):
            continue

        if intent in {"admission", "announcement"} and not any(
            term in searchable_text
            for term in ("admission", "notice", "alert", "announcement")
        ):
            continue

        # Prioritize matching content, then matching page titles.
        score = 3 * len(content_matches) + 2 * len(title_matches)
                # Prioritize the requested department page.
        if requested_department:
            department_page = (
                "it_department" if requested_department == "it"
                else requested_department.replace(" ", "_")
            )

            if department_page in source_url.lower():
                score += 10

        # Prioritize faculty information for HOD questions.
        if is_hod_query and any(
            term in searchable_text
            for term in ("hod", "head of department", "faculty", "people")
        ):
            score += 5

        if intent in {"email", "phone", "location", "established"}:
            if "main/default.aspx" in source_url.lower():
                score += 2

        if intent == "established" and "1905" in searchable_text:
            score += 5

        if intent in {"admission", "announcement"}:
            if any(term in title.lower() for term in ("admission", "notice", "alert")):
                score += 4
        if score > 0:
            matches.append({
                "title": title,
                "source_url": source_url,
                "chunk_text": content,
                "score": score,
            })
    matches.sort(key=lambda item: item["score"], reverse=True)
    return matches[:limit]


