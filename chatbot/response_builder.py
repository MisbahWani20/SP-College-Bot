import sqlite3
from pathlib import Path
import time
import re
import chatbot.query_router as qr
from chatbot.nlp import correct_spelling
from chatbot.casual_response import get_casual_response
from chatbot.college_response import college_response
from chatbot.general_admission import get_general_admission_response
from chatbot.conversation_context import conversation_context
from chatbot.pdf_search import search_pdf
from chatbot.programme_response import programme_response
from chatbot.programme_search import is_known_programme_question
from chatbot.query_intents import *
from chatbot.aliases import PROGRAMME_ALIASES
from chatbot.aliases import COLLEGE_ALIASES
from chatbot.knowledge_database import get_faculty_members
from chatbot.knowledge_database import get_topic_fields, get_topic
from chatbot.semantic_search import find_best_topic
from chatbot.web_search import search_web_knowledge
from chatbot.university_response import university_response
from chatbot.llm_service import (
    ask_llm,
    classify_with_llm,
    generate_grounded_response,
    build_canonical_query,
    classify_sp_college_question
)
from datetime import datetime
from chatbot.sp_college_search import search_sp_college
def is_sp_college_download_query(message):
    question = message.lower().strip()
    download_phrases = (
        "download",
        "college form",
        "college forms",
        "application form",
        "application forms",
        "ncc enrollment form",
        "ncc enrolment form",
        "nss registration form",
        "nss enrollment form",
        "nss enrolment form",
        "hostel admission form",
        "hostel application form",
    )
    return any(phrase in question for phrase in download_phrases)

