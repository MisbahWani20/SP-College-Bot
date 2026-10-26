import sqlite3
import re
from chatbot.aliases import COLLEGE_ALIASES, PROGRAMME_ALIASES
from chatbot.spellcheck import find_closest_subject
LAST_PROGRAMME = None
DATABASE_NAME = "chatbot/knowledge.db"
def get_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn
def normalize_question(text):
    text = (text or "").lower().strip()

    text = re.sub(r"[^a-z0-9\s&-]", " ", text)
    for short, full in sorted(
        COLLEGE_ALIASES.items(),
        key=lambda x: len(x[0]),
        reverse=True
    ):
        text = re.sub(
            rf"\b{re.escape(short.lower())}\b",
            full.lower(),
            text
        )
    for short, full in sorted(
        PROGRAMME_ALIASES.items(),
        key=lambda x: len(x[0]),
        reverse=True
    ):
        text = re.sub(
            rf"\b{re.escape(short.lower())}\b",
            full.lower(),
            text
        )
    replacements = {
        "bachelor of computer applications": "bca",
        "master of science": "msc",
        "master of arts": "ma",
        "master of computer applications": "mca",
        "master of business administration": "mba",
        "master of commerce": "mcom",
        "master of education": "med",
        "bachelor of science": "bsc",
        "bachelor of arts": "ba",
        "bachelor of commerce": "bcom",
        "bachelor of business administration": "bba",
        "bachelor of education": "bed",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return re.sub(r"\s+", " ", text).strip()
def get_words(text):
    return set(
        re.findall(
            r"[a-z0-9]+(?:-[a-z0-9]+)*",
            text.lower()
        )
    )
def find_corrected_subject(question):

    question = normalize_question(question)
    words = question.split()
    ignored_words = {
        "what",
        "is",
        "the",
        "fee",
        "fees",
        "of",
        "for",
        "me",
        "tell",
        "about",
        "please",
        "give",
        "information",
        "programme",
        "program",
        "programmes",
        "programs",
        "course",
        "courses",
        "intake",
        "seats",
        "duration",
        "eligibility",
        "admission",
        "selection",
        "process",
        "college",
        "colleges",
        "offer",
        "offers",
        "offering",
        "study",
        "available",
        "show",
        "list",
        "all",
        "can",
        "i",
        "to",
        "where",
        "which",
        "does",
        "do",
        "have",
        "has",
        "about",
        "regular",
        "general",
        "ug",
        "pg",
        "undergraduate",
        "postgraduate",
        "integrated",
        "hons",
        "hon"
    }
    subject_words = [
        word
        for word in words
        if word not in ignored_words
        and word not in UG
        and word not in PG
    ]
    if not subject_words:
        return None

    # Try the complete remaining phrase first.
    subject_text = " ".join(subject_words)

    subject, score = find_closest_subject(
        subject_text
    )

    if subject is not None:
        print(
            "SPELLCHECK SUBJECT:",
            subject_text,
            "->",
            subject,
            "| SCORE:",
            round(score, 3)
        )

        return subject

    for word in subject_words:

        subject, score = find_closest_subject(word)

        if subject is not None:

            print(
                "SPELLCHECK WORD:",
                word,
                "->",
                subject,
                "| SCORE:",
                round(score, 3)
            )

            return subject

    return None

UG = {
    "ba",
    "bsc",
    "bca",
    "bba",
    "bcom",
    "bed"
}

PG = {
    "ma",
    "msc",
    "mca",
    "mba",
    "mcom",
    "med"
}



def get_all_programmes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM academic_programmes"
    )
    programmes = cursor.fetchall()
    conn.close()
    return programmes