def get_latest_sp_announcements(limit=10, category=None):
    """Fetch and filter SP College announcements by category."""
    category_keywords = {
        "admission_fee": (
            "admission fee", "fee payment", "fee submission",
            "college component fee"
        ),
        "admission": (
            "admission", "selection list", "provisional selection",
            "application form", "admission round"
        ),
        "timetable": (
            "timetable", "time table", "date sheet", "exam schedule",
            "examination schedule"
        ),
        "hostel": (
            "hostel", "accommodation", "mess service"
        ),
        "tender": (
            "tender", "outsourcing", "quotation"
        ),
        "scholarship": (
            "scholarship", "pre-matric", "post-matric",
            "financial assistance"
        ),
    }
    with sqlite3.connect("spcollege_data.db") as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT title, item_date, url
            FROM sp_college_website_items
            WHERE item_type = 'notification'
            ORDER BY
                CASE WHEN item_date IS NULL OR item_date = ''
                     THEN 1 ELSE 0 END,
                item_date DESC
        """).fetchall()
    announcements = []
    for row in rows:
        original_title = row["title"] or ""
        title = re.sub(
            r"\s*;?\s*Dated:\s*\d{1,2}[-/][A-Za-z0-9-]+[-/]\d{2,4}.*$",
            "",
            original_title,
            flags=re.IGNORECASE
        ).strip()
        if category:
            keywords = category_keywords.get(category, ())
            if not any(word in title.lower() for word in keywords):
                continue
        announcements.append({
            "title": title or "View official notice",
            "date": row["item_date"],
            "url": row["url"]
        })
        if len(announcements) >= limit:
            break
    return announcements


def format_topic(topic_name):
    topic = get_topic(topic_name)
    if topic is None:
        return ""
    topic_id = topic[0]
    fields = get_topic_fields(topic_id)
    response = ""
    priority = [
        "Overview",
        "Programme Level",
        "Department",
        "Duration",
        "Eligibility",
        "Admission",
        "Admission Process",
        "Selection Process",
        "Documents",
        "Required Documents",
        "Examination Form",
        "Admit Card",
        "Date Sheet",
        "Result",
        "Re-evaluation",
        "Library Services",
        "Services",
        "Official Information",
        "Official Website",
        "Official Link"
    ]

    field_dict = {}
    for field in fields:
        field_dict[field[0]] = field[1]
    response += f"📘 {topic_name}\n\n"
    for item in priority:
        if item in field_dict:
            response += f"<b>{item}</b>\n"
            response += f"{field_dict[item]}\n\n"
    return response

def get_sp_college_response(user_question):
    sp_classification = classify_sp_college_question(user_question)
    print("SP College LLM Classification:", sp_classification)

    if sp_classification:
        print("SP Intent:", sp_classification.get("intent"))
        print("SP Entity:", sp_classification.get("entity"))
        print("SP Question Type:", sp_classification.get("question_type"))
        print("SP Programme Level:", sp_classification.get("level"))

    question_lower = user_question.lower().strip() 
    
    # Handle specific requests for college forms and downloads.
    specific_form_keywords = (
        "ncc form",
        "ncc enrollment",
        "ncc enrolment",
        "nss form",
        "nss registration",
        "nss enrollment",
        "nss enrolment",
        "hostel admission form",
        "hostel application form",
        "hostel registration form",
        "hostel enrollment form",
        "hostel enrolment form",
        "download form",
        "download forms",
        "college form",
        "college forms",
        "registration form",
        "enrollment form",
        "enrolment form",
    )

    # General application-form questions are too broad to assume
    # the user wants the Downloads page.
    general_application_request = (
        "application form" in question_lower
        or "application forms" in question_lower
    )

    specific_form_request = any(
        keyword in question_lower
        for keyword in specific_form_keywords
    )

    if specific_form_request and not (
        general_application_request
        and "hostel" not in question_lower
        and "ncc" not in question_lower
        and "nss" not in question_lower
    ):
        downloads_url = (
            "https://spcollege.edu.in/Main/List.aspx?Type=Download"
        )
        return (
            "<b>📥 SP College Downloads and Forms</b><br><br>"
            "Visit the official downloads section to check for "
            "available NCC, NSS, hostel admission, registration "
            "and other college forms.<br><br>"
            '<a href="' + downloads_url + '" target="_blank" '
            'rel="noopener noreferrer">'
            "Open Official Downloads and Forms</a>"
        )

    official_url = "https://spcollege.edu.in/Main/Default.aspx"
    contact_url = "https://spcollege.edu.in/Main/contactus.aspx"
    maps_url = "https://www.google.com/maps?q=34.075868,74.8204322"

    hostel_url = (
        "https://spcollege.edu.in/Main/List.aspx?Type=Download"
    )
    announcements_url = (
        "https://spcollege.edu.in/Main/List.aspx"
        "?SubType=Announcement&Type=Alert"
    )
    directorate_url = (
        "https://directorcollegesjk.in/authusers/"
        "collegeprofilepublic.aspx?shortcode=spc"
    )
    def official_link(url, label):
        return (
            f'<a href="{url}" target="_blank" '
            f'rel="noopener noreferrer">{label}</a>'
        )

    
    # Handle HOD questions directly from the department database.
    
    is_hod_query = bool(
        re.search(r"\bhod\b", question_lower)
        or (
            re.search(r"\bhead\b", question_lower)
            and (
                re.search(r"\bdepartment\b", question_lower)
                or re.search(r"\bof\b", question_lower)
            )
        )
    )

    if is_hod_query:
        department_aliases = {
            "information technology": ("information technology", "it"),
            "mathematics": ("mathematics", "maths", "math"),
            "human genetics": ("human genetics", "genetics"),
        }

        entity = ""
        if sp_classification:
            entity = (
                sp_classification.get("entity") or ""
            ).strip().lower()

        department_db_path = (
            Path(__file__).resolve().parent / "knowledge.db"
        )

        try:
            with sqlite3.connect(department_db_path) as conn:
                conn.row_factory = sqlite3.Row
                departments = conn.execute("""
                    SELECT department, hod, hod_contact
                    FROM sp_college_departments
                """).fetchall()

            requested_department = None

            for department in departments:
                name = (
                    department["department"] or ""
                ).strip().lower()

                aliases = department_aliases.get(name, (name,))
                search_text = re.sub(
                    r"\bdepartment\b",
                    "",
                    f"{question_lower} {entity}"
                )
                search_text = re.sub(r"\s+", " ", search_text).strip()

                if any(
                    re.search(
                        rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])",
                        search_text
                    )
                    for alias in aliases
                ):
                    requested_department = department
                    break

            if requested_department:
                department_name = requested_department["department"]
                hod = requested_department["hod"]

                if hod and str(hod).strip():
                    hod_contact = requested_department["hod_contact"]

                    response = (
                        f"The HOD of {department_name} Department is "
                        f"<b>{hod}</b>."
                    )

                    if hod_contact and str(hod_contact).strip():
                        hod_contact = str(hod_contact).strip()

                        # Support both phone numbers and email addresses.
                        contacts = re.split(r"[,;\n]+", hod_contact)

                        for contact in contacts:
                            contact = contact.strip()

                            if not contact:
                                continue

                            if "@" in contact:
                                response += (
                                    f"<br>Email: "
                                    f'<a href="mailto:{contact}">{contact}</a>'
                                )
                            else:
                                phone = re.sub(r"[^\d+]", "", contact)

                                if phone:
                                    response += (
                                        f"<br>Phone: "
                                        f'<a href="tel:{phone}">{contact}</a>'
                                    )

                    return response

            return (
                "I couldn't verify the HOD for that department in my saved "
                "information. Please check "
                '<a href="https://spcollege.edu.in/Main/PeopleList.aspx" '
                'target="_blank" rel="noopener noreferrer">'
                "the official SP College people directory</a>."
            )
        except sqlite3.Error as error:
            print("Department HOD lookup error:", error)

    if any(term in question_lower for term in (
        "principal",
        "college overview",
        "college established",
        "college address",
        "college email",
        "overview of sri pratap college",
        "overview of sp college",
        "overview of spc",
        "tell me about",
        "information about",
        "details about",
        "about spc",
        "about sp college",
        "about sri pratap college",
    )):
        college_db_path = Path(__file__).resolve().parent / "knowledge.db"
        try:
            with sqlite3.connect(college_db_path) as conn:
                conn.row_factory = sqlite3.Row
                college = conn.execute("""
                    SELECT *
                    FROM college_master
                    WHERE LOWER(short_name) LIKE '%sp college%'
                       OR LOWER(college_name) LIKE '%sri pratap college%'
                    LIMIT 1
                """).fetchone()
            if college:
                if "principal" in question_lower:
                    principal = college["principal"]
                    if principal and str(principal).strip():
                        return (
                            "The principal of Sri Pratap College is "
                            f"<b>{principal}</b>."
                        )
                elif "established" in question_lower:
                    return (
                        "Sri Pratap College was established in "
                        f"<b>{college['established']}</b>."
                    )
                elif "address" in question_lower:
                    return (
                        "<b>Sri Pratap College Address</b><br>"
                        f"{college['address']}"
                    )
                elif "email" in question_lower:
                    email = college["official_email"]
                    if email and str(email).strip():
                        return (
                            "Official email: "
                            f'<a href="mailto:{email}">{email}</a>'
                        )
                
                elif any(phrase in question_lower for phrase in (
                    "overview",
                    "tell me about",
                    "information about",
                    "details about",
                    "about spc",
                    "about sp college",
                    "about sri pratap college",
                )):
                    overview = college["overview"]
                    if overview and str(overview).strip():
                        return overview


        except sqlite3.Error as error:
            print("College master lookup error:", error)
    
    # Answer department-specific questions from the imported Excel data.
    department_keywords = (
        "department", "hod", "head of department", "programmes offered",
        "programs offered", "facilities", "hostel", "scholarship",
        "hod contact", "department contact"
    )
    if any(keyword in question_lower for keyword in department_keywords):
        department_db_path = Path(__file__).resolve().parent / "knowledge.db"
        try:
            with sqlite3.connect(department_db_path) as conn:
                conn.row_factory = sqlite3.Row
                departments = conn.execute("""
                    SELECT *
                    FROM sp_college_departments
                """).fetchall()
            question_words = set(re.findall(r"[a-zA-Z]+", question_lower))
            best_department = None
            best_score = 0
            for department in departments:
                department_name = (
                    department["department"] or ""
                ).strip().lower()

                if not department_name:
                    continue

                department_words = set(
                    re.findall(r"[a-zA-Z]+", department_name)
                )
                score = len(question_words & department_words)

                if department_name in question_lower:
                    score += 5

                if score > best_score:
                    best_score = score
                    best_department = department
            # Handle hostel-fee questions that do not name a department.
            if (
                "hostel" in question_lower
                and any(word in question_lower for word in ("fee", "fees", "cost", "charges"))
                and best_score == 0
            ):
                hostel_fee = next(
                    (
                        department["hostel_fee"]
                        for department in departments
                        if department["hostel_fee"]
                        and str(department["hostel_fee"]).strip()
                    ),
                    None
                )
                
                if hostel_fee:
                    return (
                        "<b>🏠 SP College Hostel Fee</b><br>"
                        f"{hostel_fee}<br><br>"
                        f"📄 {official_link(hostel_url, 'Hostel forms and downloads')}<br>"
                        f"📢 {official_link(announcements_url, 'Hostel announcements')}<br>"
                        f"🏛 {official_link(directorate_url, 'Official college profile')}"
                    )

            if best_department and best_score > 0:
                department_name = best_department["department"]
                question_type = question_lower
                
                if (
                    "contact" in question_type
                    or "email" in question_type
                    or "phone" in question_type
                    or "number" in question_type
                ):
                    hod = best_department["hod"]
                    contact = best_department["hod_contact"]
                    faculty_url = (
                        "https://spcollege.edu.in/Main/ViewPage.aspx"
                        "?Page=IT_FACULTY"
                    )
                    department_contact_url = (
                        "https://spcollege.edu.in/Main/ViewPage.aspx"
                        "?Page=IT_Contact"
                    )
                    response = (
                        f"<b>📋 Contact Details — {department_name}</b><br>"
                    )
                    if hod and str(hod).strip():
                        response += f"👤 HOD: <b>{hod}</b><br>"
                    if contact and str(contact).strip():
                        contact = str(contact).strip()
                        if "@" in contact:
                            response += (
                                f'✉️ Email: <a href="mailto:{contact}">'
                                f"{contact}</a><br>"
                            )
                        else:
                            phone = re.sub(r"[^\d+]", "", contact)
                            response += (
                                f'📞 Phone: <a href="tel:{phone}">'
                                f"{contact}</a><br>"
                            )
                    response += (
                        "<br>🔗 "
                        f'{official_link(faculty_url, "Official faculty page")}<br>'
                        "🔗 "
                        f'{official_link(department_contact_url, "Department contact page")}'
                    )
                    return response
                elif "hod" in question_type or "head of department" in question_type:
                    value = best_department["hod"]
                    label = f"HOD of {department_name}"
                elif "hostel fee" in question_type or "fee" in question_type:
                    value = best_department["hostel_fee"]
                    label = f"Hostel fee for {department_name}"
                elif "hostel" in question_type:
                    value = best_department["hostel_available"]
                    label = f"Hostel availability for {department_name}"
                elif "scholarship" in question_type:
                    value = best_department["scholarships"]
                    label = f"Scholarships for {department_name}"
                elif "facility" in question_type or "facilities" in question_type:
                    value = best_department["facilities"]
                    label = f"Facilities in {department_name}"
                elif "programme" in question_type or "program" in question_type or "course" in question_type:
                    value = best_department["programmes_offered"]
                    label = f"Programmes offered by {department_name}"
                elif "level" in question_type or "ug" in question_type or "pg" in question_type:
                    value = best_department["level"]
                    label = f"Programme level for {department_name}"
                else:
                    value = best_department["overview"]
                    label = f"About the {department_name} Department"
                if value and str(value).strip():
                    return f"<b>{label}</b><br>{value}"
        except sqlite3.Error as error:
            print("Department lookup error:", error)
    
    if (
        sp_classification
        and sp_classification.get("intent") == "admission"
        and any(phrase in question_lower for phrase in (
            "admission process",
            "how to apply",
            "how can i apply",
            "steps for admission",
            "admission procedure",
        ))
    ):
        return (
            "For admission-process details, please check the "
            '<a href="https://spcollege.edu.in/Main/Default.aspx" '
            'target="_blank" rel="noopener noreferrer">'
            "official SP College website</a> and its "
            '<a href="https://spcollege.edu.in/Main/List.aspx?Type=QuickLink" '
            'target="_blank" rel="noopener noreferrer">'
            "Quick Links</a> for application resources and current instructions."
        )

    def website_fallback():
        return (
            "Sorry, I couldn't find a verified answer in my saved "
            "SP College information. Please check the "
            f'<a href="{official_url}" target="_blank" '
            'rel="noopener noreferrer">official SP College website</a> '
            "or its "
            f'<a href="{contact_url}" target="_blank" '
            'rel="noopener noreferrer">contact page</a> '
            "for the latest details."
        )
    
    question = user_question.lower()
    db_path = Path(__file__).resolve().parent / "knowledge.db"

    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT *
                FROM academic_programmes
                WHERE LOWER(TRIM(college))
                      LIKE '%sri pratap college%'
                ORDER BY programme, specialization
            """).fetchall()
            programmes = [dict(row) for row in rows]
    except sqlite3.Error as error:
        print("SP College database error:", error)
        programmes = []

    # Identify what information the student is asking for.
    requested_field = None

    field_keywords = {
        "fee": ("fee", "fees", "tuition", "cost"),
        "duration": ("duration", "how long", "years long"),
        "eligibility": ("eligibility", "eligible", "qualification"),
        "intake": ("intake", "seats", "seat capacity"),
        "admission_process": ("admission process", "how to apply"),
        "selection_process": ("selection process", "selection criteria"),
        "overview": ("overview", "about this programme", "about this program"),
        "department": ("department", "which department"),
        "programme_type": ("programme type", "program type"),
        "level": ("programme level", "program level", "undergraduate", "postgraduate"),
        "subject_overview": ("subjects", "subject details", "what do we study"),
    }

    for field, keywords in field_keywords.items():
        if any(word in question for word in keywords):
            requested_field = field
            break

    
    # Recognise common abbreviations in course names.
    normal_question = re.sub(r"[^a-z0-9 ]", " ", question)
    normal_question = re.sub(r"\s+", " ", normal_question).strip()

    # Set safe defaults so these variables always exist.
    entity = ""
    question_type = ""
    level = "unknown"

    # Use the SP College LLM classification when available.
    if sp_classification:
        entity = str(
            sp_classification.get("entity") or ""
        ).strip()
        question_type = str(
            sp_classification.get("question_type") or ""
        ).strip().lower()
        level = str(
            sp_classification.get("level") or "unknown"
        ).strip().lower()

    if (
        sp_classification
        and sp_classification.get("intent") == "programme"
        and entity
    ):
        normal_question = f"{question_type} {entity.lower()}"

    # Normalize the query.
    normal_question = re.sub(
        r"[^a-z0-9 ]", " ", normal_question
    )
    normal_question = re.sub(
        r"\s+", " ", normal_question
    ).strip()

    # Preserve the requested programme level.
    if level in ("ug", "pg", "integrated"):
        if level not in normal_question.split():
            normal_question += f" {level}"

    print("SP Normalized Programme Query:", normal_question)




    # Normalize common programme abbreviations.
    normal_question = re.sub(
        r"\bm\s*\.?\s*sc\s+it\b",
        "msc information technology",
        normal_question
    )

    normal_question = re.sub(
        r"\bmsc\s+it\b",
        "msc information technology",
        normal_question
    )

    normal_question = re.sub(
        r"\bbsc\s+it\b",
        "bsc information technology",
        normal_question
    )
    stop_words = {
        "what", "is", "are", "the", "for", "of", "at", "in",
        "a", "an", "does", "do", "this", "that", "college",
        "sp", "sri", "pratap", "tell", "me", "about", "please",
        "give", "show", "can", "you", "has", "have", "available",
        "offer", "offers", "course", "courses", "programme",
        "programmes", "program", "programs", "fee", "fees",
        "tuition", "cost", "duration", "long", "eligibility",
        "eligible", "qualification", "intake", "seats", "seat",
        "department", "subjects", "subject", "details",
        "admission", "process", "apply", "selection", "criteria",
        "overview", "information", "technology"
    }

    question_terms = {
        word for word in normal_question.split()
        if word not in stop_words and len(word) > 1
    }

    # Include common course abbreviations in the matching terms.
    if "information technology" in normal_question:
        question_terms.add("technology")
        question_terms.add("information")
    matching_programmes = []
    for record in programmes:
        course_name = " ".join(
            str(record.get(field) or "")
            for field in ("programme", "specialization", "department")
        ).lower()
        course_name = re.sub(r"[^a-z0-9 ]", " ", course_name)
        course_name = re.sub(r"\s+", " ", course_name).strip()
        if not question_terms:
            continue
        matched_terms = sum(
            1 for term in question_terms if term in course_name.split()
        )
        if matched_terms:
            matching_programmes.append((matched_terms, record))
    matching_programmes.sort(
        key=lambda item: item[0],
        reverse=True
    )
    
    # General question: list all programmes, optionally filtered by level.
    asks_for_all_courses = bool(
        re.search(
            r"\b(courses?|programmes?|programs?)\b.*\b(offered|available|provide|provided)\b",
            question
        )
        or any(phrase in question for phrase in (
            "all courses",
            "list of courses",
            "what courses",
            "which courses",
            "what programmes",
            "what programs",
        ))
    )

    if programmes and asks_for_all_courses:
        
        requested_level = (
            str(sp_classification.get("level") or "unknown").strip().lower()
            if sp_classification else "unknown"
        )

        level_aliases = {
            "undergraduate": "ug",
            "under graduate": "ug",
            "postgraduate": "pg",
            "post graduate": "pg",
            "integrated": "integrated",
            "ug": "ug",
            "pg": "pg",
        }
        requested_level = level_aliases.get(
            requested_level, requested_level
        )

        listed_programmes = programmes

        if requested_level in ("ug", "pg", "integrated"):
            listed_programmes = [
                record for record in programmes
                if str(record.get("level") or "").strip().lower()
                in (
                    {"ug", "undergraduate", "under graduate"}
                    if requested_level == "ug"
                    else {"pg", "postgraduate", "post graduate"}
                    if requested_level == "pg"
                    else {"integrated"}
                )
            ]


        if not listed_programmes:
            return (
                "I couldn't find any matching "
                f"{requested_level.upper()} courses in the saved "
                "SP College database. Please check the "
                '<a href="https://spcollege.edu.in/Main/CourseList.aspx" '
                'target="_blank" rel="noopener noreferrer">'
                "official SP College course list</a>."
            )

        course_list = []
        seen = set()

        for record in listed_programmes:
            name = str(record.get("programme") or "Programme")
            specialization = record.get("specialization")
            record_level = record.get("level")

            if specialization:
                name += " - " + str(specialization)
            if record_level:
                name += " (" + str(record_level) + ")"

            if name.lower() not in seen:
                seen.add(name.lower())
                course_list.append(name)

        heading = (
            f"{requested_level.upper()} programmes offered at Sri Pratap College"
            if requested_level in ("ug", "pg", "integrated")
            else "Programmes offered at Sri Pratap College"
        )

        return (
            f"<b>{heading}</b><br><br>"
            + "<br>".join("• " + name for name in course_list)
            + "<br><br>For current availability, check the "
            '<a href="https://spcollege.edu.in/Main/Default.aspx" '
            'target="_blank" rel="noopener noreferrer">'
            "official SP College website</a>."
            "<br><br>📚 View the "
            '<a href="https://spcollege.edu.in/Main/CourseList.aspx" '
            'target="_blank" rel="noopener noreferrer">'
            "Official Course List</a> for course details, duration, "
            "intake and coordinators."
        )

    # Specific programme question: return the requested database field.
    if programmes and matching_programmes:
                # Filter programme results using the LLM's recognised level.
        if sp_classification and matching_programmes:
            requested_level = sp_classification.get("level", "unknown")

            if requested_level in ("ug", "pg", "integrated"):
                level_filtered = [
                    item for item in matching_programmes
                    if str(item[1].get("level", "")).strip().lower()
                    == requested_level
                ]

                if level_filtered:
                    matching_programmes = level_filtered
        best_score = matching_programmes[0][0]
        # Keep close matches so similar programme records can be shown.
        best_records = [
            record for score, record in matching_programmes
            if score == best_score
        ]
        # Avoid returning unrelated records for a weak match.
        if best_score >= 1:
            details = []
            for record in best_records[:5]:
                programme_name = str(
                    record.get("programme") or "Programme"
                )
                specialization = record.get("specialization")
                if specialization:
                    programme_name += " - " + str(specialization)
                if requested_field:
                    value = record.get(requested_field)
                    if value is None or not str(value).strip():
                        value = "This detail is not recorded in the database."
                    details.append(
                        f"<b>{programme_name}</b><br>"
                        + (
                            f"Duration: {record.get('duration') or 'Not recorded'}<br>"
                            if requested_field != "duration"
                            else ""
                        )
                        + f"{requested_field.replace('_', ' ').title()}: {value}"
                    )
                else:
                    details.append(
                        f"<b>{programme_name}</b><br>"
                        f"Level: {record.get('level') or 'Not recorded'}<br>"
                        f"Duration: {record.get('duration') or 'Not recorded'}<br>"
                        f"Eligibility: {record.get('eligibility') or 'Not recorded'}"
                    )
                heading = (
                    "Yes, the database lists these SP College programme options:"
                    if any(word in question for word in (
                        "available", "offered", "offer", "does it have"
                    ))
                    else "SP College Programme Information"
                )  

            return (
                f"<b>{heading}</b><br><br>"
                + "<br><br>".join(details)
                + "<br><br>Please verify current details on the "
                '<a href="https://spcollege.edu.in/Main/Default.aspx" '
                'target="_blank" rel="noopener noreferrer">'
                "official SP College website</a>."
            )
    matches = search_sp_college(user_question)
    if not matches:
        college_answer = college_response(user_question)
        if college_answer:
            return college_answer
        return website_fallback()
    question = user_question.lower()
    best_match = matches[0]
    content = best_match["chunk_text"]
    source_url = best_match["source_url"]
    def link(url, label):
        return (
            f'<a href="{url}" target="_blank" '
            f'rel="noopener noreferrer">{label}</a>'
        )
    answer = None
    # Phone number
    if any(term in question for term in (
        "phone", "telephone", "call", "mobile number",
        "contact number", "phone number"
    )):
        answer = (
            "The official phone number of Sri Pratap College is "
            '<a href="tel:+911942476828">0194-2476828</a>.'
        )

    # Email address
    elif "email" in question or "e-mail" in question or "mail address" in question:
        answer = (
            "Official email: "
            '<a href="mailto:sri-pratap-college@jk.gov.in">'
            "sri-pratap-college@jk.gov.in</a><br>"
            "Additional college email: "
            '<a href="mailto:spcsgr1905@gmail.com">'
            "spcsgr1905@gmail.com</a>"
        )

    # Map or directions
    elif any(term in question for term in (
        "map", "direction", "directions", "google maps",
        "route", "navigate"
    )):
        answer = (
            "Open the college location in "
            f'{link(maps_url, "Google Maps")}.'
        )

    # Address or location
    elif any(term in question for term in (
        "where", "location", "located", "situated",
        "address", "reach the college", "get there"
    )):
        answer = (
            "<b>Full address:</b><br>"
            "Sri Pratap College<br>"
            "M.A. Road, Srinagar<br>"
            "Jammu and Kashmir, India - 190001<br><br>"
            f'{link(maps_url, "View location on Google Maps")}'
        )

    # Establishment year
    elif any(term in question for term in (
        "established", "establishment", "founded"
    )):
        answer = "Sri Pratap College was established in 1905."

    # Official website
    elif any(term in question for term in (
        "website", "webpage", "web site", "official site"
    )):
        answer = link(official_url, "Visit the official SP College website")
    
    # SP College announcements with category filtering
    q_lower = user_question.lower()
    if answer is None:
        # Handle exact deadlines separately; do not invent dates.
        if any(term in q_lower for term in (
            "deadline", "last date", "exact date",
            "when does", "when is the last"
        )):
            return (
                "I couldn't verify the requested deadline in my saved "
                "SP College information. Please check "
                f'{link("https://spcollege.edu.in/Main/List.aspx?SubType=Announcement&Type=Alert", "official SP College announcements")} '
                "for the relevant notice and its confirmed dates."
            )

        category = None

        # Check fee-specific phrases before general admission phrases.
        if any(word in q_lower for word in (
            "admission fee notice", "admission fee notices",
            "admission fee notification", "admission fee notifications",
            "admission fee update", "admission fee updates",
            "admission fee announcement", "admission fee announcements",
            "show admission fee", "latest admission fee",
            "fee notices", "fee notifications"
        )):
            category = "admission_fee"

        elif any(word in q_lower for word in (
            "admission notification", "admission notifications",
            "exam notification", "exam notifications",
            "admission notice", "admission notices",
            "admission updates", "admission announcements",
            "latest admission", "show admission",
            "selection list", "application form"
        )):
            category = "admission"

        elif any(word in q_lower for word in (
            "timetable", "time table", "date sheet",
            "exam schedule", "examination schedule",
            "timetable notice", "timetable notification"
        )):
            category = "timetable"

        elif any(word in q_lower for word in (
            "hostel notice", "hostel notices",
            "hostel notification", "hostel notifications",
            "hostel announcement", "hostel announcements",
            "hostel updates", "show hostel",
            "accommodation notice", "accommodation notices"
        )):
            category = "hostel"

        elif any(word in q_lower for word in (
            "tender", "tenders", "tender notice",
            "tender notices", "tender notification",
            "tender notifications", "outsourcing notice",
            "quotation notice"
        )):
            category = "tender"

        elif any(word in q_lower for word in (
            "scholarship", "scholarships",
            "scholarship notice", "scholarship notices",
            "scholarship notification", "scholarship notifications",
            "scholarship updates", "show scholarship"
        )):
            category = "scholarship"

        is_notice_query = any(word in q_lower for word in (
            "announcement", "announcements",
            "notification", "notifications",
            "notice", "notices",
            "latest update", "latest updates",
            "latest", "recent", "show notices",
            "list notices", "all notices"
        ))

        if category or is_notice_query:
            announcements = get_latest_sp_announcements(
                limit=10,
                category=category
            )

            category_titles = {
                "admission_fee": "Admission Fee Notices",
                "admission": "Admission Notifications",
                "timetable": "Timetables and Exam Schedules",
                "hostel": "Hostel Notices",
                "tender": "Tender Notices",
                "scholarship": "Scholarship Notifications",
            }

            heading = category_titles.get(
                category, "Latest Announcements"
            )

            announcements_url = (
                "https://spcollege.edu.in/Main/List.aspx"
                "?SubType=Announcement&Type=Alert"
            )

            if not announcements:
                return (
                    f"No matching {heading.lower()} were found in the "
                    "saved announcements. Please check "
                    f'{link(announcements_url, "official SP College announcements")}.'
                )

            answer = (
                f"🏛 <b>{heading} — Sri Pratap College</b><br><br>"
            )

            for item in announcements:
                title = item["title"] or "View official notice"
                url = item["url"]
                date = item["date"]

                if url:
                    answer += f"• {link(url, title)}"
                else:
                    answer += f"• {title}"

                if date:
                    try:
                        display_date = datetime.strptime(
                            date, "%Y-%m-%d"
                        ).strftime("%d-%m-%Y")
                    except ValueError:
                        display_date = date

                    answer += f" — <b>Date:</b> {display_date}"

                answer += "<br><br>"

            answer += link(
                announcements_url,
                "View all official announcements"
            )

            return answer

        # General admission resources, not a request for notices.
        elif any(term in q_lower for term in (
            "admission", "admissions", "brochure",
            "quick link", "quick links", "syllabus"
        )):
            quick_links_url = (
                "https://spcollege.edu.in/Main/List.aspx?Type=QuickLink"
            )
            answer = (
                "For admission brochures, application resources and "
                "syllabus links, visit "
                f'{link(quick_links_url, "SP College Quick Links")}.'
            )
        # Other details must not be invented.
        elif any(term in q_lower for term in (
            "eligibility", "fee", "fees", "result",
            "timetable", "exam", "examination"
        )):
            return website_fallback()
    if not answer:
        return website_fallback()
    # Avoid repeating a document title when the answer already
    # contains a list of clickable notifications.
    if "Admission Notifications — Sri Pratap College" in (answer or ""):
        return answer
    return (
        f"🏛 <b>{best_match['title']}</b><br><br>"
        f"{answer}<br><br>"
        f"<b>Official source:</b> "
        f'{link(source_url, "View source")}'
    )

def build_response(user_question):
    original_question = user_question
    user_question = correct_spelling(user_question)
    
# Handle location follow-ups using conversation context
    question = user_question.lower().strip()

    location_followups = {
        "where is it located",
        "where is it located?",
        "where is it",
        "where is it?",
        "where is it situated",
        "where is it situated?",
    }

    if question in location_followups:
        context = conversation_context.get_context()

        last_college = context.get("last_college")
        last_query_type = context.get("last_query_type")

        if last_college and last_college.lower() in {
            "sp college",
            "sri pratap college",
            "spc",
        }:
            return get_sp_college_response("location")

        if last_query_type == "university":
            return university_response(
                "where is Cluster University Srinagar located"
            )

    print(f"Spell correction: {original_question!r} -> {user_question!r}")
    print("\n===== RESPONSE BUILDER =====")
    print("Question:", user_question)
    start = time.time()
    question_lower = user_question.lower().strip()

    # Keep Cluster University as an optional feature.
    # Explicit CUS questions continue to the existing CUS handlers.
    
    # Handle university questions without using the old CUS handlers.
    normalized_question = re.sub(
        r"[^a-z0-9 ]", " ", question_lower
    )
    normalized_question = re.sub(
        r"\s+", " ", normalized_question
    ).strip()

    