def is_known_programme_question(question):
    question = normalize_question(question)

    if not question:
        return False

    words = get_words(question)

    programmes = get_all_programmes()

    for p in programmes:
        programme = normalize_programme_name(
            p["programme"] or ""
        )

        specialization = normalize_question(
            p["specialization"] or ""
        )

        department = normalize_question(
            p["department"] or ""
        )

        programme_words = get_words(programme)
        specialization_words = get_words(specialization)
        department_words = get_words(department)

        # Exact / full programme name
        if programme and programme in question:
            return True

        # Exact specialization
        if specialization and specialization in question:
            return True

        # Match meaningful programme words
        if programme_words and programme_words.issubset(words):
            return True

        if specialization_words and specialization_words.issubset(words):
            return True

        # Department match only when it is reasonably specific
        if (
            department_words
            and len(department_words) >= 2
            and department_words.issubset(words)
        ):
            return True

    return False
def search_subject_overview(subject):
    subject = normalize_question(subject).strip()

    #new spellcheck
    if not subject:
        return None

    # if subject == "it":
    #     subject = "information technology"

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM academic_programmes
        WHERE LOWER(TRIM(specialization)) = ?
           OR LOWER(TRIM(department)) = ?
        ORDER BY id
        LIMIT 1
    """, (
        subject.lower(),
        subject.lower()
    ))

    programme = cursor.fetchone()

    if programme is None:
        corrected_subject, score = find_closest_subject(
            subject
        )
        print(
            "SUBJECT SPELLCHECK:",
            subject,
            "->",
            corrected_subject,
            "| SCORE:",
            round(score, 3)
        )
        if corrected_subject:
            corrected_subject = normalize_question(
                corrected_subject
            )
            cursor.execute("""
                SELECT *
                FROM academic_programmes
                WHERE LOWER(TRIM(specialization)) = ?
                   OR LOWER(TRIM(department)) = ?
                ORDER BY id
                LIMIT 1
            """, (
                corrected_subject.lower(),
                corrected_subject.lower()
            ))
            programme = cursor.fetchone()
            if programme is not None:
                subject = corrected_subject
    conn.close()

    if programme is None:
        return None

    overview = (
        programme["subject_overview"] or ""
    ).strip()

    if not overview:
        return None

    return {
        "subject": subject,
        "overview": overview
    }

def make_unique(programmes):
    unique = []
    seen = set()

    for p in programmes:
        key = (
            (p["programme"] or "").strip().lower(),
            (p["specialization"] or "").strip().lower(),
            (p["level"] or "").strip().lower(),
            (p["duration"] or "").strip().lower(),
            (p["college"] or "").strip().lower(),
            (p["department"] or "").strip().lower()
        )
        if key not in seen:
            seen.add(key)
            unique.append(p)
    return unique

# new
def normalize_programme_name(text):
    text = normalize_question(text)
    text = re.sub(r"\bba\s+bed\b", "ba bed", text)
    text = re.sub(r"\bbsc\s+bed\b", "bsc bed", text)
    return re.sub(r"\s+", " ", text).strip()

def detect_requested_duration(question):
    question = normalize_question(question)
    # 1 year variations
    if re.search(
        r"\b(1|one)\s*-?\s*year\b",
        question
    ):
        return "1 year"
    # 2 year variations
    if re.search(
        r"\b(2|two)\s*-?\s*years?\b",
        question
    ):
        return "2 years"

    return None

def duration_matches(requested_duration, database_duration):
    if not requested_duration:
        return True
    database_duration = (
        database_duration or ""
    ).lower().strip()
    if requested_duration == "1 year":
        return bool(
            re.search(
                r"\b1\s*year\b",
                database_duration
            )
        )

    if requested_duration == "2 years":
        return bool(
            re.search(
                r"\b2\s*years?\b",
                database_duration
            )
        )

    return True

def search_programmes(user_question):
    global LAST_PROGRAMME
    question = normalize_question(user_question)
    requested_duration = detect_requested_duration(question)
    print(
        "REQUESTED DURATION:",
        requested_duration
    )
    # spellcheck
    original_question = question

    words = get_words(question)
    programmes = get_all_programmes()
    best_match = None
    best_score = -1

    requested_programme = None
    if(
        "integrated" in words
        and "ba" in words
        and "bed" in words
    ):
        requested_programme = "ba bed"
    elif (
        "integrated" in words
        and "bsc" in words
        and "bed" in words
    ):
        requested_programme = "bsc bed"

    elif "msc" in words:
        requested_programme = "msc"
    elif "bsc" in words:
        requested_programme = "bsc"
    elif "mca" in words:
        requested_programme = "mca"
    elif "bca" in words:
        requested_programme = "bca"
    elif "mba" in words:
        requested_programme = "mba"
    elif "bba" in words:
        requested_programme = "bba"
    elif "mcom" in words:
        requested_programme = "mcom"
    elif "bcom" in words:
        requested_programme = "bcom"
    elif "med" in words:
        requested_programme = "med"
    elif "bed" in words:
        requested_programme = "bed"
    elif "ma" in words:
        requested_programme = "ma"
    elif "ba" in words:
        requested_programme = "ba"
    print("REQUESTED PROGRAMME:", requested_programme)
    corrected_subject = find_corrected_subject(
        original_question
    )
    if corrected_subject:
        corrected_subject_normalized = normalize_question(
            corrected_subject
        )
        words.update(
            corrected_subject_normalized.split()
        )
        print(
            "CORRECTED SUBJECT:",
            corrected_subject_normalized
        )
    else:
        corrected_subject_normalized = None

    for p in programmes:
        programme_name = normalize_programme_name(
            p["programme"] or ""
        )
        specialization = normalize_question(
            p["specialization"] or ""
        )
        college = normalize_question(
            p["college"] or ""
        )
        department =  normalize_question(
           p["department"] or ""
        )
        level = normalize_question (
            p["level"] or ""
        )
        duration = normalize_question(
            p["duration"] or ""
        )
        if requested_duration:
            if not duration_matches(
                requested_duration,
                duration
            ):
                continue

        programme_key = programme_name.replace(" ", "")
        if programme_key in ["msc", "m.sc"]:
            programme_key = "msc"
        

        elif programme_key in ["bsc", "b.sc"]:
            programme_key = "bsc"

        elif programme_key in ["ma", "m.a"]:
            programme_key = "ma"

        elif programme_key in ["ba", "b.a"]:
            programme_key = "ba"

        elif programme_key in ["mca", "m.c.a"]:
            programme_key = "mca"

        elif programme_key in ["bca", "b.c.a"]:
            programme_key = "bca"

        elif programme_key in ["mba", "m.b.a"]:
            programme_key = "mba"

        elif programme_key in ["bba", "b.b.a"]:
            programme_key = "bba"

        elif programme_key in ["mcom", "m.com"]:
            programme_key = "mcom"

        elif programme_key in ["bcom", "b.com"]:
            programme_key = "bcom"

        elif programme_key in ["bed", "b.ed"]:
            programme_key = "bed"

        elif programme_key in ["med", "m.ed"]:
            programme_key = "med"
   
        if requested_programme:
            if requested_programme in {"ba bed", "bsc bed"}:
                requested_parts = set(
                    requested_programme.split()
                )
                programme_words = get_words(
                    programme_name
                )
                if not requested_parts.issubset(
                    get_words(programme_name)
                ):
                    continue
            else:
                if requested_programme != programme_key:
                   continue
            if (
                requested_programme == "msc"
                and "integrated" in get_words(programme_name)
                and "integrated" not in words
            ):
                continue

            if (
                requested_programme == "bsc"
                and "integrated" in get_words(programme_name)
                and "integrated" not in words
            ):
                continue

        score = 0
        if requested_duration:
            if duration_matches(
                requested_duration,
                duration
            ):
                score += 3000

        question_key = question.replace(" ", "")
        if programme_key and programme_key in question_key:
            score += 10000
        if programme_name == question:
            score += 10000
        full_name = (
            f"{programme_name} {specialization}"
        ).strip()
        if full_name == question:
            score += 9000
    
        if programme_name:
            programme_words = get_words(programme_name)

            if programme_words.issubset(words):
               score += 5000

        if specialization:
            spec_words = get_words(specialization)

            specialization_matches = (
                spec_words.intersection(words)
            )
            if spec_words.issubset(words):
                score += 4000
            elif specialization_matches:
                score += (
                    len(specialization_matches) * 500
                )

        subject_words = (
            words
            - {
                "what",
                "is",
                "the",
                "how",
                "long",
                "where",
                "can",
                "i",
                "to",
                "study",
                "tell",
                "me",
                "about",
                "please",
                "give",
                "information",
                "programme",
                "program",
                "programmes",
                "programs",
                "course",
                "courses",
                "of",
                "for",
                "fee",
                "fees",
                "intake",
                "seats",
                "duration",
                "eligibility",
                "admission",
                "selection",
                "process",
                "integrated"
            }
            - UG
            - PG
        )
        if subject_words and specialization:
            spec_words = get_words(specialization)
            dept_words = get_words(department)
            if not (
                subject_words.issubset(spec_words)
                or subject_words.issubset(dept_words)
                ):
                continue
        if department:
            dept_words = get_words(department)
            if dept_words.issubset(words):
                score += 1000
        if college and college in question:
            score += 1000
        if level == "ug" and words.intersection(UG):
            score += 500

        if level == "pg" and words.intersection(PG):
            score += 500
        if level == "integrated" and "integrated" in words:
            score += 3000
        if score > best_score:
            best_score = score
            best_match = p
        
    if best_match and best_score > 0:
        LAST_PROGRAMME = best_match
        print(
            "BEST PROGRAMME:",
            best_match["programme"],
            "|",
            best_match["specialization"],
            "|",
            best_match["level"],
            "|",
            best_match["college"],
            "| SCORE:",
            best_score
        )
        return best_match
    return None
            
def search_all_matching_programmes(user_question):
    question = normalize_question(user_question)
    words = get_words(question)
    requested_duration = detect_requested_duration(
        question
    )

    print(
        "REQUESTED DURATION:",
        requested_duration
    )
    programmes = get_all_programmes()
    matches = []
    requested_programme = None
    if (
       "integrated" in words
       and "ba" in words
       and "bed" in words
    ):
       requested_programme = "ba bed"

    elif (
       "integrated" in words
       and "bsc" in words
       and "bed" in words
    ):
       requested_programme = "bsc bed"
    else:
       programme_order = [
         "msc",
         "bsc",
         "mca",
         "bca",
         "mba",
         "bba",
         "mcom",
         "bcom",
         "med",
         "bed",
         "ma",
         "ba"
       ]

       for programme in programme_order:
          if programme in words:
             requested_programme = programme
             break
    requested_integrated = (
        "integrated" in words
    )
    print(
        "REQUESTED PROGRAMME:",
        requested_programme
    )
    print(
        "REQUESTED INTEGRATED:",
        requested_integrated
    )
    ignored_words = {
        "which",
        "what",
        "college",
        "colleges",
        "offer",
        "offers",
        "offering",
        "provide",
        "provides",
        "provided",
        "programme",
        "programmes",
        "program",
        "programs",
        "course",
        "courses",
        "the",
        "a",
        "an",
        "of",
        "in",
        "for",
        "where",
        "can",
        "i",
        "study",
        "to",
        "me",
        "is",
        "are",
        "available",
        "show",
        "list",
        "all",
        "have",
        "has",
        "please",
        "tell",
        "give",
        "information",
        "about",
        "fee",
        "fees",
        "intake",
        "duration",
        "eligibility",
        "admission",
        "selection",
        "process"
    }
    corrected_subject = find_corrected_subject(question)

    if corrected_subject:
        corrected_subject_normalized = normalize_question(
            corrected_subject
        )
    
        requested_subject_words = get_words(
            corrected_subject_normalized
        )
    
        print(
            "CORRECTED SUBJECT:",
            corrected_subject_normalized
        )
    else:
        requested_subject_words = (
            words - ignored_words - UG - PG
        )
        requested_subject_words.discard(
            "integrated"
        )
    
    print(
        "REQUESTED SUBJECT WORDS:",
        requested_subject_words
    )
    for p in programmes:
        programme_name = (
            p["programme"] or ""
        ).lower().strip()

        specialization = (
            p["specialization"] or ""
        ).lower().strip()

        department = (
            p["department"] or ""
        ).lower().strip()

        level = (
            p["level"] or ""
        ).lower().strip()
        duration = (
            p["duration"] or ""
        ).lower().strip()

        if requested_duration:
            if not duration_matches(
                requested_duration,
                duration
            ):
                continue

        normalized_programme = (
            normalize_programme_name(
                programme_name
            )
        )

        programme_words = get_words(
            normalized_programme
        )

        if requested_programme:
            if requested_programme in {"ba bed", "bsc bed"}:
              requested_parts = set(
              requested_programme.split()
              )
              if not requested_parts.issubset(
                programme_words
              ):
                continue
            else:
              if requested_programme not in programme_words:
                continue
        if requested_integrated:
            if level != "integrated":
                continue
        else:
            if level == "integrated":
                continue

        searchable_words = (
            get_words(programme_name)
            | get_words(specialization)
            | get_words(department)
        )

        if requested_subject_words:
            subject_matches = (
                requested_subject_words.intersection(
                    searchable_words
                )
            )
            if not requested_subject_words.issubset(
                searchable_words
            ):
                continue

        score = 0
        if requested_programme:
            if requested_programme in {"ba bed", "bsc bed"}:
                requested_parts = set(
                  requested_programme.split()
                )
                if requested_parts.issubset(programme_words):
                   score += 10000
            else:
                if programme_name == requested_programme:
                   score += 10000
                elif requested_programme in programme_words:
                   score += 8000
        # Integrated exactness
        if requested_integrated:
            if level == "integrated":
                score += 5000
        # Subject / specialization match
        specialization_words = get_words(
            specialization
        )
        specialization_matches = (
            specialization_words.intersection(
                requested_subject_words
            )
        )
        if specialization_matches:
            if specialization_words.issubset(
                requested_subject_words
            ):
                score += 4000
            else:
                score += (
                    len(specialization_matches) * 1000
                )
        # Department match
        department_words = get_words(
            department
        )
        department_matches = (
            department_words.intersection(
                requested_subject_words
            )
        )
        if department_matches:
            score += (
                len(department_matches) * 100
            )
       
        if normalized_programme in question:
            score += 3000
        matches.append(
            (score, p)
        )
    if not matches:
        return []
    best_score = max(
        score
        for score, _ in matches
    )
    results = [
        p
        for score, p in matches
        if score == best_score
    ]
    return make_unique(results)
def search_programme_list(question):
    question = normalize_question(question)
    question = re.sub(
        r"\big\b",
        "integrated",
        question
    )
    question = re.sub(
        r"\bm\s+sc\b",
        "msc",
        question
    )
    question = re.sub(
        r"\bb\s+sc\b",
        "bsc",
        question
    )
    question = re.sub(
        r"\bm\s+com\b",
        "mcom",
        question
    )
    question = re.sub(
        r"\bb\s+com\b",
        "bcom",
        question
    )
    question = re.sub(
        r"\bm\s+ca\b",
        "mca",
        question
    )
    question = re.sub(
        r"\bb\s+ca\b",
        "bca",
        question
    )
    question = re.sub(
        r"\bm\s+ba\b",
        "mba",
        question
    )
    question = re.sub(
        r"\bb\s+ba\b",
        "bba",
        question
    )
    question = re.sub(
        r"\bm\s+a\b",
        "ma",
        question
    )
    question = re.sub(
        r"\bb\s+a\b",
        "ba",
        question
    )
    question = re.sub(
        r"\bm\s+ed\b",
        "med",
        question
    )
    question = re.sub(
        r"\bb\s+ed\b",
        "bed",
        question
    )
    typo_replacements = {
        "programmemes": "programmes",
        "programmee": "programme",
        "programm": "programme",
        "programs": "programmes"
    }
    for old, new in typo_replacements.items():
        question = re.sub( rf"\b{re.escape(old)}\b", new,question)
    print("------------------------------------------------")
    print("LIST SEARCH QUESTION:", question)
    requested_level = None
    if re.search(r"\bintegrated\b", question):
        requested_level = "integrated"
    elif re.search(
        r"\b(pg|postgraduate|post graduate)\b",
        question
    ):
        requested_level = "pg"
    elif re.search(
        r"\b(ug|undergraduate|under graduate)\b",
        question
    ):
        requested_level = "ug"
    print("REQUESTED LEVEL:", requested_level)
    ignore_words = {
        "list",
        "show",
        "display",
        "available",
        "offer",
        "offers",
        "offered",
        "provide",
        "provides",
        "which",
        "college",
        "colleges",
        "programme",
        "programmes",
        "programmemes",
        "program",
        "programs",
        "course",
        "courses",
        "all",
        "can",
        "study",
        "where",
        "to",
        "in",
        "for",
        "the",
        "of",
        "are",
        "is",
        "what",
        "does",
        "do",
        "me",
        "i",
        "my",
        "pg",
        "ug",
        "postgraduate",
        "post",
        "graduate",
        "undergraduate",
        "under",
        "integrated"
    }
    keywords = [
        word
        for word in re.findall(
            r"[a-z0-9]+(?:-[a-z0-9]+)*",
            question
        )
        if word not in ignore_words
    ]
    keywords = list(dict.fromkeys(keywords))
    print("LIST KEYWORDS:", keywords)
    programmes = get_all_programmes()
    results = []
    for p in programmes:
        level = (
            p["level"] or ""
        ).lower().strip()
        if requested_level and level != requested_level:
            continue
        if not requested_level and level ==  "integrated":
            continue
        programme_name = (
            p["programme"] or ""
        ).lower().strip()
        specialization = (
            p["specialization"] or ""
        ).lower().strip()
        department = (
            p["department"] or ""
        ).lower().strip()
        college = (
            p["college"] or ""
        ).lower().strip()
        school = (
            p["school"] or ""
        ).lower().strip()
        programme_words = get_words(programme_name)
        specialization_words = get_words(specialization)
        department_words = get_words(department)
        college_words = get_words(college)
        school_words = get_words(school)
        search_words = (
            programme_words
            | specialization_words
            | department_words
            | college_words
            | school_words
        )
        if not keywords:
            results.append(p)
            continue
        matched = True
        for keyword in keywords:
            if keyword == "information":
                if (
                    "information" not in programme_name
                    and "information" not in specialization
                    and "information" not in department
                ):
                    matched = False
                    break
            elif keyword == "technology":
                if (
                    "technology" not in programme_name
                    and "technology" not in specialization
                    and "technology" not in department
                ):
                    matched = False
                    break
            elif keyword not in search_words:
                matched = False
                break
        if matched:
            results.append(p)
    results = make_unique(results)

    level_order = {
        "ug": 1,
        "integrated": 2,
        "pg": 3
    }

    results.sort(
        key=lambda x: (
            level_order.get(
                (x["level"] or "").lower(),
                99
            ),
            (x["programme"] or "").lower(),
            (x["specialization"] or "").lower(),
            (x["college"] or "").lower()
        )
    )

    print("FINAL RESULTS:", len(results))

    for p in results:
        print(
            "RESULT:",
            p["programme"],
            "|",
            p["specialization"],
            "|",
            p["level"],
            "|",
            p["college"]
        )
    return results
def get_last_programme():
    return LAST_PROGRAMME