# Handle SP College affiliation questions before LLM classification.
    question_lower = user_question.lower()

    affiliation_phrases = [
        "affiliated to",
        "affiliated with",
        "affiliation of",
        "which university is sp college affiliated",
        "which university does sp college belong to",
    ]

    is_sp_affiliation_question = (
        ("sp college" in question_lower or "spc" in question_lower)
        and any(phrase in question_lower for phrase in affiliation_phrases)
    )

    if is_sp_affiliation_question:
        return (
            "Sri Pratap College (SP College) is affiliated with "
            "Cluster University Srinagar (CUS)."
        )

    # Use the LLM to identify SP College affiliation questions.
        # Classify the question once and reuse the result.
    llm_classification = classify_with_llm(user_question)
    
# Allow only questions within the SP College chatbot's scope.
    entity = (
        llm_classification.get("entity") or ""
    ).lower().strip() if isinstance(llm_classification, dict) else ""

    allowed_entities = {
        "sp college",
        "sri pratap college",
        "cluster university srinagar",
        "cus",
        "cu",
    }

    
    # Reject only when the classifier identifies another institution
    # AND the user explicitly mentions that institution in the question.
    entity_words = re.findall(r"[a-z0-9]+", entity)

    generic_entities = {
    "admission", "admissions",
    "notification", "admission notification",
    "college", "courses", "programmes", "programs",
    "ug courses", "pg courses",
    }

    explicitly_mentions_other_entity = (
        entity
        and entity not in allowed_entities
        and entity not in generic_entities
        and len(entity_words) >= 2
        and all(word in question_lower for word in entity_words)
    )

        # Allow SP College HOD and programme questions before scope rejection.
    sp_question = user_question.lower().strip()

    is_sp_hod_question = bool(
        re.search(r"\b(hod|head)\b", sp_question)
        and re.search(
            r"\b(it|information technology|department)\b",
            sp_question
        )
    )

    mentions_msc_it = bool(
        re.search(r"\b(m\.?\s*sc|master of science)\b", sp_question)
        and re.search(r"\b(it|information technology)\b", sp_question)
    )

    asks_programme_availability = bool(
        re.search(
            r"\b(provide|provides|provided|offer|offers|offered|"
            r"available|have|has)\b",
            sp_question
        )
    )

    asks_programme_detail = bool(
        re.search(
            r"\b(fee|fees|cost|duration|eligibility|intake|"
            r"seats|department|subjects)\b",
            sp_question
        )
    )

    is_sp_programme_question = (
        mentions_msc_it
        and (asks_programme_availability or asks_programme_detail)
    )

    if is_sp_hod_question or is_sp_programme_question:
        print("SP SPECIAL ROUTE:", is_sp_hod_question, is_sp_programme_question)

        answer = get_sp_college_response(user_question)
        print("SP HANDLER ANSWER:", repr(answer))

        if answer:
            conversation_context.last_college = "Sri Pratap College"
            conversation_context.last_query_type = "college"
            return answer

        if explicitly_mentions_other_entity:
            is_faculty_query = any(
                term in question_lower
                for term in (
                    "faculty", "teacher", "teachers",
                    "professor", "professors",
                    "lecturer", "lecturers",
                    "teaching staff", "staff members"
                )
            )

            if not is_faculty_query:
                return (
                    "This is a SP College chatbot. Please ask questions "
                    "about SP College only."
                )

  

    is_affiliation_question = (
        isinstance(llm_classification, dict)
        and llm_classification.get("intent", "").lower().strip()
        == "sp_college_affiliation"
    )

    
    university_terms = (
        "cluster university",
        "cusrinagar.edu.in",
        "cusrinagar",
        "vice chancellor",
        "vice-chancellor",
        "vicechancellor",
        "chancellor",
        "registrar",
        "university",
        "universities",
        "vc of",
        "vc name",
        "university website",
        "university admission",
        "university admissions",
        "university notification",
        "university notifications",
        "university result",
        "university results",
        "university syllabus",
        "university prospectus",
        "university examination",
        "university exam",
        "university contact",
        "university address",
        "university programmes",
        "university programs",
        "university courses",
        "university facilities",
    )


    explicit_cus_query = any(
        term in question_lower
        for term in university_terms
    )

    if is_affiliation_question:
        return (
            "Sri Pratap College (SP College) is affiliated with "
            "<b>Cluster University Srinagar</b>.<br><br>"
            'For more information, visit the '
            '<a href="https://www.cusrinagar.edu.in/" '
            'target="_blank" rel="noopener noreferrer">'
            'official Cluster University Srinagar website</a>.'
        )

        # Handle Cluster University syllabus questions before the general CU redirect.
    is_cu_syllabus = (
        "syllabus" in question_lower
        and (
            "university" in question_lower
            or "cluster university" in question_lower
            or re.search(r"\b(?:cu|cus)\b", question_lower)
        )
    )

    if is_cu_syllabus:
        return (
            "📚 <b>University Syllabus</b><br><br>"
            "You can view the official Cluster University Srinagar "
            "syllabus here:<br><br>"
            '<a href="https://www.cusrinagar.edu.in/Syllabus/Index/True?pp=UG" '
            'target="_blank" rel="noopener noreferrer">'
            '📖 View Official Syllabus</a>'
        )

    if explicit_cus_query and not is_affiliation_question:
        return (
            "For this university-related information, please visit "
            '<a href="https://www.cusrinagar.edu.in/" '
            'target="_blank" rel="noopener noreferrer">'
            'the official Cluster University Srinagar website</a>.'
        )


    # SP College is the default for college-related questions.
    sp_college_terms = (
        "sp college",
        "sp",
        "s.p. college",
        "s p college",
        "sri pratap",
        "spcollege.edu.in",
        "this college",
        "the college",
        "our college",
        "college",
        
    )

    sp_topic_terms = (
        "admission",
        "admissions",
        "course",
        "courses",
        "programme",
        "program",
        "programmes",
        "programs",
        "department",
        "departments",
        "syllabus",
        "fee",
        "fees",
        "hostel",
        "library",
        "laboratory",
        "laboratories",
        "labs",
        "principal",
        "hod",
        "head of department",
        "faculty",
        "staff",
        "examination",
        "exam",
        "result",
        "results",
        "notice",
        "notices",
        "notification",
        "notifications",
        "timetable",
        "contact",
        "address",
        "location",
        "phone",
        "telephone",
        "email",
        "website",
        "map",
        "directions",
        "established",
        "establishment",
        "campus",
        "facilities",
        "prospectus",
        "brochure",
        "scholarship",
        "eligibility",
        "duration",
        "intake",
        "tuition",
        "cost",
        "qualification",
        "seats",
        "programme type",
        "download",
        "downloads",
        "form",
        "forms",
        "application",
        "applications",
        "ncc",
        "nss",
        "enrollment",
        "enrolment",
        "registration",
    )

    
    # Identify other colleges using the existing aliases
    normalized_question = question_lower.lower()

    mentions_other_college = any(
        alias in normalized_question
        and college != "sri pratap college"
        for alias, college in COLLEGE_ALIASES.items()
        if alias not in ("sp", "spc", "sp college")
    )

    if mentions_other_college:
        return (
            "This is an SP College website chatbot. "
            "Please ask questions about SP College only."
        )


    
    if not explicit_cus_query and (
        any(term in question_lower for term in sp_college_terms)
        or any(term in question_lower for term in sp_topic_terms)
    ):
        
        print("SP COLLEGE QUERY DETECTED")

        conversation_context.last_college = "Sri Pratap College"
        conversation_context.last_query_type = "college"

        # Handle faculty queries using the admin-managed database
        faculty_keywords = (
            "faculty", "teacher", "teachers", "professor", "professors",
            "lecturer", "lecturers", "teaching staff", "staff members"
       )

        if any(term in question_lower for term in faculty_keywords):
            department = None

            department_prefixes = (
                "department of ", "faculty of ", "teachers of ",
                "staff of ", "professors of ", "lecturers of ",
                "in the ", "in ", "of "
           )

            for prefix in department_prefixes:
                if prefix in question_lower:
                    candidate = question_lower.split(prefix, 1)[1].strip(" ?.!")

                    for ending in (
                        " department", " faculty", " teachers",
                        " professors", " lecturers", " teaching staff",
                        " staff", " please"
                   ):
                        if candidate.endswith(ending):
                           candidate = candidate[:-len(ending)].strip()

                    if candidate:
                        department = candidate
                        break

            
            # Convert department abbreviations using existing aliases
            if department:
                department_key = department.strip().lower()
                department = PROGRAMME_ALIASES.get(
                    department_key,
                    department_key
                )

            members = get_faculty_members(
                department=department,
                active_only=True
            )


            if members:
                answer = "<b>SP College Faculty</b><br><br>"

                for member in members:
                    answer += f"<b>{member['name']}</b><br>"
                    answer += f"Department: {member['department']}<br>"

                    if member.get("designation"):
                        answer += f"Designation: {member['designation']}<br>"

                    if member.get("email"):
                        email = member["email"]
                        answer += f'Email: <a href="mailto:{email}">{email}</a><br>'

                    if member.get("phone"):
                        answer += f"Phone: {member['phone']}<br>"

                    if member.get("office"):
                        answer += f"Office: {member['office']}<br>"

                    answer += "<br>"

                return answer

            if department:
                return f"No active faculty members were found for '{department}'."

            return "No active faculty members were found in the database."

        # Keep the existing static SP College response as the fallback
        return get_sp_college_response(user_question)


    print("SP ROUTING CHECK:", question_lower)

   
    # Continue into the existing Cluster University handlers.
    context = conversation_context.get_context()
    print("Initial context:", context)

    # CONTEXTUAL PROGRAMME FOLLOW-UP
    last_programme = context.get("last_programme")   
    programme_follow_up = (
        last_programme
        and (
            user_question.startswith("what about ")
            or user_question.startswith("how about ")
            or user_question.startswith("and ")
            or user_question in [
                "tell me more",
                "tell me more about it",
                "more information",
                "more about it",
                "more about this",
                "more about that",
                "about it",
                "about this",
                "about that"
            ]
        )
    )
    if programme_follow_up:
        print("CONTEXTUAL PROGRAMME FOLLOW-UP DETECTED")
        print("Previous programme:", last_programme)
        return programme_response(user_question)


    # Handle location follow-ups before programme detection
    question = user_question.lower().strip()

    location_followups = {
        "where is it located",
        "where is it located?",
        "where is it",
        "where is it?",
        "where is it situated",
        "where is it situated?",
    }

    if question in location_followups:
        context = conversation_context.get_context()

        last_college = context.get("last_college")
        last_query_type = context.get("last_query_type")

        if last_college and last_college.lower() in {
            "sp college",
            "sri pratap college",
            "spc",
        }:
            return get_sp_college_response("location")

        if last_query_type == "university":
            return university_response(
               "where is Cluster University Srinagar located"
            )

        return "Could you please specify which college or university you mean?"

    

    # GENERAL ADMISSION
    explicit_programme_query = is_known_programme_question(
        user_question
    )
    print("EXPLICIT PROGRAMME QUERY:", explicit_programme_query)
    if not explicit_programme_query:
        general_admission_response = get_general_admission_response(
            user_question
        )
        print(
            "GENERAL ADMISSION RESPONSE:",
            repr(general_admission_response)
        )
        if general_admission_response:
            print("General Admission Time")
            return general_admission_response

    question_lower = user_question.lower().strip()
    question_lower = re.sub(r"[?.!,]+$", "", question_lower).strip()

    last_programme = context.get("last_programme")
    follow_up_words = {
        "it",
        "its",
        "this",
        "that"
    }
    programme_words = {
        "ba",
        "bsc",
        "bca",
        "bba",
        "bcom",
        "bed",
        "ma",
        "msc",
        "mca",
        "mba",
        "mcom",
        "med"
    }

    question_words = set(question_lower.split())

    explicit_programme = bool(
        question_words.intersection(programme_words)
    )

    
    follow_up_intent_words = (
        contains_any(question_lower, FEE)
        or contains_any(question_lower, DURATION)
        or contains_any(question_lower, ELIGIBILITY)
        or contains_any(question_lower, INTAKE)
        or contains_any(question_lower, DEPARTMENT)
        or contains_any(question_lower, ADMISSION)
        or contains_any(question_lower, SELECTION)
        or contains_any(question_lower, ENTRANCE)
    )
    is_follow_up = (
        (
        any(
          word in question_words
          for word in follow_up_words
        )
        and not explicit_programme
        )
        or (
            last_programme
            and follow_up_intent_words
            and not explicit_programme
        )
    )
    if is_follow_up and last_programme:
       print("FOLLOW-UP DETECTED BEFORE LLM CLASSIFICATION")
       print("Previous programme:", last_programme)
       answer = programme_response(user_question)
       if answer:
            print("Follow-up programme response received.")
            return answer

    #llm_classification = classify_with_llm(user_question)
    # Use the existing query router instead of LLM classification.

    
    # LLM CLASSIFICATION: Groq primary, Gemini fallback
    # llm_classification = classify_with_llm(user_question)
    
    # # Handle SP College affiliation using the normal classification.
    # if (
    #     llm_classification
    #     and llm_classification.get("intent") == "sp_college_affiliation"
    # ):
    #     return (
    #         "Sri Pratap College (SP College) is affiliated with "
    #         "<b>Cluster University Srinagar</b>.<br><br>"
    #         'For more information, visit the '
    #         '<a href="https://www.cusrinagar.edu.in/" '
    #         'target="_blank" rel="noopener noreferrer">'
    #         'official Cluster University Srinagar website</a>.'
    #     )
    # Reuse the classification performed at the beginning.


    # Keep the existing router as a fallback.
    query_type = qr.detect_query_type(user_question)
    programme_query = user_question

    if llm_classification:
        llm_intent = llm_classification.get("intent", "").lower().strip()

        print("\n===== LLM UNDERSTANDING =====")
        print("Intent:", llm_intent)
        print("Entity:", llm_classification.get("entity"))
        print("Question Type:", llm_classification.get("question_type"))
        print("Level:", llm_classification.get("level"))
 
        # Ask for clarification only when the classifier explicitly
        # determines that the question is ambiguous.
        if (
            llm_classification.get("needs_clarification")
            and llm_classification.get("clarification_question")
        ):
            return llm_classification["clarification_question"]

        valid_intents = {
            "programme",
            "college",
            "university",
            "admission",
            "pdf",
            "website",
            "general_ai",
        }

        if llm_intent in valid_intents:
            query_type = llm_intent

            # Convert the user's wording into a query understood
            # by the existing programme-response handler.
            if llm_intent == "programme":
                programme_query = build_canonical_query(
                    user_question,
                    llm_classification
                )

    print("Final Query Type:", query_type)
    print("Programme Query:", programme_query)


    # llm_classification = None
    # query_type = qr.detect_query_type(user_question)
    # print("LLM classification disabled for CUS.")
    # print("Final Query Type:", query_type)
    # programme_query = user_question
    # if llm_classification:
        
    #     # HANDLE LLM-IDENTIFIED CLARIFICATION
    #     needs_clarification = llm_classification.get(
    #         "needs_clarification",
    #         False
    #     )

    #     clarification_question = llm_classification.get(
    #         "clarification_question",
    #         ""
    #     )

    #     if needs_clarification and clarification_question:
    #         print("LLM REQUESTED CLARIFICATION.")
    #         print("Clarification:", clarification_question)
    #         return clarification_question

    #     print("LLM clarification not required.")

    #     llm_intent = llm_classification.get("intent")
    #     llm_entity = llm_classification.get("entity")
    #     llm_question_type = llm_classification.get(
    #         "question_type"
    #     )
    #     llm_level = llm_classification.get("level")
    #     print("\n===== LLM UNDERSTANDING =====")
    #     print("Intent:", llm_intent)
    #     print("Entity:", llm_entity)
    #     print("Question Type:", llm_question_type)
    #     print("Level:", llm_level)
    #     query_type = llm_intent
    # else:
    #     print("LLM classification unavailable.")
    #     print("Falling back to existing query router...")
    #     query_type = qr.detect_query_type(user_question)
    # print("Final Query Type:", query_type)
    # programme_query = build_canonical_query(
    #     user_question,
    #     llm_classification
    # )
    
    casual_response = get_casual_response(user_question)
    if casual_response:
        return casual_response
    
    

    # universityinfo
    
    if query_type == "university":
        return (
            "For university-related information, please visit "
            '<a href="https://www.cusrinagar.edu.in/" '
            'target="_blank" rel="noopener noreferrer">'
            "the official Cluster University Srinagar website</a>."
        )

    if query_type == "unknown_university":
        return (
            "This is an SP College website chatbot. "
            "Please ask questions about SP College only."
        )

    if query_type == "general_ai":
        return (
            "I'm specifically designed to assist with "
            "<b>SP College (Sri Pratap College)</b>. "
            "You can ask me about its programmes, admissions, "
            "departments, fees, faculty, contact details, "
            "notifications, and other college information."
        )


    #PROGRAMME 
    if query_type == "programme":
        answer = programme_response(programme_query)
        print("Programme Time:", time.time() - start)
        
        if answer and not explicit_programme_query:
            answer_lower = answer.lower()

            no_match_phrases = (
                "couldn't find a matching programme",
                "could not find a matching programme",
                "no matching programme",
                "programme was not found",
                "programme not found",
            )

            if any(
                phrase in answer_lower
                for phrase in no_match_phrases
            ):
                return (
                    "I couldn't find a matching programme in my "
                    "available Cluster University Srinagar records. "
                    "Please check the programme name or visit the "
                    '<a href="https://www.cusrinagar.edu.in/" '
                    'target="_blank" rel="noopener noreferrer">'
                    "official CUS website</a> for the current "
                    "programme list and admission information."
                )
        if answer:
            print("Official programme response received.")
            print("Generating grounded natural-language response...")
            grounded_answer = generate_grounded_response(
              user_question,
              answer
            )
            if grounded_answer:
              print("Grounded programme response generated.")
              return grounded_answer
            print(
              "Grounded response unavailable. "
              "Returning original programme response."
            )
            return answer
        
        return (
            "I couldn't find a matching programme in my available "
            "Cluster University Srinagar records. Please check the "
            '<a href="https://www.cusrinagar.edu.in/" '
            'target="_blank" rel="noopener noreferrer">'
            "official CUS website</a> for the current programme list "
            "and admission information. You can also try asking with "
            "the full programme name, such as <b>BSc IT</b>, <b>BEd</b>, "
            "<b>MSc physics</b>."
        )
    
    # COLLEGE
    if query_type == "college":
        answer = college_response(user_question)
        print("College Time:", time.time() - start)
        requested_entity = (
            llm_classification.get("entity", "")
            if llm_classification
            else ""
        )

        if answer and requested_entity:

            specific_words = []
            answer_text = ""
            entity_matches = False

            if answer and requested_entity:
                entity_words = re.findall(
                    r"[a-z0-9]+",
                    requested_entity.lower()
                )
                generic_words = {
                    "college", "colleges", "information", "details",
                    "about", "the", "of", "at", "under", "university",
                    "constituent"
                }
                specific_words = [
                    word for word in entity_words
                    if word not in generic_words
                ]

                answer_text = re.sub(
                    r"<[^>]*>", " ", answer.lower()
                )

                if "sp" in specific_words or "spc" in specific_words:
                    entity_matches = (
                        "sri pratap college" in answer_text
                        or "sp college" in answer_text
                        or "spc" in answer_text
                    )
                else:
                    entity_matches = any(
                        word in answer_text
                        for word in specific_words
                    )

                if specific_words and not entity_matches:
                    print(
                        "Returned college does not match the requested entity."
                    )
                    answer = None


        if answer:
            asks_for_details = any(
                phrase in user_question.lower()
                for phrase in (
                    "tell me about",
                    "information about",
                    "details about",
                    "give me information",
                    "overview of",
                )
            )
            if asks_for_details and len(answer.strip()) < 100:
                college_name = (
                    requested_entity
                    if requested_entity
                    else ""
                )

                if college_name:
                    answer = college_response(
                        f"tell me about {college_name}"
                    )
        if answer:
            return answer
        return (
            "I couldn't find sufficient verified information "
            "about that college in my available Cluster University "
            "Srinagar records. Please check the "
            '<a href="https://www.cusrinagar.edu.in/" '
            'target="_blank" rel="noopener noreferrer">'
            "official CUS website</a> for further details."
        )

    #KNOWLEDGE
    if query_type == "knowledge":
        topic, score = find_best_topic(user_question)
        print("Topic:", topic)
        print("Score:", score)
        if topic and score >= 0.50:
            topic_name = topic[1]
            print("Knowledge Time:", time.time() - start)
            return format_topic(topic_name)
        return (
            "I'm sorry, I couldn't find the requested information in my "
            "knowledge base. Please try asking about <b>Cluster University "
            "Srinagar</b>, its programmes, colleges, admissions, facilities, "
            "or other university-related information."
        )

    #PDF 
    if query_type == "pdf":
        question_lower = user_question.lower().strip()
        if (
            "prospectus" in question_lower
            and not any(
                word in question_lower
                for word in ["page", "pages"]
            )
        ):
            return (
               "📄 <b>Cluster University of Srinagar – E-Prospectus</b>\n\n"
               "The official university prospectus is available here.\n\n"
               '🔗 <a href="/prospectus" target="_blank">View Prospectus</a>'
            )
        pdf_result = search_pdf(user_question)
        print("PDF Time:", time.time() - start)
        if pdf_result:
           pdf_name, page, chunk = pdf_result
           if pdf_name.lower() == "prospectus.pdf":
            #question_lower = user_question.lower()
            #   import re
              page_match = re.search(
                r"\bpage\s*(?:no\.?|number)?\s*(\d+)\b",
                question_lower
              )
              if page_match:
                 requested_page = page_match.group(1)
                 return (
                    f"📄 <b>Cluster University of Srinagar – "
                    f"E-Prospectus</b>\n\n"
                    f"📑 <b>Page {requested_page}</b>\n\n"
                    f"{chunk[:2000]}\n\n"
                    f'🔗 <a href="/prospectus" target="_blank">'
                    f"View Full Prospectus</a>"
                )

              return (
                "📄 <b>Cluster University of Srinagar – "
                "E-Prospectus</b>\n\n"
                "The official university prospectus is available here.\n\n"
                '🔗 <a href="/prospectus" target="_blank">'
                "View Prospectus</a>"
              )

        # Other official PDF documents
           return (
            f"📄 <b>{pdf_name}</b>\n\n"
            f"📑 <b>Page:</b> {page}\n\n"
            f"{chunk[:2000]}"
        )

    # WEBSITE
    if query_type == "website":
        web_result = search_web_knowledge(user_question)
        print("Website Time:", time.time() - start)
        if not web_result:
            return(
                "I'm sorry, I couldn't find the requested information from the "
                "available official CUS website data. Please try again with a "
                "more specific query, or ask about the latest notifications, "
                "results, examinations, admissions, or other official updates."
            )

        # STRUCTURED WEBSITE DATA
        if isinstance(web_result, dict):
            result_type = web_result.get("type")
            items = web_result.get("items", [])

            # LATEST NOTIFICATIONS
            if result_type == "notifications":
                response = (
                    "🔔 <b>Latest Notifications – "
                    "Cluster University Srinagar</b>\n\n"
                )
                for item in items:
                    _, title, item_date, url = item
                    response += f"📌 <b>{title}</b>\n"
                    if item_date:
                        try:
                            display_date = datetime.strptime(
                              item_date,
                              "%Y-%m-%d"
                            ).strftime("%d-%B-%Y")
                        except ValueError:
                            display_date = item_date
                        response += f"📅 {display_date}\n"

                    if url:
                        response += (
                            f'🔗 <a href="{url}" target="_blank">'
                            "View Notification</a>\n"
                        )
                    response += "\n"
                response += (
                    "🌐 <b>Source:</b> "
                    '<a href="https://www.cusrinagar.edu.in/Notification/Notification" '
                    'target="_blank">Official CUS Notification Section</a>'
                )
                return response

            # EXAMINATION NOTIFICATIONS
            if result_type == "exam_notifications":
                response = (
                    "📝 <b>Latest Examination Notifications – "
                    "Cluster University Srinagar</b>\n\n"
                )
                for item in items:
                    item_type, title, item_date, url = item
                    response += f"📌 <b>{title}</b>\n"
                    if item_date:   
                        try:
                            display_date = datetime.strptime(
                               item_date,
                               "%Y-%m-%d"
                            ).strftime("%d-%B-%Y")
                        except ValueError:
                            display_date = item_date
                        response += f"📅 {display_date}\n"
                        #response += f"📅 {item_date}\n"
                    if url:
                        response += (
                            f'🔗 <a href="{url}" target="_blank">'
                            "View Notification</a>\n"
                        )
                    response += "\n"
                response += (
                    "🌐 <b>Source:</b> "
                    '<a href="https://www.cusrinagar.edu.in/Notification/Notification" '
                    'target="_blank">Official CUS Notification Section</a>'
                )
                return response

            if result_type == "admission_notifications":
                response = (
                    "🎓 <b>Latest Admission Notifications – "
                    "Cluster University Srinagar</b>\n\n"
                )
                for item in items:
                    item_type, title, item_date, url = item
                    response += f"📌 <b>{title}</b>\n"
                    if item_date:
                      try:
                         display_date = datetime.strptime(
                         item_date,
                         "%Y-%m-%d"
                         ).strftime("%d-%B-%Y")
                      except ValueError:
                         display_date = item_date
                      response += f"📅 {display_date}\n"
                    if url:
                        response += (
                          f'🔗 <a href="{url}" target="_blank">'
                          "View Notification</a>\n"
                        )
                    response += "\n"
                response += (
                  "🌐 <b>Source:</b> "
                  '<a href="https://www.cusrinagar.edu.in/Notification/Notification" '
                  'target="_blank">Official CUS Notification Section</a>'
                )
                return response

            if result_type == "job_notifications":
                response = (
                "💼 <b>Latest Job Notifications – "
                "Cluster University Srinagar</b>\n\n"
                )
                for item in items:
                    item_type, title, item_date, url = item
                    response += f"📌 <b>{title}</b>\n"
                    if item_date:
                        try:
                            display_date = datetime.strptime(
                                item_date,
                                "%Y-%m-%d"
                                ).strftime("%d-%B-%Y")
                        except ValueError:
                            display_date = item_date
                        response += f"📅 {display_date}\n"
                    if url:
                        response += (
                        f'🔗 <a href="{url}" target="_blank">'
                        "View Notification</a>\n"
                        )
                    response += "\n"
                response += (
                       "🌐 <b>Source:</b> "
                       '<a href="https://www.cusrinagar.edu.in/Notification/Notification" '
                       'target="_blank">Official CUS Notification Section</a>'
                )
                return response

            # LATEST RESULTS
            if result_type == "results":
                response = (
                    "📊 <b>Latest Results – "
                    "Cluster University Srinagar</b>\n\n"
                )
                for item in items:
                    item_type, title, item_date, url = item
                    response += f"📌 <b>{title}</b>\n"
                    if item_date:
                        try:
                            display_date = datetime.strptime(
                                item_date,
                                "%Y-%m-%d"
                            ).strftime("%d-%B-%Y")
                        except ValueError:
                            display_date = item_date
                        response += f"📅 {display_date}\n"

                    if url:
                        response += (
                            f'🔗 <a href="{url}" target="_blank">'
                            "View Result</a>\n"
                        )
                    response += "\n"
                response += (
                    "🌐 <b>Source:</b> "
                    '<a href="https://www.cusrinagar.edu.in/Result/ResultNotification" '
                    'target="_blank">Official CUS Results Section</a>'
                )
                return response

        college, title, url, chunk, chunk_no = web_result

        return f"""
🌐 <b>{title}</b>

{chunk[:1500]}

<b>Source:</b>
<a href="{url}" target="_blank">{url}</a>
"""
    
        # GEMINI FALLBACK
    print("No suitable CUS-specific answer found.")
    return (
        "I'm sorry, I couldn't find that information in the available "
        "<b>Cluster University Srinagar</b> information. "
        "You can ask me about CUS programmes, constituent colleges, "
        "admissions, examinations, official documents, notifications, "
        "results, facilities, or other university-related information."
    )
    # return (
    #     "I'm sorry, I couldn't find the requested information in the "
    #     "available official documents. Please try a more specific question "
    #     "or mention the document, prospectus, policy, ordinance, or topic "
    #     "you are looking for."
    # )

def is_general_ai_question(question):
    question_lower = question.lower().strip()

    general_patterns = [
        "what is ",
        "what are ",
        "explain ",
        "define ",
        "meaning of ",
        "how does ",
        "how do ",
        "why is ",
        "why are ",
    ]

    university_terms = [
        "cluster university",
        "cus",
        "programme",
        "program",
        "course",
        "admission",
        "fee",
        "fees",
        "eligibility",
        "duration",
        "intake",
        "seat",
        "seats",
        "college",
        "department",
        "semester",
        "cuet",
        "cuset",
        "prospectus",
        "notification",
        "result",
        "examination",
        "exam",
        "syllabus",
    ]

    starts_as_general = any(
        question_lower.startswith(pattern)
        for pattern in general_patterns
    )

    mentions_university_info = any(
        term in question_lower
        for term in university_terms
    )

    return starts_as_general and not mentions_university_info